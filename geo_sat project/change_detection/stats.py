"""
Change Detection - Statistics Module Wrapper.
Exposes area statistics calculation functions from src.change_detection.stats.
"""

from src.change_detection.stats import (
    calculate_pixel_area,
    compute_landcover_area_stats,
    export_area_stats_csv,
    plot_area_comparison,
    plot_transition_matrix
)

__all__ = [
    "calculate_pixel_area",
    "compute_landcover_area_stats",
    "export_area_stats_csv",
    "plot_area_comparison",
    "plot_transition_matrix"
]
