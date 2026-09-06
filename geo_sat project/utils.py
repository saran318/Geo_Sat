"""
Utility functions for the Person 2 Backend & Inference module.
Provides reusable helpers for logging setup, Sentinel-2 band file discovery,
common tensor transformations, automatic model weight download, and WGS84 CRS transformations.
"""

import os
import sys
import logging
import requests
from typing import Dict, Optional, Tuple, Any

import numpy as np
import torch
import torch.nn.functional as F
import rasterio
from rasterio.warp import transform_bounds

import backend_config as bcfg
from src.preprocessing.preprocess import normalize_and_stack

def get_logger(name: str) -> logging.Logger:
    """
    Initializes and returns a configured logger instance.
    
    Args:
        name (str): Name of the logger (typically __name__).
        
    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    # Prevent duplicate handlers if logger is re-initialized
    if not logger.handlers:
        logger.setLevel(bcfg.LOG_LEVEL)
        
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(bcfg.LOG_FORMAT)
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        # Avoid propagation to root logger to prevent duplicated messages
        logger.propagate = False
        
    return logger

logger = get_logger(__name__)

def download_model_weights_if_missing(
    model_path: str = bcfg.MODEL_PATH,
    url: str = bcfg.MODEL_DOWNLOAD_URL
) -> bool:
    """
    Downloads trained ResNet50 model weights from GitHub Releases if missing locally.

    Args:
        model_path (str): Destination file path for model weights.
        url (str): Remote download URL.

    Returns:
        bool: True if model is ready/downloaded, False otherwise.
    """
    if os.path.exists(model_path) and os.path.getsize(model_path) > 0:
        logger.info(f"Model checkpoint found locally at: {model_path}")
        return True

    logger.warning(f"Model weights not found at '{model_path}'. Attempting auto-download from: {url}")
    os.makedirs(os.path.dirname(os.path.abspath(model_path)), exist_ok=True)

    try:
        response = requests.get(url, stream=True, timeout=60)
        if response.status_code == 200:
            with open(model_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            logger.info(f"Successfully downloaded model weights to: {model_path}")
            return True
        else:
            logger.error(f"Failed to download model weights. Server returned HTTP status: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error during automatic model weight download: {e}")
        return False

def get_raster_wgs84_bounds(file_path_or_meta: Any) -> Dict[str, float]:
    """
    Calculates geographic bounding box coordinates in WGS84 (EPSG:4326) [min_lon, min_lat, max_lon, max_lat]
    for web map overlay visualization (Leaflet/Mapbox).

    Args:
        file_path_or_meta (Any): Path to GeoTIFF raster file OR rasterio metadata dictionary.

    Returns:
        Dict[str, float]: Bounding box dictionary: {'min_lon', 'min_lat', 'max_lon', 'max_lat'}.
    """
    if isinstance(file_path_or_meta, str):
        with rasterio.open(file_path_or_meta) as src:
            src_crs = src.crs
            bounds = src.bounds
    else:
        src_crs = file_path_or_meta['crs']
        width, height = file_path_or_meta['width'], file_path_or_meta['height']
        transform = file_path_or_meta['transform']
        left, bottom = transform * (0, height)
        right, top = transform * (width, 0)
        bounds = (left, bottom, right, top)

    # Transform coordinates to WGS84 (EPSG:4326)
    wgs84_bounds = transform_bounds(src_crs, 'EPSG:4326', *bounds)
    
    return {
        "min_lon": round(wgs84_bounds[0], 6),
        "min_lat": round(wgs84_bounds[1], 6),
        "max_lon": round(wgs84_bounds[2], 6),
        "max_lat": round(wgs84_bounds[3], 6)
    }

def find_sentinel_bands(image_dir: str) -> Dict[str, str]:
    """
    Scans a directory for the required Sentinel-2 band files (B2, B3, B4, B8).
    Supports common raster extensions defined in backend_config.py.
    Prioritizes exact matches and word boundaries to prevent matching wrong bands
    (e.g., B8A matching as B8).
    
    Args:
        image_dir (str): Path to the directory containing the satellite bands.
        
    Returns:
        Dict[str, str]: Map of band names to their absolute file paths.
        
    Raises:
        ValueError: If image_dir is not a valid directory.
        FileNotFoundError: If any of the required bands (B2, B3, B4, B8) are missing.
    """
    if not os.path.isdir(image_dir):
        raise ValueError(f"Provided path is not a directory: {image_dir}")
        
    required_bands = ["B2", "B3", "B4", "B8"]
    band_paths: Dict[str, str] = {}
    
    # Scan directory contents
    files = os.listdir(image_dir)
    
    for band in required_bands:
        match = None
        # Pass 1: Exact case-insensitive match (e.g. B2.tif, b2.tiff)
        for f in files:
            name, ext = os.path.splitext(f)
            if ext.lower() in bcfg.SUPPORTED_FORMATS and name.upper() == band.upper():
                match = f
                break
                
        # Pass 2: Suffix match with clear boundaries (e.g. sentinel_B2.tif, band-B2.tif)
        if not match:
            for f in files:
                name, ext = os.path.splitext(f)
                if ext.lower() in bcfg.SUPPORTED_FORMATS:
                    name_upper = name.upper()
                    if name_upper.endswith(f"_{band.upper()}") or name_upper.endswith(f"-{band.upper()}"):
                        match = f
                        break
                        
        # Pass 3: General token boundary match fallback
        if not match:
            for f in files:
                name, ext = os.path.splitext(f)
                if ext.lower() in bcfg.SUPPORTED_FORMATS:
                    tokens = name.replace("_", " ").replace("-", " ").upper().split()
                    if band.upper() in tokens:
                        match = f
                        break
        
        if match:
            band_paths[band] = os.path.abspath(os.path.join(image_dir, match))
        else:
            # Pass 4: Direct fallback check (e.g. B2.tif, B2.jp2)
            for ext in bcfg.SUPPORTED_FORMATS:
                test_path = os.path.join(image_dir, f"{band}{ext}")
                if os.path.exists(test_path):
                    band_paths[band] = os.path.abspath(test_path)
                    break
                    
    # Validate that all 4 bands are present
    missing_bands = [b for b in required_bands if b not in band_paths]
    if missing_bands:
        raise FileNotFoundError(
            f"Missing required band files in '{image_dir}': {missing_bands}. "
            f"Please ensure B2, B3, B4, and B8 exist in supported formats: {bcfg.SUPPORTED_FORMATS}"
        )
        
    return band_paths

def process_bands_array(bands_array: np.ndarray, target_size: int = 64) -> torch.Tensor:
    """
    Applies the common preprocessing pipeline to a raw stacked band array.
    Normalizes inputs, computes NDVI/NDWI, transposes to channels-first (C, H, W),
    resizes to target dimensions, and adds a batch dimension.
    
    Args:
        bands_array (np.ndarray): Stacked band array of shape (H, W, 4).
        target_size (int): Target spatial dimension expected by the model.
        
    Returns:
        torch.Tensor: Preprocessed tensor of shape (1, 6, target_size, target_size).
    """
    # 1. Compute NDVI/NDWI and stack -> (H, W, 6)
    processed_array = normalize_and_stack(bands_array)
    
    # 2. Transpose to PyTorch layout: channels-first -> (6, H, W)
    transposed = processed_array.transpose(2, 0, 1)
    
    # 3. Convert to FloatTensor
    tensor_img = torch.from_numpy(transposed).float()
    
    # 4. Resize spatially if dimensions differ from target input size (64x64)
    tensor_img = tensor_img.unsqueeze(0)  # Shape: (1, 6, H, W)
    
    _, _, h, w = tensor_img.shape
    if h != target_size or w != target_size:
        logger.info(f"Resizing tensor from {h}x{w} to model-expected {target_size}x{target_size}")
        tensor_img = F.interpolate(tensor_img, size=(target_size, target_size), mode="bilinear", align_corners=False)
        
    return tensor_img
