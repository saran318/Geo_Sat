import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';
import type { AreaStatRow } from '../../api/types';

interface ChangeDataTableProps {
  stats: AreaStatRow[];
}

export const ChangeDataTable: React.FC<ChangeDataTableProps> = ({ stats }) => {
  const [hoveredRow, setHoveredRow] = useState<string | null>(null);

  return (
    <div className="panel-surface p-5 rounded-2xl flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-border">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="font-semibold uppercase tracking-wider text-primary">
              Tabular Statistics
            </span>
            <span className="text-muted-foreground">· area_stats.csv</span>
          </div>
          <h2 className="text-base font-bold text-foreground tracking-tight mt-1">
            Indian Land Cover Area Breakdown
          </h2>
        </div>
      </div>

      <div className="overflow-x-auto">
        <div className="min-w-[700px] text-left text-xs" onMouseLeave={() => setHoveredRow(null)}>
          {/* Table Header */}
          <div className="grid grid-cols-[1.5fr_1fr_1fr_1fr_1fr_1fr] border-b border-border text-muted-foreground font-mono uppercase tracking-wider pb-3 px-3 mb-1">
            <div>Class Signature</div>
            <div>2019 Area (km²)</div>
            <div>2023 Area (km²)</div>
            <div>Net Change (km²)</div>
            <div>Net Change (ha)</div>
            <div className="text-right">Trend (% Change)</div>
          </div>

          {/* Table Body */}
          <div className="flex flex-col gap-1">
            {stats.map((row) => {
              const isPositive = (row.pct_change || 0) > 0;
              const isNeutral = (row.pct_change || 0) === 0;

              return (
                <div 
                  key={row.class_name} 
                  className="relative grid grid-cols-[1.5fr_1fr_1fr_1fr_1fr_1fr] py-2.5 px-3 items-center cursor-default group"
                  onMouseEnter={() => setHoveredRow(row.class_name)}
                >
                  {/* Shared Layout Hover Pill */}
                  {hoveredRow === row.class_name && (
                    <motion.div
                      layoutId="table-row-hover"
                      className="absolute inset-0 bg-muted/50 rounded-lg z-0"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1, transition: { duration: 0.15 } }}
                      exit={{ opacity: 0, transition: { duration: 0.15, delay: 0.2 } }}
                    />
                  )}

                  <div className="relative z-10 font-medium text-foreground flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-primary shrink-0" />
                    <span className="font-mono">{row.class_name}</span>
                  </div>
                  <div className="relative z-10 text-foreground font-mono">
                    {row.year1_area_km2.toFixed(2)}
                  </div>
                  <div className="relative z-10 text-foreground font-mono">
                    {row.year2_area_km2.toFixed(2)}
                  </div>
                  <div className="relative z-10 font-mono text-foreground">
                    {row.net_change_km2
                      ? row.net_change_km2 > 0
                        ? `+${row.net_change_km2.toFixed(2)}`
                        : row.net_change_km2.toFixed(2)
                      : (row.year2_area_km2 - row.year1_area_km2).toFixed(2)}
                  </div>
                  <div className="relative z-10 text-muted-foreground font-mono">
                    {row.net_change_ha
                      ? row.net_change_ha.toFixed(1)
                      : ((row.year2_area_km2 - row.year1_area_km2) * 100).toFixed(1)}
                  </div>
                  <div className="relative z-10 text-right">
                    <span
                      className={`inline-flex items-center gap-1 font-mono font-semibold text-xs ${
                        isPositive
                          ? 'text-primary'
                          : isNeutral
                          ? 'text-muted-foreground'
                          : 'text-muted-foreground'
                      }`}
                    >
                      {isPositive ? (
                        <TrendingUp className="h-3.5 w-3.5 text-primary" />
                      ) : isNeutral ? null : (
                        <TrendingDown className="h-3.5 w-3.5 text-muted-foreground" />
                      )}
                      {row.pct_change > 0 ? `+${row.pct_change.toFixed(1)}%` : `${row.pct_change.toFixed(1)}%`}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
