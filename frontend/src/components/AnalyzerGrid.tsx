import React from "react";
import { motion } from "framer-motion";
import { Users, Bus, HeartPulse, CloudRain, UserCheck, AlertTriangle } from "lucide-react";
import type { CombinedSituationReport } from "../types/api";
import RiskBadge from "./RiskBadge";
import AnimatedCounter from "./AnimatedCounter";

interface AnalyzerGridProps {
  report: CombinedSituationReport | null;
}

interface MetricItem {
  label: string;
  num?: number | null;
  suffix?: string;
  valueStr?: string;
  isFloat?: boolean;
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
        { label: "Active Issues", num: crowd?.predictions?.length || 0, suffix: " alerts" },
        { label: "Confidence", num: crowd ? crowd.confidence : null, suffix: "%" }
      ]
    },
    {
      key: "transport",
      name: "Transport Analyzer",
      data: transport,
      icon: <Bus className="w-5 h-5 text-indigo-400" />,
      desc: transport?.bus_status === "HIGH" || transport?.metro_status === "HIGH" ? "Delays reported" : "Transit grid stable",
      metrics: [
        { label: "Metro Link", valueStr: transport ? transport.metro_status : "--" },
        { label: "Parking Space", num: transport ? transport.parking_occupancy_percent : null, suffix: "%" }
      ]
    },
    {
      key: "medical",
      name: "Medical Analyzer",
      data: medical,
      icon: <HeartPulse className="w-5 h-5 text-rose-400" />,
      desc: medical?.prediction.resource_shortage ? "Resource shortage" : "First aid stable",
      metrics: [
        { label: "Ambulance Util", num: medical ? medical.ambulance_utilization_percent : null, suffix: "%" },
        { label: "Response Time", num: medical ? medical.prediction.estimated_response_time : null, suffix: "m", isFloat: true }
      ]
    },
    {
      key: "weather",
      name: "Weather Analyzer",
      data: weather,
      icon: <CloudRain className="w-5 h-5 text-amber-400" />,
      desc: weather?.prediction.expected_operational_impact || "Normal conditions",
      metrics: [
        { label: "Weather status", valueStr: weather ? weather.weather_status : "--" },
        { label: "Delays predicted", num: weather ? weather.prediction.expected_delay_minutes : null, suffix: "m" }
      ]
    },
    {
      key: "volunteer",
      name: "Volunteer Analyzer",
      data: volunteer,
      icon: <UserCheck className="w-5 h-5 text-emerald-400" />,
      desc: volunteer?.prediction.recommended_redeployment !== "None" ? "Redeployment advised" : "Coverage stable",
      metrics: [
        { label: "HQ Utilization", num: volunteer ? volunteer.volunteer_utilization_percent : null, suffix: "%" },
        { label: "Zone Coverage", num: volunteer ? volunteer.coverage_percent : null, suffix: "%" }
      ]
    }
  ];

  const getRiskPulseAnimation = (risk: string | undefined): any => {
    const r = (risk || "LOW").toUpperCase();
    if (r === "HIGH" || r === "CRITICAL") {
      return {
        boxShadow: [
          "0 0 0 0px rgba(239, 68, 68, 0.15)",
          "0 0 0 8px rgba(239, 68, 68, 0)",
          "0 0 0 0px rgba(239, 68, 68, 0.15)"
        ],
        borderColor: [
          "rgba(239, 68, 68, 0.2)",
          "rgba(239, 68, 68, 0.4)",
          "rgba(239, 68, 68, 0.2)"
        ],
        transition: {
          duration: 2.0,
          repeat: Infinity,
          ease: "easeInOut"
        }
      };
    }
    if (r === "MEDIUM" || r === "WARNING") {
      return {
        boxShadow: [
          "0 0 0 0px rgba(245, 158, 11, 0.1)",
          "0 0 0 6px rgba(245, 158, 11, 0)",
          "0 0 0 0px rgba(245, 158, 11, 0.1)"
        ],
        borderColor: [
          "rgba(245, 158, 11, 0.2)",
          "rgba(245, 158, 11, 0.35)",
          "rgba(245, 158, 11, 0.2)"
        ],
        transition: {
          duration: 2.8,
          repeat: Infinity,
          ease: "easeInOut"
        }
      };
    }
    return {};
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
      {analyzers.map((a) => {
        const failureMessage = analyzers_failed[a.key];
        const risk = a.data?.risk;

        return (
          <motion.div
            key={a.key}
            animate={failureMessage ? {} : getRiskPulseAnimation(risk)}
            whileHover={{
              y: -6,
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4)",
              borderColor: "rgba(59, 130, 246, 0.45)",
            }}
            tabIndex={0}
            aria-label={`${a.name}, status: ${failureMessage ? "failed" : risk || "unknown"}`}
            className="bg-slate-900/65 border border-gray-800 rounded-xl p-5 hover:shadow-2xl transition-colors duration-300 flex flex-col justify-between h-[240px] focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          >
            <div>
              <div className="flex items-center justify-between select-none">
                <div className="p-2 bg-gray-950 rounded-lg border border-gray-800 text-gray-400">
                  {a.icon}
                </div>
                {failureMessage ? (
                  <span className="text-[8px] font-black px-2 py-0.5 rounded border border-rose-500/20 bg-rose-950/20 text-rose-400 font-mono">
                    FAILED
                  </span>
                ) : (
                  <RiskBadge risk={(risk as "LOW" | "MEDIUM" | "HIGH") || "LOW"} />
                )}
              </div>

              <h3 className="text-xs font-black tracking-wider text-gray-200 mt-4 uppercase font-mono select-none">
                {a.name}
              </h3>

              {failureMessage ? (
                <div className="mt-2 flex items-start gap-1 p-2 bg-rose-950/10 border border-rose-500/20 text-rose-400 rounded-lg text-[9px] font-mono leading-normal select-all">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  <span className="line-clamp-3">{failureMessage}</span>
                </div>
              ) : (
                <p className="text-[10px] text-gray-400 mt-1 leading-normal font-semibold select-text">
                  {a.desc}
                </p>
              )}
            </div>

            {!failureMessage && (
              <div className="border-t border-gray-850 pt-3 space-y-1.5 text-3xs font-mono select-text">
                {a.metrics.map((m: MetricItem, mIdx) => (
                  <div key={mIdx} className="flex justify-between">
                    <span className="text-gray-500 uppercase font-bold tracking-wider">
                      {m.label}:
                    </span>
                    <span className="text-gray-300 font-bold">
                      {m.valueStr !== undefined ? (
                        m.valueStr
                      ) : m.num !== null && m.num !== undefined ? (
                        <>
                          <AnimatedCounter
                            value={m.num}
                            formatter={(val) => m.isFloat ? val.toFixed(1) : String(Math.round(val))}
                          />
                          {m.suffix}
                        </>
                      ) : (
                        "--"
                      )}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
};
export default AnalyzerGrid;
