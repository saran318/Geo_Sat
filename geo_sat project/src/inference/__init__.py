"""
Inference module for model prediction, sliding window tiling, and spatial stitching.
"""

from src.inference.stitch import TileStitcher, stitch_predictions

__all__ = ["TileStitcher", "stitch_predictions"]
