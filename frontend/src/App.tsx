import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Satellite, Download, Activity, Globe2, BarChart3, Crosshair } from 'lucide-react';
import { Navbar } from './components/common/Navbar';
import { CompareSwipeMap } from './components/map/CompareSwipeMap';
import { SatelliteMapView } from './components/map/SatelliteMapView';
import { MapLegend } from './components/map/MapLegend';
import { LandUseStackedArea } from './components/trends/LandUseStackedArea';
import { UrbanVsWaterChart } from './components/trends/UrbanVsWaterChart';
import { ChangeDataTable } from './components/trends/ChangeDataTable';
import { PatchUploader } from './components/inference/PatchUploader';
import { DownloadActionPanel } from './components/export/DownloadActionPanel';
import { HeroBanner } from './components/dashboard/HeroBanner';

import { checkHealth, fetchDemoData, fetchAreaStats, fetchAvailableLayers } from './api/client';
import type { HealthResponse, DemoDataResponse, AreaStatRow, AvailableLayersResponse } from './api/types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedCity, setSelectedCity] = useState<string>('Bengaluru');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [demoData, setDemoData] = useState<DemoDataResponse | null>(null);
  const [areaStats, setAreaStats] = useState<AreaStatRow[]>([]);
  const [layersData, setLayersData] = useState<AvailableLayersResponse | null>(null);
  const [hoveredKpi, setHoveredKpi] = useState<string | null>(null);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [healthRes, demoRes, statsRes, layersRes] = await Promise.all([
          checkHealth(),
          fetchDemoData(selectedCity),
          fetchAreaStats(selectedCity),
          fetchAvailableLayers(selectedCity),
        ]);
        setHealth(healthRes);
        setDemoData(demoRes);
        setAreaStats(statsRes);
        setLayersData(layersRes);
      } catch {
        // Fallback gracefully
      }
    };

    loadInitialData();
  }, [selectedCity]);

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      {/* Background Subtle Grid Texture */}
      <div
        className="fixed inset-0 pointer-events-none z-0 opacity-40 dark:opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(to right, var(--border) 1px, transparent 1px),
            linear-gradient(to bottom, var(--border) 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px',
          WebkitMaskImage: 'radial-gradient(ellipse 70% 60% at 50% 0%, #000 60%, transparent 100%)',
          maskImage: 'radial-gradient(ellipse 70% 60% at 50% 0%, #000 60%, transparent 100%)',
        }}
      />

      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} health={health} />

      <main className="relative z-10 py-12 px-6 lg:px-12 max-w-[1400px] mx-auto font-sans">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          {/* Sticky Left Column: Narrative & Primary Metrics */}
          <div className="lg:col-span-4 flex flex-col justify-between lg:sticky lg:top-24 h-fit gap-8">
            <div>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
                <div className="flex items-center gap-2 text-xs font-mono text-primary uppercase tracking-widest">
                  <Satellite className="h-3.5 w-3.5" />
                  GeoSat Engine
                </div>
                
                {/* City Selector */}
                <select 
                  className="bg-card text-foreground text-xs font-mono border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer w-full sm:w-auto shadow-sm"
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                >
                  <option value="Bengaluru">Bengaluru</option>
                  <option value="Mumbai">Mumbai</option>
                  <option value="Delhi">Delhi</option>
                  <option value="Chennai">Chennai</option>
                  <option value="Kolkata">Kolkata</option>
                </select>
              </div>
              <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground leading-tight">
                Satellite Land-Use & Change Detection.
              </h1>
              <p className="text-xs sm:text-sm text-muted-foreground mt-3 leading-relaxed">
                Evaluating multi-temporal spectral shifts across the Bengaluru metropolitan region using Sentinel-2 tensor extraction and ResNet-50 classification.
              </p>
            </div>

            {/* Left KPI Stream */}
            <div 
              className="flex flex-col gap-2 py-6 border-y border-border/60"
              onMouseLeave={() => setHoveredKpi(null)}
            >
              {[
                {
                  id: 'built-up',
                  label: 'Built-Up Expansion',
                  value: demoData?.metrics?.urban_growth_km2 ? `+${demoData.metrics.urban_growth_km2} km²` : '---',
                  desc: 'Urban sprawl identified',
                  valColor: 'text-foreground',
                  descColor: 'text-primary'
                },
                {
                  id: 'water',
                  label: 'Lake Water Area',
                  value: demoData?.metrics?.water_loss_km2 ? `-${demoData.metrics.water_loss_km2} km²` : '---',
                  desc: 'Surface water reduction',
                  valColor: 'text-foreground',
                  descColor: 'text-muted-foreground'
                },
                {
                  id: 'accuracy',
                  label: 'Overall Accuracy',
                  value: demoData?.metrics?.accuracy_pct ? `${demoData.metrics.accuracy_pct}%` : '---',
                  desc: 'India LULC Benchmark',
                  valColor: 'text-primary',
                  descColor: 'text-muted-foreground'
                }
              ].map((kpi) => (
                <div 
                  key={kpi.id}
                  className="relative p-4 -mx-4 rounded-xl transition-all cursor-default"
                  onMouseEnter={() => setHoveredKpi(kpi.id)}
                >
                  {hoveredKpi === kpi.id && (
                    <motion.div
                      layoutId="kpi-hover-bg"
                      className="absolute inset-0 bg-muted/50 rounded-xl z-0"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1, transition: { duration: 0.15 } }}
                      exit={{ opacity: 0, transition: { duration: 0.15, delay: 0.2 } }}
                    />
                  )}
                  <div className="relative z-10">
                    <span className="text-[11px] font-mono text-muted-foreground uppercase">{kpi.label}</span>
                    <div className={`text-3xl font-bold font-mono mt-0.5 ${kpi.valColor}`}>
                      {kpi.value}
                    </div>
                    <div className={`text-xs font-mono ${kpi.descColor}`}>{kpi.desc}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="text-xs font-mono text-muted-foreground">
              BCA Capstone · Sentinel-2 L2A · 10m Ground Resolution
            </div>
          </div>

          {/* Right Scrollable Stream: Continuous Data Sections */}
          <div className="lg:col-span-8 flex flex-col gap-16 lg:pl-6">
            
            {/* Overview Stream */}
            {activeTab === 'overview' && (
              <div className="flex flex-col gap-16 animate-fadeIn">
                <HeroBanner cityName={selectedCity} onNavigate={setActiveTab} />
                
                {/* Section: Spatial Mapping */}
                <div className="flex flex-col gap-5 border-b border-border/60 pb-12">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono uppercase text-muted-foreground">01 / SPATIAL MAPPING</span>
                  </div>
                  <h2 className="text-xl font-bold text-foreground">Multi-Temporal Change Map (2019 vs 2023)</h2>
                  <CompareSwipeMap cityName={selectedCity} year1={2019} year2={2023} />
                  <MapLegend />
                </div>

                {/* Section: Trend Analytics */}
                <div className="flex flex-col gap-5 border-b border-border/60 pb-12">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono uppercase text-muted-foreground">02 / TREND ANALYTICS</span>
                  </div>
                  <h2 className="text-xl font-bold text-foreground">Land-Use Transition Trajectories</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <LandUseStackedArea trends={demoData?.trends} />
                    <UrbanVsWaterChart trends={demoData?.trends} />
                  </div>
                </div>

                {/* Section: Transition Data */}
                <div className="flex flex-col gap-5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono uppercase text-muted-foreground">03 / TRANSITION DATA</span>
                  </div>
                  <h2 className="text-xl font-bold text-foreground">Tabular Area Breakdown</h2>
                  <ChangeDataTable stats={areaStats} />
                </div>
              </div>
            )}

            {/* Map Studio Stream */}
            {activeTab === 'map' && (
              <div className="flex flex-col gap-12 animate-fadeIn">
                <div className="flex flex-col gap-5 border-b border-border/60 pb-12">
                  <span className="text-xs font-mono uppercase text-muted-foreground">01 / INTERACTIVE STUDIO</span>
                  <h2 className="text-xl font-bold text-foreground">High-Resolution Sentinel-2 Tensors</h2>
                  <SatelliteMapView layersData={layersData} />
                  <MapLegend />
                </div>
              </div>
            )}

            {/* Trends Stream */}
            {activeTab === 'trends' && (
              <div className="flex flex-col gap-12 animate-fadeIn">
                <div className="flex flex-col gap-5 border-b border-border/60 pb-12">
                  <span className="text-xs font-mono uppercase text-muted-foreground">01 / TIME-SERIES</span>
                  <h2 className="text-xl font-bold text-foreground">Longitudinal Trajectories</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <LandUseStackedArea trends={demoData?.trends} />
                    <UrbanVsWaterChart trends={demoData?.trends} />
                  </div>
                </div>
                <div className="flex flex-col gap-5">
                  <span className="text-xs font-mono uppercase text-muted-foreground">02 / RAW TRANSITIONS</span>
                  <h2 className="text-xl font-bold text-foreground">Area Flux Calculations</h2>
                  <ChangeDataTable stats={areaStats} />
                </div>
              </div>
            )}

            {/* Inference Stream */}
            {activeTab === 'inference' && (
              <div className="flex flex-col gap-12 animate-fadeIn">
                <div className="flex flex-col gap-5">
                  <span className="text-xs font-mono uppercase text-muted-foreground">01 / LIVE INFERENCE</span>
                  <h2 className="text-xl font-bold text-foreground">Execute Tensor Classification</h2>
                  <PatchUploader />
                  <div className="mt-8">
                    <MapLegend />
                  </div>
                </div>
              </div>
            )}

            {/* Export Stream */}
            {activeTab === 'export' && (
              <div className="flex flex-col gap-12 animate-fadeIn">
                <div className="flex flex-col gap-5 border-b border-border/60 pb-12">
                  <span className="text-xs font-mono uppercase text-muted-foreground">01 / DATA EXPORT</span>
                  <h2 className="text-xl font-bold text-foreground">Retrieve Deliverables</h2>
                  <DownloadActionPanel />
                </div>
                <div className="flex flex-col gap-5">
                  <span className="text-xs font-mono uppercase text-muted-foreground">02 / REFERENCE TABLES</span>
                  <h2 className="text-xl font-bold text-foreground">Exportable Tabular Data</h2>
                  <ChangeDataTable stats={areaStats} />
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
