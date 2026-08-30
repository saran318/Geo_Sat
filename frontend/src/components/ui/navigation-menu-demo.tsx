import { cn } from '@/lib/utils';
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from '@/components/ui/navigation-menu';
import { Layers, Activity, FileText, Cpu, Satellite } from 'lucide-react';

export function NavigationMenuDemo({
  onSelectTab,
}: {
  onSelectTab?: (tab: string) => void;
}) {
  return (
    <NavigationMenu viewport={false}>
      <NavigationMenuList>
        {/* Geospatial Layers Dropdown */}
        <NavigationMenuItem>
          <NavigationMenuTrigger className="text-xs font-medium">
            <Layers className="h-3.5 w-3.5 mr-1.5 text-primary" />
            GIS Modules
          </NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[320px] gap-2 p-3 bg-card border border-border rounded-xl">
              <li>
                <NavigationMenuLink
                  onClick={() => onSelectTab?.('overview')}
                  className="p-2.5 rounded-lg hover:bg-muted cursor-pointer transition-colors"
                >
                  <div className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                    <Satellite className="h-3.5 w-3.5 text-primary" />
                    Overview Telemetry
                  </div>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    Multi-temporal composite KPIs & Sentinel-2 input bands.
                  </p>
                </NavigationMenuLink>
              </li>
              <li>
                <NavigationMenuLink
                  onClick={() => onSelectTab?.('map')}
                  className="p-2.5 rounded-lg hover:bg-muted cursor-pointer transition-colors"
                >
                  <div className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                    <Layers className="h-3.5 w-3.5 text-primary" />
                    Interactive Map Canvas
                  </div>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    Leaflet GIS viewer with layer opacity & temporal slider.
                  </p>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>

        {/* Analytics Dropdown */}
        <NavigationMenuItem>
          <NavigationMenuTrigger className="text-xs font-medium">
            <Activity className="h-3.5 w-3.5 mr-1.5 text-primary" />
            Analytics
          </NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[300px] gap-2 p-3 bg-card border border-border rounded-xl">
              <li>
                <NavigationMenuLink
                  onClick={() => onSelectTab?.('trends')}
                  className="p-2.5 rounded-lg hover:bg-muted cursor-pointer transition-colors"
                >
                  <div className="text-xs font-semibold text-foreground">Change Trajectory</div>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    Annual land cover charts and urban vs lake correlation.
                  </p>
                </NavigationMenuLink>
              </li>
              <li>
                <NavigationMenuLink
                  onClick={() => onSelectTab?.('inference')}
                  className="p-2.5 rounded-lg hover:bg-muted cursor-pointer transition-colors"
                >
                  <div className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                    <Cpu className="h-3.5 w-3.5 text-primary" />
                    Patch Inference Lab
                  </div>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    Single patch GeoTIFF classifier with latency telemetry.
                  </p>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>

        {/* Reports Direct Link */}
        <NavigationMenuItem>
          <NavigationMenuLink
            onClick={() => onSelectTab?.('export')}
            className={cn(navigationMenuTriggerStyle(), 'text-xs cursor-pointer')}
          >
            <FileText className="h-3.5 w-3.5 mr-1.5 text-primary" />
            Export & PDF
          </NavigationMenuLink>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  );
}

export default NavigationMenuDemo;
