import React, { useState, useRef, useCallback } from 'react';
import { SlidersHorizontal, Eye } from 'lucide-react';
import { motion } from 'framer-motion';

interface CompareSwipeMapProps {
  year1?: number;
  year2?: number;
}

export const CompareSwipeMap: React.FC<CompareSwipeMapProps> = ({ year1 = 2019, year2 = 2023 }) => {
  const [sliderPosition, setSliderPosition] = useState<number>(50);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [activeMode, setActiveMode] = useState<'classified' | 'change_diff'>('classified');
  const [hoverMode, setHoverMode] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
      setSliderPosition(percentage);
    },
    []
  );

  const handleMouseDown = () => setIsDragging(true);
  const handleMouseUp = () => setIsDragging(false);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      handleMove(e.clientX);
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (e.touches.length > 0) {
      handleMove(e.touches[0].clientX);
    }
  };

  const modes = [
    { id: 'classified', label: 'Classified Rasters' },
    { id: 'change_diff', label: 'Diff Heatmap' },
  ];

  return (
    <div className="panel-surface p-5 rounded-2xl flex flex-col gap-4">
      {/* Header & Controls (Clean, Non-Boxed Typography) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-border">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="font-semibold uppercase tracking-wider text-primary">
              Swipe Comparator
            </span>
            <span className="text-muted-foreground">· 10m Ground Resolution</span>
          </div>
          <h2 className="text-base font-bold text-foreground tracking-tight mt-1">
            Multi-Temporal Comparison: {year1} vs {year2}
          </h2>
        </div>

        {/* Comparison Mode Selector - Fluid Underline */}
        <div className="flex items-center space-x-1 relative">
          {modes.map((mode) => {
            const isSelected = activeMode === mode.id;
            return (
              <button
                key={mode.id}
                onClick={() => setActiveMode(mode.id as 'classified' | 'change_diff')}
                onMouseEnter={() => setHoverMode(mode.id)}
                onMouseLeave={() => setHoverMode(null)}
                className={`px-3 py-1.5 text-xs font-medium transition-colors cursor-pointer relative ${
                  isSelected ? 'text-primary font-semibold' : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <span>{mode.label}</span>
                {hoverMode === mode.id && !isSelected && (
                  <motion.div
                    layoutId="swipe-mode-hover"
                    className="absolute inset-0 bg-muted/70 rounded-md -z-10"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
                {isSelected && (
                  <motion.div
                    layoutId="swipe-mode-active"
                    className="absolute bottom-0 left-2 right-2 h-0.5 bg-primary rounded-full"
                    transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                  />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Swipe Comparison Container */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchMove={handleTouchMove}
        className="relative w-full h-[400px] md:h-[480px] rounded-xl overflow-hidden cursor-ew-resize select-none border border-border bg-background"
      >
        {/* Right Layer (Year 2: 2023 State) */}
        <div className="absolute inset-0 w-full h-full">
          <div className="w-full h-full flex items-center justify-center relative bg-muted/30">
            <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
              <div className="w-full h-full p-4 flex flex-col justify-between overflow-hidden relative">
                {/* SVG Visual Representation */}
                <svg className="absolute inset-0 w-full h-full opacity-60" preserveAspectRatio="none" viewBox="0 0 400 300">
                  <rect width="400" height="300" fill="var(--card)" />
                  <path d="M 50 20 Q 150 80 220 30 T 380 90 L 400 300 L 0 300 Z" fill="var(--secondary)" />
                  <circle cx="200" cy="150" r="110" fill="var(--border)" />
                  <circle cx="120" cy="180" r="60" fill="var(--border)" />
                  <circle cx="280" cy="130" r="70" fill="var(--border)" />
                  <ellipse cx="210" cy="140" rx="28" ry="18" fill="var(--primary)" opacity="0.8" />
                </svg>

                {/* Unboxed Minimal Floating Text */}
                <div className="z-10 flex justify-end">
                  <span className="text-foreground font-mono text-xs font-semibold drop-shadow-xs">
                    {year2} State · Built-up 42.15 km²
                  </span>
                </div>

                <div className="z-10 flex justify-between items-end text-left">
                  <div className="text-[11px] font-mono text-foreground drop-shadow-xs">
                    <div>Extent: 12.97°N, 77.59°E</div>
                    <div className="text-primary font-medium">Urban Expansion Detected</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Left Layer (Year 1: 2019 State) */}
        <div
          className="absolute inset-0 h-full overflow-hidden border-r-2 border-primary"
          style={{ width: `${sliderPosition}%` }}
        >
          <div
            className="absolute inset-0 h-full"
            style={{ width: containerRef.current ? `${containerRef.current.clientWidth}px` : '100%' }}
          >
            <div className="w-full h-full flex items-center justify-center relative bg-muted/30">
              <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
                <div className="w-full h-full p-4 flex flex-col justify-between overflow-hidden relative">
                  <svg className="absolute inset-0 w-full h-full opacity-60" preserveAspectRatio="none" viewBox="0 0 400 300">
                    <rect width="400" height="300" fill="var(--card)" />
                    <circle cx="200" cy="150" r="70" fill="var(--border)" />
                    <ellipse cx="210" cy="140" rx="55" ry="36" fill="var(--primary)" opacity="0.5" />
                  </svg>

                  {/* Unboxed Minimal Floating Text */}
                  <div className="z-10 flex justify-start">
                    <span className="text-foreground font-mono text-xs font-semibold drop-shadow-xs">
                      {year1} Baseline · Vegetation 37.5 km² · Lake 12.0 km²
                    </span>
                  </div>

                  <div className="z-10 flex justify-start items-end text-left">
                    <div className="text-[11px] font-mono text-foreground drop-shadow-xs">
                      <div>Baseline Extent: Bengaluru Metropolitan</div>
                      <div className="text-muted-foreground font-medium">High Canopy Density & Lake Area</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Draggable Divider Handle */}
        <div
          onMouseDown={handleMouseDown}
          className="absolute top-0 bottom-0 w-0.5 bg-primary cursor-ew-resize z-30 flex items-center justify-center"
          style={{ left: `${sliderPosition}%` }}
        >
          <div className="w-7 h-7 rounded-full bg-card border-2 border-primary flex items-center justify-center text-primary shadow-md active:scale-95 transition-transform">
            <SlidersHorizontal className="h-3.5 w-3.5 rotate-90" />
          </div>
        </div>
      </div>

      {/* Footer Instructions */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-muted-foreground font-mono">
        <div className="flex items-center gap-2">
          <Eye className="h-3.5 w-3.5 text-primary" />
          <span>Drag divider handle horizontally to inspect multi-year changes.</span>
        </div>
        <div>
          <span>Split: {Math.round(sliderPosition)}% / {Math.round(100 - sliderPosition)}%</span>
        </div>
      </div>
    </div>
  );
};
