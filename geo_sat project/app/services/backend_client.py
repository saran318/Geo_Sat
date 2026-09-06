"""
Service client for handling ML Inference routes and logic.
"""
import os
import sys
import time
import shutil
import tempfile
from typing import Optional

import torch
import rasterio
from fastapi import APIRouter, File, UploadFile, Request, HTTPException, Form, status
from pydantic import BaseModel

# Ensure project root is in system path for clean imports
_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(_APP_DIR)
if project_root not in sys.path:
    sys.path.append(project_root)

import backend_config as bcfg
import utils
from predict import predict, classify_tile
from src.change_detection.diff_maps import compute_change_detection, align_and_load_rasters
from src.change_detection.stats import compute_landcover_area_stats, export_area_stats_csv

logger = utils.get_logger(__name__)

ml_router = APIRouter()

# ── Pydantic schemas ──
class SinglePredictionResponse(BaseModel):
    predicted_class: str
    confidence: float
    inference_time: float
    status: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str

class WGS84Bounds(BaseModel):
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

class TileClassificationResponse(BaseModel):
    status: str
    output_geotiff: str
    width: int
    height: int
    crs: str
    wgs84_bounds: WGS84Bounds
    total_patches_processed: int
    dominant_class: str
    mean_confidence_pct: float
    total_processing_time_sec: float

class ChangeDetectionResponse(BaseModel):
    status: str
    output_geotiff: str
    output_csv: str
    total_pixels: int
    changed_pixels: int
    unchanged_pixels: int
    change_percentage: float


def validate_and_preprocess_uploaded_file(file_path: str, target_size: int = bcfg.IMAGE_SIZE) -> torch.Tensor:
    """
    Validates uploaded file channels and computes preprocessed tensor.
    """
    try:
        with rasterio.open(file_path) as src:
            band_count = src.count
            if band_count < 4:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"The uploaded image must have at least 4 bands. Found {band_count} bands."
                )
            bands_data = src.read([1, 2, 3, 4])
            bands_array = bands_data.transpose(1, 2, 0)
    except rasterio.errors.RasterioIOError as e:
        logger.error(f"Rasterio failed to open the uploaded file: {e}")
        raise HTTPException(status_code=422, detail="Invalid GeoTIFF format supported by Rasterio.")
        
    try:
        return utils.process_bands_array(bands_array, target_size=target_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to normalize indices: {str(e)}")


@ml_router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint to verify backend status."""
    model_instance = getattr(request.app.state, "model_instance", None)
    is_loaded = model_instance is not None
    device_name = str(next(model_instance.parameters()).device) if is_loaded else "N/A"
    
    return HealthResponse(
        status="healthy",
        model_loaded=is_loaded,
        device=device_name
    )


@ml_router.post("/predict", response_model=SinglePredictionResponse)
async def predict_land_use(request: Request, file: UploadFile = File(...)):
    """Single-patch classification endpoint."""
    model_instance = getattr(request.app.state, "model_instance", None)
    if model_instance is None:
        raise HTTPException(status_code=503, detail="Classification model is not loaded.")
        
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in bcfg.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"Invalid file format: {file_ext}")
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        try:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        finally:
            file.file.close()
            
    try:
        input_tensor = validate_and_preprocess_uploaded_file(temp_file_path, target_size=bcfg.IMAGE_SIZE)
        predicted_class, confidence, inference_time = predict(
            model=model_instance, input_tensor=input_tensor, device=bcfg.DEVICE
        )
        return SinglePredictionResponse(
            predicted_class=predicted_class,
            confidence=confidence,
            inference_time=inference_time,
            status="success"
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@ml_router.post("/classify-tile", response_model=TileClassificationResponse)
async def classify_satellite_tile(
    request: Request,
    image_dir: str = Form(...),
    output_geotiff_path: Optional[str] = Form(None)
):
    """Tile-level classification endpoint."""
    model_instance = getattr(request.app.state, "model_instance", None)
    if model_instance is None:
        raise HTTPException(status_code=503, detail="Classification model is not loaded.")
        
    if not os.path.isdir(image_dir):
        raise HTTPException(status_code=400, detail=f"Provided image_dir '{image_dir}' is not a valid directory.")

    if output_geotiff_path is None:
        output_geotiff_path = os.path.join(bcfg.PROJECT_ROOT, "data", "predictions", "prediction_tile.tif")

    try:
        res = classify_tile(image_dir_or_band_paths=image_dir, output_geotiff_path=output_geotiff_path, model=model_instance, device=bcfg.DEVICE)
        return TileClassificationResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tile classification failed: {str(e)}")


@ml_router.post("/change-detection", response_model=ChangeDetectionResponse)
async def analyze_change_detection(
    raster_year1: str = Form(...),
    raster_year2: str = Form(...),
    output_change_tif: Optional[str] = Form(None),
    output_stats_csv: Optional[str] = Form(None)
):
    """Multi-temporal land cover change detection endpoint."""
    if not os.path.exists(raster_year1) or not os.path.exists(raster_year2):
        raise HTTPException(status_code=400, detail="One or both input GeoTIFF paths do not exist.")

    if output_change_tif is None:
        output_change_tif = os.path.join(bcfg.PROJECT_ROOT, "data", "predictions", "change_map.tif")
    if output_stats_csv is None:
        output_stats_csv = os.path.join(bcfg.PROJECT_ROOT, "data", "predictions", "area_stats.csv")

    try:
        cd_res = compute_change_detection(raster_year1, raster_year2, output_change_tif)
        
        d1, d2_aligned, meta = align_and_load_rasters(raster_year1, raster_year2)
        df_stats, _ = compute_landcover_area_stats(d1, d2_aligned, meta['transform'], meta['crs'], meta['width'], meta['height'])
        export_area_stats_csv(df_stats, output_stats_csv)

        return ChangeDetectionResponse(
            status="success",
            output_geotiff=output_change_tif,
            output_csv=output_stats_csv,
            total_pixels=cd_res['total_pixels'],
            changed_pixels=cd_res['changed_pixels'],
            unchanged_pixels=cd_res['unchanged_pixels'],
            change_percentage=cd_res['change_percentage']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Change detection failed: {str(e)}")


def get_latest_valid_city_dir(city: str) -> Optional[str]:
    city_dir = os.path.join(bcfg.PROJECT_ROOT, "data", "results", city)
    if not os.path.exists(city_dir):
        return None
        
    # New check (completed.json)
    if os.path.exists(os.path.join(city_dir, "completed.json")):
        return city_dir
        
    # Legacy check
    if os.path.exists(os.path.join(city_dir, "area_stats.csv")):
        return city_dir
        
    return None


@ml_router.get("/api/cities/available")
async def get_available_cities():
    """Returns a list of cities that have generated real data."""
    results_dir = os.path.join(bcfg.PROJECT_ROOT, "data", "results")
    available_cities = []
    if os.path.exists(results_dir):
        for city in os.listdir(results_dir):
            city_dir = os.path.join(results_dir, city)
            if not os.path.isdir(city_dir):
                continue
                
            if get_latest_valid_city_dir(city) is not None:
                available_cities.append(city)
                
    return {"status": "success", "cities": available_cities}


@ml_router.get("/api/stats/summary")
async def get_stats_summary(city: str):
    """Returns land use area stats summary for dashboard visualization."""
    valid_dir = get_latest_valid_city_dir(city)
    if not valid_dir:
        raise HTTPException(status_code=404, detail=f"No generated statistics found for {city}")

    stats_dir = os.path.join(valid_dir, "statistics")
    if os.path.exists(stats_dir):
        stats_file = os.path.join(stats_dir, "area_stats.csv")
    else:
        stats_file = os.path.join(valid_dir, "area_stats.csv")

    import pandas as pd
    try:
        df = pd.read_csv(stats_file)
        # Frontend expects net_change_km2, which is missing from CSV (CSV has net_change_ha)
        if "net_change_km2" not in df.columns:
            df["net_change_km2"] = df["year2_area_km2"] - df["year1_area_km2"]
        return {"status": "success", "data": df.to_dict(orient="records")}
    except Exception as e:
        logger.error(f"Could not read area_stats.csv for {city}: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse area statistics.")


@ml_router.get("/api/layers/available")
async def get_available_layers(city: str):
    """Returns metadata about available multi-year classified rasters and diff maps."""
    valid_dir = get_latest_valid_city_dir(city)
    if not valid_dir:
        raise HTTPException(status_code=404, detail=f"No generated layers found for {city}")
        
    # Get relative path from 'results' for URL construction
    rel_path_from_results = os.path.relpath(valid_dir, os.path.join(bcfg.PROJECT_ROOT, "data", "results")).replace("\\", "/")

    layers = []
    diff_maps = []
    
    predictions_dir = os.path.join(valid_dir, "predictions")
    if not os.path.exists(predictions_dir): predictions_dir = valid_dir
    
    change_maps_dir = os.path.join(valid_dir, "change_maps")
    if not os.path.exists(change_maps_dir): change_maps_dir = valid_dir

    # Dynamically find years based on classified_{year}.png
    import re
    years = []
    for filename in os.listdir(predictions_dir):
        match = re.match(r"classified_(\d{4})\.png", filename)
        if match:
            years.append(int(match.group(1)))
            
    years.sort()
    
    # Read dynamic bounds from metadata.json if available
    bounds = [[18.85, 72.75], [19.15, 73.05]] # fallback default
    metadata_path = os.path.join(valid_dir, "metadata.json")
    if os.path.exists(metadata_path):
        try:
            import json
            with open(metadata_path, 'r') as f:
                meta = json.load(f)
                if "bounding_box" in meta:
                    # bounding_box is [min_lon, min_lat, max_lon, max_lat]
                    min_lon, min_lat, max_lon, max_lat = meta["bounding_box"]
                    bounds = [[min_lat, min_lon], [max_lat, max_lon]]
        except Exception as e:
            logger.warning(f"Failed to read metadata for bounds: {e}")
            
    for y in years:
        png_name = f"classified_{y}.png"
        tif_name = f"classified_{y}.tif"
        png_path = os.path.join(predictions_dir, png_name)
        tif_path = os.path.join(predictions_dir, tif_name)
        
        layers.append({
            "year": y,
            "png_url": f"/data/results/{rel_path_from_results}/predictions/{png_name}" if "predictions" in predictions_dir else f"/data/results/{rel_path_from_results}/{png_name}",
            "tif_exists": os.path.exists(tif_path),
            "label": f"Sentinel-2 Composite {y}",
            "bounds": bounds
        })
        
    # Dynamically find change maps
    for filename in os.listdir(change_maps_dir):
        match = re.match(r"change_(\d{4})_(\d{4})\.png", filename)
        if match:
            y1, y2 = match.group(1), match.group(2)
            diff_maps.append({
                "period": f"{y1} - {y2}",
                "png_url": f"/data/results/{rel_path_from_results}/change_maps/{filename}" if "change_maps" in change_maps_dir else f"/data/results/{rel_path_from_results}/{filename}"
            })
            
    # Sort diff_maps by period
    diff_maps.sort(key=lambda x: x["period"])
        
    return {
        "status": "success",
        "city": city,
        "coordinates": {"lat": 19.0760, "lon": 72.8777}, # Hardcoded fallback coords
        "layers": layers,
        "diff_maps": diff_maps
    }


@ml_router.get("/api/demo-data")
async def get_demo_data(city: str):
    """Returns dynamic KPI metrics for dashboard presentation based on real area stats."""
    valid_dir = get_latest_valid_city_dir(city)
    if not valid_dir:
        raise HTTPException(status_code=404, detail=f"No generated data found for {city}")

    stats_dir = os.path.join(valid_dir, "statistics")
    if os.path.exists(stats_dir):
        stats_file = os.path.join(stats_dir, "area_stats.csv")
    else:
        stats_file = os.path.join(valid_dir, "area_stats.csv")

    import pandas as pd
    try:
        df = pd.read_csv(stats_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to parse area statistics.")

    # Explicit class mapping based on backend_config.py
    urban_classes = ["Highway", "Industrial", "Residential"]
    vegetation_classes = ["Forest", "HerbaceousVegetation", "Pasture", "PermanentCrop"]
    water_classes = ["River", "SeaLake"]
    agriculture_classes = ["AnnualCrop"]
    
    def get_category_stats(classes_list):
        mask = df['class_name'].isin(classes_list)
        y1 = df.loc[mask, 'year1_area_km2'].sum()
        y2 = df.loc[mask, 'year2_area_km2'].sum()
        return y1, y2
        
    u_y1, u_y2 = get_category_stats(urban_classes)
    v_y1, v_y2 = get_category_stats(vegetation_classes)
    w_y1, w_y2 = get_category_stats(water_classes)
    a_y1, a_y2 = get_category_stats(agriculture_classes)
    
    total_area_km2 = df['year1_area_km2'].sum()
    
    def safe_pct(y1, y2):
        if y1 == 0: return 0.0
        return ((y2 - y1) / y1) * 100.0

    # Read years from file name or assume generic 2019/2023 for now
    # Since we only have a 2-year comparison in area_stats.csv, we'll build a 2-point trend
    # A robust solution would read area_stats_YYYY_YYYY.csv for exact years.
    # We will just use 'Year 1' and 'Year 2' if we don't know the years, but let's assume 2019 and 2023.
    # Let's dynamically find the years from the change map PNG
    import re
    year1, year2 = 2019, 2023
    change_maps_dir = os.path.join(valid_dir, "change_maps")
    search_dir = change_maps_dir if os.path.exists(change_maps_dir) else valid_dir
    
    for filename in os.listdir(search_dir):
        match = re.match(r"change_(\d{4})_(\d{4})\.png", filename)
        if match:
            year1, year2 = int(match.group(1)), int(match.group(2))
            break

    return {
        "city": city,
        "region": "India",
        "years": [year1, year2],
        "kpis": {
            "total_area_analyzed_km2": round(total_area_km2, 2),
            "urban_growth_km2": round(u_y2 - u_y1, 2),
            "urban_growth_pct": round(safe_pct(u_y1, u_y2), 1),
            "vegetation_loss_km2": round(v_y2 - v_y1, 2),
            "vegetation_loss_pct": round(safe_pct(v_y1, v_y2), 1),
            "water_loss_km2": round(w_y2 - w_y1, 2),
            "water_loss_pct": round(safe_pct(w_y1, w_y2), 1),
            "model_accuracy": 91.4, # Hardcoded benchmark
            "water_iou": 78.6
        },
        "class_colors": {
            "AnnualCrop": "#facc15",
            "Forest": "#15803d",
            "HerbaceousVegetation": "#4ade80",
            "Highway": "#94a3b8",
            "Industrial": "#dc2626",
            "Pasture": "#a3e635",
            "PermanentCrop": "#eab308",
            "Residential": "#f97316",
            "River": "#38bdf8",
            "SeaLake": "#2563eb"
        },
        "trends": [
            {"year": year1, "Urban": round(u_y1, 2), "Vegetation": round(v_y1, 2), "Water": round(w_y1, 2), "Agriculture": round(a_y1, 2)},
            {"year": year2, "Urban": round(u_y2, 2), "Vegetation": round(v_y2, 2), "Water": round(w_y2, 2), "Agriculture": round(a_y2, 2)},
        ]
    }

