"""
Predict module for Sentinel-2 Land-Use Classification.
Re-exports single patch prediction and tile-level classification functions from src.inference.predict.
"""

import os
import sys

# Ensure project root is in system path for clean imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.inference.predict import (
    load_inference_model,
    preprocess_image,
    predict,
    run_single_inference,
    classify_tile
)

__all__ = [
    "load_inference_model",
    "preprocess_image",
    "predict",
    "run_single_inference",
    "classify_tile"
]

if __name__ == "__main__":
    import argparse
    import backend_config as bcfg
    import utils

    logger = utils.get_logger(__name__)

    parser = argparse.ArgumentParser(description="Sentinel-2 Land Use Classification - Inference CLI")
    parser.add_argument(
        "--image_dir", 
        type=str, 
        default="dummy_data",
        help="Path to directory containing Sentinel-2 bands (B2, B3, B4, B8)"
    )
    parser.add_argument(
        "--model_path", 
        type=str, 
        default=bcfg.MODEL_PATH,
        help="Path to the trained ResNet50 model weights (.pt)"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default=bcfg.MODEL_NAME,
        choices=["resnet50", "cnn"],
        help="Model architecture name"
    )
    parser.add_argument(
        "--output_geotiff",
        type=str,
        default=None,
        help="Optional path to output georeferenced prediction GeoTIFF for tile classification"
    )
    
    args = parser.parse_args()
    
    logger.info("=== Starting Sentinel-2 Inference Utility ===")

    if args.output_geotiff:
        result = classify_tile(
            image_dir_or_band_paths=args.image_dir,
            output_geotiff_path=args.output_geotiff,
            model_path=args.model_path
        )
        print("\n" + "=" * 45)
        print(" FULL TILE CLASSIFICATION RESULT")
        print("=" * 45)
        print(f" Output GeoTIFF : {result['output_geotiff']}")
        print(f" Resolution     : {result['width']} x {result['height']}")
        print(f" Patches        : {result['total_patches_processed']}")
        print(f" Dominant Class : {result['dominant_class']}")
        print(f" Mean Conf      : {result['mean_confidence_pct']}%")
        print(f" Latency        : {result['total_processing_time_sec']} sec")
        print("=" * 45 + "\n")
    else:
        result = run_single_inference(
            image_dir=args.image_dir,
            model_path=args.model_path,
            model_name=args.model,
        )
        
        if result["status"] == "success":
            print("\n" + "=" * 45)
            print(" LAND USE PREDICTION RESULT")
            print("=" * 45)
            print(f" Predicted Class : {result['class']}")
            print(f" Confidence      : {result['confidence']:.2f}%")
            print(f" Latency         : {result['time_ms']:.2f} ms")
            print(f" Device Used     : {result['device']}")
            print("=" * 45 + "\n")
        else:
            print("\n" + "=" * 45)
            print(" ERROR: Prediction pipeline failed.")
            print(f" Reason: {result['error_message']}")
            print("=" * 45 + "\n")
            sys.exit(1)
