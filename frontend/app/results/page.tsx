'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft, AlertCircle, Download, FileText } from 'lucide-react';
import { getFullReportUrl } from '@/services/api';
import ResultCard from '@/components/ResultCard';
import DashboardStats from '@/components/DashboardStats';
import { DetectionResult, DetectionResponse } from '@/services/api';

interface ResultData extends DetectionResponse {
  imageUrl: string | null;
  report_url?: string;
  video_url?: string;
  originalVideoUrl?: string | null;
}

export default function ResultsPage() {
  const router = useRouter();
  const [result, setResult] = useState<ResultData | null>(null);
  const [mounted, setMounted] = useState(false);
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    setMounted(true);
    console.log("ResultsPage mounted, checking session storage...");
    
    // Task 2: Retrieve session storage safely
    const raw = sessionStorage.getItem('resultData');
    if (raw) {
      try {
        const data = JSON.parse(raw);
        console.log("Result page data successfully loaded:", data);
        setResult(data);
      } catch (err) {
        console.error('CRITICAL: Failed to parse resultData', err);
        router.push('/upload');
      }
    } else {
      console.warn("No resultData found in session storage, redirecting to upload...");
      router.push('/upload');
    }
  }, [router]);

  if (!mounted || !result) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-zinc-800 border-t-white rounded-full animate-spin" />
      </div>
    );
  }

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setImageSize({ width: img.naturalWidth, height: img.naturalHeight });
  };

  const severityColorMap = {
    small: 'border-zinc-700',
    medium: 'border-zinc-400',
    large: 'border-white',
  };

  const hasDetections = result.detections && result.detections.length > 0;

  return (
    <div className="min-h-screen bg-black relative flex flex-col pt-32 px-6 pb-20">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="max-w-7xl mx-auto w-full"
      >
        {/* Navigation & Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div className="flex flex-col gap-4">
            <button
              onClick={() => router.push('/upload')}
              className="inline-flex items-center gap-2 text-zinc-500 hover:text-white transition-colors text-xs font-bold uppercase tracking-widest"
            >
              <ArrowLeft className="w-4 h-4" />
              Analyze New Asset
            </button>
            <h1 className="text-4xl md:text-6xl font-black tracking-tighter text-white uppercase">
              Analysis Results
            </h1>
          </div>

          {/* Always show report download button if URL exists, regardless of detections count */}
          {result.report_url && (
            <motion.a
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              href={getFullReportUrl(result.report_url || '')}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-3 px-8 py-4 rounded-xl bg-white text-black font-black text-sm uppercase tracking-widest transition-all duration-300"
            >
              <Download className="w-5 h-5" />
              Download Report
            </motion.a>
          )}
        </div>

        {/* Dash Stats */}
        <DashboardStats
          totalPotholes={result.total_potholes}
          totalCost={result.total_cost}
          severityDistribution={result.severity_distribution}
        />

        {/* Detailed Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12">
          {/* Visual Evidence Card - Expanded if video exists */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className={`rounded-3xl overflow-hidden bg-zinc-900/20 border border-zinc-900 ${result.video_url ? 'lg:col-span-2' : ''}`}
          >
            <div className="p-6 border-b border-zinc-900 flex items-center justify-between">
              <h2 className="text-sm font-black text-white uppercase tracking-widest">Visual Evidence</h2>
              {result.imageUrl && <span className="text-[10px] text-zinc-500 font-bold uppercase">{imageSize.width}x{imageSize.height} PX</span>}
            </div>
            <div className="relative p-6">
              {result.video_url ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left: Original Video */}
                  <div className="flex flex-col gap-4">
                    <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest">Initial Upload</p>
                    <div className="relative rounded-2xl overflow-hidden border border-zinc-800 bg-black aspect-video">
                      {result.originalVideoUrl && (
                        <video 
                          src={getFullReportUrl(result.originalVideoUrl || '')} 
                          autoPlay 
                          muted 
                          loop 
                          playsInline
                          className="w-full h-full object-cover"
                        />
                      )}
                    </div>
                  </div>
                  {/* Right: Processed Video */}
                  <div className="flex flex-col gap-4">
                    <p className="text-[10px] font-black text-zinc-500 uppercase tracking-widest">AI Detection Overlay</p>
                    <div className="relative rounded-2xl overflow-hidden border border-zinc-800 bg-black aspect-video">
                      <video 
                        src={getFullReportUrl(result.video_url)} 
                        autoPlay 
                        muted 
                        loop 
                        playsInline
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="relative rounded-2xl overflow-hidden border border-zinc-800 bg-black">
                  {result.imageUrl ? (
                    <>
                      <img
                        src={getFullReportUrl(result.imageUrl || '')}
                        alt="Analyzed road"
                        onLoad={handleImageLoad}
                        className="w-full h-auto"
                      />
                      {imageSize.width > 0 && result.detections?.map((detection: DetectionResult, idx: number) => {
                        const bbox = detection.bbox;
                        const xMin = (bbox[0] / 100) * imageSize.width;
                        const yMin = (bbox[1] / 100) * imageSize.height;
                        const width = ((bbox[2] - bbox[0]) / 100) * imageSize.width;
                        const height = ((bbox[3] - bbox[1]) / 100) * imageSize.height;

                        return (
                          <div
                            key={idx}
                            className={`absolute border-2 ${severityColorMap[detection.severity as keyof typeof severityColorMap] || 'border-zinc-500'} rounded-[2px] shadow-[0_0_0_1px_rgba(0,0,0,0.5)]`}
                            style={{
                              left: `${(xMin / imageSize.width) * 100}%`,
                              top: `${(yMin / imageSize.height) * 100}%`,
                              width: `${(width / imageSize.width) * 100}%`,
                              height: `${(height / imageSize.height) * 100}%`,
                            }}
                          >
                            <div className={`absolute -top-6 left-0 px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-tighter ${
                              detection.severity === 'large' ? 'bg-white text-black' :
                              detection.severity === 'medium' ? 'bg-zinc-400 text-black' : 'bg-zinc-700 text-white'
                            }`}>
                              ID-{idx + 1}
                            </div>
                          </div>
                        );
                      })}
                    </>
                  ) : (
                    <div className="aspect-video flex flex-col items-center justify-center text-zinc-700">
                      <FileText className="w-16 h-16 mb-4 opacity-20" />
                      <p className="text-sm font-black uppercase tracking-widest">Analysis Result Missing</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </motion.div>

          {/* Detections List Card */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="rounded-3xl overflow-hidden bg-zinc-900/20 border border-zinc-900 flex flex-col h-full"
          >
            <div className="p-6 border-b border-zinc-900">
              <h2 className="text-sm font-black text-white uppercase tracking-widest">Defect Inventory</h2>
              <p className="text-[10px] text-zinc-500 font-bold uppercase mt-1">{(result.detections?.length || 0)} Total Objects Found</p>
            </div>
            <div className="p-6 flex-grow max-h-[600px] overflow-y-auto space-y-4">
              {!hasDetections ? (
                <div className="flex flex-col items-center justify-center h-full py-12 text-zinc-500">
                  <AlertCircle className="w-12 h-12 mb-4 opacity-10" />
                  <p className="font-black uppercase tracking-widest text-[10px]">No Potholes Detected</p>
                  <p className="text-[8px] uppercase tracking-tighter mt-2 opacity-50">Road surface appears clear of identifiable defects</p>
                </div>
              ) : (
                result.detections?.map((detection, index) => (
                  <ResultCard key={index} detection={detection} index={index} />
                ))
              )}
            </div>
          </motion.div>
        </div>

        {/* Data Inspector */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-12"
        >
          <div className="rounded-3xl p-8 border border-zinc-900 bg-zinc-900/10">
            <h2 className="text-xs font-black text-white uppercase tracking-[0.3em] mb-6">RAW PAYLOAD INSPECTOR</h2>
            <div className="bg-black/50 border border-zinc-900 rounded-2xl p-6 overflow-x-auto max-h-[300px] scrollbar-thin">
              <pre className="text-[11px] font-mono leading-relaxed text-zinc-500">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}