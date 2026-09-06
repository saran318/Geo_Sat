# Colab 10-City Batch Processing Guide

This guide explains how to run the automated land-cover change-detection pipeline for 10 major Indian cities on Google Colab, leveraging cloud GPUs while keeping results systematically structured in Google Drive.

## Project Architecture & Responsibility
- **Local Machine / Frontend**: Reads from local `data/results` or downloaded Google Drive folders to display stats and maps. Does *not* perform heavy computation.
- **Colab GPU**: Executes Sentinel-2 downloading, patching, ResNet-50 inference, stitching, and statistical aggregation.
- **Google Drive**: Acts as persistent cloud storage for the PyTorch model, GEE credentials, and all pipeline outputs.

## Required Google Drive Setup
Before running the notebook, configure your Google Drive as follows:
```
MyDrive/
└── LandCoverChangeResults/
    ├── models/
    │   └── resnet50_best.pt        <-- Upload your trained model here
    └── service_account.json        <-- Upload your GEE credentials here
```

## How to Open and Run the Notebook
1. Navigate to `notebooks/Colab_Inference_Pipeline.ipynb`.
2. Open it in Google Colab (e.g. upload it to Colab, or use GitHub integration).
3. **Important:** Go to `Runtime > Change runtime type` and select **T4 GPU**.
4. In the `Configuration` cell, set `PROCESS_MODE` to `"selected"` or `"all"`.
   - Start with `"selected"` and `SELECTED_CITIES = ["TinyMumbai"]` to ensure your drive is mounted properly and the pipeline works.
   - Once verified, change to `"all"` to process the remaining 10 cities.
5. Run all cells (`Runtime > Run all`).
6. Follow the prompt to Authorize Google Drive access.

## City Processing Logic and Resilience
Colab sessions can disconnect unpredictably. To solve this, the pipeline incorporates **Stateful Resumption**:
- Output is written sequentially per city.
- A `completed.json` file is written after a city successfully completes.
- The notebook maintains a `processing_status.json` at the root of `LandCoverChangeResults/`.
- If Colab disconnects, you can simply re-run the notebook. It will check `completed.json` and automatically skip cities it already finished.

To force a rerun of a completed city, set `FORCE_RERUN = True` in the configuration cell.

## Checking Progress
You can check progress in two ways:
1. **Notebook Output**: Colab will print step-by-step logs.
2. **Drive Status File**: Open `LandCoverChangeResults/processing_status.json` in your browser to see JSON metadata indicating which cities are pending, running, failed, or completed.

## Storage Structure
Outputs are synced to Drive in the following format:
```
LandCoverChangeResults/
├── Mumbai/
│   ├── predictions/
│   │   ├── classified_2019.tif
│   │   └── classified_2019.png
│   ├── change_maps/
│   │   ├── change_2019_2023.tif
│   │   └── change_2019_2023.png
│   ├── statistics/
│   │   └── area_stats.csv
│   ├── metadata.json
│   └── completed.json
└── processing_status.json
```

## Serving to the Dashboard
1. Download the `LandCoverChangeResults` folder (or specific city folders) from Google Drive.
2. Move the downloaded city folders into `data/results/` on your local machine.
3. Start the FastAPI backend: `uvicorn app.main:app --reload`.
4. The dashboard will automatically read `completed.json` and the `predictions/` and `change_maps/` subdirectories.

## Security Precaution
**Never** commit your `service_account.json` or `resnet50_best.pt` to GitHub. The code explicitly reads them from Google Drive to avoid accidental exposure.
