import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, ImageOverlay, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Sliders, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';
import type { AvailableLayersResponse } from '../../api/types';

// Custom Map Reset / FlyTo helper
const MapViewController: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
};

// Fix default leaflet marker icon in React
const customMarkerIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface SatelliteMapViewProps {
  layersData: AvailableLayersResponse | null;
}

export const SatelliteMapView: React.FC<SatelliteMapViewProps> = ({ layersData }) => {
  const [selectedYear, setSelectedYear] = useState<number>(2023);
  const [overlayOpacity, setOverlayOpacity] = useState<number>(0.85);
  const [baseMapType, setBaseMapType] = useState<'dark' | 'satellite'>('dark');
  const [hoverYear, setHoverYear] = useState<number | null>(null);
  const [hoverMapType, setHoverMapType] = useState<string | null>(null);

  const defaultCenter: [number, number] = [12.9716, 77.5946]; // Bengaluru
  const bounds: [[number, number], [number, number]] = [
    [12.85, 77.45],
    [13.15, 77.75],
  ];

  const currentLayer = layersData?.layers.find((l) => l.year === selectedYear);

  return (
    <div className="panel-surface p-5 rounded-2xl flex flex-col gap-4">
      {/* Top Map Controls Bar (Clean, Borderless Navigation) */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-border">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono font-medium uppercase text-primary bg-muted px-2 py-0.5 rounded">
              GIS Canvas
            </span>
            <span className="text-xs text-muted-foreground font-mono">EPSG:4326</span>
          </div>
          <h2 className="text-base font-bold text-foreground tracking-tight mt-1">
            Bengaluru Metropolitan · Sentinel-2 Classified Land Cover
          </h2>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          {/* Year Selector - Fluid Underline / Pill without Boxed Outlines */}
          <div className="flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5 text-muted-foreground mr-1" />
            <div className="flex items-center relative">
              {[2019, 2020, 2021, 2022, 2023].map((y) => {
                const isSelected = selectedYear === y;
                return (
                  <button
                    key={y}
                    onClick={() => setSelectedYear(y)}
                    onMouseEnter={() => setHoverYear(y)}
                    onMouseLeave={() => setHoverYear(null)}
                    className={`px-3 py-1.5 text-xs font-mono font-medium transition-colors cursor-pointer relative ${
                      isSelected ? 'text-primary font-bold' : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    <span>{y}</span>
                    {hoverYear === y && !isSelected && (
                      <motion.div
                        layoutId="map-year-hover"
                        className="absolute inset-0 bg-muted/70 rounded-md -z-10"
                        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                      />
                    )}
                    {isSelected && (
                      <motion.div
                        layoutId="map-year-active"
                        className="absolute bottom-0 left-2 right-2 h-0.5 bg-primary rounded-full"
                        transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                      />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Base Map Switcher - Borderless Pill Switcher */}
          <div className="flex items-center relative pl-2 border-l border-border">
            {[
              { id: 'dark', label: 'Carto Dark' },
              { id: 'satellite', label: 'Satellite' },
            ].map((mapItem) => {
              const isSelected = baseMapType === mapItem.id;
              return (
                <button
                  key={mapItem.id}
                  onClick={() => setBaseMapType(mapItem.id as 'dark' | 'satellite')}
                  onMouseEnter={() => setHoverMapType(mapItem.id)}
                  onMouseLeave={() => setHoverMapType(null)}
                  className={`px-3 py-1.5 text-xs font-medium transition-colors cursor-pointer relative ${
                    isSelected ? 'text-primary font-semibold' : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <span>{mapItem.label}</span>
                  {hoverMapType === mapItem.id && !isSelected && (
                    <motion.div
                      layoutId="map-type-hover"
                      className="absolute inset-0 bg-muted/70 rounded-md -z-10"
                      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                    />
                  )}
                  {isSelected && (
                    <motion.div
                      layoutId="map-type-active"
                      className="absolute bottom-0 left-2 right-2 h-0.5 bg-primary rounded-full"
                      transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                    />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Map Canvas */}
      <div className="w-full h-[450px] lg:h-[520px] rounded-xl overflow-hidden border border-border relative">
        <MapContainer
          center={defaultCenter}
          zoom={11}
          scrollWheelZoom={true}
          className="w-full h-full z-10"
        >
          <MapViewController center={defaultCenter} zoom={11} />

          {/* Base Tile Layer */}
          {baseMapType === 'dark' ? (
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
          ) : (
            <TileLayer
              attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          )}

          {/* Classified Raster Overlay */}
          {currentLayer?.png_url ? (
            <ImageOverlay
              url={currentLayer.png_url}
              bounds={bounds}
              opacity={overlayOpacity}
            />
          ) : (
            <ImageOverlay
              url="/data/results/classified_2023.png"
              bounds={bounds}
              opacity={overlayOpacity}
            />
          )}

          {/* Center City Pin */}
          <Marker position={defaultCenter} icon={customMarkerIcon}>
            <Popup className="font-sans text-xs">
              <div className="p-1">
                <div className="font-bold text-slate-900">Bengaluru Center</div>
                <div className="text-slate-600 font-mono">12.9716° N, 77.5946° E</div>
                <div className="text-primary font-medium mt-1">Active Sentinel-2 Tile Grid</div>
              </div>
            </Popup>
          </Marker>
        </MapContainer>

        {/* Floating Layer Opacity HUD */}
        <div className="absolute bottom-4 right-4 z-20 bg-card/95 backdrop-blur-md border border-border p-3 rounded-xl flex items-center gap-3 shadow-md">
          <Sliders className="h-4 w-4 text-primary" />
          <div className="flex flex-col gap-1">
            <div className="flex items-center justify-between text-[11px] font-mono text-muted-foreground">
              <span>Layer Opacity</span>
              <span className="text-foreground">{Math.round(overlayOpacity * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.05"
              value={overlayOpacity}
              onChange={(e) => setOverlayOpacity(parseFloat(e.target.value))}
              className="w-28 h-1 bg-muted rounded appearance-none cursor-pointer accent-primary"
            />
          </div>
        </div>

        {/* Floating Layer Badge */}
        <div className="absolute top-4 left-4 z-20 bg-card/95 backdrop-blur-md border border-border px-3 py-1.5 rounded-lg flex items-center gap-2 shadow-md">
          <span className="w-2 h-2 rounded-full bg-primary" />
          <span className="text-xs font-mono font-medium text-foreground">Layer: Sentinel-2 ({selectedYear})</span>
        </div>
      </div>
    </div>
  );
};
