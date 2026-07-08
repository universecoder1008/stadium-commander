import React from "react";
import { Users, Bus, HeartPulse, CloudRain, UserCheck, AlertTriangle } from "lucide-react";
import type { CombinedSituationReport } from "../types/api";
import RiskBadge from "./RiskBadge";

interface AnalyzerGridProps {
  report: CombinedSituationReport | null;
}

export const AnalyzerGrid: React.FC<AnalyzerGridProps> = ({ report }) => {
  if (!report) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {[1, 2, 3, 4, 5].map((idx) => (
          <div
            key={idx}
            className="bg-gray-900/40 border border-gray-800 rounded-xl p-5 h-[240px] flex flex-col items-center justify-center text-center animate-pulse"
          >
            <div className="text-gray-700 font-mono text-2xs uppercase tracking-widest">
              Telemetry Offline
            </div>
          </div>
        ))}
      </div>
    );
  }

  const { crowd, transport, medical, weather, volunteer, analyzers_failed } = report;

  const analyzers = [
    {
      key: "crowd",
      name: "Crowd Analyzer",
      data: crowd,
      icon: <Users className="w-5 h-5 text-blue-400" />,
      desc: crowd?.predictions?.[0]?.issue || "All gates stable",
      metrics: [
        { label: "Active Issues", value: `${crowd?.predictions?.length || 0} alerts` },
        { label: "Confidence", value: crowd ? `${(crowd.confidence).toFixed(0)}%` : "--" }
      ]
    },
    {
      key: "transport",
      name: "Transport Analyzer",
      data: transport,
      icon: <Bus className="w-5 h-5 text-indigo-400" />,
      desc: transport?.bus_status === "HIGH" || transport?.metro_status === "HIGH" ? "Delays reported" : "Transit grid stable",
      metrics: [
        { label: "Metro Link", value: transport ? transport.metro_status : "--" },
        { label: "Parking Space", value: transport ? `${transport.parking_occupancy_percent.toFixed(0)}%` : "--" }
      ]
    },
    {
      key: "medical",
      name: "Medical Analyzer",
      data: medical,
      icon: <HeartPulse className="w-5 h-5 text-rose-400" />,
      desc: medical?.prediction.resource_shortage ? "Resource shortage" : "First aid stable",
      metrics: [
        { label: "Ambulance Util", value: medical ? `${medical.ambulance_utilization_percent.toFixed(0)}%` : "--" },
        { label: "Response Time", value: medical ? `${medical.prediction.estimated_response_time.toFixed(1)}m` : "--" }
      ]
    },
    {
      key: "weather",
      name: "Weather Analyzer",
      data: weather,
      icon: <CloudRain className="w-5 h-5 text-amber-400" />,
      desc: weather?.prediction.expected_operational_impact || "Normal conditions",
      metrics: [
        { label: "Weather status", value: weather ? weather.weather_status : "--" },
        { label: "Delays predicted", value: weather ? `${weather.prediction.expected_delay_minutes}m` : "--" }
      ]
    },
    {
      key: "volunteer",
      name: "Volunteer Analyzer",
      data: volunteer,
      icon: <UserCheck className="w-5 h-5 text-emerald-400" />,
      desc: volunteer?.prediction.recommended_redeployment !== "None" ? "Redeployment advised" : "Coverage stable",
      metrics: [
        { label: "HQ Utilization", value: volunteer ? `${volunteer.volunteer_utilization_percent.toFixed(0)}%` : "--" },
        { label: "Zone Coverage", value: volunteer ? `${volunteer.coverage_percent.toFixed(0)}%` : "--" }
      ]
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
      {analyzers.map((a) => {
        const failureMessage = analyzers_failed[a.key];

        return (
          <div
            key={a.key}
            className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 hover:border-blue-500/20 hover:shadow-lg transition-all duration-300 flex flex-col justify-between h-[240px]"
          >
            <div>
              <div className="flex items-center justify-between">
                <div className="p-2 bg-gray-950 rounded-lg border border-gray-800 text-gray-400">
                  {a.icon}
                </div>
                {failureMessage ? (
                  <span className="text-[8px] font-black px-2 py-0.5 rounded border border-rose-500/20 bg-rose-950/20 text-rose-400 font-mono">
                    FAILED
                  </span>
                ) : (
                  <RiskBadge risk={(a.data?.risk as "LOW" | "MEDIUM" | "HIGH") || "LOW"} />
                )}
              </div>

              <h3 className="text-xs font-black tracking-wider text-gray-200 mt-4 uppercase font-mono">
                {a.name}
              </h3>

              {failureMessage ? (
                <div className="mt-2 flex items-start gap-1 p-2 bg-rose-950/10 border border-rose-500/20 text-rose-400 rounded-lg text-[9px] font-mono leading-normal select-all">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  <span className="line-clamp-3">{failureMessage}</span>
                </div>
              ) : (
                <p className="text-[10px] text-gray-500 mt-1 leading-normal font-semibold select-text">
                  {a.desc}
                </p>
              )}
            </div>

            {!failureMessage && (
              <div className="border-t border-gray-850 pt-3 space-y-1.5 text-3xs font-mono select-text">
                {a.metrics.map((m, mIdx) => (
                  <div key={mIdx} className="flex justify-between">
                    <span className="text-gray-500 uppercase font-bold tracking-wider">
                      {m.label}:
                    </span>
                    <span className="text-gray-300 font-bold">{m.value}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
export default AnalyzerGrid;
