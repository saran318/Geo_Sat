"""
Main application module integrating Person 2's ML Inference API with Person 3's Jinja2 Frontend.
"""

import os
import sys
import time
import shutil
import tempfile
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List

import torch
import rasterio
from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Ensure project root is in system path for clean imports
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(_APP_DIR)
if project_root not in sys.path:
    sys.path.append(project_root)

import backend_config as bcfg
import utils
from predict import load_inference_model, predict, classify_tile
from src.change_detection.diff_maps import compute_change_detection, align_and_load_rasters
from src.change_detection.stats import compute_landcover_area_stats, export_area_stats_csv

logger = utils.get_logger(__name__)

# Global model instance placeholder
model_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that handles server startup and shutdown tasks.
    Pre-loads the trained PyTorch model into memory once on startup.
    Automatic GitHub release weight download is triggered if weights are missing locally.
    """
    global model_instance
    logger.info("Initializing API Lifespan: Loading trained model...")
    
    # Auto-download weights if missing
    if not os.path.exists(bcfg.MODEL_PATH):
        utils.download_model_weights_if_missing(bcfg.MODEL_PATH, bcfg.MODEL_DOWNLOAD_URL)

    try:
        model_instance = load_inference_model(
            model_path=bcfg.MODEL_PATH,
            model_name=bcfg.MODEL_NAME,
            num_classes=bcfg.NUM_CLASSES,
            device=bcfg.DEVICE
        )
        app.state.model_instance = model_instance
        logger.info("Model loaded successfully and cached for inference requests.")
    except Exception as e:
        logger.error(f"Failed to load model on startup: {e}")
        app.state.model_instance = None
            
    yield
    # Shutdown operations
    logger.info("API Lifespan closing. Cleaning up resources...")
    if model_instance is not None:
        del model_instance
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# Initialize FastAPI application
app = FastAPI(
    title="Geo-Sat Land Use Classifier",
    description="Full-stack application serving the Jinja2 UI and ML REST endpoints.",
    version="3.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware for external access if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount StaticFiles
app.mount("/static", StaticFiles(directory=os.path.join(_APP_DIR, "static")), name="static")
app.mount("/data", StaticFiles(directory=os.path.join(project_root, "data")), name="data") # Exposing images for frontend

# Setup Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(_APP_DIR, "templates"))


# ── FRONTEND ROUTES ──
@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Dashboard | Geo-Sat"})

@app.get("/analysis", response_class=HTMLResponse)
async def serve_analysis(request: Request):
    return templates.TemplateResponse("analysis.html", {"request": request})

@app.get("/map", response_class=HTMLResponse)
async def serve_map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})

@app.get("/trends", response_class=HTMLResponse)
async def serve_trends(request: Request):
    return templates.TemplateResponse("trends.html", {"request": request})

@app.get("/export", response_class=HTMLResponse)
async def serve_export(request: Request):
    return templates.TemplateResponse("export.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def serve_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


# ── INCLUDE ML ROUTER ──
from app.services.backend_client import ml_router
app.include_router(ml_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
