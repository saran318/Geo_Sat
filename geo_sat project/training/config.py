import torch
import os

# Data parameters
PATCH_SIZE = 64
STRIDE = 32
IMAGE_SIZE = 64
NUM_CLASSES = 10

# Dataloader parameters
BATCH_SIZE = 32
NUM_WORKERS = 2

# Training parameters
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4
EPOCHS = 25
SEED = 42

# Device Configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Optional settings
USE_TENSORBOARD = False
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)
