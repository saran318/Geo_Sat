export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  device: string;
}

export interface SinglePredictionResponse {
  predicted_class: string;
  confidence: number;
  inference_time: number;
  status: string;
}

export interface WGS84Bounds {
  min_lon: number;
  min_lat: number;
  max_lon: number;
  max_lat: number;
}

export interface TileClassificationResponse {
  status: string;
  output_geotiff: string;
  width: number;
  height: number;
  crs: string;
  wgs84_bounds: WGS84Bounds;
  total_patches_processed: number;
  dominant_class: string;
  mean_confidence_pct: number;
  total_processing_time_sec: number;
}

export interface ChangeDetectionResponse {
  status: string;
  output_geotiff: string;
  output_csv: string;
  total_pixels: number;
  changed_pixels: number;
  unchanged_pixels: number;
  change_percentage: number;
}

export interface AreaStatRow {
  class_index: number;
  class_name: string;
  year1_pixels?: number;
  year2_pixels?: number;
  year1_area_ha?: number;
  year2_area_ha?: number;
  year1_area_km2: number;
  year2_area_km2: number;
  net_change_ha?: number;
  net_change_km2?: number;
  pct_change: number;
}

export interface LayerMetadata {
  year: number;
  png_url: string | null;
  tif_exists: boolean;
  label: string;
  bounds: [[number, number], [number, number]];
}

export interface DiffMapMetadata {
  period: string;
  png_url: string | null;
}

export interface AvailableLayersResponse {
  status: string;
  city: string;
  coordinates: { lat: number; lon: number };
  layers: LayerMetadata[];
  diff_maps: DiffMapMetadata[];
}

export interface TrendDataPoint {
  year: number;
  Urban: number;
  Vegetation: number;
  Water: number;
  Agriculture: number;
}

export interface DemoDataResponse {
  city: string;
  region: string;
  years: number[];
  kpis: {
    total_area_analyzed_km2: number;
    urban_growth_km2: number;
    urban_growth_pct: number;
    vegetation_loss_km2: number;
    vegetation_loss_pct: number;
    water_loss_km2: number;
    water_loss_pct: number;
    model_accuracy: number;
    water_iou: number;
  };
  class_colors: Record<string, string>;
  trends: TrendDataPoint[];
}
