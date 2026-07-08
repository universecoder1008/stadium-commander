import React, { useState, useEffect, useRef } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import StatusHeader from "../components/StatusHeader";
import CommandPanel from "../components/CommandPanel";
import StadiumMap from "../components/StadiumMap";
import AnalyzerGrid from "../components/AnalyzerGrid";
import Timeline from "../components/Timeline";
import type { ToastData } from "../types/api";

interface DashboardProps {
  sim: {
    status: {
      current_phase: string;
      phase_index: number;
      total_phases: number;
      latest_report: any;
    };
    decision: any;
    loading: boolean;
    error: string | null;
    isAutoSimulating: boolean;
    events: any[];
    toasts: ToastData[];
    fetchStatus: () => void;
    simulateTimeline: () => void;
    startSimulation: () => void;
    pauseSimulation: () => void;
    resetSimulation: () => void;
    dismissToast: (id: string) => void;
    latencyMs: number;
  };
}

interface PhaseMetadata {
  title: string;
  icon: string;
  subtitle: string;
  description: string;
}

const PHASE_DETAILS: Record<string, PhaseMetadata> = {
  "T-120": {
    title: "T-120",
    icon: "🟢",
    subtitle: "Stadium Opening",
    description: "Fans begin arriving at gates"
  },
  "T-90": {
    title: "T-90",
    icon: "🚇",
    subtitle: "Transport Surge",
    description: "Metro and transit traffic increasing"
  },
  "T-60": {
    title: "T-60",
    icon: "👥",
    subtitle: "Crowd Build-up",
    description: "Entry queues growing across outer zones"
  },
  "T-30": {
    title: "T-30",
    icon: "🚨",
    subtitle: "Security Peak",
    description: "High density crowd operations active"
  },
  "Kickoff": {
    title: "Kickoff",
    icon: "⚽",
    subtitle: "Match Started",
    description: "In-stadium operations stabilized"
  },
  "Halftime": {
    title: "Halftime",
    icon: "🍔",
    subtitle: "Concourse Surge",
    description: "High concession and restroom queue demand"
  },
  "Rain Event": {
    title: "Rain Event",
    icon: "🌧",
    subtitle: "Weather Alert",
    description: "Heavy rainfall detected\nVisibility reduced\nMedical demand increasing"
  },
  "Medical Incident": {
    title: "Medical Incident",
    icon: "🚑",
    subtitle: "Emergency Response",
    description: "Critical medical response resources engaged in sector"
  },
  "Full-time": {
    title: "Full-time",
    icon: "🚗",
    subtitle: "Exit Rush",
    description: "Mass spectator departure and egress flows active"
  }
};

export const Dashboard: React.FC<DashboardProps> = ({ sim }) => {
  const [activeOverlayPhase, setActiveOverlayPhase] = useState<string | null>(null);
  const prevPhase = useRef<string | null>(null);

  // Monitor phase changes to launch cinematic transition overlay
  useEffect(() => {
    const currentPhase = sim.status.current_phase;
    
    // Normalizing phase naming checks
    if (currentPhase && prevPhase.current && prevPhase.current !== currentPhase) {
      setActiveOverlayPhase(currentPhase);
      const timer = setTimeout(() => {
        setActiveOverlayPhase(null);
      }, 2800);
      return () => clearTimeout(timer);
    }
    
    if (currentPhase) {
      prevPhase.current = currentPhase;
    }
  }, [sim.status.current_phase]);

  return (
    <div className="space-y-6 relative">
      {/* Graceful error handling notice with Retry option */}
      {sim.error && (
        <div className="bg-rose-950/20 border border-rose-500/30 text-rose-300 p-4 rounded-xl flex items-center justify-between gap-3 text-xs font-mono animate-pulse">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-rose-500 shrink-0" />
            <span>ERROR: {sim.error}</span>
          </div>
          <button
            onClick={() => sim.fetchStatus()}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg transition-all active:scale-95 cursor-pointer font-bold uppercase tracking-wider font-mono focus:outline-none focus:ring-2 focus:ring-rose-500/50"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Link
          </button>
        </div>
      )}

      {/* 1. Status Header (Live Metrics) */}
      <StatusHeader
        report={sim.status.latest_report}
        isAutoSimulating={sim.isAutoSimulating}
        currentPhase={sim.status.current_phase}
        loading={sim.loading}
        error={sim.error}
        latencyMs={sim.latencyMs}
      />

      {/* 2. Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (Command Console - 35%) */}
        <div className="lg:col-span-4">
          <CommandPanel
            decision={sim.decision}
            report={sim.status.latest_report}
            onSimulate={sim.simulateTimeline}
            loading={sim.loading}
            isAutoSimulating={sim.isAutoSimulating}
            onStart={sim.startSimulation}
            onPause={sim.pauseSimulation}
            onReset={sim.resetSimulation}
            error={sim.error}
          />
        </div>

        {/* Right Column (Stadium Map - 65%) */}
        <div className="lg:col-span-8">
          <StadiumMap report={sim.status.latest_report} />
        </div>
      </div>

      {/* 3. Analyzer Grid */}
      <div className="pt-2">
        <div className="mb-4 select-none">
          <h2 className="text-xs font-black tracking-wider text-gray-200 uppercase font-mono">
            Operational Telemetry Analyzer Feeds
          </h2>
          <p className="text-[9px] text-gray-500 font-bold uppercase tracking-widest mt-0.5 font-mono">
            Realtime Sub-system Analyzer Status
          </p>
        </div>
        <AnalyzerGrid report={sim.status.latest_report} />
      </div>

      {/* 4. Timeline Log */}
      <Timeline events={sim.events} />

      {/* 5. Custom Toast notification overlay stack */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
        <AnimatePresence>
          {sim.toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 35, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.18 } }}
              className="pointer-events-auto bg-slate-900/95 backdrop-blur-md border border-gray-800 rounded-xl p-4 shadow-2xl flex items-center justify-between gap-3 text-xs font-mono select-none"
            >
              <div className="flex items-center gap-2">
                <span className={
                  toast.type === "success"
                    ? "text-emerald-500 font-bold"
                    : toast.type === "warning"
                    ? "text-amber-500 font-bold"
                    : toast.type === "error"
                    ? "text-rose-500 font-bold"
                    : "text-blue-500 font-bold"
                }>
                  {toast.type === "success" ? "✓" : toast.type === "warning" ? "⚠" : toast.type === "error" ? "✖" : "🤖"}
                </span>
                <span className={
                  toast.type === "success"
                    ? "text-emerald-300"
                    : toast.type === "warning"
                    ? "text-amber-300"
                    : toast.type === "error"
                    ? "text-rose-300"
                    : "text-blue-300"
                }>
                  {toast.message}
                </span>
              </div>
              <button
                onClick={() => sim.dismissToast(toast.id)}
                aria-label="Dismiss Notification"
                className="text-gray-500 hover:text-gray-300 transition-colors p-1 cursor-pointer shrink-0 focus:outline-none focus:ring-1 focus:ring-blue-500/50 rounded"
              >
                ✕
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* 6. Cinematic Phase Advanced Overlay */}
      <AnimatePresence>
        {activeOverlayPhase && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-gray-950/65 backdrop-blur-xs pointer-events-none"
          >
            {(() => {
              const details = PHASE_DETAILS[activeOverlayPhase] || {
                title: activeOverlayPhase,
                icon: "⚡",
                subtitle: "Operational Shift",
                description: "Stadium parameters updated"
              };
              return (
                <motion.div
                  initial={{ scale: 0.88, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.88, opacity: 0 }}
                  transition={{ type: "spring", stiffness: 240, damping: 24 }}
                  className="bg-slate-900/90 border border-gray-800 rounded-3xl p-8 max-w-md w-full shadow-2xl text-center backdrop-blur-md pointer-events-auto select-none mx-4"
                >
                  <p className="text-[10px] text-blue-400 font-black uppercase tracking-widest font-mono">
                    ⚡ MATCH PHASE ADVANCED
                  </p>
                  
                  <div className="my-6">
                    <motion.div
                      animate={{ scale: [1, 1.12, 1] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                      className="text-5xl mb-4"
                    >
                      {details.icon}
                    </motion.div>
                    <h2 className="text-3xl font-black text-white font-mono uppercase tracking-wider">
                      {details.title}
                    </h2>
                    <p className="text-sm font-bold text-gray-300 font-mono mt-1 uppercase tracking-wide">
                      {details.subtitle}
                    </p>
                  </div>
                  
                  <div className="border-t border-gray-800/80 pt-4 mt-4">
                    <p className="text-2xs font-mono text-gray-400 font-semibold leading-relaxed whitespace-pre-wrap">
                      {details.description}
                    </p>
                  </div>
                </motion.div>
              );
            })()}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
export default Dashboard;
