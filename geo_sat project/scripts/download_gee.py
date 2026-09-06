"""
Google Earth Engine (GEE) Automated Sentinel-2 Downloader.
Queries, cloud-masks, median-composites, and downloads Sentinel-2 Surface Reflectance
bands (B2, B3, B4, B8) for a specified Region of Interest (ROI) and year.
Outputs GeoTIFF rasters compatible with Person 1's preprocessing pipeline.
Implements robust adaptive tiling and HTTP backoff for large regions.
"""

import os
import sys
import argparse
import time
import requests
import rasterio
from rasterio.merge import merge
from typing import Dict, List, Tuple, Optional
import json

# Ensure project root is in system path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

import backend_config as bcfg
import utils

logger = utils.get_logger(__name__)

# Default Region of Interest (Rome, Italy bounding box)
DEFAULT_ROI = [12.45, 41.85, 12.55, 41.95]
TILE_SIZE_DEGREES = 0.05
MAX_DEPTH = 5


def initialize_gee() -> bool:
    """
    Initializes the Google Earth Engine API using service account credentials.
    Reads from .env if available.
    """
    try:
        import ee
        import os
        from dotenv import load_dotenv

        load_dotenv(os.path.join(bcfg.PROJECT_ROOT, ".env"))

        service_account = os.getenv("GEE_SERVICE_ACCOUNT")
        key_path = os.getenv("GEE_KEY_JSON_PATH")

        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not service_account and google_creds and os.path.exists(google_creds):
            import json
            try:
                with open(google_creds, 'r') as f:
                    creds_data = json.load(f)
                    service_account = creds_data.get("client_email")
                    key_path = google_creds
            except Exception as e:
                logger.error(f"Could not parse GOOGLE_APPLICATION_CREDENTIALS: {e}")

        if service_account and key_path:
            full_key_path = os.path.join(bcfg.PROJECT_ROOT, key_path)
            logger.info(f"Authenticating GEE with Service Account: {service_account}")
            credentials = ee.ServiceAccountCredentials(service_account, full_key_path)
            ee.Initialize(credentials)
            logger.info("Google Earth Engine initialized successfully via Service Account.")
            return True
        else:
            try:
                ee.Initialize()
                logger.info("Google Earth Engine initialized successfully via default credentials.")
                return True
            except Exception:
                logger.warning("GEE credentials not active. Attempting ee.Authenticate()...")
                ee.Authenticate()
                ee.Initialize()
                logger.info("Google Earth Engine authenticated and initialized.")
                return True
    except ImportError:
        logger.error("`earthengine-api` or `python-dotenv` is not installed.")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Google Earth Engine: {e}")
        return False


def mask_s2_clouds_gee(image):
    """Applies QA60 cloud bitmasking."""
    import ee
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).add(
        qa.bitwiseAnd(cirrus_bit_mask).eq(0)
    )
    return image.updateMask(mask).divide(10000)


def _validate_geotiff(path: str) -> bool:
    """Validates that a downloaded GeoTIFF is not corrupt and has valid bounds."""
    if not os.path.exists(path):
        return False
    if os.path.getsize(path) == 0:
        return False
    try:
        with rasterio.open(path) as src:
            if src.count < 1:
                return False
            if src.width == 0 or src.height == 0:
                return False
            # Ensure it is readable
            _ = src.read(1)
        return True
    except Exception:
        return False


def _download_http_with_retries(url: str, output_path: str, band: str, tile_id: str) -> bool:
    """Robust HTTP downloader with exponential backoff and 50MB error detection."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            # GEE download URLs are redirects, allow_redirects=True is critical
            response = requests.get(url, stream=True, timeout=(30, 300), allow_redirects=True)
            
            # Detect 50MB error embedded in JSON response if 400
            if response.status_code == 400:
                try:
                    error_json = response.json()
                    error_msg = error_json.get('error', {}).get('message', '')
                    if "Total request size" in error_msg and "must be less than or equal to 50331648 bytes" in error_msg:
                        logger.warning(f"GEE download size limit exceeded for {band} tile {tile_id}. Will require sub-tiling.")
                        return False # Return false to trigger adaptive sub-tiling
                except json.JSONDecodeError:
                    pass
                
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()
            content_length = response.headers.get("content-length")
            
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                logger.info(f"Expected download size for {band} tile {tile_id}: {size_mb:.2f} MB (Type: {content_type})")
            else:
                logger.info(f"Downloading {band} tile {tile_id}... (Type: {content_type})")

            tmp_path = output_path + ".tmp.tif"
            with open(tmp_path, "wb") as output_file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        output_file.write(chunk)

            if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
                raise OSError(f"Downloaded file is empty for {band} tile {tile_id}")

            duration = time.time() - start_time
            downloaded_mb = os.path.getsize(tmp_path) / (1024 * 1024)
            
            if _validate_geotiff(tmp_path):
                os.rename(tmp_path, output_path)
                logger.info(f"Successfully downloaded and validated {band} tile {tile_id} ({downloaded_mb:.2f} MB in {duration:.1f}s)")
                return True
            else:
                logger.error(f"Downloaded GeoTIFF is corrupt or invalid: {band} tile {tile_id}")
                os.remove(tmp_path)
                raise ValueError("Corrupt GeoTIFF")
                
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                # Log safe truncated response body for debugging
                body = e.response.text[:1000]
                logger.warning(f"HTTP {e.response.status_code} for {band} tile {tile_id}. Body: {body}")
                
                # Permanent errors: do not retry
                if e.response.status_code in [400, 401, 403, 404]:
                    raise OSError(f"Permanent HTTP {e.response.status_code} for {band}: {e}")
            
            wait = 2 ** attempt
            logger.warning(f"Download failed for {band} tile {tile_id} (Attempt {attempt+1}/{max_retries}): {e}. Retrying in {wait}s...")
            time.sleep(wait)
            
    raise OSError(f"Failed to download {band} tile {tile_id} after {max_retries} attempts.")


def download_region_recursive(
    band_image, 
    band_name: str, 
    year: int, 
    bbox: List[float], 
    output_dir: str, 
    tile_id: str = "0", 
    depth: int = 0
) -> List[str]:
    """
    Recursively downloads a bounding box. If it fails with the 50MB limit (returns False from HTTP downloader),
    it splits the bounding box into 4 quadrants and recursively downloads each.
    Returns a list of successfully downloaded GeoTIFF paths for this branch.
    """
    import ee
    
    tile_path = os.path.join(output_dir, f"{band_name}_{year}_tile_{tile_id}.tif")
    if _validate_geotiff(tile_path):
        logger.info(f"Skipping already downloaded and valid tile: {tile_path}")
        return [tile_path]

    min_lon, min_lat, max_lon, max_lat = bbox
    geometry = ee.Geometry.BBox(min_lon, min_lat, max_lon, max_lat)
    
    url = band_image.getDownloadURL({
        'name': f"{band_name}_{year}_{tile_id}",
        'scale': 10,
        'crs': 'EPSG:4326',
        'region': geometry,
        'format': 'GEO_TIFF'
    })
    
    # Try download. If False, it means 50MB limit was hit.
    try:
        success = _download_http_with_retries(url, tile_path, band_name, tile_id)
    except Exception as e:
        logger.error(f"Unrecoverable error during tile download: {e}")
        raise
        
    if success:
        return [tile_path]
        
    # If 50MB limit hit, we must subdivide
    if depth >= MAX_DEPTH:
        raise RuntimeError(f"Max recursive tile depth ({MAX_DEPTH}) reached for {band_name}. Tile is still >50MB at this small scale!")
        
    logger.info(f"Subdividing {band_name} tile {tile_id} (Depth {depth} -> {depth+1})...")
    mid_lon = (min_lon + max_lon) / 2.0
    mid_lat = (min_lat + max_lat) / 2.0
    
    # 4 Quadrants: bottom-left, bottom-right, top-left, top-right
    quads = [
        ([min_lon, min_lat, mid_lon, mid_lat], f"{tile_id}_bl"),
        ([mid_lon, min_lat, max_lon, mid_lat], f"{tile_id}_br"),
        ([min_lon, mid_lat, mid_lon, max_lat], f"{tile_id}_tl"),
        ([mid_lon, mid_lat, max_lon, max_lat], f"{tile_id}_tr")
    ]
    
    downloaded_paths = []
    for quad_bbox, quad_id in quads:
        paths = download_region_recursive(band_image, band_name, year, quad_bbox, output_dir, quad_id, depth+1)
        downloaded_paths.extend(paths)
        
    return downloaded_paths


def merge_tiles(tile_paths: List[str], output_path: str) -> bool:
    """Merges multiple GeoTIFF tiles into a single output raster safely."""
    if not tile_paths:
        return False
        
    if len(tile_paths) == 1:
        # Just rename/copy it directly
        os.rename(tile_paths[0], output_path)
        return True
        
    logger.info(f"Merging {len(tile_paths)} tiles into {output_path}...")
    src_files_to_mosaic = []
    try:
        for fp in tile_paths:
            src = rasterio.open(fp)
            src_files_to_mosaic.append(src)
            
        mosaic, out_trans = merge(src_files_to_mosaic)
        
        out_meta = src_files_to_mosaic[0].meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans
        })
        
        tmp_output = output_path + ".tmp.tif"
        with rasterio.open(tmp_output, "w", **out_meta) as dest:
            dest.write(mosaic)
            
        for src in src_files_to_mosaic:
            src.close()
            
        if _validate_geotiff(tmp_output):
            os.rename(tmp_output, output_path)
            # Cleanup tiles
            for fp in tile_paths:
                if os.path.exists(fp):
                    os.remove(fp)
            logger.info(f"Successfully merged tiles into {output_path}")
            return True
        else:
            logger.error(f"Merged GeoTIFF is invalid: {tmp_output}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to merge tiles: {e}")
        # Make sure to close resources
        for src in src_files_to_mosaic:
            if not src.closed:
                src.close()
        return False


def download_sentinel2_gee(
    year: int,
    output_dir: str,
    roi_bbox: List[float] = DEFAULT_ROI,
    bands: List[str] = ["B2", "B3", "B4", "B8"],
    max_cloud_pct: int = 20
) -> Dict[str, str]:
    """
    Robust adaptive GEE Sentinel-2 Downloader.
    """
    if not initialize_gee():
        raise RuntimeError("Google Earth Engine initialization failed.")

    import ee

    os.makedirs(output_dir, exist_ok=True)
    temp_tiles_dir = os.path.join(output_dir, "tiles_tmp")
    os.makedirs(temp_tiles_dir, exist_ok=True)
    
    logger.info(f"Fetching Sentinel-2 composite for year {year} over ROI {roi_bbox}...")

    geometry = ee.Geometry.BBox(roi_bbox[0], roi_bbox[1], roi_bbox[2], roi_bbox[3])
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    s2_collection = (
        ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_pct))
        .map(mask_s2_clouds_gee)
    )

    count = s2_collection.size().getInfo()
    logger.info(f"Found {count} Sentinel-2 scenes for year {year}.")

    if count == 0:
        raise ValueError(f"No Sentinel-2 scenes found for year {year} matching criteria.")

    median_composite = s2_collection.median().multiply(10000).uint16().clip(geometry)

    downloaded_paths = {}
    
    # Pre-split into initial grid based on TILE_SIZE_DEGREES
    min_lon, min_lat, max_lon, max_lat = roi_bbox
    lon_steps = max(1, int((max_lon - min_lon) / TILE_SIZE_DEGREES) + 1)
    lat_steps = max(1, int((max_lat - min_lat) / TILE_SIZE_DEGREES) + 1)
    
    initial_tiles = []
    lon_step_size = (max_lon - min_lon) / lon_steps
    lat_step_size = (max_lat - min_lat) / lat_steps
    
    for i in range(lon_steps):
        for j in range(lat_steps):
            t_min_lon = min_lon + i * lon_step_size
            t_max_lon = min_lon + (i + 1) * lon_step_size
            t_min_lat = min_lat + j * lat_step_size
            t_max_lat = min_lat + (j + 1) * lat_step_size
            initial_tiles.append([t_min_lon, t_min_lat, t_max_lon, t_max_lat])
            
    logger.info(f"Split ROI into {len(initial_tiles)} initial tiles.")

    for band in bands:
        final_band_path = os.path.join(output_dir, f"{band}.tif")
        
        # Resumability: check if final file already exists and is valid
        if _validate_geotiff(final_band_path):
            logger.info(f"Band {band} already fully downloaded and valid at {final_band_path}. Skipping.")
            downloaded_paths[band] = os.path.abspath(final_band_path)
            continue
            
        band_image = median_composite.select(band)
        all_band_tile_paths = []
        
        # Download all initial tiles
        for t_idx, t_bbox in enumerate(initial_tiles):
            paths = download_region_recursive(
                band_image=band_image,
                band_name=band,
                year=year,
                bbox=t_bbox,
                output_dir=temp_tiles_dir,
                tile_id=f"T{t_idx}",
                depth=0
            )
            all_band_tile_paths.extend(paths)
            
        # Merge them
        if merge_tiles(all_band_tile_paths, final_band_path):
            downloaded_paths[band] = os.path.abspath(final_band_path)
        else:
            raise IOError(f"Failed to merge tiles for band {band}")

    return downloaded_paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Earth Engine Sentinel-2 Tile Downloader")
    parser.add_argument("--year", type=int, default=2023, help="Acquisition year (e.g. 2020 or 2023)")
    parser.add_argument("--out_dir", type=str, default=None, help="Output directory for band GeoTIFFs")
    parser.add_argument("--roi", type=str, default="12.45,41.85,12.55,41.95", help="Bounding box as min_lon,min_lat,max_lon,max_lat (default is Rome)")
    args = parser.parse_args()

    roi_list = [float(x.strip()) for x in args.roi.split(",")]
    target_dir = args.out_dir or os.path.join(bcfg.PROJECT_ROOT, "data", "raw", "sentinel2", str(args.year))
    
    try:
        paths = download_sentinel2_gee(year=args.year, output_dir=target_dir, roi_bbox=roi_list)
        print("\n" + "=" * 45)
        print(" GEE DOWNLOAD COMPLETE")
        print("=" * 45)
        for b, p in paths.items():
            print(f" {b} -> {p}")
        print("=" * 45 + "\n")
    except Exception as e:
        logger.error(f"GEE Script Execution failed: {e}")
        sys.exit(1)
