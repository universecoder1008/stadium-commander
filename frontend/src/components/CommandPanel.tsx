import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Terminal } from "lucide-react";
import type { CommanderResponse, CombinedSituationReport } from "../types/api";

interface CommandPanelProps {
  decision: CommanderResponse | null;
  report: CombinedSituationReport | null;
  onSimulate: () => void;
  loading: boolean;
  isAutoSimulating: boolean;
  onStart: () => void;
  onPause: () => void;
  onReset: () => void;
  error?: string | null;
}

const truncateToWords = (str: string, maxWords: number) => {
  if (!str) return "";
  const words = str.split(/\s+/);
  if (words.length <= maxWords) return str;
  return words.slice(0, maxWords).join(" ") + "...";
};

const getProgressBar = (conf: number) => {
  const totalBlocks = 10;
  const filledBlocks = Math.round(conf * totalBlocks);
  const emptyBlocks = totalBlocks - filledBlocks;
  return "█".repeat(filledBlocks) + "░".repeat(emptyBlocks) + ` ${(conf * 100).toFixed(0)}%`;
};

const reasoningSteps = [
  "🤖 Receiving telemetry",
  "🧠 Analyzing stadium operations",
  "📊 Prioritizing operational risks",
  "⚙️ Generating recommendations"
];

export const CommandPanel: React.FC<CommandPanelProps> = ({
  decision,
  report,
  onSimulate,
  loading,
  isAutoSimulating,
  onStart,
  onPause,
  onReset,
  error
}) => {
  const [lastUpdatedText, setLastUpdatedText] = useState("Awaiting advance");
  const lastUpdatedTime = useRef<number | null>(null);
  const [currentStepIdx, setCurrentStepIdx] = useState(0);

  // Trigger step indices at 300ms intervals when loading is active
  useEffect(() => {
    let timer: any;
    if (loading) {
      setCurrentStepIdx(0);
      timer = setInterval(() => {
        setCurrentStepIdx((prev) => {
          if (prev < 3) return prev + 1;
          clearInterval(timer);
          return prev;
        });
      }, 300);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [loading]);

  useEffect(() => {
    if (decision) {
      lastUpdatedTime.current = Date.now();
      setLastUpdatedText("Updated just now");
    } else {
      lastUpdatedTime.current = null;
      setLastUpdatedText("Awaiting advance");
    }
  }, [decision]);

  useEffect(() => {
    const timer = setInterval(() => {
      if (lastUpdatedTime.current) {
        const diff = Math.floor((Date.now() - lastUpdatedTime.current) / 1000);
        if (diff < 5) {
          setLastUpdatedText("Updated just now");
        } else if (diff < 60) {
          setLastUpdatedText(`Updated ${diff}s ago`);
        } else {
          setLastUpdatedText(`Updated ${Math.floor(diff / 60)}m ago`);
        }
      }
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const getSupportingRisks = () => {
    if (!report) return [];
    const risks: string[] = [];
    if (report.crowd && report.crowd.risk !== "LOW") {
      risks.push(`Crowd: ${report.crowd.predictions?.[0]?.issue || "Ingress congestion"}`);
    }
    if (report.transport && report.transport.risk !== "LOW") {
      risks.push(`Transport: Metro status is ${report.transport.metro_status}`);
    }
    if (report.medical && report.medical.risk !== "LOW") {
      risks.push(`Medical: Ambulance utilization at ${report.medical.ambulance_utilization_percent.toFixed(0)}%`);
    }
    if (report.weather && report.weather.risk !== "LOW") {
      risks.push(`Weather: ${report.weather.weather_status} - ${report.weather.prediction.expected_operational_impact}`);
    }
    if (report.volunteer && report.volunteer.risk !== "LOW") {
      risks.push(`Volunteer: Coverage is at ${report.volunteer.coverage_percent.toFixed(0)}%`);
    }
    return risks.slice(0, 3);
  };

  const supportingRisks = getSupportingRisks();

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
  const confidence = decision?.confidence || 0.0;

  const [animatedConfidence, setAnimatedConfidence] = useState(confidence);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);
    const listener = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener("change", listener);
    return () => mediaQuery.removeEventListener("change", listener);
  }, []);

  useEffect(() => {
    if (prefersReducedMotion) {
      setAnimatedConfidence(confidence);
      return;
    }

    const startValue = animatedConfidence;
    const endValue = confidence;
    if (startValue === endValue) return;

    let startTime: number | null = null;
    let frameId: number;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / 600, 1);
      const easedProgress = progress * (2 - progress);
      const current = startValue + (endValue - startValue) * easedProgress;

      setAnimatedConfidence(current);

      if (progress < 1) {
        frameId = requestAnimationFrame(animate);
      }
    };

    frameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameId);
  }, [confidence, prefersReducedMotion]);

  // Animation variants
  const containerVariants: any = {
    hidden: { opacity: 0, y: 12 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3,
        staggerChildren: 0.08
      }
    }
  };

  const listContainerVariants: any = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.06,
      },
    },
  };

  const listItemVariants: any = {
    hidden: { opacity: 0, x: -8 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.25, ease: "easeOut" },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="bg-slate-900 border border-gray-800 rounded-2xl p-6 flex flex-col justify-between h-full shadow-2xl hover:border-blue-500/20 transition-colors duration-300 font-sans"
    >
      <div className="space-y-6">
        {/* Title & Priority Badge */}
        <div className="flex items-center justify-between border-b border-gray-800 pb-4 select-none">
          <div className="flex items-center gap-2">
            <span className="text-xl" role="img" aria-label="robot logo">🤖</span>
            <h2 className="text-sm font-black tracking-widest text-gray-200 uppercase font-mono">
              AI Commander
            </h2>
          </div>

          {decision && !loading && (
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
          <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider font-mono select-none">
            Simulation Controller
          </span>
          <div className="flex items-center gap-2 flex-wrap">
            {isAutoSimulating ? (
              <button
                onClick={onPause}
                disabled={loading}
                aria-label="Pause Simulation"
                className="flex items-center gap-1 px-2.5 py-1.5 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-amber-50 text-[10px] font-bold font-mono tracking-wider rounded-lg transition-all duration-200 active:scale-95 cursor-pointer focus:outline-none focus:ring-2 focus:ring-amber-500/50"
              >
                ⏸ Pause
              </button>
            ) : (
              <button
                onClick={onStart}
                disabled={loading}
                aria-label="Start Simulation"
                className="flex items-center gap-1 px-2.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-emerald-50 text-[10px] font-bold font-mono tracking-wider rounded-lg transition-all duration-200 active:scale-95 cursor-pointer focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              >
                ▶ Start Simulation
              </button>
            )}

            <button
              onClick={onSimulate}
              disabled={loading || isAutoSimulating}
              aria-label="Next Simulation Phase"
              className="flex items-center gap-1 px-2.5 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-blue-50 text-[10px] font-bold font-mono tracking-wider rounded-lg transition-all duration-200 active:scale-95 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            >
              ⏭ Next Phase
            </button>

            <button
              onClick={onReset}
              disabled={loading || isAutoSimulating}
              aria-label="Reset Simulation Timeline"
              className="flex items-center gap-1 px-2.5 py-1.5 bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-rose-50 text-[10px] font-bold font-mono tracking-wider rounded-lg transition-all duration-200 active:scale-95 cursor-pointer focus:outline-none focus:ring-2 focus:ring-rose-500/50"
            >
              🔄 Reset
            </button>

            {loading && (
              <span className="flex items-center gap-1.5 text-[9px] font-mono text-blue-400 font-bold uppercase ml-auto animate-pulse select-none">
                <span className="animate-spin w-3.5 h-3.5 border-2 border-blue-500 border-t-transparent rounded-full shrink-0" />
                RUNNING...
              </span>
            )}
          </div>
        </div>

        <AnimatePresence mode="wait">
          {error && !loading ? (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center h-48 text-center text-rose-400 font-mono"
            >
              <span className="text-2xl mb-2 animate-bounce" role="img" aria-label="warning symbol">⚠</span>
              <p className="text-2xs uppercase tracking-widest font-black">
                AI UNAVAILABLE
              </p>
              <button
                onClick={onSimulate}
                className="mt-3.5 px-3.5 py-1.5 bg-rose-950/40 border border-rose-500/30 text-rose-300 hover:bg-rose-900/30 text-2xs font-bold font-mono tracking-wider rounded-lg transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-rose-500/50"
              >
                Retry
              </button>
            </motion.div>
          ) : loading ? (
            <motion.div
              key="loading-reasoning"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center h-48 text-center text-gray-400 font-mono select-none"
            >
              <motion.div
                animate={{ scale: [1, 1.04, 1] }}
                transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
                className="text-2xs uppercase tracking-widest font-black flex flex-col items-center gap-3.5"
              >
                <span className="text-2xl animate-pulse">🤖</span>
                <span className="flex items-center font-bold">
                  {reasoningSteps[currentStepIdx]}
                  <span className="inline-flex gap-0.5 ml-1">
                    <span className="animate-bounce delay-0">.</span>
                    <span className="animate-bounce delay-150">.</span>
                    <span className="animate-bounce delay-300">.</span>
                  </span>
                </span>
              </motion.div>
            </motion.div>
          ) : decision ? (
            <motion.div
              key={decision.top_risk}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="space-y-4"
            >
              {/* 🚨 TOP RISK */}
              <div className="space-y-1 select-none">
                <p className="text-[10px] text-rose-400 font-bold uppercase tracking-wider font-mono">
                  🚨 TOP RISK
                </p>
                <motion.h3 
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: "spring", stiffness: 300, damping: 15 }}
                  className="text-xs font-black text-white tracking-wide mt-1 pl-1.5 truncate select-all" 
                  title={decision.top_risk}
                >
                  {decision.top_risk}
                </motion.h3>
              </div>

              <div className="border-t border-gray-800/80 my-3" />

              {/* ⚠ SUPPORTING RISKS */}
              <div className="space-y-1.5 select-none">
                <p className="text-[10px] text-amber-500 font-bold uppercase tracking-wider font-mono">
                  ⚠ SUPPORTING RISKS
                </p>
                <ul className="space-y-1 pl-1.5">
                  {supportingRisks.length > 0 ? (
                    supportingRisks.map((risk, idx) => (
                      <li key={idx} className="text-2xs text-gray-400 font-mono flex items-start gap-1.5 truncate" title={risk}>
                        <span className="text-gray-600 font-bold">•</span>
                        <span className="select-text">{risk}</span>
                      </li>
                    ))
                  ) : (
                    <li className="text-2xs text-gray-500 font-mono italic">
                      All secondary sectors stable.
                    </li>
                  )}
                </ul>
              </div>

              <div className="border-t border-gray-800/80 my-3" />

              {/* 🎯 RECOMMENDED ACTIONS */}
              <div className="space-y-2 select-none">
                <p className="text-[10px] text-blue-400 font-bold uppercase tracking-wider font-mono">
                  🎯 RECOMMENDED ACTIONS
                </p>
                <motion.ul
                  variants={listContainerVariants}
                  initial="hidden"
                  animate="visible"
                  className="space-y-1.5 pl-1.5"
                >
                  {decision.actions.slice(0, 4).map((action, idx) => (
                    <motion.li
                      key={idx}
                      variants={listItemVariants}
                      className="text-2xs text-gray-200 font-mono flex items-start gap-1.5 select-text line-clamp-2"
                      title={action}
                    >
                      <span className="text-blue-500 font-black">✓</span>
                      <span>{action}</span>
                    </motion.li>
                  ))}
                </motion.ul>
              </div>

              {/* Expected Impact & Confidence Block */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center pt-2 border-t border-gray-800/80">
                {/* 📈 EXPECTED IMPACT */}
                <div
                  className="md:col-span-8 bg-emerald-950/20 border border-emerald-500/20 rounded-xl p-3 flex flex-col justify-between min-h-[85px] h-auto break-words"
                >
                  <div className="text-[8px] text-emerald-400 font-bold tracking-wider font-mono select-none">
                    📈 EXPECTED IMPACT
                  </div>
                  <div className="text-2xs font-bold text-emerald-300 font-mono mt-1.5 select-text line-clamp-2" title={decision.estimated_impact}>
                    {truncateToWords(decision.estimated_impact, 15)}
                  </div>
                </div>

                {/* 🎯 CONFIDENCE */}
                <div
                  className="md:col-span-4 bg-gray-950/50 border border-gray-800 rounded-xl p-3 flex flex-col justify-between min-h-[85px] h-auto font-mono text-3xs select-none text-left"
                >
                  <div className="text-gray-500 font-bold uppercase tracking-wider">
                    🎯 CONFIDENCE
                  </div>
                  <div className="text-[9px] text-blue-400 font-black mt-2 font-mono whitespace-nowrap">
                    {getProgressBar(animatedConfidence)}
                  </div>
                  <div className="text-[7px] text-gray-600 font-bold uppercase mt-1">
                    OPTIMAL REASONING
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center h-48 text-center text-gray-600 font-mono"
            >
              <span className="text-2xl mb-2" role="img" aria-label="lightning bolt">⚡</span>
              <p className="text-2xs uppercase tracking-widest font-bold">
                SYS STATUS: WAITING FOR ADVANCE
              </p>
              <p className="text-[10px] mt-1 text-gray-500">
                Advance the simulation phase index to load AI analytics.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-900 flex items-center justify-between text-2xs font-mono text-gray-500 select-none">
        <span className="flex items-center gap-1.5">
          <Terminal className="w-3.5 h-3.5 text-blue-500" />
          {lastUpdatedText}
        </span>
        <span>Telemetry online</span>
      </div>
    </motion.div>
  );
};
export default CommandPanel;
