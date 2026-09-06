"""
Google Earth Engine (GEE) Automated Sentinel-2 Downloader.
Queries, cloud-masks, median-composites, and downloads Sentinel-2 Surface Reflectance
bands (B2, B3, B4, B8) for a specified Region of Interest (ROI) and year.
Outputs GeoTIFF rasters compatible with Person 1's preprocessing pipeline.
"""

import os
import sys
import argparse
import logging
from typing import Dict, List, Tuple, Optional

# Ensure project root is in system path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

import backend_config as bcfg
import utils

logger = utils.get_logger(__name__)

# Default Region of Interest (Rome, Italy bounding box: [min_lon, min_lat, max_lon, max_lat])
DEFAULT_ROI = [12.45, 41.85, 12.55, 41.95]

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

        # Automatically extract from GOOGLE_APPLICATION_CREDENTIALS if set (e.g., in Colab)
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
    """
    Applies QA60 cloud bitmasking to Sentinel-2 image in GEE.

    Args:
        image (ee.Image): Raw Sentinel-2 image.

    Returns:
        ee.Image: Cloud-masked Sentinel-2 image.
    """
    import ee
    qa = image.select('QA60')
    # Bits 10 and 11 are clouds and cirrus, respectively.
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    # Both flags should be set to zero, indicating clear conditions.
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).add(
        qa.bitwiseAnd(cirrus_bit_mask).eq(0)
    )

    return image.updateMask(mask).divide(10000)

def download_sentinel2_gee(
    year: int,
    output_dir: str,
    roi_bbox: List[float] = DEFAULT_ROI,
    bands: List[str] = ["B2", "B3", "B4", "B8"],
    max_cloud_pct: int = 20
) -> Dict[str, str]:
    """
    Queries GEE for Sentinel-2 Level-2A surface reflectance, filters by ROI, date, and cloud cover,
    computes an annual median composite, and exports individual band GeoTIFFs.

    Args:
        year (int): Target acquisition year (e.g. 2020, 2023).
        output_dir (str): Destination directory for band GeoTIFF files.
        roi_bbox (List[float]): Bounding box [min_lon, min_lat, max_lon, max_lat].
        bands (List[str]): List of band names to extract.
        max_cloud_pct (int): Maximum cloud cover percentage filter.

    Returns:
        Dict[str, str]: Dictionary mapping band names to local file paths.
    """
    if not initialize_gee():
        raise RuntimeError("Google Earth Engine initialization failed.")

    import ee

    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Fetching Sentinel-2 composite for year {year} over ROI {roi_bbox}...")

    # Define GEE geometry
    geometry = ee.Geometry.BBox(roi_bbox[0], roi_bbox[1], roi_bbox[2], roi_bbox[3])
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    # Query Sentinel-2 Harmonized Surface Reflectance
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

    # Compute annual median composite and scale back to UINT16 for pipeline compatibility
    median_composite = s2_collection.median().multiply(10000).uint16().clip(geometry)

    downloaded_paths = {}
    for band in bands:
        band_image = median_composite.select(band)
        out_file = os.path.join(output_dir, f"{band}.tif")

        # Download URL generation via GEE GetDownloadURL API
        url = band_image.getDownloadURL({
            'name': f"{band}_{year}",
            'scale': 10,
            'crs': 'EPSG:4326',
            'region': geometry,
            'format': 'GEO_TIFF'
        })

        logger.info(f"Downloading {band} for {year} from GEE...")
        import requests
        resp = requests.get(url, stream=True)
        if resp.status_code == 200:
            with open(out_file, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            downloaded_paths[band] = os.path.abspath(out_file)
            logger.info(f"Saved {band} to {out_file}")
        else:
            raise IOError(f"Failed to download band {band} from GEE URL.")

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
