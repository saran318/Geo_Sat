import React from 'react';
import { ArrowRight, Activity, Layers, MapPin } from 'lucide-react';

interface HeroBannerProps {
  onNavigate: (tab: string) => void;
}

export const HeroBanner: React.FC<HeroBannerProps> = ({ onNavigate }) => {
  const bands = [
    { code: 'B2', name: 'Blue 490nm', col: '#3b6b80' },
    { code: 'B3', name: 'Green 560nm', col: '#2d5e3f' },
    { code: 'B4', name: 'Red 665nm', col: '#8c4a38' },
    { code: 'B8', name: 'NIR 842nm', col: '#1b3a27' },
    { code: 'NDVI', name: 'Veg. Index', col: '#5f936c' },
    { code: 'NDWI', name: 'Water Index', col: '#2a5a68' },
  ];

  return (
    <section className="panel-surface rounded-2xl p-6 lg:p-7 shadow-xs">
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        {/* Left Headline & Content */}
        <div className="max-w-2xl">
          {/* Unboxed Minimal Eyebrow */}
          <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground mb-2">
            <span className="font-semibold text-primary">Sentinel-2 Multi-Spectral</span>
            <span>·</span>
            <span className="flex items-center gap-1">
              <MapPin className="h-3 w-3 text-primary" />
              Bengaluru (2019–2023)
            </span>
          </div>

          <h2 className="text-xl sm:text-2xl lg:text-[1.65rem] font-bold text-foreground tracking-tight leading-snug">
            Satellite Land-Cover & Change Intelligence
          </h2>

          <p className="text-xs sm:text-sm text-muted-foreground mt-2 leading-relaxed max-w-[62ch]">
            6-channel ResNet-50 pipeline combining Sentinel-2 bands with mathematical NDVI and NDWI indices for 10m land classification.
          </p>

          {/* Clean Inline Input Tensors without Boxed Rectangles */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-4 pt-3 border-t border-border/80 text-xs font-mono">
            <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
              Input Tensors:
            </span>
            {bands.map((b) => (
              <span key={b.code} className="inline-flex items-center gap-1.5 text-foreground">
                <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: b.col }} />
                <span className="font-semibold text-foreground">{b.code}</span>
                <span className="text-[11px] text-muted-foreground font-normal">({b.name})</span>
              </span>
            ))}
          </div>
        </div>

        {/* Right CTA Actions */}
        <div className="flex flex-col sm:flex-row lg:flex-col gap-2.5 w-full lg:w-auto shrink-0">
          <button
            onClick={() => onNavigate('map')}
            className="px-4 py-2.5 rounded-lg bg-primary hover:opacity-90 active:scale-[0.98] text-primary-foreground font-medium text-xs flex items-center justify-center gap-2 transition-all cursor-pointer shadow-xs"
          >
            <Layers className="h-3.5 w-3.5" />
            <span>Open Map Studio</span>
            <ArrowRight className="h-3 w-3" />
          </button>
          <button
            onClick={() => onNavigate('trends')}
            className="px-4 py-2.5 rounded-lg hover:bg-muted/70 active:scale-[0.98] text-foreground font-medium text-xs flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            <Activity className="h-3.5 w-3.5 text-primary" />
            <span>Inspect Trajectory</span>
          </button>
        </div>
      </div>
    </section>
  );
};
