import React from 'react';
import { Satellite, Download } from 'lucide-react';

/**
 * TEMPLATE 5: SPLIT STREAM VIEW (Linear-style fluid column)
 * Aesthetic: Sticky left narrative + fluid continuous right stream.
 * Zero white boxes, zero container cards.
 */
export const Template5_SplitStreamView: React.FC = () => {
  return (
    <div className="min-h-screen bg-background text-foreground py-12 px-6 lg:px-16 max-w-7xl mx-auto font-sans">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
        {/* Sticky Left Column: Narrative & Primary Metrics */}
        <div className="lg:col-span-5 flex flex-col justify-between lg:sticky lg:top-12 h-fit gap-8">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-primary uppercase tracking-widest mb-2">
              <Satellite className="h-3.5 w-3.5" />
              GeoSat Intelligence Engine
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground leading-tight">
              Satellite Land-Use & Change Detection.
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-3 leading-relaxed">
              Evaluating multi-temporal spectral shifts across 85.59 km² of the Bengaluru metropolitan region using 6-channel Sentinel-2 tensor extraction and ResNet-50 classification.
            </p>
          </div>

          {/* Left KPI Stream */}
          <div className="flex flex-col gap-6 py-6 border-y border-border/60">
            <div>
              <span className="text-[11px] font-mono text-muted-foreground uppercase">Built-Up Expansion</span>
              <div className="text-3xl font-bold font-mono text-foreground mt-0.5">+10.75 km²</div>
              <div className="text-xs font-mono text-primary">+34.2% five-year surge</div>
            </div>
            <div>
              <span className="text-[11px] font-mono text-muted-foreground uppercase">Lake Water Area</span>
              <div className="text-3xl font-bold font-mono text-foreground mt-0.5">-2.90 km²</div>
              <div className="text-xs font-mono text-muted-foreground">-24.1% surface reduction</div>
            </div>
            <div>
              <span className="text-[11px] font-mono text-muted-foreground uppercase">Validation Accuracy</span>
              <div className="text-3xl font-bold font-mono text-primary mt-0.5">91.4%</div>
              <div className="text-xs font-mono text-muted-foreground">EuroSAT 8-Class Benchmark</div>
            </div>
          </div>

          <div className="text-xs font-mono text-muted-foreground">
            BCA Capstone · Sentinel-2 L2A · 10m Ground Resolution
          </div>
        </div>

        {/* Right Scrollable Stream: Continuous Data Sections (Zero Card Boxes) */}
        <div className="lg:col-span-7 flex flex-col gap-12 lg:pl-6">
          {/* Stream Section 1: Spectral Tensors */}
          <div className="flex flex-col gap-3 pb-8 border-b border-border/60">
            <span className="text-xs font-mono uppercase text-muted-foreground">01 / SPECTRAL TENSOR CHANNELS</span>
            <h2 className="text-lg font-bold text-foreground">6-Band Sentinel-2 Mathematical Matrix</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-2 text-xs font-mono">
              {[
                { name: 'B02 (Blue)', nm: '490nm', col: '#3b6b80' },
                { name: 'B03 (Green)', nm: '560nm', col: '#2d5e3f' },
                { name: 'B04 (Red)', nm: '665nm', col: '#8c4a38' },
                { name: 'B08 (NIR)', nm: '842nm', col: '#1b3a27' },
                { name: 'NDVI Index', nm: 'Veg. Density', col: '#5f936c' },
                { name: 'NDWI Index', nm: 'Water Body', col: '#2a5a68' },
              ].map((c) => (
                <div key={c.name} className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: c.col }} />
                  <div>
                    <div className="font-semibold text-foreground">{c.name}</div>
                    <div className="text-[11px] text-muted-foreground">{c.nm}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Stream Section 2: Area Breakdown */}
          <div className="flex flex-col gap-3 pb-8 border-b border-border/60">
            <span className="text-xs font-mono uppercase text-muted-foreground">02 / AREA TRANSITION BREAKDOWN</span>
            <h2 className="text-lg font-bold text-foreground">EuroSAT Multi-Year Transition</h2>
            <div className="flex flex-col gap-3 pt-2 text-xs font-mono">
              {[
                { name: 'Residential & Built-up', change: '+6.80 km² (+24.0%)', col: '#93634e' },
                { name: 'Annual Crop / Farmland', change: '-2.67 km² (-12.6%)', col: '#7fa867' },
                { name: 'Dense Forest Canopy', change: '-2.40 km² (-16.5%)', col: '#1b3a27' },
                { name: 'Lakes & Water Bodies', change: '-2.40 km² (-27.9%)', col: '#2a5a68' },
              ].map((item) => (
                <div key={item.name} className="flex items-center justify-between py-1.5 border-b border-border/30">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: item.col }} />
                    <span className="font-medium text-foreground">{item.name}</span>
                  </div>
                  <span className="text-foreground font-semibold">{item.change}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Stream Section 3: Deliverables */}
          <div className="flex flex-col gap-3">
            <span className="text-xs font-mono uppercase text-muted-foreground">03 / DELIVERABLES & EXPORTS</span>
            <h2 className="text-lg font-bold text-foreground">Download Spatial Reports & Datasets</h2>
            <div className="flex flex-wrap gap-4 pt-2">
              <button className="px-4 py-2 text-xs font-medium bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity cursor-pointer flex items-center gap-1.5">
                <Download className="h-3.5 w-3.5" /> Download PDF Report
              </button>
              <button className="px-4 py-2 text-xs font-medium text-foreground hover:bg-muted/60 rounded-lg transition-colors cursor-pointer flex items-center gap-1.5">
                <Download className="h-3.5 w-3.5 text-primary" /> Download CSV Dataset
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Template5_SplitStreamView;
