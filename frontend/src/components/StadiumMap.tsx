import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Users, Info, X, MapPin } from "lucide-react";
import StadiumZone from "./StadiumZone";
import type { RiskLevel } from "./StadiumZone";
import Legend from "./Legend";
import type { CombinedSituationReport } from "../types/api";

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

export const StadiumMap: React.FC<StadiumMapProps> = ({ report }) => {
  const [selectedZoneName, setSelectedZoneName] = useState<string | null>(null);

  const getRiskForZone = (name: string): RiskLevel => {
    if (!report) return "UNKNOWN";
    switch (name) {
      case "Gate A":
      case "Gate C":
      case "Gate D":
        return (report.crowd?.risk as RiskLevel) || "LOW";
      case "Gate B":
        return (report.crowd?.risk as RiskLevel) || "LOW";
      case "Parking":
        return (report.transport?.risk as RiskLevel) || "LOW";
      case "Metro":
        return (report.transport?.risk as RiskLevel) || "LOW";
      case "Food Court":
        return (report.crowd?.risk as RiskLevel) || "LOW";
      case "Medical Center":
        return (report.medical?.risk as RiskLevel) || "LOW";
      case "VIP Entrance":
        return (report.crowd?.risk as RiskLevel) || "LOW";
      case "Broadcast Area":
        return (report.weather?.risk as RiskLevel) || "LOW";
      case "Volunteer HQ":
        return (report.volunteer?.risk as RiskLevel) || "LOW";
      default:
        return "UNKNOWN";
    }
  };

  const getStatusForZone = (name: string): string => {
    if (!report) return "Offline";
    switch (name) {
      case "Gate B":
        return report.crowd?.predictions?.[0]?.issue || "Normal Ingress";
      case "Parking":
        return report.transport ? `${report.transport.parking_occupancy_percent.toFixed(0)}% Occupied` : "Operational";
      case "Metro":
        return report.transport ? (report.transport.metro_status === "HIGH" ? "Heavy delays" : "Stable link") : "Stable link";
      case "Medical Center":
        return report.medical ? (report.medical.prediction.resource_shortage ? "Shortage flagged" : "Operational") : "Operational";
      case "Broadcast Area":
        return report.weather ? report.weather.weather_status : "Clear";
      case "Volunteer HQ":
        return report.volunteer ? `${report.volunteer.volunteer_utilization_percent.toFixed(0)}% Utilized` : "Operational";
      default:
        return "Normal flow";
    }
  };

  const getIssueForZone = (name: string): string => {
    if (!report) return "No telemetry synchronisation.";
    switch (name) {
      case "Gate B":
        return report.crowd?.predictions?.[0]?.issue || "No anomalies flagged.";
      case "Parking":
        return report.transport && report.transport.parking_occupancy_percent >= 90
          ? "Parking lot is nearing capacity limits."
          : "Parking volumes within normal thresholds.";
      case "Metro":
        return report.transport?.metro_status === "HIGH"
          ? "Metro delay active due to train link bottlenecks."
          : "Metro link timing within regular limits.";
      case "Medical Center":
        return report.medical?.prediction.resource_shortage
          ? "Paramedic dispatches congested. Ambulance utilization high."
          : "First aid queues and dispatches stable.";
      case "Broadcast Area":
        return report.weather && report.weather.risk !== "LOW"
          ? report.weather.prediction.expected_operational_impact
          : "Weather sensors clear.";
      case "Volunteer HQ":
        return report.volunteer && report.volunteer.coverage_percent < 80
          ? "Suboptimal volunteer zone coverage detected."
          : "Volunteers active and assigned.";
      default:
        return "Baseline operations proceeding normally.";
    }
  };

  const getActionForZone = (name: string): string => {
    if (!report) return "Establish connection.";
    switch (name) {
      case "Gate B":
        return "Redirect ingress flows to East stands scanner stations.";
      case "Parking":
        return "Update highway displays to redirect traffic to Lot C.";
      case "Metro":
        return "Dispatch transit buses to bridge station arrivals.";
      case "Medical Center":
        return "Request backup responders from standbys.";
      case "Broadcast Area":
        return report.weather && report.weather.risk !== "LOW"
          ? report.weather.prediction.recommendation
          : "No warning actions.";
      case "Volunteer HQ":
        return "Prepare deployment groups for Gate redirects.";
      default:
        return "Continue monitor channels.";
    }
  };

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

  return (
    <div className="bg-slate-900 border border-gray-800 rounded-2xl p-5 relative overflow-hidden h-[400px] flex flex-col justify-between group hover:border-blue-500/20 transition-all duration-300">
      <div className="flex items-center justify-between z-10 select-none">
        <div>
          <h2 className="text-sm font-black tracking-wider text-gray-200 uppercase font-mono flex items-center gap-1.5">
            <span>🏟</span> Stadium Operations Map
          </h2>
          <p className="text-[9px] text-gray-500 font-bold uppercase tracking-widest mt-0.5">
            Mission Control Tactical Visual Overlay
          </p>
        </div>
        <Legend />
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
                isSelected={selectedZoneName === name}
                positionClass={zone.positionClass}
              />
            );
          })}
        </motion.div>
      </div>

      {/* Slide-out details drawer overlay */}
      <AnimatePresence>
        {selectedZone && selectedZoneName && (
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ type: "spring", stiffness: 260, damping: 25 }}
            className="absolute top-0 right-0 w-[260px] h-full bg-gray-950 border-l border-gray-800 p-5 z-30 flex flex-col justify-between shadow-2xl font-mono text-xs text-gray-300"
          >
            <div className="space-y-4">
              {/* Drawer Header */}
              <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-blue-500" />
                  Zone Telemetry:
                </span>
                <button
                  onClick={() => setSelectedZoneName(null)}
                  className="p-1 hover:bg-gray-900 rounded-lg text-gray-500 hover:text-gray-300 cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Title & Status */}
              <div>
                <h3 className="text-sm font-black text-white uppercase tracking-wider leading-none">
                  {selectedZoneName}
                </h3>
                <span
                  className={`mt-2 px-2.5 py-0.5 rounded border text-[9px] font-black uppercase inline-flex items-center ${getRiskColor(
                    getRiskForZone(selectedZoneName)
                  )}`}
                >
                  {getRiskForZone(selectedZoneName)} RISK
                </span>
              </div>

              {/* Volunteers Count */}
              <div className="flex items-center gap-2 text-2xs text-gray-400 bg-gray-900/60 border border-gray-800/80 px-3 py-2 rounded-xl">
                <Users className="w-4 h-4 text-blue-400" />
                <span>Volunteers Deployed: <b>{selectedZone.volunteers}</b></span>
              </div>

              {/* Active Issue */}
              <div className="space-y-1">
                <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider">
                  Active Issue:
                </span>
                <p className="text-2xs text-gray-200 bg-slate-900/40 p-2.5 rounded-lg border border-gray-805 leading-relaxed select-text">
                  {getIssueForZone(selectedZoneName)}
                </p>
              </div>

              {/* Action plan */}
              <div className="space-y-1">
                <span className="text-[9px] text-gray-500 font-bold uppercase tracking-wider flex items-center gap-1">
                  <Info className="w-3.5 h-3.5 text-blue-400" />
                  Operational Action:
                </span>
                <p className="text-2xs text-blue-400 leading-normal pl-1.5 font-bold select-text">
                  {getActionForZone(selectedZoneName)}
                </p>
              </div>
            </div>

            {/* Close instruction */}
            <div className="text-[9px] text-gray-600 font-bold text-center uppercase tracking-widest pt-2 border-t border-gray-900">
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
