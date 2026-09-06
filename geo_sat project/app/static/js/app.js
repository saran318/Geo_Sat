/**
 * Geo-Sat Land Use Classifier - Frontend State Management & API Client
 */

const API_BASE_URL = 'http://127.0.0.1:8080';

// Global state object
const state = {
    isLoading: false,
};

// Utility to handle loading states for any button
function setLoading(isLoading, elementId = null) {
    state.isLoading = isLoading;
    if (elementId) {
        const el = document.getElementById(elementId);
        if (el) {
            if (isLoading) {
                el.classList.add('loading');
                el.disabled = true;
                el.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Processing...';
            } else {
                el.classList.remove('loading');
                el.disabled = false;
                el.innerHTML = el.getAttribute('data-original-text') || 'Submit';
            }
        }
    }
}

// Check Backend Health
async function fetchHealthStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        const statusIndicator = document.getElementById('api-health-status');
        if (statusIndicator) {
            if (data.status === 'healthy') {
                statusIndicator.innerHTML = `<span style="color: var(--accent-green)"><i class="bi bi-check-circle-fill"></i> Model Loaded: ${data.device}</span>`;
            } else {
                statusIndicator.innerHTML = `<span style="color: #ffb4ab"><i class="bi bi-x-circle-fill"></i> Model Not Loaded</span>`;
            }
        }
    } catch (error) {
        console.error("Failed to fetch health status", error);
        const statusIndicator = document.getElementById('api-health-status');
        if (statusIndicator) {
            statusIndicator.innerHTML = `<span style="color: #ffb4ab"><i class="bi bi-exclamation-triangle-fill"></i> Backend Offline</span>`;
        }
    }
}

// Trigger Tile Classification
async function runClassification() {
    const dirInput = document.getElementById('image-dir-input');
    if (!dirInput || !dirInput.value) {
        alert("Please select a dataset.");
        return;
    }

    setLoading(true, 'upload-btn');
    const resultContainer = document.getElementById('classification-result');
    if (resultContainer) resultContainer.style.display = 'none';

    try {
        const formData = new FormData();
        formData.append('image_dir', dirInput.value);

        const response = await fetch(`${API_BASE_URL}/classify-tile`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            if (resultContainer) {
                resultContainer.innerHTML = `
                    <div style="background: rgba(68, 243, 169, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--accent-green);">
                        <h4 style="color: var(--accent-green); margin-bottom: 8px;"><i class="bi bi-check-circle"></i> Classification Complete</h4>
                        <p><strong>Dominant Class:</strong> ${data.dominant_class}</p>
                        <p><strong>Patches Processed:</strong> ${data.total_patches_processed}</p>
                        <p><strong>Mean Confidence:</strong> ${(data.mean_confidence_pct * 100).toFixed(2)}%</p>
                        <p><strong>Processing Time:</strong> ${data.total_processing_time_sec.toFixed(2)}s</p>
                    </div>
                `;
                resultContainer.style.display = 'block';
            }
        } else {
            alert(`Error: ${data.detail || 'Failed to classify tile'}`);
        }
    } catch (error) {
        console.error("Classification error:", error);
        alert("A network error occurred while running the classification.");
    } finally {
        setLoading(false, 'upload-btn');
    }
}

// Trigger Change Detection
async function runChangeDetection() {
    const year1Input = document.getElementById('raster-year1');
    const year2Input = document.getElementById('raster-year2');
    
    if (!year1Input || !year2Input || !year1Input.value || !year2Input.value) {
        alert("Please select both baseline and comparison datasets.");
        return;
    }

    setLoading(true, 'detect-btn');
    const resultContainer = document.getElementById('change-result');
    if (resultContainer) resultContainer.style.display = 'none';

    try {
        const formData = new FormData();
        formData.append('raster_year1', year1Input.value);
        formData.append('raster_year2', year2Input.value);

        const response = await fetch(`${API_BASE_URL}/change-detection`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            if (resultContainer) {
                resultContainer.innerHTML = `
                    <div style="background: rgba(0, 240, 255, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--accent-cyan);">
                        <h4 style="color: var(--accent-cyan); margin-bottom: 8px;"><i class="bi bi-bar-chart-fill"></i> Change Detection Complete</h4>
                        <p><strong>Total Pixels Analyzed:</strong> ${data.total_pixels}</p>
                        <p><strong>Changed Pixels:</strong> ${data.changed_pixels} (${data.change_percentage.toFixed(2)}%)</p>
                        <p><strong>Output CSV:</strong> ${data.output_csv}</p>
                    </div>
                `;
                resultContainer.style.display = 'block';
            }
        } else {
            alert(`Error: ${data.detail || 'Failed to detect changes'}`);
        }
    } catch (error) {
        console.error("Change detection error:", error);
        alert("A network error occurred while running change detection.");
    } finally {
        setLoading(false, 'detect-btn');
    }
}

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    console.log("Geo-Sat UI Initialized");
    fetchHealthStatus();
});
