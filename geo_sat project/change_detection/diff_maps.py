"""
Change Detection - Difference Map Module Wrapper.
Exposes diff map functions from src.change_detection.diff_maps.
"""

from src.change_detection.diff_maps import (
    align_and_load_rasters,
    generate_change_map,
    export_change_geotiff,
    compute_change_detection
)

__all__ = [
    "align_and_load_rasters",
    "generate_change_map",
    "export_change_geotiff",
    "compute_change_detection"
]
