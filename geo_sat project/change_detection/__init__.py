"""
Change Detection Module Top-level Package.
"""

from src.change_detection.diff_maps import (
    align_and_load_rasters,
    generate_change_map,
    export_change_geotiff,
    compute_change_detection
)
from src.change_detection.stats import (
    calculate_pixel_area,
    compute_landcover_area_stats,
    export_area_stats_csv,
    plot_area_comparison,
    plot_transition_matrix
)

__all__ = [
    "align_and_load_rasters",
    "generate_change_map",
    "export_change_geotiff",
    "compute_change_detection",
    "calculate_pixel_area",
    "compute_landcover_area_stats",
    "export_area_stats_csv",
    "plot_area_comparison",
    "plot_transition_matrix"
]
