import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { AlertCircle } from 'lucide-react';
import type { TrendDataPoint } from '../../api/types';

interface UrbanVsWaterChartProps {
  trends?: TrendDataPoint[];
}

export const UrbanVsWaterChart: React.FC<UrbanVsWaterChartProps> = ({ trends }) => {
  const data = trends || [
    { year: 2019, Urban: 31.4, Water: 12.0 },
    { year: 2020, Urban: 33.8, Water: 11.2 },
    { year: 2021, Urban: 36.5, Water: 10.5 },
    { year: 2022, Urban: 39.2, Water: 9.8 },
    { year: 2023, Urban: 42.15, Water: 9.1 },
  ];

  return (
    <div className="panel-surface p-5 rounded-2xl flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-border">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="font-semibold uppercase tracking-wider text-primary">
              Trend Analysis
            </span>
            <span className="text-muted-foreground">· Area in km²</span>
          </div>
          <h2 className="text-base font-bold text-foreground tracking-tight mt-1">
            Urban Expansion vs Lake Depletion
          </h2>
        </div>
      </div>

      <div className="w-full h-80 pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
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
            <Line
              type="monotone"
              dataKey="Urban"
              stroke="#8c533c"
              strokeWidth={2.5}
              dot={{ r: 4, fill: '#8c533c' }}
              activeDot={{ r: 6 }}
              name="Urban Built-Up (km²)"
            />
            <Line
              type="monotone"
              dataKey="Water"
              stroke="#2a5a68"
              strokeWidth={2.5}
              dot={{ r: 4, fill: '#2a5a68' }}
              activeDot={{ r: 6 }}
              name="Water Bodies (km²)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="p-3.5 rounded-xl bg-muted/40 flex items-center gap-3">
        <AlertCircle className="h-4 w-4 text-primary shrink-0" />
        <p className="text-xs text-foreground leading-relaxed font-sans">
          <strong>Finding:</strong> For every <strong>+3.2 km²</strong> of urban growth between 2019 and 2023, approximately <strong>0.85 km²</strong> of lake surface area and wetlands were depleted.
        </p>
      </div>
    </div>
  );
};
