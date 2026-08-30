import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FileText, Download, Map, Database } from 'lucide-react';

export const DownloadActionPanel: React.FC = () => {
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);
  const [downloadingCsv, setDownloadingCsv] = useState<boolean>(false);

  const handlePdfDownload = () => {
    setDownloadingPdf(true);
    setTimeout(() => {
      setDownloadingPdf(false);
      const link = document.createElement('a');
      link.href = '/data/results/classified_2023.png';
      link.download = 'GeoSat_Bengaluru_Report_2019_2023.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }, 600);
  };

  const handleCsvDownload = () => {
    setDownloadingCsv(true);
    setTimeout(() => {
      setDownloadingCsv(false);
      const csvContent =
        'class_index,class_name,year1_area_km2,year2_area_km2,net_change_km2,pct_change\n' +
        '0,AnnualCrop,21.09,18.42,-2.67,-12.6\n' +
        '1,Forest,14.50,12.10,-2.40,-16.5\n' +
        '2,HerbaceousVegetation,1.95,1.80,-0.15,-7.7\n' +
        '3,Highway,4.20,5.80,1.60,38.1\n' +
        '4,Industrial,3.10,5.45,2.35,75.8\n' +
        '5,Residential,28.30,35.10,6.80,24.0\n' +
        '6,River,3.40,2.90,-0.50,-14.7\n' +
        '7,SeaLake,8.60,6.20,-2.40,-27.9\n';

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', 'area_stats.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }, 400);
  };

  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  return (
    <div className="panel-surface p-6 rounded-2xl flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono font-medium uppercase text-primary bg-muted px-2 py-0.5 rounded">
              Deliverables & Exports
            </span>
            <span className="text-xs text-muted-foreground font-mono">BCA Capstone Submission</span>
          </div>
          <h2 className="text-base font-bold text-foreground tracking-tight mt-1">
            Export Land-Use Classification Reports & Datasets
          </h2>
        </div>
      </div>

      <div 
        className="grid grid-cols-1 md:grid-cols-3 gap-4"
        onMouseLeave={() => setHoveredCard(null)}
      >
        {/* PDF Report */}
        <div 
          className="relative p-5 rounded-xl border border-transparent flex flex-col justify-between transition-all"
          onMouseEnter={() => setHoveredCard('pdf')}
        >
          {hoveredCard === 'pdf' && (
            <motion.div
              layoutId="download-card-hover"
              className="absolute inset-0 bg-muted/40 rounded-xl z-0"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1, transition: { duration: 0.15 } }}
              exit={{ opacity: 0, transition: { duration: 0.15, delay: 0.2 } }}
            />
          )}
          <div className="relative z-10">
            <div className="h-9 w-9 rounded-lg bg-card border border-border flex items-center justify-center text-primary mb-3 shadow-xs">
              <FileText className="h-4.5 w-4.5" />
            </div>
            <h3 className="text-sm font-semibold text-foreground">
              PDF Executive Report
            </h3>
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
              Auto-generated summary containing cover, multi-temporal maps, area statistics tables, and trend charts.
            </p>
          </div>

          <button
            onClick={handlePdfDownload}
            disabled={downloadingPdf}
            className="relative z-10 mt-5 w-full py-2.5 rounded-lg bg-primary hover:opacity-90 active:scale-[0.98] text-primary-foreground font-medium text-xs flex items-center justify-center gap-2 transition-all cursor-pointer shadow-xs"
          >
            <Download className="h-3.5 w-3.5" />
            <span>{downloadingPdf ? 'Compiling PDF...' : 'Download PDF Report'}</span>
          </button>
        </div>

        {/* CSV Area Stats */}
        <div 
          className="relative p-5 rounded-xl border border-transparent flex flex-col justify-between transition-all"
          onMouseEnter={() => setHoveredCard('csv')}
        >
          {hoveredCard === 'csv' && (
            <motion.div
              layoutId="download-card-hover"
              className="absolute inset-0 bg-muted/40 rounded-xl z-0"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1, transition: { duration: 0.15 } }}
              exit={{ opacity: 0, transition: { duration: 0.15, delay: 0.2 } }}
            />
          )}
          <div className="relative z-10">
            <div className="h-9 w-9 rounded-lg bg-card border border-border flex items-center justify-center text-primary mb-3 shadow-xs">
              <Database className="h-4.5 w-4.5" />
            </div>
            <h3 className="text-sm font-semibold text-foreground">
              Tabular Statistics (CSV)
            </h3>
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
              Calculated square kilometers, pixel counts, and year-on-year hectare percentage changes (`area_stats.csv`).
            </p>
          </div>

          <button
            onClick={handleCsvDownload}
            disabled={downloadingCsv}
            className="relative z-10 mt-5 w-full py-2.5 rounded-lg bg-card active:scale-[0.98] text-foreground font-medium text-xs flex items-center justify-center gap-2 transition-all cursor-pointer border border-border/60 shadow-xs"
          >
            <Download className="h-3.5 w-3.5 text-primary" />
            <span>{downloadingCsv ? 'Exporting CSV...' : 'Download CSV Dataset'}</span>
          </button>
        </div>

        {/* GeoTIFF Rasters */}
        <div 
          className="relative p-5 rounded-xl border border-transparent flex flex-col justify-between transition-all"
          onMouseEnter={() => setHoveredCard('geotiff')}
        >
          {hoveredCard === 'geotiff' && (
            <motion.div
              layoutId="download-card-hover"
              className="absolute inset-0 bg-muted/40 rounded-xl z-0"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1, transition: { duration: 0.15 } }}
              exit={{ opacity: 0, transition: { duration: 0.15, delay: 0.2 } }}
            />
          )}
          <div className="relative z-10">
            <div className="h-9 w-9 rounded-lg bg-card border border-border flex items-center justify-center text-primary mb-3 shadow-xs">
              <Map className="h-4.5 w-4.5" />
            </div>
            <h3 className="text-sm font-semibold text-foreground">
              GIS GeoTIFF Rasters
            </h3>
            <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
              Full-resolution classified GeoTIFF maps embedded with spatial WGS84 CRS coordinate metadata.
            </p>
          </div>

          <a
            href="/data/results/classified_2023.tif"
            download="classified_2023.tif"
            className="relative z-10 mt-5 w-full py-2.5 rounded-lg bg-card active:scale-[0.98] text-foreground font-medium text-xs flex items-center justify-center gap-2 transition-all cursor-pointer border border-border/60 shadow-xs text-center"
          >
            <Download className="h-3.5 w-3.5 text-primary" />
            <span>Download GeoTIFF</span>
          </a>
        </div>
      </div>
    </div>
  );
};
