"""
Stitching and Georeferencing Module for Satellite Image Inference.
Reconstructs spatial predictions from patch-level sliding window inferences into a single
georeferenced GeoTIFF (preserving CRS, affine transform, spatial extent, and pixel resolution).
"""

import os
import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import rasterio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TileStitcher:
    """
    Reconstructs patch predictions into full-extent GeoTIFF maps.
    Supports majority voting and probability accumulation for overlapping sliding windows.
    """

    def __init__(self, meta: Dict[str, Any], num_classes: int = 10):
        """
        Args:
            meta (Dict[str, Any]): Raster metadata dictionary containing 'width', 'height',
                                   'crs', and 'transform'.
            num_classes (int): Total number of land-use target classes.
        """
        self.meta = meta
        self.width = meta['width']
        self.height = meta['height']
        self.crs = meta['crs']
        self.transform = meta['transform']
        self.num_classes = num_classes

        # Accumulator arrays for overlapping patch predictions
        self.class_counts = np.zeros((self.height, self.width, self.num_classes), dtype=np.float32)
        self.confidence_sum = np.zeros((self.height, self.width), dtype=np.float32)
        self.patch_coverage = np.zeros((self.height, self.width), dtype=np.int32)

    def add_patch_prediction(
        self,
        coords: Tuple[int, int, int, int],
        predicted_class_idx: int,
        confidence: float,
        probs: Optional[np.ndarray] = None
    ) -> None:
        """
        Accumulates a single patch prediction into the global spatial grid.

        Args:
            coords (Tuple[int, int, int, int]): (row_off, col_off, patch_h, patch_w).
            predicted_class_idx (int): Predicted class index (0-9).
            confidence (float): Confidence score (percentage 0-100 or probability 0-1).
            probs (Optional[np.ndarray]): Probability vector of shape (num_classes,) or patch grid.
        """
        row_off, col_off, patch_h, patch_w = coords
        row_end = min(row_off + patch_h, self.height)
        col_end = min(col_off + patch_w, self.width)

        if probs is not None:
            if probs.ndim == 1:
                # Uniform probability broadcast over patch
                self.class_counts[row_off:row_end, col_off:col_end, :] += probs
            elif probs.ndim == 3:
                # Spatial probability grid
                self.class_counts[row_off:row_end, col_off:col_end, :] += probs[:row_end-row_off, :col_end-col_off, :]
        else:
            self.class_counts[row_off:row_end, col_off:col_end, predicted_class_idx] += 1.0

        self.confidence_sum[row_off:row_end, col_off:col_end] += confidence
        self.patch_coverage[row_off:row_end, col_off:col_end] += 1

    def finalize(self, nodata_val: int = 255) -> Tuple[np.ndarray, np.ndarray]:
        """
        Finalizes grid accumulation into land cover class map and average confidence map.

        Args:
            nodata_val (int): Pixel value assigned to un-covered regions.

        Returns:
            Tuple[np.ndarray, np.ndarray]: (class_map, confidence_map)
                class_map shape: (H, W) uint8
                confidence_map shape: (H, W) float32
        """
        valid_mask = self.patch_coverage > 0

        # Resolve land cover class map via argmax across probability/vote accumulation
        class_map = np.full((self.height, self.width), nodata_val, dtype=np.uint8)
        class_map[valid_mask] = np.argmax(self.class_counts[valid_mask], axis=-1).astype(np.uint8)

        # Compute mean confidence map
        confidence_map = np.zeros((self.height, self.width), dtype=np.float32)
        confidence_map[valid_mask] = self.confidence_sum[valid_mask] / self.patch_coverage[valid_mask]

        return class_map, confidence_map

    def save_geotiff(
        self,
        output_path: str,
        class_map: np.ndarray,
        confidence_map: Optional[np.ndarray] = None,
        nodata_val: int = 255
    ) -> str:
        """
        Writes the prediction class map (and optionally confidence map) to a georeferenced GeoTIFF.
        Preserves exact spatial reference system (CRS), affine transform, extent, and resolution.

        Args:
            output_path (str): File path for output GeoTIFF.
            class_map (np.ndarray): 2D array of predicted class indices.
            confidence_map (Optional[np.ndarray]): 2D array of confidence scores.
            nodata_val (int): Nodata value.

        Returns:
            str: Path to saved GeoTIFF.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        num_bands = 2 if confidence_map is not None else 1
        dtype = 'uint8' if num_bands == 1 else 'float32'

        profile = {
            'driver': 'GTiff',
            'height': self.height,
            'width': self.width,
            'count': num_bands,
            'dtype': dtype,
            'crs': self.crs,
            'transform': self.transform,
            'nodata': nodata_val,
            'compress': 'lzw'
        }

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(class_map.astype(np.float32 if num_bands == 2 else np.uint8), 1)
            dst.set_band_description(1, "LandCover_Class")

            if confidence_map is not None:
                dst.write(confidence_map.astype(np.float32), 2)
                dst.set_band_description(2, "Confidence_Score")

        logger.info(f"Georeferenced prediction GeoTIFF saved to: {output_path}")
        return output_path


def stitch_predictions(
    patch_predictions: List[Dict[str, Any]],
    meta: Dict[str, Any],
    output_geotiff_path: str,
    num_classes: int = 10,
    nodata_val: int = 255
) -> Tuple[str, np.ndarray, np.ndarray]:
    """
    Convenience function to stitch a list of patch predictions into a GeoTIFF.

    Args:
        patch_predictions (List[Dict[str, Any]]): List of patch result dicts containing:
            - 'coords': (row_off, col_off, h, w)
            - 'class_idx': int
            - 'confidence': float
            - optional 'probs': np.ndarray
        meta (Dict[str, Any]): Image metadata with 'crs', 'transform', 'width', 'height'.
        output_geotiff_path (str): Output GeoTIFF destination.
        num_classes (int): Number of land use classes.
        nodata_val (int): Nodata indicator.

    Returns:
        Tuple[str, np.ndarray, np.ndarray]: (output_path, class_map, confidence_map)
    """
    stitcher = TileStitcher(meta, num_classes=num_classes)

    for patch in patch_predictions:
        stitcher.add_patch_prediction(
            coords=patch['coords'],
            predicted_class_idx=patch['class_idx'],
            confidence=patch['confidence'],
            probs=patch.get('probs')
        )

    class_map, confidence_map = stitcher.finalize(nodata_val=nodata_val)
    stitcher.save_geotiff(output_geotiff_path, class_map, confidence_map, nodata_val=nodata_val)

    return output_geotiff_path, class_map, confidence_map
