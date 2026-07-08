import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import StatusHeader from "../components/StatusHeader";
import CommandPanel from "../components/CommandPanel";
import StadiumMap from "../components/StadiumMap";
import AnalyzerGrid from "../components/AnalyzerGrid";
import Timeline from "../components/Timeline";

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
    toast: { message: string; type: "error" | "success" } | null;
    fetchStatus: () => void;
    simulateTimeline: () => void;
    startSimulation: () => void;
    pauseSimulation: () => void;
    resetSimulation: () => void;
    dismissToast: () => void;
  };
}

export const Dashboard: React.FC<DashboardProps> = ({ sim }) => {
  return (
    <div className="space-y-6">
      {/* Graceful error handling notice with Retry option */}
      {sim.error && (
        <div className="bg-rose-950/20 border border-rose-500/30 text-rose-300 p-4 rounded-xl flex items-center justify-between gap-3 text-xs font-mono">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-rose-500 shrink-0" />
            <span>ERROR: {sim.error}</span>
          </div>
          <button
            onClick={() => sim.fetchStatus()}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg transition-all active:scale-95 cursor-pointer font-bold uppercase tracking-wider"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Link
          </button>
        </div>
      )}

      {/* 1. Status Header (Live Metrics) */}
      <StatusHeader report={sim.status.latest_report} decision={sim.decision} />

      {/* 2. Main Content Grid (Left 35% Command Console, Right 65% Tactical Map) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (Command Console - 35%) */}
        <div className="lg:col-span-4">
          <CommandPanel
            decision={sim.decision}
            onSimulate={sim.simulateTimeline}
            loading={sim.loading}
            isAutoSimulating={sim.isAutoSimulating}
            onStart={sim.startSimulation}
            onPause={sim.pauseSimulation}
            onReset={sim.resetSimulation}
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
          <p className="text-[9px] text-gray-500 font-bold uppercase tracking-widest mt-0.5">
            Realtime Sub-system Analyzer Status
          </p>
        </div>
        <AnalyzerGrid report={sim.status.latest_report} />
      </div>

      {/* 4. Timeline Log */}
      <Timeline events={sim.events} />

      {/* 5. Custom Toast notification overlay */}
      {sim.toast && (
        <div className="fixed bottom-6 right-6 z-50 max-w-sm bg-slate-900 border border-gray-800 rounded-xl p-4 shadow-2xl flex items-center justify-between gap-3 text-xs font-mono select-none animate-in slide-in-from-bottom duration-300">
          <div className="flex items-center gap-2">
            <span className={sim.toast.type === "success" ? "text-emerald-500 font-bold" : "text-rose-500 font-bold"}>
              {sim.toast.type === "success" ? "✓" : "⚠"}
            </span>
            <span className={sim.toast.type === "success" ? "text-emerald-300" : "text-rose-300"}>
              {sim.toast.message}
            </span>
          </div>
          <button
            onClick={() => sim.dismissToast()}
            className="text-gray-500 hover:text-gray-300 transition-colors p-1 cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
};
export default Dashboard;
