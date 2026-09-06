import os
import glob
import numpy as np
import imageio.v3 as iio
from tqdm import tqdm

# Source and target directories
RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "raw", "eurosat", "extracted", "EuroSAT_MS"))
PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed", "eurosat_6channel"))

def process_file(file_path, cls_dir_out):
    """
    Reads a 13-band EuroSAT TIFF using imageio, extracts Blue, Green, Red, NIR, 
    computes NDVI and NDWI, and saves as a 6-channel .npy tensor.
    """
    try:
        data = iio.imread(file_path) # Shape: (64, 64, 13)
            
        # EuroSAT MS bands (last dimension): 
        # B1(0), B2(1, Blue), B3(2, Green), B4(3, Red), B5(4), B6(5), B7(6), B8(7, NIR)
        blue = data[:, :, 1].astype(np.float32) / 10000.0
        green = data[:, :, 2].astype(np.float32) / 10000.0
        red = data[:, :, 3].astype(np.float32) / 10000.0
        nir = data[:, :, 7].astype(np.float32) / 10000.0
        
        # Calculate NDVI: (NIR - RED) / (NIR + RED + 1e-6)
        ndvi = (nir - red) / (nir + red + 1e-6)
        
        # Calculate NDWI: (GREEN - NIR) / (GREEN + NIR + 1e-6)
        ndwi = (green - nir) / (green + nir + 1e-6)
        
        # Stack channels: (64, 64, 6)
        stacked = np.stack([blue, green, red, nir, ndvi, ndwi], axis=-1)
        
        # Save to .npy
        basename = os.path.splitext(os.path.basename(file_path))[0]
        out_path = os.path.join(cls_dir_out, f"{basename}.npy")
        np.save(out_path, stacked)
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    print(f"Preprocessing EuroSAT dataset from {RAW_DIR} to {PROCESSED_DIR}")
    
    classes = [d for d in os.listdir(RAW_DIR) if os.path.isdir(os.path.join(RAW_DIR, d))]
    
    tasks = []
    for cls_name in classes:
        cls_dir_in = os.path.join(RAW_DIR, cls_name)
        cls_dir_out = os.path.join(PROCESSED_DIR, cls_name)
        os.makedirs(cls_dir_out, exist_ok=True)
        
        files = glob.glob(os.path.join(cls_dir_in, "*.tif"))
        for f in files:
            tasks.append((f, cls_dir_out))
            
    print(f"Found {len(tasks)} images to process.")
    
    success_count = 0
    # Process sequentially to avoid memory spikes or rasterio multi-threading issues on Windows
    for task in tqdm(tasks):
        if process_file(task[0], task[1]):
            success_count += 1
            
    print(f"Successfully processed {success_count}/{len(tasks)} images.")
    
if __name__ == "__main__":
    main()
