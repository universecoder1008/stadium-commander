import React from "react";
import { AlertCircle, ShieldAlert, CloudSun, Users, CheckCircle } from "lucide-react";
import type { CombinedSituationReport, CommanderResponse } from "../types/api";

interface StatusHeaderProps {
  report: CombinedSituationReport | null;
  decision: CommanderResponse | null;
}

export const StatusHeader: React.FC<StatusHeaderProps> = ({ report, decision }) => {
  const priority = decision?.priority || report?.system_status || "LOW";
  const topRisk = decision?.top_risk || "None Flagged";
  
  // Format weather info
  const weatherText = report?.weather
    ? `Risk: ${report.weather.risk}`
    : "No Data";
  const weatherSub = report?.weather?.prediction
    ? report.weather.prediction.expected_operational_impact
    : "Sensors pending";

  // Format attendance/transport info
  const parkingOccupancy = report?.transport?.parking_occupancy_percent
    ? `${report.transport.parking_occupancy_percent.toFixed(0)}%`
    : "No Data";
  const transportSub = report?.transport?.arrival_prediction
    ? `ETA: ${report.transport.arrival_prediction.estimated_arrival_minutes}m`
    : "Sensors pending";

  // Format system status
  const systemValue = report
    ? Object.keys(report.analyzers_failed).length > 0
      ? "DEGRADED"
      : "NORMAL"
    : "OFFLINE";
  const systemSub = report
    ? `Completed: ${report.analyzers_completed.length}/${report.analyzers_completed.length + Object.keys(report.analyzers_failed).length}`
    : "Awaiting sync";

  const getPriorityStyle = (lvl: string) => {
    const l = lvl.toUpperCase();
    if (l === "CRITICAL" || l === "HIGH") {
      return {
        bg: "bg-rose-950/20 border-rose-500/20 text-rose-400",
        icon: <AlertCircle className="w-5 h-5 text-rose-500" />
      };
    }
    if (l === "MEDIUM" || l === "WARNING") {
      return {
        bg: "bg-amber-950/20 border-amber-500/20 text-amber-400",
        icon: <ShieldAlert className="w-5 h-5 text-amber-500" />
      };
    }
    return {
      bg: "bg-emerald-950/20 border-emerald-500/20 text-emerald-400",
      icon: <CheckCircle className="w-5 h-5 text-emerald-400" />
    };
  };

  const priorityStyles = getPriorityStyle(priority);

  const metrics = [
    {
      title: "Priority Level",
      value: priority,
      subtext: isPriorityHighOrCritical(priority) ? "Action required" : "Routine checks",
      icon: priorityStyles.icon,
      bg: priorityStyles.bg
    },
    {
      title: "Top Risk Vectors",
      value: topRisk,
      subtext: "Risk advisor assessment",
      icon: <ShieldAlert className="w-5 h-5 text-amber-500" />,
      bg: "bg-amber-950/20 border-amber-500/20 text-amber-400"
    },
    {
      title: "Weather status",
      value: weatherText,
      subtext: weatherSub,
      icon: <CloudSun className="w-5 h-5 text-sky-400" />,
      bg: "bg-sky-950/20 border-sky-500/20 text-sky-400"
    },
    {
      title: "Attendance Load",
      value: parkingOccupancy,
      subtext: transportSub,
      icon: <Users className="w-5 h-5 text-blue-400" />,
      bg: "bg-blue-950/20 border-blue-500/20 text-blue-400"
    },
    {
      title: "System Status",
      value: systemValue,
      subtext: systemSub,
      icon: <CheckCircle className="w-5 h-5 text-emerald-400" />,
      bg: "bg-emerald-950/20 border-emerald-500/20 text-emerald-400"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
      {metrics.map((m, idx) => (
        <div
          key={idx}
          className={`border rounded-xl p-4 flex flex-col justify-between shadow-sm transition-all hover:scale-[1.01] ${m.bg}`}
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-black uppercase tracking-wider opacity-85">
              {m.title}
            </span>
            {m.icon}
          </div>
          <div className="mt-3">
            <div className="text-sm font-black tracking-tight font-mono truncate select-all">{m.value}</div>
            <div className="text-[9px] opacity-75 font-semibold mt-0.5 uppercase tracking-wide truncate">
              {m.subtext}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

function isPriorityHighOrCritical(priority: string) {
  const p = priority.toUpperCase();
  return p === "HIGH" || p === "CRITICAL";
}

export default StatusHeader;
