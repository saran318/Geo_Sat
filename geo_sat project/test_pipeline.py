import os
import sys
import gc
import psutil
import numpy as np
import torch  # type: ignore
import rasterio
from rasterio.transform import from_origin

sys.path.append(os.path.abspath('.'))

from src.preprocessing.preprocess import validate_bands, load_bands, extract_patches
from training.dataset import SatelliteDataset, get_data_loaders

def print_mem(step=""):
    mem = psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)
    print(f"[{step}] Memory Usage: {mem:.2f} MB")

print_mem("Start")

# 1. Create dummy dataset
os.makedirs("dummy_data", exist_ok=True)
dummy_bands = {'B2': 'dummy_data/B2.tif', 'B3': 'dummy_data/B3.tif', 'B4': 'dummy_data/B4.tif', 'B8': 'dummy_data/B8.tif'}

width, height = 500, 500
transform = from_origin(0, 0, 10, 10)
for band, path in dummy_bands.items():
    data = np.random.randint(100, 8000, (height, width), dtype=np.uint16)
    with rasterio.open(path, 'w', driver='GTiff', height=height, width=width, count=1, 
                       dtype=data.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(data, 1)

print_mem("After Dummy Data Generation")

# 2. Test validate_bands
meta = validate_bands(dummy_bands)
assert meta['width'] == 500
assert meta['height'] == 500
print("✅ validate_bands passed")

# 3. Test patch generator
gen = extract_patches(dummy_bands, patch_size=64, stride=64)
for i, patch_info in enumerate(gen):
    patch = patch_info['image_patch']
    assert patch.shape == (64, 64, 6)
    assert patch.dtype == np.float32
    # Verify NDVI bounds roughly
    ndvi = patch[:, :, 4]
    assert np.all(ndvi >= -1.0) and np.all(ndvi <= 1.0)
    if i == 5:
        break
print("✅ Generator & Normalization (NDVI/NDWI) passed")
print_mem("During generator iterations")

# 4. Test dataset & dataloader
os.makedirs("dummy_dataset/ClassA", exist_ok=True)
os.makedirs("dummy_dataset/ClassB", exist_ok=True)

for i in range(5):
    np.save(f"dummy_dataset/ClassA/patch_{i}.npy", np.random.rand(64, 64, 6).astype(np.float32))
    np.save(f"dummy_dataset/ClassB/patch_{i}.npy", np.random.rand(64, 64, 6).astype(np.float32))

dataset = SatelliteDataset(root_dir="dummy_dataset")
assert len(dataset) == 10
img, label = dataset[0]
assert img.shape == (6, 64, 64)
assert isinstance(img, torch.Tensor)
print("✅ Dataset passed")

train_loader, val_loader, test_loader = get_data_loaders("dummy_dataset", batch_size=2, num_workers=0)
for batch_x, batch_y in train_loader:
    assert batch_x.shape == (2, 6, 64, 64)
    break
print("✅ DataLoader passed")
print_mem("End")
