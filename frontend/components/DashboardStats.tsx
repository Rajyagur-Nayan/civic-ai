"use client";

import { motion } from "framer-motion";
import { AlertTriangle, DollarSign, BarChart3 } from "lucide-react";

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
  // Defensive check for missing severityDistribution
  const safeDist = severityDistribution || { small: 0, medium: 0, large: 0 };
  const total =
    (safeDist.small || 0) + (safeDist.medium || 0) + (safeDist.large || 0);
  const safeTotal = total || 1;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0 }}
        className="rounded-2xl p-6 border bg-gradient-to-br from-cyan-500/20 to-cyan-500/5 border-cyan-500/30"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center">
            <AlertTriangle className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <p className="text-white/60 text-sm">Total Potholes</p>
            <p className="text-3xl font-bold text-white">{totalPotholes}</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="rounded-2xl p-6 border bg-gradient-to-br from-purple-500/20 to-purple-500/5 border-purple-500/30"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
            <DollarSign className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <p className="text-white/60 text-sm">Total Estimated Cost</p>
            <p className="text-3xl font-bold text-white">
              ₹{totalCost.toFixed(2)}
            </p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-2xl p-6 border bg-gradient-to-br from-orange-500/20 to-orange-500/5 border-orange-500/30"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-orange-500/20 flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-orange-400" />
          </div>
          <div>
            <p className="text-white/60 text-sm">Severity Distribution</p>
            <p className="text-3xl font-bold text-white">{total} total</p>
          </div>
        </div>
        <div className="flex gap-2 mt-2">
          <div className="flex-1">
            <div
              className="h-2 rounded-full bg-green-500"
              style={{
                width: `${((safeDist.small || 0) / safeTotal) * 100}%`,
                maxWidth: "100%",
              }}
            />
            <p className="text-xs text-white/40 mt-1">
              Small ({safeDist.small || 0})
            </p>
          </div>
          <div className="flex-1">
            <div
              className="h-2 rounded-full bg-yellow-500"
              style={{
                width: `${((safeDist.medium || 0) / safeTotal) * 100}%`,
                maxWidth: "100%",
              }}
            />
            <p className="text-xs text-white/40 mt-1">
              Med ({safeDist.medium || 0})
            </p>
          </div>
          <div className="flex-1">
            <div
              className="h-2 rounded-full bg-red-500"
              style={{
                width: `${((safeDist.large || 0) / safeTotal) * 100}%`,
                maxWidth: "100%",
              }}
            />
            <p className="text-xs text-white/40 mt-1">
              Large ({safeDist.large || 0})
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
