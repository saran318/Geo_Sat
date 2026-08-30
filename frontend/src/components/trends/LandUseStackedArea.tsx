import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { TrendDataPoint } from '../../api/types';

interface LandUseStackedAreaProps {
  trends?: TrendDataPoint[];
}

export const LandUseStackedArea: React.FC<LandUseStackedAreaProps> = ({ trends }) => {
  const data = trends || [
    { year: 2019, Urban: 31.4, Vegetation: 37.5, Water: 12.0, Agriculture: 4.69 },
    { year: 2020, Urban: 33.8, Vegetation: 36.1, Water: 11.2, Agriculture: 4.49 },
    { year: 2021, Urban: 36.5, Vegetation: 34.8, Water: 10.5, Agriculture: 3.79 },
    { year: 2022, Urban: 39.2, Vegetation: 33.2, Water: 9.8, Agriculture: 3.39 },
    { year: 2023, Urban: 42.15, Vegetation: 32.28, Water: 9.1, Agriculture: 2.06 },
  ];

  return (
    <div className="panel-surface p-5 rounded-2xl flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-border">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="font-semibold uppercase tracking-wider text-primary">
              Multi-Year Composition
            </span>
            <span className="text-muted-foreground">· Area (km²)</span>
          </div>
          <h2 className="text-base font-bold text-foreground tracking-tight mt-1">
            Land Cover Trajectory (2019–2023)
          </h2>
        </div>
        <div className="text-xs font-mono text-muted-foreground">
          Source: Sentinel-2 Multi-Temporal Composites
        </div>
      </div>

      <div className="w-full h-80 pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorUrban" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#93634e" stopOpacity={0.7} />
                <stop offset="95%" stopColor="#93634e" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="colorVeg" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2d5e3f" stopOpacity={0.7} />
                <stop offset="95%" stopColor="#2d5e3f" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="colorWater" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2a5a68" stopOpacity={0.7} />
                <stop offset="95%" stopColor="#2a5a68" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="colorAgri" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7fa867" stopOpacity={0.7} />
                <stop offset="95%" stopColor="#7fa867" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="year" stroke="var(--muted-foreground)" tick={{ fill: 'var(--muted-foreground)', fontSize: 11, fontFamily: 'var(--font-mono)' }} />
            <YAxis stroke="var(--muted-foreground)" tick={{ fill: 'var(--muted-foreground)', fontSize: 11, fontFamily: 'var(--font-mono)' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--card)',
                borderColor: 'var(--border)',
                borderRadius: '8px',
                color: 'var(--foreground)',
                fontSize: '12px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
            <Area
              type="monotone"
              dataKey="Urban"
              stackId="1"
              stroke="#93634e"
              fillOpacity={1}
              fill="url(#colorUrban)"
              name="Urban Built-up"
            />
            <Area
              type="monotone"
              dataKey="Vegetation"
              stackId="1"
              stroke="#2d5e3f"
              fillOpacity={1}
              fill="url(#colorVeg)"
              name="Forest Canopy"
            />
            <Area
              type="monotone"
              dataKey="Water"
              stackId="1"
              stroke="#2a5a68"
              fillOpacity={1}
              fill="url(#colorWater)"
              name="Lakes & Reservoirs"
            />
            <Area
              type="monotone"
              dataKey="Agriculture"
              stackId="1"
              stroke="#7fa867"
              fillOpacity={1}
              fill="url(#colorAgri)"
              name="Agricultural Crops"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
