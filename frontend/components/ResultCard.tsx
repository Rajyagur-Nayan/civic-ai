'use client';

import { motion } from 'framer-motion';
import { AlertTriangle, Ruler, DollarSign, Users, Clock } from 'lucide-react';

interface ResultCardProps {
  detection: {
    bbox: number[];
    area: number;
    severity: string;
    workers: number;
    cost: number;
    time: number;
    confidence: number;
  };
  index: number;
}

export default function ResultCard({ detection, index }: ResultCardProps) {
  const getSeverityStyles = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'large':
        return 'border-white text-white bg-white/10';
      case 'medium':
        return 'border-zinc-500 text-zinc-300 bg-zinc-500/10';
      default:
        return 'border-zinc-700 text-zinc-500 bg-zinc-700/10';
    }
  };

  const stats = [
    { icon: Ruler, label: 'Area', value: `${detection.area.toFixed(1)} m²` },
    { icon: DollarSign, label: 'Est. Cost', value: `₹${detection.cost.toFixed(0)}` },
    { icon: Users, label: 'Team', value: `${detection.workers}` },
    { icon: Clock, label: 'Time', value: `${detection.time}h` },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="p-5 rounded-2xl bg-zinc-950 border border-zinc-800 hover:border-zinc-700 transition-all duration-300 group"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter border ${getSeverityStyles(detection.severity)}`}>
            {detection.severity}
          </div>
          <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest">
            #{index + 1}
          </span>
        </div>
        <div className="flex items-center gap-1 text-zinc-500 text-[10px] font-bold">
          <AlertTriangle className="w-3 h-3" />
          {(detection.confidence * 100).toFixed(0)}%
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {stats.map((stat, i) => (
          <div key={i} className="flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-zinc-500">
              <stat.icon className="w-3.5 h-3.5" />
              <span className="text-[10px] font-medium uppercase tracking-wider">{stat.label}</span>
            </div>
            <p className="text-sm font-bold text-white tracking-tight">
              {stat.value}
            </p>
          </div>
        ))}
      </div>
    </motion.div>
  );
}