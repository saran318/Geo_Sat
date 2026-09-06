"""
Configuration settings for the Person 2 Backend & Inference module.
Centrally stores all configurable hyperparameters, file paths, supported formats,
and class definitions to ensure consistency across CLI and REST API modules.
"""

import os
import torch

# Base Directories
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

# Model Configuration
MODEL_PATH = os.path.join(MODELS_DIR, "resnet50_best.pt")
MODEL_NAME = "resnet50"
NUM_CLASSES = 10
MODEL_DOWNLOAD_URL = "https://github.com/Antigravity/geo_sat_project/releases/download/v1.0.0/resnet50_best.pt"

# Image & Preprocessing Parameters
IMAGE_SIZE = 64  # Input spatial dimension (64x64) expected by ResNet50 model
SUPPORTED_FORMATS = [".tif", ".tiff", ".jp2"]

# Device Auto-detection with optimization settings
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Centralized list of land-use classes in alphabetical order
CLASS_NAMES = [
    "AnnualCrop",
    "Forest",
    "HerbaceousVegetation",
    "Highway",
    "Industrial",
    "Pasture",
    "PermanentCrop",
    "Residential",
    "River",
    "SeaLake"
]

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
