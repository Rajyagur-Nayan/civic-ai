'use client';

import { motion } from 'framer-motion';
import { PotholeDetection } from '@/services/api';
import { AlertTriangle, Ruler, DollarSign, Users } from 'lucide-react';

interface ResultCardProps {
  detection: PotholeDetection;
  index: number;
}

const severityColors = {
  low: 'from-green-500/20 to-green-500/5 border-green-500/30',
  medium: 'from-yellow-500/20 to-yellow-500/5 border-yellow-500/30',
  high: 'from-red-500/20 to-red-500/5 border-red-500/30',
};

const severityBadges = {
  low: 'bg-green-500/20 text-green-400',
  medium: 'bg-yellow-500/20 text-yellow-400',
  high: 'bg-red-500/20 text-red-400',
};

export default function ResultCard({ detection, index }: ResultCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`rounded-2xl p-6 border bg-gradient-to-br ${severityColors[detection.severity]}`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${severityBadges[detection.severity]}`}>
            {detection.severity.toUpperCase()}
          </div>
          <span className="text-white/40 text-sm">
            #{detection.pothole_id}
          </span>
        </div>
        <div className="flex items-center gap-1 text-white/60 text-sm">
          <AlertTriangle className="w-4 h-4" />
          {(detection.confidence * 100).toFixed(1)}%
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
            <Ruler className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <p className="text-white/40 text-xs">Area</p>
            <p className="text-white font-semibold">{detection.area.toFixed(1)} m²</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
            <DollarSign className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <p className="text-white/40 text-xs">Est. Cost</p>
            <p className="text-white font-semibold">${detection.estimated_cost.toFixed(2)}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
            <Users className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <p className="text-white/40 text-xs">Workers</p>
            <p className="text-white font-semibold">{detection.workers_needed}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
            <svg className="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <div>
            <p className="text-white/40 text-xs">Coordinates</p>
            <p className="text-white font-semibold text-xs">
              ({detection.x_min}, {detection.y_min})
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}