'use client';

import { motion } from 'framer-motion';
import { DetectionResult } from '@/services/api';
import { AlertTriangle, Ruler, DollarSign, Users, Clock } from 'lucide-react';

interface ResultCardProps {
  detection: DetectionResult;
  index: number;
}

const severityColors = {
  small: 'from-green-500/20 to-green-500/5 border-green-500/30',
  medium: 'from-yellow-500/20 to-yellow-500/5 border-yellow-500/30',
  large: 'from-red-500/20 to-red-500/5 border-red-500/30',
};

const severityBadges = {
  small: 'bg-green-500/20 text-green-400',
  medium: 'bg-yellow-500/20 text-yellow-400',
  large: 'bg-red-500/20 text-red-400',
};

export default function ResultCard({ detection, index }: ResultCardProps) {
  const bbox = detection.bbox;
  
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
            #{index + 1}
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
            <p className="text-white font-semibold">${detection.cost.toFixed(2)}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
            <Users className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <p className="text-white/40 text-xs">Workers</p>
            <p className="text-white font-semibold">{detection.workers}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
            <Clock className="w-5 h-5 text-orange-400" />
          </div>
          <div>
            <p className="text-white/40 text-xs">Time</p>
            <p className="text-white font-semibold">{detection.time} hrs</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}