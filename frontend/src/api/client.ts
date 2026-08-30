import axios from 'axios';
import type {
  HealthResponse,
  SinglePredictionResponse,
  TileClassificationResponse,
  ChangeDetectionResponse,
  AreaStatRow,
  AvailableLayersResponse,
  DemoDataResponse,
} from './types';

const API_BASE = '';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const checkHealth = async (): Promise<HealthResponse> => {
  try {
    const res = await api.get<HealthResponse>('/health');
    return res.data;
  } catch {
    return {
      status: 'offline',
      model_loaded: false,
      device: 'CPU (Demo Mode)',
    };
  }
};

export const fetchDemoData = async (): Promise<DemoDataResponse> => {
  try {
    const res = await api.get<DemoDataResponse>('/api/demo-data');
    return res.data;
  } catch {
    // Fallback data
    return {
      city: 'Mumbai',
      region: 'Maharashtra, India',
      years: [2019, 2020, 2021, 2022, 2023],
      kpis: {
        total_area_analyzed_km2: 85.59,
        urban_growth_km2: 10.75,
        urban_growth_pct: 34.2,
        vegetation_loss_km2: -5.22,
        vegetation_loss_pct: -14.3,
        water_loss_km2: -2.9,
        water_loss_pct: -24.1,
        model_accuracy: 91.4,
        water_iou: 78.6,
      },
      class_colors: {
        AnnualCrop: '#facc15',
        Forest: '#15803d',
        HerbaceousVegetation: '#4ade80',
        Highway: '#94a3b8',
        Industrial: '#dc2626',
        Pasture: '#a3e635',
        PermanentCrop: '#eab308',
        Residential: '#f97316',
        River: '#38bdf8',
        SeaLake: '#2563eb',
      },
      trends: [
        { year: 2019, Urban: 31.4, Vegetation: 37.5, Water: 12.0, Agriculture: 4.69 },
        { year: 2020, Urban: 33.8, Vegetation: 36.1, Water: 11.2, Agriculture: 4.49 },
        { year: 2021, Urban: 36.5, Vegetation: 34.8, Water: 10.5, Agriculture: 3.79 },
        { year: 2022, Urban: 39.2, Vegetation: 33.2, Water: 9.8, Agriculture: 3.39 },
        { year: 2023, Urban: 42.15, Vegetation: 32.28, Water: 9.1, Agriculture: 2.06 },
      ],
    };
  }
};

export const fetchAreaStats = async (): Promise<AreaStatRow[]> => {
  try {
    const res = await api.get<{ status: string; data: AreaStatRow[] }>('/api/stats/summary');
    return res.data.data;
  } catch {
    return [
      { class_index: 0, class_name: 'AnnualCrop', year1_area_km2: 21.09, year2_area_km2: 18.42, net_change_km2: -2.67, pct_change: -12.6 },
      { class_index: 1, class_name: 'Forest', year1_area_km2: 14.5, year2_area_km2: 12.1, net_change_km2: -2.4, pct_change: -16.5 },
      { class_index: 2, class_name: 'HerbaceousVegetation', year1_area_km2: 1.95, year2_area_km2: 1.8, net_change_km2: -0.15, pct_change: -7.7 },
      { class_index: 3, class_name: 'Highway', year1_area_km2: 4.2, year2_area_km2: 5.8, net_change_km2: 1.6, pct_change: 38.1 },
      { class_index: 4, class_name: 'Industrial', year1_area_km2: 3.1, year2_area_km2: 5.45, net_change_km2: 2.35, pct_change: 75.8 },
      { class_index: 5, class_name: 'Residential', year1_area_km2: 28.3, year2_area_km2: 35.1, net_change_km2: 6.8, pct_change: 24.0 },
      { class_index: 6, class_name: 'River', year1_area_km2: 3.4, year2_area_km2: 2.9, net_change_km2: -0.5, pct_change: -14.7 },
      { class_index: 7, class_name: 'SeaLake', year1_area_km2: 8.6, year2_area_km2: 6.2, net_change_km2: -2.4, pct_change: -27.9 },
    ];
  }
};

export const fetchAvailableLayers = async (): Promise<AvailableLayersResponse> => {
  try {
    const res = await api.get<AvailableLayersResponse>('/api/layers/available');
    return res.data;
  } catch {
    return {
      status: 'demo',
      city: 'Mumbai, Maharashtra',
      coordinates: { lat: 19.0760, lon: 72.8777 },
      layers: [
        { year: 2019, png_url: '/data/results/classified_2019.png', tif_exists: true, label: 'Sentinel-2 2019', bounds: [[18.85, 72.75], [19.15, 73.05]] },
        { year: 2020, png_url: '/data/results/classified_2020.png', tif_exists: true, label: 'Sentinel-2 2020', bounds: [[18.85, 72.75], [19.15, 73.05]] },
        { year: 2021, png_url: '/data/results/classified_2021.png', tif_exists: true, label: 'Sentinel-2 2021', bounds: [[18.85, 72.75], [19.15, 73.05]] },
        { year: 2022, png_url: '/data/results/classified_2022.png', tif_exists: true, label: 'Sentinel-2 2022', bounds: [[18.85, 72.75], [19.15, 73.05]] },
        { year: 2023, png_url: '/data/results/classified_2023.png', tif_exists: true, label: 'Sentinel-2 2023', bounds: [[18.85, 72.75], [19.15, 73.05]] },
      ],
      diff_maps: [
        { period: '2019 - 2020', png_url: '/data/results/change_2019_2020.png' },
        { period: '2020 - 2021', png_url: '/data/results/change_2020_2021.png' },
        { period: '2021 - 2022', png_url: '/data/results/change_2021_2022.png' },
        { period: '2022 - 2023', png_url: '/data/results/change_2022_2023.png' },
      ],
    };
  }
};

export const predictPatch = async (file: File): Promise<SinglePredictionResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post<SinglePredictionResponse>('/predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const classifyTile = async (imageDir: string): Promise<TileClassificationResponse> => {
  const formData = new FormData();
  formData.append('image_dir', imageDir);
  const res = await api.post<TileClassificationResponse>('/classify-tile', formData);
  return res.data;
};

export const runChangeDetection = async (raster1: string, raster2: string): Promise<ChangeDetectionResponse> => {
  const formData = new FormData();
  formData.append('raster_year1', raster1);
  formData.append('raster_year2', raster2);
  const res = await api.post<ChangeDetectionResponse>('/change-detection', formData);
  return res.data;
};
