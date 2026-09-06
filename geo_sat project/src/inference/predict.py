"""
Inference & Tile Classification Module for Sentinel-2 Satellite Imagery.
Refactored inference engine exposing both single-patch prediction and full-scene `classify_tile()`.
Includes sliding window tiler, automatic weight downloading, spatial stitching into georeferenced GeoTIFFs,
and WGS84 CRS coordinate metadata generation for frontend map overlays.
"""

import os
import sys
import time
import logging
from typing import Dict, Tuple, Any, List, Optional

import numpy as np
import torch
import torch.nn as nn

import backend_config as bcfg
import utils
from training.model import get_model
from src.preprocessing.preprocess import validate_bands, extract_patches, load_bands
from src.inference.stitch import TileStitcher, stitch_predictions

logger = utils.get_logger(__name__)

def load_inference_model(
    model_path: str = bcfg.MODEL_PATH,
    model_name: str = bcfg.MODEL_NAME,
    num_classes: int = bcfg.NUM_CLASSES,
    device: str = bcfg.DEVICE
) -> nn.Module:
    """
    Instantiates the model architecture and populates it with trained weights.
    Triggers automatic download from GitHub release if weights are missing locally.
    
    Args:
        model_path (str): Path to saved model weights.
        model_name (str): Model architecture name ('resnet50' or 'cnn').
        num_classes (int): Number of target land-use classes.
        device (str): Target computational device ('cuda' or 'cpu').
        
    Returns:
        nn.Module: Loaded PyTorch model in evaluation mode.
    """
    logger.info(f"Loading inference model '{model_name}' on device: {device}")
    
    # 1. Automatic model weight download if missing
    if not os.path.exists(model_path):
        utils.download_model_weights_if_missing(model_path, bcfg.MODEL_DOWNLOAD_URL)
        
    # 2. Instantiate architecture
    try:
        model = get_model(model_name=model_name, num_classes=num_classes)
    except Exception as e:
        logger.error(f"Failed to instantiate model '{model_name}': {e}")
        raise

    # 3. Populate state dictionary
    if os.path.exists(model_path):
        try:
            checkpoint = torch.load(model_path, map_location=device)
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                model.load_state_dict(checkpoint["model_state_dict"])
            else:
                model.load_state_dict(checkpoint)
            logger.info("Loaded state dictionary successfully.")
        except Exception as e:
            logger.error(f"Error loading model weights from {model_path}: {e}")
            raise
    else:
        logger.warning(f"Weights file not found at {model_path}. Running with uninitialized weights.")

    model = model.to(device)
    model.eval()

    if device == "cuda":
        torch.backends.cudnn.benchmark = True

    return model


def predict(
    model: nn.Module,
    input_tensor: torch.Tensor,
    device: str = bcfg.DEVICE
) -> Tuple[str, float, float]:
    """
    Performs inference on a single 6-channel patch tensor.

    Args:
        model (nn.Module): Loaded model.
        input_tensor (torch.Tensor): Preprocessed batch tensor (1, 6, 64, 64).
        device (str): Inference device.

    Returns:
        Tuple[str, float, float]: (predicted_class_name, confidence_percentage, latency_ms)
    """
    input_tensor = input_tensor.to(device)
    start_time = time.perf_counter()

    with torch.inference_mode():
        outputs = model(input_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        conf_tensor, idx_tensor = torch.max(probabilities, 1)

        class_idx = int(idx_tensor.cpu().item())
        confidence = float(conf_tensor.cpu().item()) * 100.0

    latency_ms = (time.perf_counter() - start_time) * 1000.0
    predicted_class = bcfg.CLASS_NAMES[class_idx]

    return predicted_class, confidence, latency_ms


def preprocess_image(image_dir: str, target_size: int = bcfg.IMAGE_SIZE) -> torch.Tensor:
    """
    Finds Sentinel-2 bands in image_dir, loads them, normalizes, computes NDVI/NDWI,
    and returns a preprocessed PyTorch FloatTensor of shape (1, 6, target_size, target_size).
    """
    band_paths = utils.find_sentinel_bands(image_dir)
    bands_array = load_bands(band_paths)
    return utils.process_bands_array(bands_array, target_size=target_size)


def run_single_inference(
    image_dir: str,
    model_path: str = bcfg.MODEL_PATH,
    model_name: str = bcfg.MODEL_NAME,
    device: str = bcfg.DEVICE
) -> Dict[str, Any]:
    """
    High-level utility for running single-patch inference on a directory containing Sentinel-2 bands.
    """
    try:
        model = load_inference_model(model_path=model_path, model_name=model_name, device=device)
        input_tensor = preprocess_image(image_dir)
        pred_class, conf, latency = predict(model, input_tensor, device=device)
        return {
            "status": "success",
            "class": pred_class,
            "confidence": conf,
            "time_ms": latency,
            "device": device
        }
    except Exception as e:
        logger.exception(f"Error during single inference: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }


def classify_tile(
    image_dir_or_band_paths: Any,
    output_geotiff_path: str,
    model: Optional[nn.Module] = None,
    model_path: str = bcfg.MODEL_PATH,
    patch_size: int = bcfg.IMAGE_SIZE,
    stride: int = 32,
    scl_path: Optional[str] = None,
    device: str = bcfg.DEVICE,
    batch_size: int = 32
) -> Dict[str, Any]:
    """
    Classifies a full Sentinel-2 satellite scene/tile using sliding window patch extraction,
    stitching patch predictions into a georeferenced GeoTIFF output map.

    Preserves CRS, spatial transform, resolution, and bounding extent.

    Args:
        image_dir_or_band_paths (Any): Directory containing band files OR dictionary of band paths.
        output_geotiff_path (str): File destination path for exported prediction GeoTIFF.
        model (Optional[nn.Module]): Optional loaded model instance.
        model_path (str): Weights checkpoint path if model is None.
        patch_size (int): Spatial dimension of patches (64).
        stride (int): Stride for sliding window.
        scl_path (Optional[str]): Optional Scene Classification Layer (SCL) path for cloud masking.
        device (str): Hardware device.

    Returns:
        Dict[str, Any]: Comprehensive result dictionary containing prediction details,
                        WGS84 lat/lon bounds, spatial metadata, and performance metrics.
    """
    start_total_time = time.perf_counter()

    # 1. Resolve band paths dictionary
    if isinstance(image_dir_or_band_paths, str):
        band_paths = utils.find_sentinel_bands(image_dir_or_band_paths)
    else:
        band_paths = image_dir_or_band_paths

    # 2. Validate raster properties and get reference metadata
    meta = validate_bands(band_paths)
    wgs84_bounds = utils.get_raster_wgs84_bounds(meta)

    # 3. Load model if not provided
    if model is None:
        model = load_inference_model(model_path=model_path, device=device)

    # 4. Extract patches lazily and run sliding window inference
    logger.info(f"Extracting patches from scene ({meta['width']}x{meta['height']}) with patch_size={patch_size}, stride={stride}...")
    
    patch_predictions: List[Dict[str, Any]] = []
    patch_count = 0

    patch_gen = extract_patches(
        band_paths=band_paths,
        patch_size=patch_size,
        stride=stride,
        scl_path=scl_path
    )

    batch_tensors = []
    batch_coords = []
    
    def process_batch(tensors, coords_list):
        if not tensors: return
        batch_tensor = torch.cat(tensors, dim=0).to(device)
        with torch.inference_mode():
            outputs = model(batch_tensor)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()
            
        for i in range(len(coords_list)):
            class_idx = int(np.argmax(probs[i]))
            confidence = float(probs[i][class_idx]) * 100.0
            patch_predictions.append({
                'coords': coords_list[i],
                'class_idx': class_idx,
                'confidence': confidence,
                'probs': probs[i]
            })

    for patch_info in patch_gen:
        image_patch = patch_info['image_patch']  # Shape: (64, 64, 6)
        coords = patch_info['coords']

        # Format patch into PyTorch FloatTensor: (1, 6, 64, 64)
        transposed = image_patch.transpose(2, 0, 1)
        patch_tensor = torch.from_numpy(transposed).float().unsqueeze(0)

        # Explicit Model Input Validation
        if patch_tensor.ndim != 4:
            raise ValueError(f"Expected a 4D tensor [N,C,H,W], got {patch_tensor.shape}")
        
        if patch_tensor.shape[1] != 6:
            raise ValueError(
                f"Expected 6 input channels [B2,B3,B4,B8,NDVI,NDWI], "
                f"got {patch_tensor.shape[1]}"
            )
            
        if not torch.isfinite(patch_tensor).all():
            raise ValueError("Model input contains NaN or infinite values")
        
        batch_tensors.append(patch_tensor)
        batch_coords.append(coords)
        patch_count += 1
        
        if len(batch_tensors) >= batch_size:
            process_batch(batch_tensors, batch_coords)
            batch_tensors = []
            batch_coords = []

    # Process remaining patches
    if len(batch_tensors) > 0:
        process_batch(batch_tensors, batch_coords)

    # 5. Stitch predictions into a spatial GeoTIFF raster
    logger.info(f"Stitching {patch_count} patch predictions into full spatial GeoTIFF map...")
    out_path, class_map, conf_map = stitch_predictions(
        patch_predictions=patch_predictions,
        meta=meta,
        output_geotiff_path=output_geotiff_path,
        num_classes=bcfg.NUM_CLASSES
    )

    total_latency_sec = time.perf_counter() - start_total_time

    # 6. Calculate summary metrics
    valid_pixels = class_map[class_map != 255]
    if len(valid_pixels) > 0:
        dominant_idx = int(np.bincount(valid_pixels).argmax())
        dominant_class = bcfg.CLASS_NAMES[dominant_idx]
        mean_confidence = float(np.mean(conf_map[class_map != 255]))
    else:
        dominant_class = "Unknown"
        mean_confidence = 0.0

    return {
        "status": "success",
        "output_geotiff": out_path,
        "width": meta['width'],
        "height": meta['height'],
        "crs": str(meta['crs']),
        "wgs84_bounds": wgs84_bounds,
        "total_patches_processed": patch_count,
        "dominant_class": dominant_class,
        "mean_confidence_pct": round(mean_confidence, 2),
        "total_processing_time_sec": round(total_latency_sec, 2)
    }
