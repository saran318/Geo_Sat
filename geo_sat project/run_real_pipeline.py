import os
import sys
import argparse
import subprocess
import time
import pandas as pd
import rasterio
import numpy as np
from PIL import Image
import json
import datetime

# Ensure project root is in system path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

import backend_config as bcfg
import utils
from src.inference.predict import classify_tile, load_inference_model
from src.change_detection.diff_maps import compute_change_detection, align_and_load_rasters
from src.change_detection.stats import compute_landcover_area_stats, export_area_stats_csv
from scripts.download_gee import download_sentinel2_gee, initialize_gee

logger = utils.get_logger(__name__)

# Load cities config
cities_config_path = os.path.join(bcfg.PROJECT_ROOT, "config", "cities.json")
with open(cities_config_path, "r") as f:
    CITIES_CONFIG = json.load(f)

# Keep CITIES dictionary compatible with existing code but extract bbox from json
CITIES = {name: data["bbox"] for name, data in CITIES_CONFIG.items()}

def colorize_class_map(tif_path: str, png_path: str):
    """Converts a 1-band class index TIF into a colored PNG for the frontend."""
    import rasterio
    import numpy as np
    
    # These colors match the frontend class_colors
    color_map = {
        0: (250, 204, 21),   # AnnualCrop #facc15
        1: (21, 128, 61),    # Forest #15803d
        2: (74, 222, 128),   # HerbaceousVegetation #4ade80
        3: (148, 163, 184),  # Highway #94a3b8
        4: (220, 38, 38),    # Industrial #dc2626
        5: (163, 230, 53),   # Pasture #a3e635
        6: (234, 179, 8),    # PermanentCrop #eab308
        7: (249, 115, 22),   # Residential #f97316
        8: (56, 189, 248),   # River #38bdf8
        9: (37, 99, 235),    # SeaLake #2563eb
        255: (0, 0, 0)       # NoData
    }
    
    with rasterio.open(tif_path) as src:
        data = src.read(1)
        
    height, width = data.shape
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    
    for class_idx, color in color_map.items():
        mask = (data == class_idx)
        rgba[mask, 0] = color[0]
        rgba[mask, 1] = color[1]
        rgba[mask, 2] = color[2]
        rgba[mask, 3] = 200 if class_idx != 255 else 0
        
    img = Image.fromarray(rgba)
    img.save(png_path)
    logger.info(f"Colorized PNG saved to {png_path}")

def run_pipeline(city: str, years: list, batch_size: int = 32):
    if city not in CITIES:
        logger.error(f"City '{city}' not found in predefined ROIs. Available: {list(CITIES.keys())}")
        sys.exit(1)
        
    if len(years) != 2:
        logger.error("Exactly two years must be provided (e.g., --years 2019 2023).")
        sys.exit(1)
        
    years = sorted(years)
    y1, y2 = years[0], years[1]
        
    roi = CITIES[city]
    logger.info(f"Starting Batch Pipeline for {city} ({y1}-{y2}) with ROI {roi}")
    
    start_time = datetime.datetime.now()
    
    # Output directories
    results_dir = os.path.join(bcfg.PROJECT_ROOT, "data", "results", city)
    predictions_dir = os.path.join(results_dir, "predictions")
    change_maps_dir = os.path.join(results_dir, "change_maps")
    stats_dir = os.path.join(results_dir, "statistics")
    
    os.makedirs(predictions_dir, exist_ok=True)
    os.makedirs(change_maps_dir, exist_ok=True)
    os.makedirs(stats_dir, exist_ok=True)
    
    # Load model once
    model = load_inference_model(model_path=bcfg.MODEL_PATH, device=bcfg.DEVICE)
    
    tif_paths = {}
    patch_counts = {}
    
    for year in years:
        logger.info(f"--- Processing Year: {year} ---")
        
        # 1. Download data
        target_dir = os.path.join(bcfg.PROJECT_ROOT, "data", "raw", "sentinel2", str(year))
        os.makedirs(target_dir, exist_ok=True)
        download_sentinel2_gee(year=year, output_dir=target_dir, roi_bbox=roi)
        
        # Validate Raw Bands
        expected_bands = ['B2.tif', 'B3.tif', 'B4.tif', 'B8.tif']
        for band_file in expected_bands:
            band_path = os.path.join(target_dir, band_file)
            if not os.path.exists(band_path):
                logger.error(f"Validation failed: Raw band missing: {band_path}")
                sys.exit(1)
            
            try:
                with rasterio.open(band_path) as src:
                    if src.count < 1:
                        logger.error(f"Validation failed: {band_path} has no bands.")
                        sys.exit(1)
                    data = src.read(1)
                    if (src.nodata is not None and np.all(data == src.nodata)) or np.all(data == 0):
                        logger.error(f"Validation failed: {band_path} contains only empty/nodata.")
                        sys.exit(1)
            except Exception as e:
                logger.error(f"Validation failed: Could not open {band_path}: {e}")
                sys.exit(1)
                
        # 2. Run Inference
        out_tif = os.path.join(predictions_dir, f"classified_{year}.tif")
        out_png = os.path.join(predictions_dir, f"classified_{year}.png")
        
        res = classify_tile(
            image_dir_or_band_paths=target_dir,
            output_geotiff_path=out_tif,
            model=model,
            device=bcfg.DEVICE,
            batch_size=batch_size
        )
        
        patch_counts[year] = res.get("total_patches_processed", 0)
        
        # 3. Colorize for frontend
        colorize_class_map(out_tif, out_png)
        tif_paths[year] = out_tif

    # 4. Change Detection & Stats
    logger.info(f"--- Computing Change Detection for {y1} - {y2} ---")
    
    diff_tif = os.path.join(change_maps_dir, f"change_{y1}_{y2}.tif")
    diff_png = os.path.join(change_maps_dir, f"change_{y1}_{y2}.png")
    stats_csv = os.path.join(stats_dir, f"area_stats_{y1}_{y2}.csv")
    main_stats = os.path.join(stats_dir, "area_stats.csv")
    
    compute_change_detection(tif_paths[y1], tif_paths[y2], diff_tif)
    
    # Create a simple red visualization for change map
    with rasterio.open(diff_tif) as src:
        diff_data = src.read(1)
    h, w = diff_data.shape
    diff_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    diff_rgba[diff_data == 1] = [255, 0, 0, 180] # Changed pixels = Red
    Image.fromarray(diff_rgba).save(diff_png)
    
    # Generate stats
    d1, d2_aligned, meta = align_and_load_rasters(tif_paths[y1], tif_paths[y2])
    df_stats, _ = compute_landcover_area_stats(d1, d2_aligned, meta['transform'], meta['crs'], meta['width'], meta['height'])
    
    export_area_stats_csv(df_stats, main_stats)
    export_area_stats_csv(df_stats, stats_csv)
    
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Generate metadata.json
    metadata = {
        "city": city,
        "first_year": y1,
        "second_year": y2,
        "bounding_box": roi,
        "crs": str(meta["crs"]),
        "image_resolution": f"{meta['width']}x{meta['height']}",
        "model_name": bcfg.MODEL_NAME,
        "input_channels": 6,
        "output_classes": bcfg.NUM_CLASSES,
        "patch_count": max(patch_counts.values()) if patch_counts else 0,
        "start_time": start_time.isoformat(),
        "completion_time": end_time.isoformat(),
        "processing_duration_sec": round(duration, 2),
        "output_file_list": os.listdir(results_dir),
        "processing_status": "success"
    }
    
    metadata_path = os.path.join(results_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
        
    # Validate files exist before creating completed.json
    expected_files = [
        metadata_path,
        os.path.join(predictions_dir, f"classified_{y1}.tif"),
        os.path.join(predictions_dir, f"classified_{y2}.tif"),
        os.path.join(change_maps_dir, f"change_{y1}_{y2}.tif"),
        os.path.join(stats_dir, "area_stats.csv")
    ]
    all_exist = all(os.path.exists(f) for f in expected_files)
    
    if all_exist:
        with open(os.path.join(results_dir, "completed.json"), "w") as f:
            json.dump({"status": "completed", "time": end_time.isoformat()}, f, indent=4)
        logger.info(f"Pipeline Complete! Check {results_dir} folder.")
    else:
        logger.error(f"Validation failed: Not all expected output files exist in {results_dir}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", type=str, default="Mumbai", help="Target city (e.g. Mumbai)")
    parser.add_argument("--years", nargs="+", type=int, default=[2019, 2023], help="Exactly two years to process")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for GPU inference")
    args = parser.parse_args()
    
    run_pipeline(args.city, args.years, args.batch_size)
