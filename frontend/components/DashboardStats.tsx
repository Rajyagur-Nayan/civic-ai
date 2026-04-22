"use client";

import { motion } from "framer-motion";
import { AlertTriangle, IndianRupee, BarChart3 } from "lucide-react";

interface DashboardStatsProps {
  totalPotholes: number;
  totalCost: number;
  severityDistribution: {
    small: number;
    medium: number;
    large: number;
  };
}

export default function DashboardStats({
  totalPotholes = 0,
  totalCost = 0,
  severityDistribution = { small: 0, medium: 0, large: 0 },
}: DashboardStatsProps) {
  const safeDist = severityDistribution || { small: 0, medium: 0, large: 0 };
  const total =
    (safeDist.small || 0) + (safeDist.medium || 0) + (safeDist.large || 0);
  const safeTotal = total || 1;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl p-6 border border-zinc-800 bg-zinc-900/30"
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-white/5 border border-zinc-800 flex items-center justify-center">
            <AlertTriangle className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="text-zinc-500 text-sm font-medium uppercase tracking-wider">Potholes Detected</p>
            <p className="text-3xl font-bold text-white tracking-tight">{totalPotholes}</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="rounded-2xl p-6 border border-zinc-800 bg-zinc-900/30"
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-white/5 border border-zinc-800 flex items-center justify-center">
            <IndianRupee className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="text-zinc-500 text-sm font-medium uppercase tracking-wider">Est. Repair Cost</p>
            <p className="text-3xl font-bold text-white tracking-tight">
              ₹{totalCost.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
            </p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-2xl p-6 border border-zinc-800 bg-zinc-900/30"
      >
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-white/5 border border-zinc-800 flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="text-zinc-500 text-sm font-medium uppercase tracking-wider">Severity Mix</p>
            <p className="text-3xl font-bold text-white tracking-tight">{total}</p>
          </div>
        </div>
        <div className="flex gap-2 mt-4 h-2 rounded-full overflow-hidden bg-zinc-800">
          <div
            className="h-full bg-zinc-600 transition-all duration-500"
            style={{ width: `${((safeDist.small || 0) / safeTotal) * 100}%` }}
          />
          <div
            className="h-full bg-zinc-400 transition-all duration-500"
            style={{ width: `${((safeDist.medium || 0) / safeTotal) * 100}%` }}
          />
          <div
            className="h-full bg-white transition-all duration-500"
            style={{ width: `${((safeDist.large || 0) / safeTotal) * 100}%` }}
          />
        </div>
        <div className="flex justify-between mt-3">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-zinc-600" />
            <span className="text-[10px] text-zinc-500 font-medium uppercase">Small</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-zinc-400" />
            <span className="text-[10px] text-zinc-500 font-medium uppercase">Med</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-white" />
            <span className="text-[10px] text-zinc-500 font-medium uppercase">Large</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

