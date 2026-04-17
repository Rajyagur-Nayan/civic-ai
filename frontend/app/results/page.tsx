'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import ResultCard from '@/components/ResultCard';
import DashboardStats from '@/components/DashboardStats';
import { DetectionResult, DetectionResponse } from '@/services/api';

interface ResultData extends DetectionResponse {
  imageUrl: string;
}

export default function ResultsPage() {
  const router = useRouter();
  const [result, setResult] = useState<ResultData | null>(null);
  const [mounted, setMounted] = useState(false);
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    setMounted(true);
    const stored = sessionStorage.getItem('detectionResult');
    if (stored) {
      try {
        setResult(JSON.parse(stored));
      } catch (err) {
        console.error('Failed to parse detection result', err);
        router.push('/upload');
      }
    } else {
      router.push('/upload');
    }
  }, [router]);

  if (!mounted || !result) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
      </div>
    );
  }

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setImageSize({ width: img.naturalWidth, height: img.naturalHeight });
  };

  const severityColorMap = {
    small: 'border-green-500',
    medium: 'border-yellow-500',
    large: 'border-red-500',
  };

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-cyan-900/20 via-black to-black" />
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMyMDIyMzIiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMSIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="relative z-10 min-h-screen"
      >
        <header className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <motion.div
                initial={{ rotate: 0 }}
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center"
              >
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </motion.div>
              <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                Civ-AI
              </span>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/" className="px-4 py-2 rounded-lg text-white/60 hover:text-white transition-colors">
                Home
              </Link>
              <Link href="/upload" className="px-4 py-2 rounded-lg text-white/60 hover:text-white transition-colors">
                Upload
              </Link>
            </nav>
          </div>
        </header>

        <main className="pt-32 pb-20">
          <section className="max-w-7xl mx-auto px-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="mb-8"
            >
              <Link
                href="/upload"
                className="inline-flex items-center gap-2 text-white/60 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Upload New Image
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="mb-12"
            >
              <h1 className="text-4xl md:text-5xl font-bold mb-4">
                <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                  Detection Results
                </span>
              </h1>
            </motion.div>

            <DashboardStats
              totalPotholes={result.total_potholes}
              totalCost={result.total_cost}
              severityDistribution={result.severity_distribution}
            />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="rounded-2xl overflow-hidden bg-white/5 border border-white/10"
              >
                <div className="p-4 border-b border-white/10">
                  <h2 className="text-lg font-semibold text-white">Analyzed Image</h2>
                </div>
                <div className="relative p-4">
                  <div className="relative">
                    <img
                      src={result.imageUrl}
                      alt="Analyzed road"
                      onLoad={handleImageLoad}
                      className="w-full rounded-xl"
                    />
                    {imageSize.width > 0 && result.detections.map((detection: DetectionResult, idx: number) => {
                      const bbox = detection.bbox;
                      const xMin = (bbox[0] / 100) * imageSize.width;
                      const yMin = (bbox[1] / 100) * imageSize.height;
                      const width = ((bbox[2] - bbox[0]) / 100) * imageSize.width;
                      const height = ((bbox[3] - bbox[1]) / 100) * imageSize.height;

                      return (
                        <div
                          key={idx}
                          className={`absolute border-2 ${severityColorMap[detection.severity]} rounded-sm`}
                          style={{
                            left: xMin,
                            top: yMin,
                            width: width || 1,
                            height: height || 1,
                          }}
                        >
                          <div className={`absolute -top-6 left-0 px-2 py-0.5 rounded text-xs font-medium ${
                            detection.severity === 'small' ? 'bg-green-500' :
                            detection.severity === 'medium' ? 'bg-yellow-500' : 'bg-red-500'
                          } text-black`}>
                            #{idx + 1}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="rounded-2xl overflow-hidden bg-white/5 border border-white/10"
              >
                <div className="p-4 border-b border-white/10">
                  <h2 className="text-lg font-semibold text-white">Detected Potholes</h2>
                  <p className="text-white/50 text-sm">{result.detections.length} potholes detected</p>
                </div>
                <div className="p-4 max-h-[600px] overflow-y-auto space-y-4">
                  {result.detections.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-white/40">
                      <AlertCircle className="w-12 h-12 mb-4" />
                      <p>No potholes detected in this image.</p>
                    </div>
                  ) : (
                    result.detections.map((detection, index) => (
                      <ResultCard key={index} detection={detection} index={index} />
                    ))
                  )}
                </div>
              </motion.div>
            </div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="mt-12"
            >
              <div className="rounded-2xl p-6 bg-white/5 border border-white/10">
                <h2 className="text-lg font-semibold text-white mb-4">Raw API Response</h2>
                <pre className="bg-black/50 rounded-xl p-4 text-sm text-cyan-400 overflow-x-auto max-h-96">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </motion.div>
          </section>
        </main>
      </motion.div>
    </div>
  );
}