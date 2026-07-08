import React, { useState, useEffect } from "react";
import type { CombinedSituationReport } from "../types/api";
import AnimatedCounter from "./AnimatedCounter";

interface StatusHeaderProps {
  report: CombinedSituationReport | null;
  isAutoSimulating: boolean;
  currentPhase: string;
  loading: boolean;
  error: string | null;
  latencyMs: number;
}

export const StatusHeader: React.FC<StatusHeaderProps> = React.memo(({
  report,
  isAutoSimulating,
  currentPhase,
  loading,
  error,
  latencyMs
}) => {
  const [updatedTime, setUpdatedTime] = useState("--:--:--");

  // Refresh timestamp whenever new telemetry report arrives
  useEffect(() => {
    if (report) {
      const now = new Date();
      setUpdatedTime(now.toLocaleTimeString([], { hour12: false }));
    }
  }, [report]);

  // Determine Gemini AI Status
  const getAiStatus = () => {
    if (loading) {
      return (
        <span className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-xs">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75 animate-ping"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          <span className="text-blue-400">Thinking</span>
        </span>
      );
    }
    if (error) {
      return (
        <span className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-xs">
          <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
          <span className="text-rose-450">Unavailable</span>
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-xs">
        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        <span className="text-emerald-400">Connected</span>
      </span>
    );
  };

  // Determine Global System Status
  const getSystemStatus = () => {
    if (!report) return { text: "OFFLINE", colorClass: "text-gray-500 border-gray-800 bg-gray-950/30" };

    const failedCount = Object.keys(report.analyzers_failed).length;
    if (failedCount > 0) {
      return { text: "CRITICAL", colorClass: "text-rose-400 border-rose-500/20 bg-rose-950/20" };
    }

    const crowdRisk = report.crowd?.risk;
    const transportRisk = report.transport?.risk;
    const medicalRisk = report.medical?.risk;
    const volunteerRisk = report.volunteer?.risk;
    const weatherRisk = report.weather?.risk;

    const risks = [crowdRisk, transportRisk, medicalRisk, volunteerRisk, weatherRisk];
    if (risks.includes("HIGH") || risks.includes("CRITICAL")) {
      return { text: "CRITICAL", colorClass: "text-rose-400 border-rose-500/20 bg-rose-950/20" };
    }
    if (risks.includes("MEDIUM") || risks.includes("WARNING")) {
      return { text: "WARNING", colorClass: "text-amber-400 border-amber-500/20 bg-amber-950/20" };
    }
    return { text: "NORMAL", colorClass: "text-emerald-400 border-emerald-500/20 bg-emerald-950/20" };
  };

  const sysStatus = getSystemStatus();

  return (
    <div
      role="status"
      aria-label="Live Stadium Operations System Status Bar"
      tabIndex={0}
      className="bg-slate-900 border border-gray-800 rounded-xl p-4 flex flex-col md:grid md:grid-cols-7 items-center justify-between gap-4 md:gap-2 shadow-2xl font-mono text-xs select-none text-gray-300 divide-y md:divide-y-0 md:divide-x divide-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
    >
      {/* 1. Live Indicator (Gentle pulse every 2s) */}
      <div className="flex items-center gap-2 justify-center w-full md:pr-4">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 duration-[2000ms]"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
        </span>
        <span className="text-white font-black tracking-widest text-[13px]">
          LIVE
        </span>
      </div>

      {/* 2. Match Phase */}
      <div className="flex flex-col items-center md:items-start justify-center w-full pt-3 md:pt-0 md:px-4">
        <span className="text-[8px] text-gray-500 font-bold uppercase tracking-wider">
          Phase
        </span>
        <span className="text-gray-200 font-black tracking-wide truncate max-w-[120px] mt-0.5" title={currentPhase}>
          {currentPhase || "Awaiting Data"}
        </span>
      </div>

      {/* 3. System Status (Smooth colors change) */}
      <div className="flex flex-col items-center md:items-start justify-center w-full pt-3 md:pt-0 md:px-4">
        <span className="text-[8px] text-gray-500 font-bold uppercase tracking-wider">
          Status
        </span>
        <span className={`text-3xs px-2 py-0.5 border rounded-md font-black tracking-widest mt-1.5 transition-colors duration-500 ${sysStatus.colorClass}`}>
          {sysStatus.text}
        </span>
      </div>

      {/* 4. Last Updated */}
      <div className="flex flex-col items-center md:items-start justify-center w-full pt-3 md:pt-0 md:px-4">
        <span className="text-[8px] text-gray-500 font-bold uppercase tracking-wider">
          Updated
        </span>
        <span className="text-gray-300 font-black tracking-wide mt-0.5">
          {updatedTime}
        </span>
      </div>

      {/* 5. Latency (Animated counters) */}
      <div className="flex flex-col items-center md:items-start justify-center w-full pt-3 md:pt-0 md:px-4">
        <span className="text-[8px] text-gray-500 font-bold uppercase tracking-wider">
          Latency
        </span>
        <span className="text-gray-300 font-black tracking-wide mt-0.5">
          <AnimatedCounter value={latencyMs} /> ms
        </span>
      </div>

      {/* 6. AI Connection Status */}
      <div className="flex flex-col items-center md:items-start justify-center w-full pt-3 md:pt-0 md:px-4">
        <span className="text-[8px] text-gray-500 font-bold uppercase tracking-wider">
          AI Status
        </span>
        <div className="mt-1">
          {getAiStatus()}
        </div>
      </div>

      {/* 7. Simulation Mode Speed */}
      <div className="flex flex-col items-center md:items-start justify-center w-full pt-3 md:pt-0 md:pl-4">
        <span className="text-[8px] text-gray-500 font-bold uppercase tracking-wider">
          Simulation
        </span>
        <span className="text-gray-350 font-black tracking-wide mt-0.5">
          {isAutoSimulating ? "Realtime" : "Manual Step"}
        </span>
      </div>
    </div>
  );
});

export default StatusHeader;
