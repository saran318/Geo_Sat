import React, { useState } from 'react';
import { Satellite, TrendingUp, TrendingDown } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

/**
 * TEMPLATE 1: MINIMALIST CANVAS
 * Aesthetic: 100% Card-less & Box-free. Everything flows seamlessly on the canvas.
 * Dividers are subtle hairlines; typography and spatial rhythm create the structure.
 */
export const Template1_MinimalistCanvas: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'map' | 'analytics' | 'inference'>('map');

  const trendData = [
    { year: 2019, urban: 31.4, veg: 37.5, water: 12.0 },
    { year: 2020, urban: 33.8, veg: 36.1, water: 11.2 },
    { year: 2021, urban: 36.5, veg: 34.8, water: 10.5 },
    { year: 2022, urban: 39.2, veg: 33.2, water: 9.8 },
    { year: 2023, urban: 42.15, veg: 32.28, water: 9.1 },
  ];

  const signatures = [
    { name: 'Dense Forest', area: '12.1 km²', change: '-16.5%', color: '#1b3a27' },
    { name: 'Woodlands', area: '18.4 km²', change: '-12.6%', color: '#2d5e3f' },
    { name: 'Herbaceous', area: '1.8 km²', change: '-7.7%', color: '#4a7856' },
    { name: 'Pasture', area: '5.8 km²', change: '+38.1%', color: '#5f936c' },
    { name: 'Farmland', area: '18.4 km²', change: '-12.6%', color: '#7fa867' },
    { name: 'Lakes / NDWI', area: '6.2 km²', change: '-27.9%', color: '#2a5a68' },
    { name: 'Residential', area: '35.1 km²', change: '+24.0%', color: '#93634e' },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground py-10 px-6 sm:px-12 max-w-6xl mx-auto flex flex-col gap-12 font-sans selection:bg-primary/20">
      {/* 1. Header (Zero boxes) */}
      <header className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-4 pb-6 border-b border-border/60">
        <div>
          <div className="text-xs font-mono text-primary uppercase tracking-widest mb-1 flex items-center gap-1.5">
            <Satellite className="h-3.5 w-3.5" />
            Sentinel-2 L2A · ResNet-50 Pipeline
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
            GeoSat Intelligence
          </h1>
        </div>
        <div className="flex items-center gap-6 text-xs font-medium">
          {(['map', 'analytics', 'inference'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`capitalize transition-colors cursor-pointer pb-1 relative ${
                activeTab === tab
                  ? 'text-primary font-semibold border-b-2 border-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </header>

      {/* 2. Hero Headline (Zero boxes) */}
      <section className="flex flex-col gap-3 max-w-3xl">
        <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground leading-tight">
          Monitoring Urban Growth & Water Depletion across Bengaluru (2019–2023).
        </h2>
        <p className="text-sm text-muted-foreground leading-relaxed">
          6-channel tensor classification at 10m spatial resolution. Built-up area expanded by <strong className="text-foreground">+34.2%</strong> while lake surface area reduced by <strong className="text-foreground">-24.1%</strong>.
        </p>
      </section>

      {/* 3. Metric Stream (Border-free typography) */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-8 py-6 border-y border-border/60">
        <div>
          <span className="text-xs font-mono text-muted-foreground uppercase">Urban Sprawl</span>
          <div className="text-3xl font-bold font-mono tracking-tight text-foreground mt-1">+10.75 km²</div>
          <div className="text-xs text-primary font-mono mt-0.5 flex items-center gap-0.5">
            <TrendingUp className="h-3 w-3" /> +34.2% expansion
          </div>
        </div>
        <div>
          <span className="text-xs font-mono text-muted-foreground uppercase">Forest Canopy</span>
          <div className="text-3xl font-bold font-mono tracking-tight text-foreground mt-1">-5.22 km²</div>
          <div className="text-xs text-muted-foreground font-mono mt-0.5 flex items-center gap-0.5">
            <TrendingDown className="h-3 w-3 text-primary" /> -14.3% reduction
          </div>
        </div>
        <div>
          <span className="text-xs font-mono text-muted-foreground uppercase">Lake Surface Area</span>
          <div className="text-3xl font-bold font-mono tracking-tight text-foreground mt-1">-2.90 km²</div>
          <div className="text-xs text-muted-foreground font-mono mt-0.5 flex items-center gap-0.5">
            <TrendingDown className="h-3 w-3 text-primary" /> -24.1% depletion
          </div>
        </div>
        <div>
          <span className="text-xs font-mono text-muted-foreground uppercase">ResNet-50 Accuracy</span>
          <div className="text-3xl font-bold font-mono tracking-tight text-foreground mt-1">91.4%</div>
          <div className="text-xs text-primary font-mono mt-0.5">Water IoU 78.6%</div>
        </div>
      </section>

      {/* 4. Trajectory Chart Stream (Card-free) */}
      <section className="flex flex-col gap-4">
        <div className="flex items-baseline justify-between">
          <h3 className="text-base font-bold text-foreground">Multi-Year Trajectory Stream</h3>
          <span className="text-xs font-mono text-muted-foreground">Area in km²</span>
        </div>
        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trendData}>
              <XAxis dataKey="year" stroke="var(--muted-foreground)" tick={{ fontSize: 11 }} />
              <YAxis stroke="var(--muted-foreground)" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)' }} />
              <Area type="monotone" dataKey="urban" stroke="#93634e" fill="#93634e" fillOpacity={0.3} name="Urban" />
              <Area type="monotone" dataKey="veg" stroke="#2d5e3f" fill="#2d5e3f" fillOpacity={0.3} name="Vegetation" />
              <Area type="monotone" dataKey="water" stroke="#2a5a68" fill="#2a5a68" fillOpacity={0.3} name="Water" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* 5. Classification Signatures (Clean list) */}
      <section className="flex flex-col gap-4 pt-6 border-t border-border/60">
        <h3 className="text-base font-bold text-foreground">EuroSAT Botanical Signatures</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-xs">
          {signatures.map((s) => (
            <div key={s.name} className="flex flex-col gap-1">
              <div className="flex items-center gap-2 font-medium text-foreground">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: s.color }} />
                <span>{s.name}</span>
              </div>
              <div className="text-muted-foreground font-mono pl-4.5">
                {s.area} · <span className={s.change.startsWith('+') ? 'text-primary' : 'text-muted-foreground'}>{s.change}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Template1_MinimalistCanvas;
