# Geo-Satellite Imagery Project

## Project Overview
This project focuses on the acquisition, organization, and visualization of satellite imagery, specifically from the Sentinel-2 mission. It provides an automated setup to download specific Sentinel-2 tiles using the `sentinelsat` library and provides scripts to download and explore the multi-spectral EuroSAT land cover classification dataset.

## Installation

### Python Environment & Virtual Environment Creation
It is highly recommended to use a virtual environment to isolate the dependencies of this project.

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages using the generated requirements file:
```bash
pip install -r requirements.txt
```

### Google Colab Setup
If you prefer running the visualization notebooks in Google Colab:
1. Upload the project folder to your Google Drive.
2. Open the notebook in Google Colab.
3. Run `!pip install -r requirements.txt` in the very first cell.
4. Mount your Google Drive so the notebook can access the downloaded datasets:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

### GPU Setup
If you plan to extend this project to deep learning tasks later:
- **Local:** Ensure you have the appropriate NVIDIA drivers and CUDA toolkit installed for your GPU. When installing PyTorch later, use the index provided by `pytorch.org` (e.g., `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`).
- **Google Colab:** Go to `Runtime` -> `Change runtime type` and select `GPU` (e.g., T4 or A100) as the hardware accelerator.

## Registrations

### Copernicus Open Access Hub (Copernicus Data Space Ecosystem)
*Note: The traditional Copernicus Open Access Hub has transitioned to the Copernicus Data Space Ecosystem (CDSE).*
1. Go to the [Copernicus Data Space Ecosystem portal](https://dataspace.copernicus.eu/).
2. Click on "Login/Register" in the top right corner.
3. Fill out the registration form with your details.
4. Verify your email address.
5. You will use these credentials (username and password) in the `sentinelsat` python script to download Sentinel-2 imagery.

### Google Earth Engine (GEE)
1. Go to the [Google Earth Engine signup page](https://earthengine.google.com/signup/).
2. Log in with your Google Account.
3. Register your project (Non-commercial / Academic / Research depending on your use case).
4. Once your account is approved, you can authenticate via Python using `ee.Authenticate()` and `ee.Initialize()` if you extend the project to use the GEE Python API.

## Dataset Overview
- **EuroSAT:** A dataset and deep learning benchmark for land use and land cover classification based on Sentinel-2 satellite images. It contains 27,000 labeled and georeferenced images spanning 10 different land cover classes. This project uses the Multi-spectral (13-band) version.
- **Sentinel-2 Tiles:** High-resolution optical imagery covering 13 spectral bands. We filter these tiles to ensure high quality (e.g., 0-10% cloud cover).

## Workflow Phases
- **Phase 1 (Setup & Download)**: Local (Antigravity IDE)
- **Phase 2 (Data Preprocessing)**: Local (Antigravity IDE)
- **Phase 3 (Model Training)**: Google Colab GPU (Optional: Local if sufficient GPU is available)

## Phase 2: Data Preprocessing
Phase 2 implements a memory-efficient preprocessing pipeline to convert raw multi-band Sentinel-2 imagery (B2, B3, B4, B8) into 6-channel tensors (Blue, Green, Red, NIR, NDVI, NDWI) ready for PyTorch model training.

### Key Components
- **`src/preprocessing/preprocess.py`**: A shared module designed to securely read satellite bands lazily using `rasterio` windowed reading. It computes indices and yields patches through a memory-efficient generator, preventing Out-Of-Memory errors on restricted environments.
- **`training/dataset.py`**: A custom PyTorch `Dataset` that implements lazy loading of generated patches structured in an `ImageFolder` layout. Includes robust tensor augmentation (Random Flips, Rotations) and automatically handles Dataset splits (70/15/15) with customized `DataLoaders`.
- **`notebooks/data_pipeline.ipynb`**: An interactive demonstration covering the end-to-end data pipeline, including band visualization, memory tracking (`psutil`), generator-based patch extraction, and DataLoader consumption.

### Memory Optimization Guidelines (Local & Colab)
When extending or executing the data pipeline:
- Use `extract_patches()` generator directly; **never** store large sets of patches in lists.
- PyTorch tensors default to `float32` instead of `float64`.
- Intermediate arrays are manually deleted (`del array`) and `gc.collect()` is triggered after memory-intensive operations.

## Phase 3: Model Training
Phase 3 orchestrates the training, evaluation, and checkpointing of the deep learning models. This phase is designed to run efficiently on Google Colab GPUs but is fully compatible with local setups.

### Architectures
- **BaselineCNN**: A custom Convolutional Neural Network built for 6-channel input.
- **ResNet50 (Transfer Learning)**: Modifies `torchvision.models.resnet50` to accept 6 channels. The first 3 channels inherit pretrained RGB weights, and the additional channels (NIR, NDVI, NDWI) are initialized using the mean of the RGB weights. Only the final blocks and classifier are trained.

### Configuration (`training/config.py`)
All configurable parameters (hyperparameters, batch size, epochs, device detection) are centralized in `training/config.py`. Adjust this file before running training to configure the pipeline. Optional TensorBoard support can also be toggled here.

### How to Train
You can train locally or run the provided `train_colab.ipynb` notebook on Google Colab.
To train via CLI:
```bash
python training/train.py --data_dir data/preprocessed --model resnet50
```
Available `--model` options: `resnet50` or `cnn`.

### How to Resume Training
To resume training from a saved checkpoint, use the `--resume` flag:
```bash
python training/train.py --data_dir data/preprocessed --model resnet50 --resume models/resnet50_best.pt
```

### Outputs
Models, checkpoints, and evaluation metrics are saved to the `models/` directory:
- `[model]_best.pt`: The model checkpoint with the lowest validation loss.
- `[model]_history.json`: Epoch-by-epoch training statistics.
- `confusion_matrix.png`, `roc_curve.png`, `training_history.png`: Visual evaluation artifacts.
- `classification_report.txt`: Precision, recall, and F1 scores.

## Phase 5: Streamlit Frontend & Deploy
Phase 5 introduces an interactive web application built with Streamlit. It visualizes the multi-year land cover classifications on a Folium map and provides Plotly charts for year-over-year trend analysis (Urban growth vs Vegetation decline).

### Running the App Locally
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Since real Google Earth Engine data is missing, generate synthetic Person 2 data by running:
   ```bash
   python run_person2_pipeline.py
   ```
3. Start the Streamlit app:
   ```bash
   streamlit run app/streamlit_app.py
   ```

### Live Application & Demo
- **Live URL**: [Streamlit Cloud Deployment (Coming Soon)](#)
- **Demo Video**: [YouTube Link (Coming Soon)](#)
