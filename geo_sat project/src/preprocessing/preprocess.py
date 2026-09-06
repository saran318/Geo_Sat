"""
Data Preprocessing module for Sentinel-2 satellite images.
Memory-optimized for local execution in Antigravity IDE.
Compatible with Google Colab for Phase 3 training.
Includes Sentinel-2 SCL (Scene Classification Layer) cloud masking support.
"""

import gc
import logging
from typing import Dict, Any, Generator, Optional, List, Tuple

import numpy as np
import rasterio
from rasterio.windows import Window

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Standard Sentinel-2 SCL (Scene Classification Layer) invalid pixel codes
# 3: Cloud Shadows, 8: Cloud Medium Probability, 9: Cloud High Probability, 10: Thin Cirrus, 11: Snow
DEFAULT_INVALID_SCL_CODES = [3, 8, 9, 10, 11]

def validate_bands(band_paths: Dict[str, str]) -> Dict[str, Any]:
    """
    Validates that all provided bands have the exact same CRS, spatial dimensions,
    and affine transform.
    
    Args:
        band_paths (Dict[str, str]): Dictionary mapping band names (e.g., 'B2') to file paths.
        
    Returns:
        Dict[str, Any]: A dictionary containing 'crs', 'transform', 'width', and 'height'.
        
    Raises:
        ValueError: If any of the bands do not match in spatial properties.
    """
    if not band_paths:
        raise ValueError("Band paths dictionary is empty.")
    
    reference_meta = None
    ref_band = None
    
    for band_name, path in band_paths.items():
        try:
            with rasterio.open(path) as src:
                meta = {
                    'crs': src.crs,
                    'transform': src.transform,
                    'width': src.width,
                    'height': src.height
                }
                
                if reference_meta is None:
                    reference_meta = meta
                    ref_band = band_name
                else:
                    if meta['crs'] != reference_meta['crs']:
                        raise ValueError(f"CRS mismatch between {ref_band} and {band_name}")
                    if meta['transform'] != reference_meta['transform']:
                        raise ValueError(f"Transform mismatch between {ref_band} and {band_name}")
                    if meta['width'] != reference_meta['width'] or meta['height'] != reference_meta['height']:
                        raise ValueError(f"Dimension mismatch between {ref_band} and {band_name}")
        except rasterio.errors.RasterioIOError as e:
            logger.error(f"Failed to read {path}: {e}")
            raise
            
    return reference_meta

def load_scl_band(scl_path: str, window: Optional[Window] = None) -> np.ndarray:
    """
    Reads the Sentinel-2 Scene Classification Layer (SCL) band raster.
    
    Args:
        scl_path (str): Path to SCL band file.
        window (Optional[Window]): Optional spatial window to load.
        
    Returns:
        np.ndarray: 2D integer array containing SCL classification values.
    """
    with rasterio.open(scl_path) as src:
        if window is not None:
            scl_data = src.read(1, window=window)
        else:
            scl_data = src.read(1)
    return scl_data

def apply_scl_cloud_mask(
    bands_array: np.ndarray,
    scl_array: np.ndarray,
    invalid_codes: List[int] = DEFAULT_INVALID_SCL_CODES,
    fill_value: float = 0.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Applies cloud and shadow masking based on Sentinel-2 Scene Classification Layer (SCL).
    
    Args:
        bands_array (np.ndarray): Multi-spectral array of shape (H, W, C).
        scl_array (np.ndarray): SCL classification array of shape (H, W).
        invalid_codes (List[int]): SCL codes to treat as cloudy/shadow/invalid.
        fill_value (float): Replacement value for invalid pixels.
        
    Returns:
        Tuple[np.ndarray, np.ndarray]: (masked_bands_array, cloud_boolean_mask)
    """
    # Create boolean mask where True = cloud/shadow/invalid pixel
    cloud_mask = np.isin(scl_array, invalid_codes)
    
    masked_array = bands_array.copy()
    masked_array[cloud_mask] = fill_value
    
    cloud_pixel_pct = (np.sum(cloud_mask) / cloud_mask.size) * 100.0
    logger.debug(f"SCL Cloud Mask applied: {cloud_pixel_pct:.2f}% pixels masked as cloud/shadow.")
    
    return masked_array, cloud_mask

def load_bands(band_paths: Dict[str, str], window: Window = None) -> np.ndarray:
    """
    Lazily loads specified Sentinel-2 bands (e.g., B2, B3, B4, B8).
    
    Args:
        band_paths (Dict[str, str]): Dictionary with keys like 'B2', 'B3', 'B4', 'B8' and values as file paths.
        window (rasterio.windows.Window, optional): Window to read. If None, reads the whole image.
        
    Returns:
        np.ndarray: A stacked numpy array of shape (H, W, C).
    """
    validate_bands(band_paths)
    
    # Define expected order
    expected_bands = ['B2', 'B3', 'B4', 'B8']
    
    loaded_bands = []
    
    for band_name in expected_bands:
        if band_name not in band_paths:
            raise KeyError(f"Missing expected band: {band_name} in provided band paths.")
            
        with rasterio.open(band_paths[band_name]) as src:
            if window is not None:
                band_data = src.read(1, window=window)
            else:
                band_data = src.read(1)
            loaded_bands.append(band_data)
            
    # Stack along the last axis -> (H, W, 4)
    # Using np.dstack to efficiently stack along the 3rd dimension
    stacked = np.dstack(loaded_bands)
    
    # Explicitly delete the list to free memory before next steps
    del loaded_bands
    gc.collect()
    
    return stacked

def normalize_and_stack(bands_array: np.ndarray) -> np.ndarray:
    """
    Normalizes Sentinel-2 reflectance (divides by 10000), converts to float32,
    computes NDVI and NDWI, and returns a 6-channel stacked image.
    
    Channels output order: Blue (B2), Green (B3), Red (B4), NIR (B8), NDVI, NDWI
    
    Args:
        bands_array (np.ndarray): Input array of shape (H, W, 4) containing B2, B3, B4, B8.
        
    Returns:
        np.ndarray: Stacked array of shape (H, W, 6) in float32 format.
    """
    # Convert to float32 to save memory (avoid float64)
    bands_array = bands_array.astype(np.float32)
    
    # Normalize by 10000
    bands_array /= 10000.0
    
    # Extract individual bands
    blue = bands_array[:, :, 0]
    green = bands_array[:, :, 1]
    red = bands_array[:, :, 2]
    nir = bands_array[:, :, 3]
    
    # Calculate NDVI: (NIR - RED) / (NIR + RED + 1e-6)
    ndvi = (nir - red) / (nir + red + 1e-6)
    
    # Calculate NDWI: (GREEN - NIR) / (GREEN + NIR + 1e-6)
    ndwi = (green - nir) / (green + nir + 1e-6)
    
    # Expand dims for stacking
    ndvi = np.expand_dims(ndvi, axis=-1)
    ndwi = np.expand_dims(ndwi, axis=-1)
    
    # Stack all together: Blue, Green, Red, NIR, NDVI, NDWI
    final_stack = np.concatenate([bands_array, ndvi, ndwi], axis=-1)
    
    # Cleanup memory
    del bands_array
    del blue, green, red, nir, ndvi, ndwi
    gc.collect()
    
    return final_stack

def extract_patches(
    band_paths: Dict[str, str],
    patch_size: int = 64,
    stride: int = 32,
    scl_path: Optional[str] = None,
    max_cloud_pct: float = 30.0
) -> Generator[Dict[str, Any], None, None]:
    """
    Memory-efficient generator that yields patches from large satellite images.
    Uses rasterio window reading to avoid loading the entire image into RAM.
    Includes optional Sentinel-2 SCL cloud masking filtering.
    
    Args:
        band_paths (Dict[str, str]): Dictionary mapping bands to file paths.
        patch_size (int): The size of the patch (e.g., 64 for 64x64 patches).
        stride (int): The stride of the sliding window.
        scl_path (Optional[str]): Path to SCL band for cloud filtering.
        max_cloud_pct (float): Maximum cloud pixel percentage allowed to yield patch.
        
    Yields:
        Dict[str, Any]: A dictionary containing the 6-channel image patch and its coordinates.
    """
    meta = validate_bands(band_paths)
    width = meta['width']
    height = meta['height']
    
    for row_off in range(0, height - patch_size + 1, stride):
        for col_off in range(0, width - patch_size + 1, stride):
            window = Window(col_off, row_off, patch_size, patch_size)
            
            # Load only the specific window
            raw_bands = load_bands(band_paths, window=window)

            # Apply SCL cloud mask if SCL path provided
            is_cloudy = False
            cloud_pct = 0.0
            if scl_path and os.path.exists(scl_path):
                scl_data = load_scl_band(scl_path, window=window)
                raw_bands, cloud_mask = apply_scl_cloud_mask(raw_bands, scl_data)
                cloud_pct = (np.sum(cloud_mask) / cloud_mask.size) * 100.0
                if cloud_pct > max_cloud_pct:
                    is_cloudy = True

            if is_cloudy:
                logger.debug(f"Skipping patch at {(row_off, col_off)} due to high cloudiness ({cloud_pct:.1f}%).")
                del raw_bands
                continue
            
            # Process and compute NDVI/NDWI
            processed_patch = normalize_and_stack(raw_bands)
            
            # Delete raw_bands reference
            del raw_bands
            
            yield {
                "image_patch": processed_patch,
                "coords": (row_off, col_off, patch_size, patch_size),
                "cloud_pct": cloud_pct
            }
            
            # Clean up after yielding to ensure memory is released before the next iteration
            del processed_patch
            gc.collect()
