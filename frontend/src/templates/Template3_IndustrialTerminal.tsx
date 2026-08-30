import React, { useState } from 'react';
import { Terminal } from 'lucide-react';

/**
 * TEMPLATE 3: INDUSTRIAL TERMINAL & TELEMETRY
 * Aesthetic: Raw CAD blueprint & satellite ground terminal. Monospace-driven, crosshair markers.
 * Zero rounded boxes, zero white card containers.
 */
export const Template3_IndustrialTerminal: React.FC = () => {
  const [selectedBand, setSelectedBand] = useState<string>('B08');

  const telemetryLogs = [
    { time: '09:14:02.102', event: 'SENTINEL2_L2A_GRANULE_ACQUIRED', status: 'OK' },
    { time: '09:14:02.340', event: 'EXTRACT_BANDS_B2_B3_B4_B8', status: 'OK' },
    { time: '09:14:02.580', event: 'COMPUTE_NDVI_NDWI_CHANNELS', status: 'OK' },
    { time: '09:14:03.110', event: 'RESNET50_TENSOR_FORWARD_PASS', status: '27.4ms' },
    { time: '09:14:03.450', event: 'AREA_STATISTICS_AGGREGATED', status: '85.59 km²' },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground py-8 px-6 sm:px-10 max-w-7xl mx-auto flex flex-col gap-8 font-mono text-xs selection:bg-primary/20">
      {/* 1. Terminal Top Bar */}
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-border/80">
        <div className="flex items-center gap-3">
          <Terminal className="h-4 w-4 text-primary" />
          <span className="font-bold tracking-wider uppercase text-foreground">
            SYS::GEOSAT_SATELLITE_TERMINAL_V2.4
          </span>
        </div>
        <div className="flex items-center gap-4 text-muted-foreground">
          <span>LAT: 12.9716°N</span>
          <span>LON: 77.5946°E</span>
          <span className="text-primary font-bold">MODE: INFERENCE_ONLINE</span>
        </div>
      </header>

      {/* 2. Main Terminal Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Telemetry Column */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          <div>
            <span className="text-[11px] text-muted-foreground uppercase block mb-1">
              [PRIMARY_TELEMETRY_STREAM]
            </span>
            <div className="text-2xl font-bold tracking-tight text-foreground font-sans">
              BENGALURU MULTI-TEMPORAL CLASSIFICATION MATRIX
            </div>
          </div>

          {/* Crosshair Data Matrix */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-4 border-y border-border/80">
            <div>
              <div className="text-muted-foreground uppercase text-[10px]">::URBAN_EXPANSION</div>
              <div className="text-xl font-bold text-foreground mt-1">+10.75 KM²</div>
              <div className="text-[11px] text-primary">+34.20% SURGE</div>
            </div>
            <div>
              <div className="text-muted-foreground uppercase text-[10px]">::VEGETATION_DELTA</div>
              <div className="text-xl font-bold text-foreground mt-1">-5.22 KM²</div>
              <div className="text-[11px] text-muted-foreground">-14.30% LOSS</div>
            </div>
            <div>
              <div className="text-muted-foreground uppercase text-[10px]">::LAKE_SURFACE_NDWI</div>
              <div className="text-xl font-bold text-foreground mt-1">-2.90 KM²</div>
              <div className="text-[11px] text-muted-foreground">-24.10% DEPLETED</div>
            </div>
            <div>
              <div className="text-muted-foreground uppercase text-[10px]">::ACCURACY_VAL</div>
              <div className="text-xl font-bold text-primary mt-1">91.40%</div>
              <div className="text-[11px] text-muted-foreground">IOU: 78.60%</div>
            </div>
          </div>

          {/* Interactive Band Inspector (No boxes) */}
          <div className="flex flex-col gap-3">
            <span className="text-[11px] text-muted-foreground uppercase">
              [CHANNEL_SPECTRAL_SELECTOR]
            </span>
            <div className="flex flex-wrap items-center gap-6">
              {[
                { band: 'B02', label: 'BLUE (490nm)' },
                { band: 'B03', label: 'GREEN (560nm)' },
                { band: 'B04', label: 'RED (665nm)' },
                { band: 'B08', label: 'NIR (842nm)' },
                { band: 'NDVI', label: 'VEG_INDEX' },
                { band: 'NDWI', label: 'WATER_INDEX' },
              ].map((b) => (
                <button
                  key={b.band}
                  onClick={() => setSelectedBand(b.band)}
                  className={`text-left cursor-pointer transition-colors ${
                    selectedBand === b.band
                      ? 'text-primary font-bold underline underline-offset-4'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  [{b.band}] <span className="text-[11px] font-normal">{b.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Event Stream Log */}
        <div className="lg:col-span-4 flex flex-col gap-3 border-l border-border/80 pl-0 lg:pl-6">
          <span className="text-[11px] text-muted-foreground uppercase">
            [LIVE_EVENT_LOG]
          </span>
          <div className="flex flex-col gap-2 font-mono text-[11px]">
            {telemetryLogs.map((log, idx) => (
              <div key={idx} className="flex items-start justify-between gap-2 border-b border-border/40 pb-1.5">
                <span className="text-muted-foreground">{log.time}</span>
                <span className="text-foreground">{log.event}</span>
                <span className="text-primary font-bold">{log.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Template3_IndustrialTerminal;
