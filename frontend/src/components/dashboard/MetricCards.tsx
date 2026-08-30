import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, CheckCircle2, Droplet, Trees, Building2 } from 'lucide-react';
import type { DemoDataResponse } from '../../api/types';

interface MetricCardsProps {
  demoData: DemoDataResponse | null;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ demoData }) => {
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  const kpis = demoData?.kpis || {
    total_area_analyzed_km2: 85.59,
    urban_growth_km2: 10.75,
    urban_growth_pct: 34.2,
    vegetation_loss_km2: -5.22,
    vegetation_loss_pct: -14.3,
    water_loss_km2: -2.9,
    water_loss_pct: -24.1,
    model_accuracy: 91.4,
    water_iou: 78.6,
  };

  const cards = [
    {
      id: 'urban',
      title: 'Urban Expansion (2019–2023)',
      value: `+${kpis.urban_growth_km2} km²`,
      subtitle: `+${kpis.urban_growth_pct}% total built-up surge`,
      trend: 'up',
      color: '#93634e',
      icon: Building2,
    },
    {
      id: 'vegetation',
      title: 'Vegetation & Forest Canopy',
      value: `${kpis.vegetation_loss_km2} km²`,
      subtitle: `${kpis.vegetation_loss_pct}% canopy reduction`,
      trend: 'down',
      color: '#2d5e3f',
      icon: Trees,
    },
    {
      id: 'water',
      title: 'Water Bodies & Lakes (NDWI)',
      value: `${kpis.water_loss_km2} km²`,
      subtitle: `${kpis.water_loss_pct}% lake surface reduction`,
      trend: 'down',
      color: '#2a5a68',
      icon: Droplet,
    },
    {
      id: 'accuracy',
      title: 'ResNet-50 Validation Accuracy',
      value: `${kpis.model_accuracy}%`,
      subtitle: `Indian LULC 6-channel · Water IoU: ${kpis.water_iou}%`,
      trend: 'neutral',
      color: '#1b3a27',
      icon: CheckCircle2,
    },
  ];

  return (
    <div 
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      onMouseLeave={() => setHoveredCard(null)}
    >
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.id}
            className="relative p-5 rounded-2xl border border-border flex flex-col justify-between"
            onMouseEnter={() => setHoveredCard(card.id)}
          >
            {hoveredCard === card.id && (
              <motion.div
                layoutId="metric-card-hover"
                className="absolute inset-0 bg-card rounded-2xl shadow-sm z-0"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1, transition: { duration: 0.15 } }}
                exit={{ opacity: 0, transition: { duration: 0.15, delay: 0.2 } }}
              />
            )}
            <div className="relative z-10 flex items-center justify-between mb-3">
              <span className="text-[11px] font-semibold text-muted-foreground uppercase font-mono tracking-wider">
                {card.title}
              </span>
              <Icon className="h-4 w-4 shrink-0" style={{ color: card.color }} />
            </div>

            <div className="relative z-10 flex items-baseline gap-2 mb-1.5">
              <span className="text-2xl font-bold text-foreground font-mono tracking-tight">
                {card.value}
              </span>
              {card.trend === 'up' && (
                <span className="flex items-center text-xs font-mono font-medium text-primary">
                  <TrendingUp className="h-3 w-3 mr-0.5" /> +34.2%
                </span>
              )}
              {card.trend === 'down' && (
                <span className="flex items-center text-xs font-mono font-medium text-muted-foreground">
                  <TrendingDown className="h-3 w-3 mr-0.5 text-primary" /> Net Loss
                </span>
              )}
            </div>

            <p className="relative z-10 text-xs text-muted-foreground leading-normal font-sans">
              {card.subtitle}
            </p>
          </div>
        );
      })}
    </div>
  );
};
