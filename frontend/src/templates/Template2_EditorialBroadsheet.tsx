import React from 'react';
import { ArrowDownRight, ArrowUpRight, Globe, Download } from 'lucide-react';

/**
 * TEMPLATE 2: EDITORIAL BROADSHEET
 * Aesthetic: Swiss Typographic Grid, Asymmetric broadsheet column hierarchy.
 * Zero rounded cards, zero boxes. Pure typographic contrast and crisp editorial rules.
 */
export const Template2_EditorialBroadsheet: React.FC = () => {
  return (
    <div className="min-h-screen bg-background text-foreground py-12 px-6 lg:px-16 max-w-7xl mx-auto flex flex-col gap-12 font-sans">
      {/* 1. Masthead */}
      <header className="grid grid-cols-1 md:grid-cols-12 gap-6 pb-6 border-b border-foreground/20 items-end">
        <div className="md:col-span-8">
          <span className="text-[11px] font-mono uppercase tracking-widest text-primary block mb-1">
            EARTH OBSERVATION REPORT · BENGALURU SECTOR
          </span>
          <h1 className="text-3xl sm:text-5xl font-black tracking-tighter text-foreground uppercase">
            LAND CLASSIFICATION & URBAN SHIFT
          </h1>
        </div>
        <div className="md:col-span-4 text-xs font-mono text-muted-foreground flex flex-col md:items-end gap-1">
          <div>DATA: SENTINEL-2 L2A (10M)</div>
          <div>INTERVAL: 2019 — 2023</div>
          <div>CRS: EPSG:4326 WGS84</div>
        </div>
      </header>

      {/* 2. Editorial Summary & Giant KPI */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        <div className="lg:col-span-5 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-border/60 pb-8 lg:pb-0 lg:pr-10">
          <div>
            <h2 className="text-xl font-bold text-foreground mb-3 leading-snug">
              Rapid urban infill converted 10.75 km² of agricultural and wetland buffer into high-density built-up structures.
            </h2>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Using a customized ResNet-50 architecture incorporating 6 spectral channels (B2, B3, B4, B8, NDVI, NDWI), multi-temporal analysis indicates profound ecological displacement across eastern technology corridors.
            </p>
          </div>

          <div className="pt-8">
            <span className="text-xs font-mono text-muted-foreground uppercase tracking-wider block">Net Urban Growth Surge</span>
            <div className="text-6xl font-black font-mono tracking-tighter text-primary mt-1">+34.2%</div>
            <span className="text-xs text-muted-foreground font-mono mt-1 block">Baseline: 31.40 km² → 2023: 42.15 km²</span>
          </div>
        </div>

        {/* 3. Metric Breakdown Columns */}
        <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-8">
          <div className="flex flex-col gap-2 pb-6 border-b border-border/60">
            <span className="text-xs font-mono text-muted-foreground uppercase flex items-center justify-between">
              Forest & Canopy Loss
              <ArrowDownRight className="h-3.5 w-3.5 text-primary" />
            </span>
            <span className="text-4xl font-bold font-mono text-foreground">-5.22 km²</span>
            <span className="text-xs text-muted-foreground">-14.3% decline in continuous vegetative canopy.</span>
          </div>

          <div className="flex flex-col gap-2 pb-6 border-b border-border/60">
            <span className="text-xs font-mono text-muted-foreground uppercase flex items-center justify-between">
              Water Reservoir Depletion
              <ArrowDownRight className="h-3.5 w-3.5 text-primary" />
            </span>
            <span className="text-4xl font-bold font-mono text-foreground">-2.90 km²</span>
            <span className="text-xs text-muted-foreground">-24.1% surface loss across Bellandur & Varthur lakes.</span>
          </div>

          <div className="flex flex-col gap-2 pb-6 border-b border-border/60 sm:border-b-0">
            <span className="text-xs font-mono text-muted-foreground uppercase flex items-center justify-between">
              Highway & Infrastructure
              <ArrowUpRight className="h-3.5 w-3.5 text-primary" />
            </span>
            <span className="text-4xl font-bold font-mono text-foreground">+1.60 km²</span>
            <span className="text-xs text-muted-foreground">+38.1% transportation corridor expansion.</span>
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-xs font-mono text-muted-foreground uppercase flex items-center justify-between">
              Validation Accuracy
              <Globe className="h-3.5 w-3.5 text-primary" />
            </span>
            <span className="text-4xl font-bold font-mono text-foreground">91.4%</span>
            <span className="text-xs text-muted-foreground">EuroSAT benchmarked with 78.6% Water IoU.</span>
          </div>
        </div>
      </section>

      {/* 4. Editorial Data Table (Zero card container) */}
      <section className="pt-6 border-t border-foreground/20">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-mono uppercase font-bold tracking-wider text-foreground">
            Table 1.0 — Area Transition Matrix (2019 vs 2023)
          </h3>
          <button className="text-xs font-mono text-primary hover:underline flex items-center gap-1 cursor-pointer">
            <Download className="h-3.5 w-3.5" /> Export CSV
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-foreground/20 text-muted-foreground">
                <th className="py-2">CLASS SIGNATURE</th>
                <th className="py-2">2019 (KM²)</th>
                <th className="py-2">2023 (KM²)</th>
                <th className="py-2">NET CHANGE (KM²)</th>
                <th className="py-2 text-right">PERCENTAGE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {[
                { name: 'Residential & Built-up', y1: '28.30', y2: '35.10', diff: '+6.80', pct: '+24.0%' },
                { name: 'Annual Crop / Farmland', y1: '21.09', y2: '18.42', diff: '-2.67', pct: '-12.6%' },
                { name: 'Dense Forest Canopy', y1: '14.50', y2: '12.10', diff: '-2.40', pct: '-16.5%' },
                { name: 'Lakes & Water Bodies', y1: '8.60', y2: '6.20', diff: '-2.40', pct: '-27.9%' },
                { name: 'Industrial Corridors', y1: '3.10', y2: '5.45', diff: '+2.35', pct: '+75.8%' },
              ].map((row) => (
                <tr key={row.name}>
                  <td className="py-2.5 font-medium text-foreground">{row.name}</td>
                  <td className="py-2.5 text-muted-foreground">{row.y1}</td>
                  <td className="py-2.5 text-muted-foreground">{row.y2}</td>
                  <td className="py-2.5 text-foreground">{row.diff}</td>
                  <td className="py-2.5 text-right font-bold text-primary">{row.pct}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default Template2_EditorialBroadsheet;
