import os
import sys
import numpy as np
import torch
import shutil
import psutil

sys.path.append(os.path.abspath('.'))

import training.config as cfg
from training.train import train_model
from training.evaluate import evaluate_model
from training.model import get_model, BaselineCNN

def print_mem(step=""):
    mem = psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)
    print(f"[{step}] Memory Usage: {mem:.2f} MB")

def validate_resnet_initialization():
    print("Validating ResNet50 initialization...")
    model = get_model(model_name="resnet50", num_classes=10)
    conv1 = model.conv1
    assert conv1.in_channels == 6, "ResNet50 first conv does not accept 6 channels!"
    # Original weights have 3 channels.
    # The new channels (3:6) should be initialized with the mean of the first 3 channels.
    weights = conv1.weight.detach()
    rgb_mean = weights[:, :3, :, :].mean(dim=1, keepdim=True)
    new_channels = weights[:, 3:, :, :]
    
    # Check if they are close (allowing floating point tolerance)
    assert torch.allclose(new_channels[:, 0:1, :, :], rgb_mean), "Channel 4 (NIR) not correctly initialized!"
    assert torch.allclose(new_channels[:, 1:2, :, :], rgb_mean), "Channel 5 (NDVI) not correctly initialized!"
    assert torch.allclose(new_channels[:, 2:3, :, :], rgb_mean), "Channel 6 (NDWI) not correctly initialized!"
    print("ResNet50 6-channel initialization validation passed!")
    
    # Validate outputs
    x = torch.randn(2, 6, 64, 64)
    out = model(x)
    assert out.shape == (2, 10), f"Expected output shape (2, 10), got {out.shape}"
    print("ResNet50 output validation passed!")

def run_test():
    print_mem("Start")
    validate_resnet_initialization()
    
    print("Setting up dummy dataset for validation...")
    data_dir = "dummy_train_dataset"
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        
    classes = [f"Class{i}" for i in range(10)]
    for c in classes:
        os.makedirs(os.path.join(data_dir, c), exist_ok=True)
        # Create 10 patches per class (6 channels, 64x64)
        for i in range(10):
            patch = np.random.rand(64, 64, 6).astype(np.float32)
            np.save(os.path.join(data_dir, c, f"patch_{i}.npy"), patch)
            
    print_mem("After Dataset Creation")
            
    print("Modifying config for quick test...")
    cfg.EPOCHS = 2
    cfg.BATCH_SIZE = 4
    cfg.NUM_WORKERS = 0 # for windows safe testing
    cfg.NUM_CLASSES = 10
    
    print("Testing CNN Training...")
    try:
        cnn_path = train_model(data_dir, model_name="cnn")
        print(f"CNN Training passed. Best model saved to: {cnn_path}")
        evaluate_model(cnn_path, data_dir, model_name="cnn")
        print("CNN Evaluation passed.")
    except Exception as e:
        print(f"CNN Test Failed: {e}")
        import traceback
        traceback.print_exc()

    print_mem("After CNN")

    print("Testing ResNet50 Training...")
    try:
        resnet_path = train_model(data_dir, model_name="resnet50")
        print(f"ResNet50 Training passed. Best model saved to: {resnet_path}")
        evaluate_model(resnet_path, data_dir, model_name="resnet50")
        print("ResNet50 Evaluation passed.")
        
        # Test resuming
        print("Testing Resume Training...")
        cfg.EPOCHS = 3
        train_model(data_dir, model_name="resnet50", resume_from=resnet_path)
        print("Resume Training passed.")
    except Exception as e:
        print(f"ResNet50 Test Failed: {e}")
        import traceback
        traceback.print_exc()
        
    print_mem("End of test")
    print("All tests completed.")

if __name__ == "__main__":
    run_test()
