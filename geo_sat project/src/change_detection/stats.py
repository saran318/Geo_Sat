"""
Change Detection - Area Statistics and Visualization Module.
Calculates pixel-wise land cover statistics, area metrics (Hectares / km²),
net transition matrices, exports CSV summaries, and provides plot visualization helpers.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import rasterio
import pyproj
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info

import backend_config as bcfg

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_pixel_area(
    transform: rasterio.Affine,
    crs: rasterio.crs.CRS,
    width: int,
    height: int
) -> float:
    """
    Computes single pixel area in square meters from affine transform.
    Handles EPSG:4326 by projecting to local UTM.

    Args:
        transform (rasterio.Affine): Affine transform matrix of raster.
        crs (rasterio.crs.CRS): Coordinate Reference System of raster.
        width (int): Raster width in pixels.
        height (int): Raster height in pixels.

    Returns:
        float: Area of 1 pixel in square meters (m²).
    """
    if crs is None:
        raise ValueError("Raster CRS is missing. Cannot calculate area.")

    if crs.is_projected:
        pixel_width = abs(transform.a)
        pixel_height = abs(transform.e)
        return pixel_width * pixel_height
    elif crs.to_epsg() == 4326:
        # Reproject to local UTM
        min_lon = transform.c
        max_lat = transform.f
        max_lon = min_lon + transform.a * width
        min_lat = max_lat + transform.e * height
        
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2
        
        utm_crs_list = query_utm_crs_info(
            datum_name='WGS 84',
            area_of_interest=AreaOfInterest(center_lon, center_lat, center_lon, center_lat)
        )
        
        if not utm_crs_list:
            raise ValueError(f"Could not find UTM zone for coordinates ({center_lat}, {center_lon})")
            
        utm_crs = pyproj.CRS.from_epsg(utm_crs_list[0].code)
        transformer = pyproj.Transformer.from_crs(crs, utm_crs, always_xy=True)
        
        x0, y0 = transformer.transform(min_lon, min_lat)
        x1, y1 = transformer.transform(max_lon, max_lat)
        
        total_area = abs((x1 - x0) * (y1 - y0))
        return total_area / (width * height)
    else:
        raise ValueError(f"Unsupported CRS for area calculation: {crs}")


def compute_landcover_area_stats(
    array1: np.ndarray,
    array2: np.ndarray,
    transform: rasterio.Affine,
    crs: rasterio.crs.CRS,
    width: int,
    height: int,
    class_names: List[str] = bcfg.CLASS_NAMES,
    nodata_val: int = 255
) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Computes class-wise land cover area statistics and 2D transition matrix.

    Args:
        array1 (np.ndarray): Year 1 prediction array (H, W).
        array2 (np.ndarray): Year 2 prediction array (H, W).
        transform (rasterio.Affine): Raster spatial transform.
        crs (rasterio.crs.CRS): Coordinate Reference System of raster.
        width (int): Raster width in pixels.
        height (int): Raster height in pixels.
        class_names (List[str]): List of class names.
        nodata_val (int): Nodata value.

    Returns:
        Tuple[pd.DataFrame, np.ndarray]:
            - df_stats: Pandas DataFrame with area statistics in Hectares (ha) and km².
            - transition_matrix: 2D array of shape (num_classes, num_classes) containing transition pixel counts.
    """
    pixel_area_m2 = calculate_pixel_area(transform, crs, width, height)
    logger.info(f"Calculated pixel area: {pixel_area_m2:.4f} m2 for CRS {crs.to_string() if crs else 'None'}")
    num_classes = len(class_names)
    
    valid_mask = (array1 != nodata_val) & (array2 != nodata_val)
    
    # 1. Initialize transition matrix (rows = Year 1, cols = Year 2)
    transition_matrix = np.zeros((num_classes, num_classes), dtype=np.int64)

    for c1 in range(num_classes):
        for c2 in range(num_classes):
            mask = (array1 == c1) & (array2 == c2) & valid_mask
            transition_matrix[c1, c2] = np.sum(mask)

    # 2. Compute class summaries
    y1_counts = np.sum(transition_matrix, axis=1)  # Total in Year 1
    y2_counts = np.sum(transition_matrix, axis=0)  # Total in Year 2

    stats_list = []
    for idx, name in enumerate(class_names):
        count_y1 = y1_counts[idx]
        count_y2 = y2_counts[idx]
        
        area_y1_ha = (count_y1 * pixel_area_m2) / 10000.0
        area_y2_ha = (count_y2 * pixel_area_m2) / 10000.0
        net_change_ha = area_y2_ha - area_y1_ha
        
        pct_change = ((area_y2_ha - area_y1_ha) / area_y1_ha * 100.0) if area_y1_ha > 0 else 0.0
        
        stats_list.append({
            "class_index": idx,
            "class_name": name,
            "year1_pixels": count_y1,
            "year2_pixels": count_y2,
            "year1_area_ha": round(area_y1_ha, 2),
            "year2_area_ha": round(area_y2_ha, 2),
            "year1_area_km2": round(area_y1_ha / 100.0, 4),
            "year2_area_km2": round(area_y2_ha / 100.0, 4),
            "net_change_ha": round(net_change_ha, 2),
            "pct_change": round(pct_change, 2)
        })

    df_stats = pd.DataFrame(stats_list)
    return df_stats, transition_matrix


def export_area_stats_csv(df_stats: pd.DataFrame, output_csv_path: str) -> str:
    """
    Exports land cover area statistics DataFrame to CSV.

    Args:
        df_stats (pd.DataFrame): Area statistics DataFrame.
        output_csv_path (str): File destination path (e.g., area_stats.csv).

    Returns:
        str: CSV output path.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_csv_path)), exist_ok=True)
    df_stats.to_csv(output_csv_path, index=False)
    logger.info(f"Land cover area statistics exported to: {output_csv_path}")
    return output_csv_path


def plot_area_comparison(
    df_stats: pd.DataFrame,
    output_image_path: Optional[str] = None
) -> plt.Figure:
    """
    Generates a grouped bar chart comparing Year 1 vs Year 2 land cover area (Hectares).

    Args:
        df_stats (pd.DataFrame): Statistics dataframe.
        output_image_path (Optional[str]): Path to save chart image.

    Returns:
        plt.Figure: Matplotlib figure object.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(df_stats))
    width = 0.35

    rects1 = ax.bar(x - width/2, df_stats['year1_area_ha'], width, label='Year 1 (ha)', color='#4C72B0')
    rects2 = ax.bar(x + width/2, df_stats['year2_area_ha'], width, label='Year 2 (ha)', color='#55A868')

    ax.set_ylabel('Area (Hectares)')
    ax.set_title('Land Cover Area Comparison Across Years')
    ax.set_xticks(x)
    ax.set_xticklabels(df_stats['class_name'], rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()

    if output_image_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_image_path)), exist_ok=True)
        plt.savefig(output_image_path, dpi=300)
        logger.info(f"Area comparison plot saved to: {output_image_path}")

    return fig


def plot_transition_matrix(
    transition_matrix: np.ndarray,
    class_names: List[str] = bcfg.CLASS_NAMES,
    output_image_path: Optional[str] = None
) -> plt.Figure:
    """
    Generates a heatmap of class-to-class pixel transition count.

    Args:
        transition_matrix (np.ndarray): 2D transition matrix.
        class_names (List[str]): List of class labels.
        output_image_path (Optional[str]): Save destination.

    Returns:
        plt.Figure: Matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(
        transition_matrix,
        annot=True,
        fmt='d',
        cmap='YlGnBu',
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax
    )
    
    ax.set_title('Land Cover Transition Matrix (Pixel Count)')
    ax.set_xlabel('Year 2 Class (Target)')
    ax.set_ylabel('Year 1 Class (Source)')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    if output_image_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_image_path)), exist_ok=True)
        plt.savefig(output_image_path, dpi=300)
        logger.info(f"Transition matrix heatmap saved to: {output_image_path}")

    return fig
