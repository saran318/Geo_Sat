import React, { useState } from 'react';
import { Satellite, Calendar } from 'lucide-react';

/**
 * TEMPLATE 4: FULL-BLEED MAP STUDIO
 * Aesthetic: Full-bleed geospatial cockpit. The map dominates the entire viewport,
 * with floating borderless text telemetry HUDs. Zero white card boxes.
 */
export const Template4_FullBleedMapStudio: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number>(2023);

  return (
    <div className="relative w-full h-screen bg-background overflow-hidden font-sans text-foreground flex flex-col justify-between p-6 lg:p-10">
      {/* 1. Top HUD (Floating text overlay without card box) */}
      <div className="z-20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-primary uppercase tracking-wider">
            <Satellite className="h-4 w-4" />
            Sentinel-2 Spatial Studio · 10m L2A
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground mt-0.5">
            Bengaluru Metropolitan Basin ({selectedYear})
          </h1>
        </div>

        {/* Year Scrubber (Fluid text buttons) */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
          {[2019, 2020, 2021, 2022, 2023].map((y) => (
            <button
              key={y}
              onClick={() => setSelectedYear(y)}
              className={`cursor-pointer transition-colors ${
                selectedYear === y
                  ? 'text-primary font-bold underline underline-offset-4'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {y}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Middle Map Simulation Canvas */}
      <div className="absolute inset-0 z-0 bg-muted flex items-center justify-center">
        {/* Synthetic Vector / SVG Satellite Raster Simulation */}
        <svg className="w-full h-full opacity-70" preserveAspectRatio="none" viewBox="0 0 1000 600">
          <rect width="1000" height="600" fill="var(--card)" />
          <path d="M 100 50 Q 450 200 650 100 T 950 250 L 1000 600 L 0 600 Z" fill="var(--secondary)" />
          <circle cx="500" cy="300" r="180" fill="var(--border)" opacity="0.6" />
          <ellipse cx="520" cy="290" rx="90" ry="45" fill="var(--primary)" opacity="0.6" />
        </svg>
      </div>

      {/* 3. Bottom Floating HUD Telemetry (Zero card container) */}
      <div className="z-20 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="flex flex-col gap-2 max-w-md">
          <span className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
            Live Extent Telemetry
          </span>
          <div className="text-sm font-semibold text-foreground">
            12.9716° N, 77.5946° E · Total Extent: 85.59 km²
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Classified with 8 EuroSAT signatures. High-density residential expansion detected along outer ring corridor.
          </p>
        </div>

        {/* Quick KPI stats inline */}
        <div className="flex items-center gap-8 text-xs font-mono">
          <div>
            <div className="text-muted-foreground uppercase text-[10px]">Urban Expansion</div>
            <div className="text-lg font-bold text-foreground">+10.75 km² (+34.2%)</div>
          </div>
          <div>
            <div className="text-muted-foreground uppercase text-[10px]">Water Loss</div>
            <div className="text-lg font-bold text-foreground">-2.90 km² (-24.1%)</div>
          </div>
          <div>
            <div className="text-muted-foreground uppercase text-[10px]">ResNet-50 Accuracy</div>
            <div className="text-lg font-bold text-primary">91.4% (IoU 78.6%)</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Template4_FullBleedMapStudio;
