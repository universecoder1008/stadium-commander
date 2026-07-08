import React, { useState, useMemo, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Info, X, MapPin } from "lucide-react";
import StadiumZone from "./StadiumZone";
import type { RiskLevel } from "./StadiumZone";
import Legend from "./Legend";
import type { CombinedSituationReport } from "../types/api";
import AnimatedCounter from "./AnimatedCounter";

interface StadiumMapProps {
  report: CombinedSituationReport | null;
}

interface ZoneDetails {
  name: string;
  volunteers: number;
  positionClass: string;
}

const ZONE_STATIC_METADATA: Record<string, ZoneDetails> = {
  "Gate A": { name: "Gate A", volunteers: 8, positionClass: "top-[16%] left-[16%]" },
  "Gate B": { name: "Gate B", volunteers: 4, positionClass: "top-[16%] right-[16%]" },
  "Gate C": { name: "Gate C", volunteers: 6, positionClass: "bottom-[16%] left-[16%]" },
  "Gate D": { name: "Gate D", volunteers: 6, positionClass: "bottom-[16%] right-[16%]" },
  "Parking": { name: "Parking", volunteers: 2, positionClass: "top-[38%] left-[4%]" },
  "Metro": { name: "Metro", volunteers: 4, positionClass: "bottom-[38%] left-[4%]" },
  "Food Court": { name: "Food Court", volunteers: 3, positionClass: "top-[38%] right-[4%]" },
  "Medical Center": { name: "Medical Center", volunteers: 5, positionClass: "bottom-[38%] right-[4%]" },
  "VIP Entrance": { name: "VIP Entrance", volunteers: 3, positionClass: "top-[5%] left-[50%] -translate-x-1/2" },
  "Broadcast Area": { name: "Broadcast Area", volunteers: 0, positionClass: "bottom-[5%] left-[50%] -translate-x-1/2" },
  "Volunteer HQ": { name: "Volunteer HQ", volunteers: 12, positionClass: "top-[50%] left-[50%] -translate-x-1/2 -translate-y-1/2 bg-slate-950/80 border-dashed border-gray-700 hover:border-gray-500" }
};

interface ZoneData {
  analyzerName: string;
  risk: RiskLevel;
  confidence: number;
  reasoning: string[];
  recommendation: string;
  issue: string;
  matchPhase: string;
}

export const StadiumMap: React.FC<StadiumMapProps> = ({ report }) => {
  const [selectedZoneName, setSelectedZoneName] = useState<string | null>(null);
  const [hoveredZoneName, setHoveredZoneName] = useState<string | null>(null);

  // Close drawer tooltip with Escape key for accessibility
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setSelectedZoneName(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Map zone names dynamically to backend sensors
  const getZoneData = useCallback((zoneName: string): ZoneData | null => {
    if (!report) return null;

    let analyzerName = "";
    let risk: RiskLevel = "UNKNOWN";
    let confidence = 0;
    let reasoning: string[] = [];
    let recommendation = "Monitor operational status.";
    let issue = "Normal operations.";

    switch (zoneName) {
      case "Gate A":
      case "Gate B":
      case "Gate C":
      case "Gate D":
      case "VIP Entrance":
      case "Food Court":
        analyzerName = "Crowd Analyzer";
        if (report.crowd) {
          risk = (report.crowd.risk as RiskLevel) || "LOW";
          confidence = report.crowd.confidence > 1.0 ? report.crowd.confidence / 100 : report.crowd.confidence;
          reasoning = report.crowd.reasoning;
          if (report.crowd.predictions?.length > 0) {
            const pred = report.crowd.predictions[0];
            issue = pred.issue || "High ingress volume";
            recommendation = `Manage gate scanners. ETA: ${pred.eta_minutes}m.`;
          }
        }
        break;

      case "Parking":
      case "Metro":
        analyzerName = "Transport Analyzer";
        if (report.transport) {
          risk = (report.transport.risk as RiskLevel) || "LOW";
          confidence = report.transport.confidence;
          reasoning = report.transport.reasoning;
          issue = zoneName === "Parking"
            ? `Parking occupancy: ${report.transport.parking_occupancy_percent.toFixed(0)}%`
            : `Metro Status: ${report.transport.metro_status === "HIGH" ? "Delays reported" : "Stable link"}`;
          recommendation = `Redirect arrival flows. Metro ETA: ${report.transport.arrival_prediction.estimated_arrival_minutes}m.`;
        }
        break;

      case "Medical Center":
        analyzerName = "Medical Analyzer";
        if (report.medical) {
          risk = (report.medical.risk as RiskLevel) || "LOW";
          confidence = report.medical.confidence;
          reasoning = report.medical.reasoning;
          issue = report.medical.prediction.resource_shortage
            ? "Ambulance/paramedic resource shortage flagged!"
            : `Ambulance utilization: ${report.medical.ambulance_utilization_percent.toFixed(0)}%`;
          recommendation = `Request paramedic backup. Response ETA: ${report.medical.prediction.estimated_response_time.toFixed(1)}m.`;
        }
        break;

      case "Volunteer HQ":
        analyzerName = "Volunteer Analyzer";
        if (report.volunteer) {
          risk = (report.volunteer.risk as RiskLevel) || "LOW";
          confidence = report.volunteer.confidence;
          reasoning = report.volunteer.reasoning;
          issue = `Volunteers utilized: ${report.volunteer.volunteer_utilization_percent.toFixed(0)}%. Coverage: ${report.volunteer.coverage_percent.toFixed(0)}%`;
          recommendation = report.volunteer.prediction.recommended_redeployment || "No redeployments advised.";
        }
        break;

      case "Broadcast Area":
        analyzerName = "Weather Analyzer";
        if (report.weather) {
          risk = (report.weather.risk as RiskLevel) || "LOW";
          confidence = report.weather.confidence;
          reasoning = report.weather.reasoning;
          issue = `Weather Status: ${report.weather.weather_status}`;
          recommendation = report.weather.prediction.recommendation || "Maintain watch.";
        }
        break;
    }

    return {
      analyzerName,
      risk,
      confidence,
      reasoning,
      recommendation,
      issue,
      matchPhase: report.match_phase
    };
  }, [report]);

  const getRiskForZone = useCallback((name: string): RiskLevel => {
    const data = getZoneData(name);
    return data ? data.risk : "UNKNOWN";
  }, [getZoneData]);

  const getStatusForZone = useCallback((name: string): string => {
    const data = getZoneData(name);
    if (!data) return "Offline";
    return data.risk === "UNKNOWN" ? "Offline" : data.issue;
  }, [getZoneData]);

  const getRiskColor = (risk: RiskLevel) => {
    switch (risk) {
      case "HIGH":
        return "text-rose-400 bg-rose-950/20 border-rose-500/20";
      case "MEDIUM":
        return "text-amber-400 bg-amber-950/20 border-amber-500/20";
      case "LOW":
        return "text-emerald-400 bg-emerald-950/20 border-emerald-500/20";
      default:
        return "text-gray-400 bg-gray-900 border-gray-800";
    }
  };

  const selectedZone = selectedZoneName ? ZONE_STATIC_METADATA[selectedZoneName] : null;

  // Memoize counts of risks in the map zone datasets
  const counts = useMemo(() => {
    let low = 0;
    let medium = 0;
    let high = 0;
    let unknown = 0;

    Object.keys(ZONE_STATIC_METADATA).forEach((name) => {
      const risk = getRiskForZone(name);
      if (risk === "LOW") low++;
      else if (risk === "MEDIUM") medium++;
      else if (risk === "HIGH") high++;
      else unknown++;
    });

    return { low, medium, high, unknown };
  }, [getRiskForZone]);

  return (
    <div className="bg-slate-900 border border-gray-800 rounded-2xl p-5 relative overflow-hidden h-[400px] flex flex-col justify-between group hover:border-blue-500/20 transition-all duration-300">
      <div className="flex items-center justify-between z-10 select-none">
        <div>
          <h2 className="text-sm font-black tracking-wider text-gray-200 uppercase font-mono flex items-center gap-1.5">
            <span>🏟</span> Stadium Operations Map
          </h2>
          <p className="text-[9px] text-gray-500 font-bold uppercase tracking-widest mt-0.5 font-mono">
            Mission Control Tactical Visual Overlay
          </p>
        </div>
        <Legend
          lowCount={counts.low}
          mediumCount={counts.medium}
          highCount={counts.high}
          unknownCount={counts.unknown}
        />
      </div>

      {/* Stadium Oval Graphic Container */}
      <div className="absolute inset-0 flex items-center justify-center p-8 mt-6">
        <svg viewBox="0 0 400 300" className="w-full max-w-[280px] h-auto opacity-20 pointer-events-none">
          <ellipse
            cx="200"
            cy="150"
            rx="180"
            ry="110"
            className="fill-none stroke-gray-800 stroke-[1.5]"
            strokeDasharray="6,4"
          />
          <ellipse
            cx="200"
            cy="150"
            rx="120"
            ry="75"
            className="fill-none stroke-gray-800 stroke-[1]"
          />
          <ellipse
            cx="200"
            cy="150"
            rx="60"
            ry="38"
            className="fill-none stroke-gray-800 stroke-[1]"
          />
        </svg>

        {/* Map Zone Nodes */}
        <motion.div
          initial="hidden"
          animate="visible"
          variants={{
            hidden: {},
            visible: { transition: { staggerChildren: 0.05 } }
          }}
          className="absolute inset-0 w-full h-full"
        >
          {Object.entries(ZONE_STATIC_METADATA).map(([name, zone]) => {
            const risk = getRiskForZone(name);
            const status = getStatusForZone(name);

            return (
              <StadiumZone
                key={name}
                name={name}
                risk={risk}
                status={status}
                onClick={() => setSelectedZoneName(name)}
                onMouseEnter={() => setHoveredZoneName(name)}
                onMouseLeave={() => setHoveredZoneName(null)}
                isSelected={selectedZoneName === name}
                positionClass={zone.positionClass}
              />
            );
          })}
        </motion.div>
      </div>

      {/* Dynamic Hover Tooltip Card */}
      <AnimatePresence>
        {hoveredZoneName && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute bottom-4 left-4 z-20 max-w-xs w-[240px] bg-slate-950/95 backdrop-blur-md border border-gray-800 rounded-xl p-3.5 shadow-2xl font-mono text-2xs text-gray-300 pointer-events-none select-none"
          >
            {(() => {
              const info = getZoneData(hoveredZoneName);
              if (!info) return null;
              return (
                <div className="space-y-2">
                  <div className="flex items-center justify-between border-b border-gray-850 pb-1.5">
                    <span className="text-white font-black text-2xs uppercase">{hoveredZoneName}</span>
                    <span className="text-blue-500 font-bold uppercase text-[7px]">{info.analyzerName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 font-bold uppercase">Risk Status:</span>
                    <span className={
                      info.risk === "HIGH"
                        ? "text-rose-400 font-bold animate-pulse"
                        : info.risk === "MEDIUM"
                        ? "text-amber-400 font-bold"
                        : "text-emerald-400 font-bold"
                    }>{info.risk}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 font-bold uppercase">Active Phase:</span>
                    <span className="text-gray-300 font-bold uppercase">{info.matchPhase}</span>
                  </div>
                  <div className="border-t border-gray-850 pt-2 space-y-1">
                    <span className="text-blue-400 font-bold uppercase text-[8px]">Latest Recommendation:</span>
                    <p className="text-gray-400 font-semibold leading-normal break-words text-[9px] line-clamp-2">
                      {info.recommendation}
                    </p>
                  </div>
                </div>
              );
            })()}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Slide-out details drawer overlay */}
      <AnimatePresence>
        {selectedZone && selectedZoneName && (
          <motion.div
            initial={{ opacity: 0, x: 60 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 60 }}
            transition={{ type: "spring", stiffness: 280, damping: 26 }}
            className="absolute top-0 right-0 w-[260px] h-full bg-slate-950/95 backdrop-blur-md border-l border-gray-800 p-5 z-30 flex flex-col justify-between shadow-2xl font-mono text-xs text-gray-300"
          >
            <div className="space-y-4 flex-1 flex flex-col justify-start">
              {/* Drawer Header */}
              <div className="flex items-center justify-between border-b border-gray-850 pb-2.5">
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-blue-500" />
                  Tactical Feeds:
                </span>
                <button
                  onClick={() => setSelectedZoneName(null)}
                  aria-label="Close details drawer"
                  className="p-1 hover:bg-gray-900 rounded-lg text-gray-500 hover:text-gray-300 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {(() => {
                const info = getZoneData(selectedZoneName);
                if (!info) return null;

                return (
                  <div className="space-y-4 flex-1 flex flex-col justify-start">
                    {/* Title & Status */}
                    <div>
                      <h3 className="text-sm font-black text-white uppercase tracking-wider leading-none select-all">
                        {selectedZoneName}
                      </h3>
                      <span
                        className={`mt-2.5 px-2.5 py-0.5 rounded border text-[9px] font-black uppercase inline-flex items-center ${getRiskColor(
                          info.risk
                        )}`}
                      >
                        {info.risk} RISK
                      </span>
                    </div>

                    {/* Confidence Rating */}
                    <div className="flex items-center gap-2 text-2xs text-gray-400 bg-gray-905 border border-gray-850 px-3 py-2 rounded-xl select-all">
                      <span>AI Confidence: <b><AnimatedCounter value={info.confidence * 100} />%</b></span>
                    </div>

                    {/* Active Issue */}
                    <div className="space-y-1">
                      <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider">
                        Telemetry Signals:
                      </span>
                      <p className="text-2xs text-gray-200 bg-slate-905 p-2.5 rounded-lg border border-gray-850 leading-relaxed select-all">
                        {info.issue}
                      </p>
                    </div>

                    {/* Action plan */}
                    <div className="space-y-1">
                      <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider flex items-center gap-1">
                        <Info className="w-3.5 h-3.5 text-blue-400" />
                        AI Action Directive:
                      </span>
                      <p className="text-2xs text-blue-400 leading-normal pl-1 select-all font-bold">
                        {info.recommendation}
                      </p>
                    </div>

                    {/* Decision Reasoning List */}
                    <div className="space-y-1.5 flex-1 overflow-y-auto max-h-[160px] scrollbar-thin">
                      <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider block">
                        Decision Reasoning:
                      </span>
                      <ul className="space-y-1.5 pl-1 select-text">
                        {info.reasoning.length > 0 ? (
                          info.reasoning.map((reason, idx) => (
                            <li key={idx} className="text-[10px] text-gray-400 list-disc list-inside leading-snug">
                              {reason}
                            </li>
                          ))
                        ) : (
                          <li className="text-[10px] text-gray-500 italic">No reasoning logs found.</li>
                        )}
                      </ul>
                    </div>
                  </div>
                );
              })()}
            </div>

            {/* Close instruction */}
            <div className="text-[9px] text-gray-600 font-bold text-center uppercase tracking-widest pt-2 border-t border-gray-900 select-none">
              SYS STATUS: SECURE NETWORK
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="z-10 text-[9px] text-gray-600 font-mono font-bold pt-2 border-t border-gray-900 select-none">
        MAP RADAR ACTIVE. CLICK ON ZONE NODES FOR DETAILED SIGNALS.
      </div>
    </div>
  );
};
export default StadiumMap;
