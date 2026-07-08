import React from "react";
import { motion } from "framer-motion";
import { Terminal, ShieldAlert, CheckSquare } from "lucide-react";
import type { CommanderResponse } from "../types/api";

interface CommandPanelProps {
  decision: CommanderResponse | null;
  onSimulate: () => void;
  loading: boolean;
  isAutoSimulating: boolean;
  onStart: () => void;
  onPause: () => void;
  onReset: () => void;
}

export const CommandPanel: React.FC<CommandPanelProps> = ({
  decision,
  onSimulate,
  loading,
  isAutoSimulating,
  onStart,
  onPause,
  onReset
}) => {
  const getPriorityStyle = (priority: string | undefined) => {
    const p = (priority || "LOW").toUpperCase();
    if (p === "CRITICAL" || p === "HIGH") {
      return "text-rose-400 border-rose-500/30 bg-rose-950/20";
    }
    if (p === "MEDIUM" || p === "WARNING") {
      return "text-amber-400 border-amber-500/30 bg-amber-950/20";
    }
    return "text-emerald-400 border-emerald-500/30 bg-emerald-950/20";
  };

  const isHigh = decision?.priority.toUpperCase() === "HIGH" || decision?.priority.toUpperCase() === "CRITICAL";

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        staggerChildren: 0.15
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.4 } }
  };

  // Circular gauge setup
  const confidence = decision?.confidence || 0.0;
  const radius = 20;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - confidence * circumference;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="bg-slate-900 border border-gray-800 rounded-2xl p-6 flex flex-col justify-between h-full shadow-2xl hover:border-blue-500/20 transition-colors duration-300 font-sans"
    >
      <div className="space-y-6">
        {/* Title & Priority Badge */}
        <div className="flex items-center justify-between border-b border-gray-800 pb-4">
          <div className="flex items-center gap-2">
            <span className="text-xl">🤖</span>
            <h2 className="text-sm font-black tracking-widest text-gray-200 uppercase font-mono">
              AI Commander
            </h2>
          </div>

          {decision && (
            <motion.span
              animate={isHigh ? {
                scale: [1, 1.05, 1],
                boxShadow: [
                  "0 0 0 0px rgba(239, 68, 68, 0.4)",
                  "0 0 0 6px rgba(239, 68, 68, 0)",
                  "0 0 0 0px rgba(239, 68, 68, 0)"
                ]
              } : {}}
              transition={isHigh ? {
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              } : undefined}
              className={`px-3 py-1 rounded-full text-xs font-black font-mono tracking-wider border uppercase flex items-center gap-1.5 ${getPriorityStyle(
                decision.priority
              )}`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  isHigh
                    ? "bg-rose-400"
                    : decision.priority === "MEDIUM"
                    ? "bg-amber-400"
                    : "bg-emerald-400"
                }`}
              />
              {decision.priority}
            </motion.span>
          )}
        </div>

        {/* Simulation Controls Row */}
        <div className="flex flex-col gap-2 bg-gray-950/40 p-3 rounded-xl border border-gray-800/80">
          <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider font-mono">
            Simulation Controller
          </span>
          <div className="flex items-center gap-2 flex-wrap">
            {isAutoSimulating ? (
              <button
                onClick={onPause}
                disabled={loading}
                className="flex items-center gap-1 px-2.5 py-1.5 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-amber-50 text-[10px] font-bold font-mono tracking-wider rounded-lg transition-all duration-200 active:scale-95 cursor-pointer"
              >
                ⏸ Pause
              </button>
            ) : (
              <button
                onClick={onStart}
                disabled={loading}
                className="flex items-center gap-1 px-2.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-emerald-50 text-[10px] font-bold font-mono tracking-wider rounded-lg transition-all duration-200 active:scale-95 cursor-pointer"
              >
                ▶ Start Simulation
              </button>
            )}

            <button
              onClick={onSimulate}
              disabled={loading || isAutoSimulating}
              className="flex items-center gap-1 px-2.5 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-blue-50 text-[10px] font-bold font-mono tracking-wider rounded-lg transition-all duration-200 active:scale-95 cursor-pointer"
            >
              ⏭ Next Phase
            </button>

            <button
              onClick={onReset}
              disabled={loading || isAutoSimulating}
              className="flex items-center gap-1 px-2.5 py-1.5 bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-rose-50 text-[10px] font-bold font-mono tracking-wider rounded-lg transition-all duration-200 active:scale-95 cursor-pointer"
            >
              🔄 Reset
            </button>

            {loading && (
              <span className="flex items-center gap-1.5 text-[9px] font-mono text-blue-400 font-bold uppercase ml-auto animate-pulse">
                <span className="animate-spin w-3.5 h-3.5 border-2 border-blue-500 border-t-transparent rounded-full shrink-0" />
                RUNNING...
              </span>
            )}
          </div>
        </div>

        {decision ? (
          <div className="space-y-4">
            {/* Top Risk Vector */}
            <motion.div variants={itemVariants} className="space-y-1">
              <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest flex items-center gap-1.5 font-mono">
                <ShieldAlert className="w-4 h-4 text-rose-500 shrink-0" />
                Top Operation Risk Vector:
              </p>
              <h3 className="text-base font-black text-white tracking-wide mt-1.5 pl-5.5 leading-snug">
                {decision.top_risk}
              </h3>
            </motion.div>

            {/* Operational Summary */}
            <motion.div variants={itemVariants} className="space-y-1.5">
              <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest font-mono">
                Situation Summary:
              </p>
              <p className="text-gray-300 text-xs leading-relaxed pl-5.5 select-text">
                {decision.summary}
              </p>
            </motion.div>

            {/* Recommended Checklist Actions */}
            <motion.div variants={itemVariants} className="space-y-2">
              <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest font-mono">
                Recommended Action Directives:
              </p>
              <ul className="space-y-2 pl-5.5">
                {decision.actions.map((action, idx) => (
                  <motion.li
                    key={idx}
                    variants={itemVariants}
                    className="flex items-start gap-2 text-xs text-gray-100 font-mono select-text"
                  >
                    <CheckSquare className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                    <span>{action}</span>
                  </motion.li>
                ))}
              </ul>
            </motion.div>

            {/* Estimated Impact Grid & Confidence Gauge */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center pt-2 border-t border-gray-800/80">
              {/* Estimated Impact Card */}
              <motion.div
                variants={itemVariants}
                className="md:col-span-8 bg-emerald-950/20 border border-emerald-500/20 rounded-xl p-3.5 flex flex-col justify-between h-[85px]"
              >
                <div className="text-[8px] text-emerald-400 font-bold tracking-wider font-mono">
                  ESTIMATED IMPACT FORECAST:
                </div>
                <div className="text-2xs font-bold text-emerald-300 font-mono mt-1 select-text">
                  {decision.estimated_impact}
                </div>
              </motion.div>

              {/* Confidence Circle */}
              <motion.div
                variants={itemVariants}
                className="md:col-span-4 flex items-center justify-center gap-3 bg-gray-950/50 border border-gray-800 rounded-xl p-3 h-[85px]"
              >
                <div className="relative w-12 h-12 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="24"
                      cy="24"
                      r={radius}
                      className="stroke-gray-800 fill-none"
                      strokeWidth="3.5"
                    />
                    <motion.circle
                      cx="24"
                      cy="24"
                      r={radius}
                      className="stroke-blue-500 fill-none glow-blue"
                      strokeWidth="3.5"
                      strokeDasharray={circumference}
                      initial={{ strokeDashoffset: circumference }}
                      animate={{ strokeDashoffset }}
                      transition={{ duration: 1.2, ease: "easeOut" }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center font-mono font-bold text-2xs text-white">
                    {(confidence * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div className="text-[7px] text-gray-500 font-bold uppercase tracking-wider font-mono">
                    CONFIDENCE
                  </div>
                  <div className="text-[9px] text-gray-400 font-bold font-mono">
                    OPTIMAL
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-48 text-center text-gray-600 font-mono">
            <span className="text-2xl mb-2">⚡</span>
            <p className="text-2xs uppercase tracking-widest font-bold">
              SYS STATUS: WAITING FOR ADVANCE
            </p>
            <p className="text-[10px] mt-1 text-gray-500">
              Click &quot;SIMULATE&quot; to advance match timeline index.
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-900 flex items-center justify-between text-2xs font-mono text-gray-500 select-none">
        <span className="flex items-center gap-1.5">
          <Terminal className="w-3.5 h-3.5 text-blue-500" />
          SYS: SIGNAL AGENT DISPATCH
        </span>
        <span>Telemetry online</span>
      </div>
    </motion.div>
  );
};
export default CommandPanel;
