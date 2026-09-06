"""
EuroSAT Dataset Downloader Script.

This script safely downloads and extracts the EuroSAT multi-spectral 
dataset (all bands) from its official source.
"""

import os
import requests
import zipfile
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

EUROSAT_URL = "https://zenodo.org/records/7711810/files/EuroSAT_MS.zip"

def download_file(url: str, output_path: str, max_retries: int = 10) -> bool:
    """
    Download a file from a URL to the specified output path with a progress bar and robust resuming.
    """
    import time
    for attempt in range(max_retries):
        try:
            headers = {}
            file_mode = 'wb'
            downloaded = 0
            if os.path.exists(output_path):
                downloaded = os.path.getsize(output_path)
                headers['Range'] = f'bytes={downloaded}-'
                file_mode = 'ab'
                
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            
            if response.status_code == 416: # Range Not Satisfiable (already fully downloaded)
                return True
                
            if response.status_code not in [200, 206]:
                logger.error(f"Failed to connect. Status code: {response.status_code}")
                continue
                
            if response.status_code == 200 and downloaded > 0:
                logger.info("Server doesn't support resume, restarting download...")
                file_mode = 'wb'
                downloaded = 0
                
            total_size = int(response.headers.get('content-length', 0)) + downloaded
            block_size = 1024 * 64
            
            progress_bar = tqdm(total=total_size, initial=downloaded, unit='iB', unit_scale=True, desc=os.path.basename(output_path))
            
            with open(output_path, file_mode) as file:
                for data in response.iter_content(block_size):
                    if data:
                        progress_bar.update(len(data))
                        file.write(data)
                        
            progress_bar.close()
            
            if total_size != 0 and progress_bar.n >= total_size:
                return True
                
            logger.warning(f"Download incomplete on attempt {attempt + 1}")
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
            
    return False

def extract_zip(zip_path: str, extract_dir: str) -> bool:
    """
    Extract a zip file to the specified directory.
    
    Args:
        zip_path (str): Path to the zip file.
        extract_dir (str): Directory where contents will be extracted.
        
    Returns:
        bool: True if extraction was successful, False otherwise.
    """
    try:
        logger.info("Extracting %s to %s... This might take a minute.", zip_path, extract_dir)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        logger.info("Extraction complete.")
        return True
    except (zipfile.BadZipFile, IOError) as e:
        logger.error("Failed to extract %s. Error: %s", zip_path, e)
        return False

def download_and_organize_eurosat(base_dir: str) -> None:
    """
    Orchestrate the downloading and extraction of the EuroSAT dataset.
    
    Args:
        base_dir (str): The base directory for data storage.
    """
    raw_dir = os.path.join(base_dir, "raw", "eurosat")
    zip_path = os.path.join(raw_dir, "EuroSAT_MS.zip")
    extract_dir = os.path.join(raw_dir, "extracted")

    os.makedirs(raw_dir, exist_ok=True)

    logger.info("Downloading EuroSAT dataset from %s...", EUROSAT_URL)
    success = download_file(EUROSAT_URL, zip_path)
    if not success:
        logger.error("Aborting process due to download failure.")
        return

    # Protection against duplicate extractions
    if not os.path.exists(extract_dir) or not os.listdir(extract_dir):
        os.makedirs(extract_dir, exist_ok=True)
        extract_zip(zip_path, extract_dir)
    else:
        logger.info("Dataset already extracted at %s.", extract_dir)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_base_dir = os.path.join(script_dir, "..", "data")
    download_and_organize_eurosat(base_dir=target_base_dir)
