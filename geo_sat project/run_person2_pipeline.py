import os
import pandas as pd
import numpy as np
from PIL import Image

def generate_synthetic_data():
    results_dir = "data/results"
    os.makedirs(results_dir, exist_ok=True)
    
    years = [2019, 2020, 2021, 2022, 2023]
    classes = ["Urban", "Forest", "Vegetation", "Water", "Agriculture"]
    colors = {
        "Urban": (138, 122, 110),       # #8a7a6e
        "Forest": (45, 90, 39),         # #2d5a27
        "Vegetation": (110, 168, 78),   # #6ea84e
        "Water": (74, 143, 168),        # #4a8fa8
        "Agriculture": (200, 169, 110)  # #c8a96e
    }
    
    # 1. Generate area_stats.csv
    # We will simulate urban growth and vegetation decline over the years
    stats_list = []
    
    # Initial areas in sq km
    base_areas = {
        "Urban": 150.0,
        "Forest": 300.0,
        "Vegetation": 250.0,
        "Water": 100.0,
        "Agriculture": 200.0
    }
    
    current_areas = base_areas.copy()
    
    for year in years:
        for cls_idx, cls_name in enumerate(classes):
            stats_list.append({
                "year": year,
                "class_index": cls_idx,
                "class_name": cls_name,
                "area_km2": round(current_areas[cls_name], 2)
            })
        
        # Simulate trends for next year
        current_areas["Urban"] += 15.0         # Urban grows
        current_areas["Vegetation"] -= 10.0    # Vegetation shrinks
        current_areas["Agriculture"] -= 5.0    # Agriculture shrinks
        # Forest and Water stay roughly the same, maybe slight variations
        current_areas["Forest"] -= 1.0
        current_areas["Water"] += 1.0
        
    df = pd.DataFrame(stats_list)
    csv_path = os.path.join(results_dir, "area_stats.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated {csv_path}")

    # 2. Generate Map PNGs (dummy maps with just solid colors or random noise)
    width, height = 800, 600
    for year in years:
        # Create a base image (e.g. vegetation color)
        img_array = np.full((height, width, 4), [110, 168, 78, 180], dtype=np.uint8) # RGBA
        
        # Add a block for Urban that grows each year
        urban_size = int(200 + (year - 2019) * 40)
        img_array[height//2 - urban_size//2 : height//2 + urban_size//2, 
                  width//2 - urban_size//2 : width//2 + urban_size//2] = [138, 122, 110, 180]
                  
        # Add a block for Water
        img_array[50:150, 50:250] = [74, 143, 168, 180]
        
        img = Image.fromarray(img_array)
        png_path = os.path.join(results_dir, f"classified_{year}.png")
        img.save(png_path)
        print(f"Generated {png_path}")
        
    # Generate diff maps
    for i in range(len(years) - 1):
        year1 = years[i]
        year2 = years[i+1]
        
        # Diff map: mostly transparent, red where changed
        diff_array = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Draw some red to simulate change
        diff_size = int(200 + (year2 - 2019) * 40)
        prev_diff_size = int(200 + (year1 - 2019) * 40)
        
        # The rim that changed
        diff_array[height//2 - diff_size//2 : height//2 + diff_size//2, 
                  width//2 - diff_size//2 : width//2 + diff_size//2] = [255, 0, 0, 180]
        diff_array[height//2 - prev_diff_size//2 : height//2 + prev_diff_size//2, 
                  width//2 - prev_diff_size//2 : width//2 + prev_diff_size//2] = [0, 0, 0, 0]
                  
        img = Image.fromarray(diff_array)
        diff_path = os.path.join(results_dir, f"change_{year1}_{year2}.png")
        img.save(diff_path)
        print(f"Generated {diff_path}")

if __name__ == "__main__":
    generate_synthetic_data()
