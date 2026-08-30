import React, { useState, useEffect } from 'react';
import {
  Satellite,
  Sun,
  Moon,
  Layers,
  Activity,
  FileText,
  Cpu,
  Map as MapIcon,
  BarChart3,
  Zap,
  Download,
} from 'lucide-react';
import type { HealthResponse } from '../../api/types';
import { DropdownNavigation, type NavItem } from '@/components/ui/dorpdown-navigation';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  health: HealthResponse | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, health }) => {
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const isHealthy = health?.model_loaded || health?.status === 'healthy';

  const navItems: NavItem[] = [
    {
      id: 'overview',
      label: 'Overview',
      onClick: () => setActiveTab('overview'),
    },
    {
      id: 'map',
      label: 'Map Studio',
      onClick: () => setActiveTab('map'),
      subMenus: [
        {
          title: 'Spatial Canvas',
          items: [
            {
              label: 'Leaflet GIS Canvas',
              description: 'Real-time 10m Sentinel-2 raster layers',
              icon: MapIcon,
              onClick: () => setActiveTab('map'),
            },
            {
              label: 'Multi-Temporal Slider',
              description: 'Swipe comparator (2019 vs 2023)',
              icon: Layers,
              onClick: () => setActiveTab('map'),
            },
          ],
        },
      ],
    },
    {
      id: 'trends',
      label: 'Change Analytics',
      onClick: () => setActiveTab('trends'),
      subMenus: [
        {
          title: 'Trajectory & Telemetry',
          items: [
            {
              label: 'Land Cover Trajectory',
              description: '5-year stacked area composition',
              icon: BarChart3,
              onClick: () => setActiveTab('trends'),
            },
            {
              label: 'Urban Sprawl vs Lake Depletion',
              description: 'Correlation dual-axis line charts',
              icon: Activity,
              onClick: () => setActiveTab('trends'),
            },
          ],
        },
      ],
    },
    {
      id: 'inference',
      label: 'Inference Lab',
      onClick: () => setActiveTab('inference'),
      subMenus: [
        {
          title: 'Neural Engine',
          items: [
            {
              label: 'GeoTIFF Single Patch',
              description: '64×64 pixel 6-channel inference',
              icon: Zap,
              onClick: () => setActiveTab('inference'),
            },
            {
              label: 'ResNet-50 Classifier',
              description: 'Indian 8-signature classifier',
              icon: Cpu,
              onClick: () => setActiveTab('inference'),
            },
          ],
        },
      ],
    },
    {
      id: 'export',
      label: 'Reports & Export',
      onClick: () => setActiveTab('export'),
      subMenus: [
        {
          title: 'Deliverables',
          items: [
            {
              label: 'Executive PDF Report',
              description: 'Summary charts, maps & statistics',
              icon: FileText,
              onClick: () => setActiveTab('export'),
            },
            {
              label: 'Raw Area Dataset',
              description: 'Class breakdown area_stats.csv',
              icon: Download,
              onClick: () => setActiveTab('export'),
            },
          ],
        },
      ],
    },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-card/90 backdrop-blur-md px-4 lg:px-8 py-2.5 transition-colors">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand & Project Title (Pure Clean Typography without Text Boxes) */}
        <div className="flex items-center gap-2.5 shrink-0">
          <Satellite className="h-5 w-5 text-primary" />
          <div>
            <div className="flex items-center gap-1.5 text-[11px] font-mono">
              <span className="font-semibold text-primary">Sentinel-2 L2A</span>
              <span className="text-muted-foreground">· ResNet-50</span>
            </div>
            <h1 className="text-sm font-semibold tracking-tight text-foreground">
              GeoSat Intelligence
            </h1>
          </div>
        </div>

        {/* Dropdown Navigation (Borderless, Non-Boxed Layout) */}
        <nav className="hidden md:flex items-center justify-center">
          <DropdownNavigation navItems={navItems} activeId={activeTab} />
        </nav>

        {/* Right Controls: Device Status & Theme Switcher (No Boxed Text) */}
        <div className="flex items-center gap-3">
          {/* Status Indicator */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className={`h-2 w-2 rounded-full shrink-0 ${isHealthy ? 'bg-primary' : 'bg-muted-foreground'}`} />
            <span className="text-muted-foreground">{isHealthy ? 'Ready' : 'Demo'}</span>
            <span className="font-semibold text-foreground">{health?.device || 'CUDA'}</span>
          </div>

          {/* Light / Dark Mode Toggle */}
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="h-8 w-8 rounded-lg hover:bg-muted/70 text-foreground transition-all flex items-center justify-center cursor-pointer active:scale-95"
            title={isDarkMode ? 'Switch to Minimal Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle theme"
          >
            {isDarkMode ? <Sun className="h-4 w-4 text-primary" /> : <Moon className="h-4 w-4 text-muted-foreground" />}
          </button>
        </div>
      </div>
    </header>
  );
};
