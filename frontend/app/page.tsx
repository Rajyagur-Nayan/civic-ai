'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, MapPin, Zap, Shield, BarChart3 } from 'lucide-react';

export default function Home() {
  const features = [
    {
      icon: Zap,
      title: 'Real-time Detection',
      description: 'Precision AI identifies road defects in milliseconds.',
    },
    {
      icon: BarChart3,
      title: 'Resource Planning',
      description: 'Automated cost and labor estimation for repairs.',
    },
    {
      icon: Shield,
      title: 'Asset Resilience',
      description: 'Prioritize data-driven city infrastructure maintenance.',
    },
  ];

  return (
    <div className="min-h-screen bg-black relative flex flex-col items-center">
      {/* Subtle Noise/Grain overlay for texture */}
      <div className="absolute inset-0 bg-black z-0" />
      
      <main className="relative z-10 w-full max-w-7xl px-6 pt-32 pb-24 flex flex-col items-center">
        {/* Hero Section */}
        <section className="text-center mb-24 max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-zinc-800 bg-zinc-900/50 text-zinc-400 text-[10px] font-bold uppercase tracking-widest mb-8"
          >
            <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
            Infrastructure Intelligence v1.0
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-6xl md:text-8xl font-black tracking-tighter text-white mb-8 leading-[0.9]"
          >
            DECODE THE ROAD.<br />
            <span className="text-zinc-600">SMARTER CITIES.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-lg md:text-xl text-zinc-500 font-medium max-w-2xl mx-auto mb-12 leading-relaxed"
          >
            Civ-AI leverages computer vision to automate road assessments, 
            providing instant visibility into infrastructure health and repair strategies.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
          >
            <Link
              href="/upload"
              className="inline-flex items-center gap-3 px-10 py-5 rounded-2xl bg-white text-black font-black text-xl hover:bg-zinc-200 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
            >
              LAUNCH ANALYSIS
              <ArrowRight className="w-6 h-6" />
            </Link>
          </motion.div>
        </section>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              className="p-8 rounded-3xl border border-zinc-900 bg-zinc-900/20 hover:border-zinc-800 transition-all duration-300 group"
            >
              <div className="w-12 h-12 rounded-xl bg-white/5 border border-zinc-800 flex items-center justify-center mb-6 group-hover:bg-white transition-all duration-300">
                <feature.icon className="w-6 h-6 text-white group-hover:text-black transition-colors" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3 tracking-tight">
                {feature.title}
              </h3>
              <p className="text-zinc-500 leading-relaxed text-sm font-medium">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </main>

      {/* Footer Branding */}
      <footer className="mt-auto py-12 text-center text-zinc-800 font-bold uppercase tracking-[0.5em] text-[10px]">
        Civic Intelligence Systems &bull; MMXXVI
      </footer>
    </div>
  );
}