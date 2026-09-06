"""
Change Detection - Difference Map Generation Module.
Compares consecutive or multi-year land cover prediction GeoTIFFs pixel-by-pixel,
ensuring strict spatial alignment (CRS, transform, resolution) and producing
transition maps and change GeoTIFF exports.
"""

import os
import logging
from typing import Tuple, Dict, Any, Optional, List
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

import backend_config as bcfg

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def align_and_load_rasters(
    raster_path1: str,
    raster_path2: str
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Reads two GeoTIFF rasters and ensures they are perfectly aligned spatially.
    If dimensions, CRS, or transforms differ, reprojects raster 2 to match raster 1.

    Args:
        raster_path1 (str): Path to reference (Year 1) GeoTIFF map.
        raster_path2 (str): Path to comparison (Year 2) GeoTIFF map.

    Returns:
        Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
            (array1, array2_aligned, metadata_ref)
    """
    with rasterio.open(raster_path1) as src1:
        data1 = src1.read(1)
        meta1 = src1.meta.copy()

    with rasterio.open(raster_path2) as src2:
        data2 = src2.read(1)
        meta2 = src2.meta.copy()

    # Check if spatial properties match exactly
    if (meta1['crs'] == meta2['crs'] and 
        meta1['transform'] == meta2['transform'] and 
        data1.shape == data2.shape):
        logger.info("Rasters are natively aligned spatially.")
        return data1, data2, meta1

    logger.info("Spatial mismatch detected. Reprojecting and resampling Raster 2 to align with Raster 1...")
    
    # Destination array with reference shape
    data2_aligned = np.zeros(data1.shape, dtype=data1.dtype)

    reproject(
        source=data2,
        destination=data2_aligned,
        src_transform=meta2['transform'],
        src_crs=meta2['crs'],
        dst_transform=meta1['transform'],
        dst_crs=meta1['crs'],
        resampling=Resampling.nearest
    )

    return data1, data2_aligned, meta1


def generate_change_map(
    array_year1: np.ndarray,
    array_year2: np.ndarray,
    nodata_val: int = 255
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generates pixel-wise land cover change maps.

    Args:
        array_year1 (np.ndarray): 2D array of class indices for Year 1.
        array_year2 (np.ndarray): 2D array of class indices for Year 2.
        nodata_val (int): Nodata value to exclude from change analysis.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]:
            - binary_change (np.ndarray): 0 = unchanged, 1 = changed, 255 = nodata (uint8)
            - transition_codes (np.ndarray): from_class * 100 + to_class (uint16)
            - change_mask (np.ndarray): Boolean mask of valid changed pixels.
    """
    valid_mask = (array_year1 != nodata_val) & (array_year2 != nodata_val)
    
    # Binary change map: 0 = No change, 1 = Changed
    binary_change = np.full(array_year1.shape, nodata_val, dtype=np.uint8)
    changed_pixels = (array_year1 != array_year2) & valid_mask
    unchanged_pixels = (array_year1 == array_year2) & valid_mask

    binary_change[unchanged_pixels] = 0
    binary_change[changed_pixels] = 1

    # Unique transition code: from_class * 100 + to_class (e.g. Class 1 to Class 3 -> 103)
    transition_codes = np.full(array_year1.shape, 65535, dtype=np.uint16)
    transition_codes[valid_mask] = (array_year1[valid_mask].astype(np.uint16) * 100) + array_year2[valid_mask].astype(np.uint16)

    return binary_change, transition_codes, changed_pixels


def export_change_geotiff(
    output_path: str,
    binary_change: np.ndarray,
    transition_codes: np.ndarray,
    ref_meta: Dict[str, Any]
) -> str:
    """
    Exports binary change map and transition codes as a 2-band georeferenced GeoTIFF.

    Args:
        output_path (str): File destination path (e.g., change_2020_2021.tif).
        binary_change (np.ndarray): 1st band - 0=Unchanged, 1=Changed.
        transition_codes (np.ndarray): 2nd band - Transition codes.
        ref_meta (Dict[str, Any]): Reference raster metadata.

    Returns:
        str: Absolute path to saved GeoTIFF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    meta = ref_meta.copy()
    meta.update({
        'count': 2,
        'dtype': 'uint16',
        'nodata': 65535,
        'compress': 'lzw'
    })

    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(binary_change.astype(np.uint16), 1)
        dst.set_band_description(1, "Binary_Change_0Unchanged_1Changed")

        dst.write(transition_codes, 2)
        dst.set_band_description(2, "Transition_Code_From100To")

    logger.info(f"Change detection GeoTIFF exported to: {output_path}")
    return output_path


def compute_change_detection(
    raster_path1: str,
    raster_path2: str,
    output_change_geotiff: str
) -> Dict[str, Any]:
    """
    High-level function to run end-to-end change detection between two annual prediction rasters.

    Args:
        raster_path1 (str): Year 1 prediction GeoTIFF path.
        raster_path2 (str): Year 2 prediction GeoTIFF path.
        output_change_geotiff (str): Output change GeoTIFF file path.

    Returns:
        Dict[str, Any]: Summary dictionary with spatial and change statistics.
    """
    data1, data2_aligned, meta = align_and_load_rasters(raster_path1, raster_path2)
    binary_change, transition_codes, change_mask = generate_change_map(data1, data2_aligned)
    
    export_change_geotiff(output_change_geotiff, binary_change, transition_codes, meta)

    total_valid_pixels = np.sum((data1 != 255) & (data2_aligned != 255))
    changed_pixels = np.sum(change_mask)
    change_percentage = (changed_pixels / total_valid_pixels * 100.0) if total_valid_pixels > 0 else 0.0

    return {
        "status": "success",
        "output_geotiff": output_change_geotiff,
        "total_pixels": int(total_valid_pixels),
        "changed_pixels": int(changed_pixels),
        "unchanged_pixels": int(total_valid_pixels - changed_pixels),
        "change_percentage": round(change_percentage, 2)
    }
