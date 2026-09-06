import os
import sys
import requests
from dotenv import load_dotenv

# Ensure project root is in system path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

import backend_config as bcfg

# Ensure .env is loaded
load_dotenv(os.path.join(bcfg.PROJECT_ROOT, ".env"))

USER = os.getenv("COPERNICUS_USERNAME", "your_username")
PASSWORD = os.getenv("COPERNICUS_PASSWORD", "your_password")

def get_cdse_token():
    """Generates an OAuth2 token from the Copernicus Data Space Ecosystem"""
    url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    data = {
        "client_id": "cdse-public",
        "username": USER,
        "password": PASSWORD,
        "grant_type": "password"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def download_sentinel_tile(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Authenticating with Copernicus Data Space Ecosystem...")
    try:
        token = get_cdse_token()
    except Exception as e:
        print(f"Authentication failed. Please check your credentials in the .env file. Error: {e}")
        return

    print("Authentication successful. Searching for Sentinel-2 products (0-10% cloud cover)...")
    
    # OpenSearch API is recommended for geospatial queries
    search_url = "https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json"
    params = {
        "startDate": "2023-01-01T00:00:00Z",
        "completionDate": "2023-01-31T23:59:59Z",
        "cloudCover": "[0,10]",
        "geometry": "POINT(12.4924 41.8902)", # Rome, Italy
        "productType": "S2MSI2A", # Sentinel-2 Level-2A Surface Reflectance
        "maxRecords": 10
    }
    
    resp = requests.get(search_url, params=params)
    if resp.status_code != 200:
        print(f"Search failed: {resp.text}")
        return
        
    features = resp.json().get("features", [])
    if not features:
        print("No products found matching the criteria.")
        return
    
    # Sort by cloud cover (lowest first)
    features.sort(key=lambda x: x["properties"].get("cloudCover", 100))
    best_product = features[0]
    
    product_id = best_product["id"]
    title = best_product["properties"]["title"]
    cloud_cover = best_product["properties"].get("cloudCover")
    
    print(f"Selected Product: {title}")
    print(f"Cloud Cover: {cloud_cover:.2f}%")
    
    # Ensure token is passed in header for download
    download_url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
    headers = {"Authorization": f"Bearer {token}"}
    
    output_path = os.path.join(output_dir, f"{title}.zip")
    print(f"Downloading product to {output_path}...")
    
    # Stream the file to disk (since Sentinel-2 zips are ~1GB each)
    try:
        with requests.get(download_url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"Download complete: {output_path}")
    except Exception as e:
        print(f"Failed to download. Error: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_output_dir = os.path.join(script_dir, "..", "data", "raw", "sentinel2")
    download_sentinel_tile(output_dir=target_output_dir)
