"""
Test suite for the Person 2 Backend API.
Uses pytest and FastAPI's TestClient to test the /predict and /health endpoints.
Covers valid uploads, unsupported formats, invalid files, preprocessing failures, and missing model files.
"""

import os
import sys
import tempfile
import pytest
import numpy as np
import rasterio
from rasterio.transform import from_origin
import torch
import torch.nn as nn
from fastapi.testclient import TestClient

# Ensure project root is in path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the FastAPI application, config, and variables
from api import app
import api
import backend_config as bcfg

# Initialize the TestClient
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_mock_model():
    """
    Ensure a model is always loaded for test execution.
    If the real model is missing (e.g. in light-weight testing environments),
    instantiates a mock model to allow testing endpoints and preprocessing paths.
    """
    if api.model_instance is None:
        class MockSatelliteModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.param = nn.Parameter(torch.zeros(1))
            def forward(self, x):
                # Returns zero logits for the 10 classes
                batch_size = x.shape[0]
                return torch.zeros((batch_size, 10))
                
        api.model_instance = MockSatelliteModel()
        yield
        api.model_instance = None
    else:
        yield


def create_mock_multiband_tiff(file_path: str, num_bands: int = 4, width: int = 64, height: int = 64) -> None:
    """
    Helper function to generate a mock multi-band GeoTIFF file for testing.
    Simulates Sentinel-2 uint16 band values.
    """
    transform = from_origin(0, 0, 10, 10)
    # Generate random values typical of Sentinel-2 bands (100 - 8000 uint16)
    data = np.random.randint(100, 8000, (num_bands, height, width), dtype=np.uint16)
    
    with rasterio.open(
        file_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=num_bands,
        dtype='uint16',
        crs='+proj=latlong',
        transform=transform
    ) as dst:
        for i in range(1, num_bands + 1):
            dst.write(data[i - 1], i)

@pytest.fixture
def valid_tiff_file():
    """
    Fixture that yields a valid 4-band GeoTIFF file and deletes it after testing.
    """
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
        file_path = tmp.name
    
    create_mock_multiband_tiff(file_path, num_bands=4)
    yield file_path
    
    if os.path.exists(file_path):
        os.remove(file_path)

@pytest.fixture
def insufficient_bands_tiff_file():
    """
    Fixture that yields an invalid 3-band GeoTIFF file (e.g., standard RGB).
    """
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
        file_path = tmp.name
        
    create_mock_multiband_tiff(file_path, num_bands=3)
    yield file_path
    
    if os.path.exists(file_path):
        os.remove(file_path)

def test_health_endpoint() -> None:
    """
    Test the GET /health endpoint to ensure it returns 200 OK
    and correctly reflects the application status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert "model_loaded" in json_data
    assert "device" in json_data

def test_predict_valid_image(valid_tiff_file) -> None:
    """
    Test POST /predict with a valid 4-band Sentinel-2 image.
    Verifies that the server returns HTTP 200, success status, predicted class,
    confidence score, and inference latency.
    """
    with open(valid_tiff_file, "rb") as f:
        response = client.post(
            "/predict",
            files={"file": (os.path.basename(valid_tiff_file), f, "image/tiff")}
        )
        
    assert response.status_code == 200
    json_data = response.json()
    
    assert json_data["status"] == "success"
    assert "predicted_class" in json_data
    assert isinstance(json_data["predicted_class"], str)
    assert json_data["predicted_class"] in bcfg.CLASS_NAMES
    
    assert "confidence" in json_data
    assert isinstance(json_data["confidence"], float)
    assert 0.0 <= json_data["confidence"] <= 100.0
    
    assert "inference_time" in json_data
    assert isinstance(json_data["inference_time"], float)
    assert json_data["inference_time"] >= 0.0

def test_predict_unsupported_format() -> None:
    """
    Test POST /predict with an unsupported file extension (e.g., .png).
    Verifies that the server returns HTTP 400 Bad Request with a clear error message.
    """
    # Create a mock text file with .png extension
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(b"fake image bytes")
        file_path = tmp.name
        
    try:
        with open(file_path, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("image.png", f, "image/png")}
            )
            
        assert response.status_code == 400
        json_data = response.json()
        assert "Invalid file format" in json_data["detail"]
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_predict_invalid_corrupted_file() -> None:
    """
    Test POST /predict with a file that has a valid extension (.tif) but corrupted or non-geotiff contents.
    Verifies that the server handles Rasterio decoding errors and returns HTTP 422 Unprocessable Entity.
    """
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
        tmp.write(b"not a real geotiff file, just corrupted text bytes")
        file_path = tmp.name
        
    try:
        with open(file_path, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": ("corrupted.tif", f, "image/tiff")}
            )
            
        assert response.status_code == 422
        json_data = response.json()
        assert "not a valid GeoTIFF" in json_data["detail"]
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_predict_preprocessing_failure_insufficient_bands(insufficient_bands_tiff_file) -> None:
    """
    Test POST /predict with a GeoTIFF that has insufficient bands (e.g., only 3 bands).
    Verifies that the server returns HTTP 400 Bad Request indicating insufficient bands.
    """
    with open(insufficient_bands_tiff_file, "rb") as f:
        response = client.post(
            "/predict",
            files={"file": (os.path.basename(insufficient_bands_tiff_file), f, "image/tiff")}
        )
        
    assert response.status_code == 400
    json_data = response.json()
    assert "must have at least 4 bands" in json_data["detail"]

def test_predict_missing_model(valid_tiff_file) -> None:
    """
    Test POST /predict when the model checkpoint is missing or failed to load.
    Temporarily sets the global model instance to None and verifies the endpoint
    returns HTTP 503 Service Unavailable. Restores the model instance afterwards.
    """
    # Keep track of the original loaded model instance
    original_model = api.model_instance
    
    try:
        # Simulate missing model by setting global instance to None
        api.model_instance = None
        
        with open(valid_tiff_file, "rb") as f:
            response = client.post(
                "/predict",
                files={"file": (os.path.basename(valid_tiff_file), f, "image/tiff")}
            )
            
        assert response.status_code == 503
        json_data = response.json()
        assert "model is not loaded" in json_data["detail"]
        
    finally:
        # Crucial step: restore original model to avoid breaking subsequent tests
        api.model_instance = original_model
