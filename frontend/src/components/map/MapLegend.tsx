import React from 'react';
import { Info } from 'lucide-react';

export const MapLegend: React.FC = () => {
  const classes = [
    { name: 'Dense Forest Canopy', color: '#1b3a27', desc: 'Dense coniferous & broadleaf forests' },
    { name: 'Woodlands & Reserves', color: '#2d5e3f', desc: 'Protected tree cover & green buffers' },
    { name: 'Herbaceous Vegetation', color: '#4a7856', desc: 'Natural shrubs & wild vegetation' },
    { name: 'Pasture & Grasslands', color: '#5f936c', desc: 'Meadows, grazing land, open green' },
    { name: 'Annual Crops / Farmland', color: '#7fa867', desc: 'Seasonal agricultural crops & fields' },
    { name: 'Permanent Plantation', color: '#98b890', desc: 'Orchards, agroforestry, cultivated plots' },
    { name: 'Lakes & Water Reservoirs', color: '#2a5a68', desc: 'Lakes (Bellandur, Varthur), tanks' },
    { name: 'Residential & Built-up', color: '#93634e', desc: 'Urban settlements, buildings, roads' },
  ];

  return (
    <div className="panel-surface p-5 rounded-2xl flex flex-col gap-3">
      <div className="flex items-center justify-between pb-2 border-b border-border">
        <div className="flex items-center gap-2">
          <Info className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-semibold text-foreground tracking-tight">
            Indian Land Cover Signatures
          </h3>
        </div>
        <span className="text-xs font-mono text-muted-foreground">Botanical Range</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-1">
        {classes.map((c) => (
          <div
            key={c.name}
            className="flex items-start gap-2.5 p-1 text-left"
          >
            <span
              className="w-2.5 h-2.5 rounded-full mt-1 shrink-0"
              style={{ backgroundColor: c.color }}
            />
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-foreground leading-tight">
                {c.name}
              </span>
              <span className="text-[11px] text-muted-foreground leading-tight mt-0.5">
                {c.desc}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
