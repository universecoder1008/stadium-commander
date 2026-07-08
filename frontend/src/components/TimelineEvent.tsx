import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Users,
  Bus,
  HeartPulse,
  CloudRain,
  UserCheck,
  Cpu,
  Terminal,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import clsx from "clsx";

export type EventCategory =
  | "Crowd"
  | "Transport"
  | "Medical"
  | "Weather"
  | "Volunteer"
  | "AI Commander"
  | "System";

export type EventPriority = "LOW" | "MEDIUM" | "HIGH";

export interface EventData {
  time: string;
  category: EventCategory;
  title: string;
  description: string;
  priority: EventPriority;
}

interface TimelineEventProps {
  event: EventData;
  isNewest: boolean;
  isExpanded: boolean;
  onToggle: () => void;
}

export const TimelineEvent: React.FC<TimelineEventProps> = ({
  event,
  isNewest,
  isExpanded,
  onToggle
}) => {
  const { time, category, title, description, priority } = event;

  // Category Icon Mapping
  const getCategoryIcon = () => {
    switch (category) {
      case "Crowd":
        return <Users className="w-4 h-4 text-blue-400" />;
      case "Transport":
        return <Bus className="w-4 h-4 text-indigo-400" />;
      case "Medical":
        return <HeartPulse className="w-4 h-4 text-rose-400" />;
      case "Weather":
        return <CloudRain className="w-4 h-4 text-amber-400" />;
      case "Volunteer":
        return <UserCheck className="w-4 h-4 text-emerald-400" />;
      case "AI Commander":
        return <Cpu className="w-4 h-4 text-violet-400" />;
      default:
        return <Terminal className="w-4 h-4 text-gray-400" />;
    }
  };

  // Priority Color Mapping
  const getPriorityStyle = () => {
    switch (priority) {
      case "HIGH":
        return "text-rose-400 border-rose-500/30 bg-rose-950/20";
      case "MEDIUM":
        return "text-amber-400 border-amber-500/30 bg-amber-950/20";
      default:
        return "text-emerald-400 border-emerald-500/30 bg-emerald-950/20";
    }
  };

  return (
    <motion.div
      layout="position"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      onClick={onToggle}
      className={clsx(
        "bg-slate-900/40 backdrop-blur-md border rounded-2xl p-4 flex gap-4 cursor-pointer select-none transition-all duration-300 hover:border-gray-700",
        {
          "border-blue-500/40 shadow-lg shadow-blue-500/5 ring-1 ring-blue-500/20": isNewest,
          "border-gray-800/80": !isNewest,
        }
      )}
    >
      {/* Category Icon and Vertical Line Trace */}
      <div className="flex flex-col items-center gap-1.5">
        <div className="w-8 h-8 rounded-lg bg-gray-950 border border-gray-800 flex items-center justify-center relative shrink-0">
          {getCategoryIcon()}
          
          {/* Pulse alert badge for the newest event */}
          {isNewest && (
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-blue-500"></span>
            </span>
          )}
        </div>
        <div className="w-[1.5px] bg-gray-800 flex-1 min-h-[20px]" />
      </div>

      {/* Main details content */}
      <div className="flex-1 space-y-2">
        <div className="flex flex-wrap items-center justify-between gap-2 text-2xs font-mono">
          <div className="flex items-center gap-2">
            <span className="text-blue-400 font-bold tracking-wider">{time}</span>
            <span className="text-gray-500 font-bold uppercase tracking-wider">
              {category}
            </span>
          </div>

          <span
            className={clsx(
              "px-2 py-0.5 rounded border text-[9px] font-black uppercase tracking-wider",
              getPriorityStyle()
            )}
          >
            {priority}
          </span>
        </div>

        <div>
          <h4 className="text-xs font-black text-gray-100 uppercase tracking-wide flex items-center justify-between">
            {title}
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            )}
          </h4>
          
          {/* Smooth expanded description details */}
          <AnimatePresence initial={false}>
            {isExpanded ? (
              <motion.p
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="text-[11px] text-gray-400 mt-2 leading-relaxed font-semibold overflow-hidden"
              >
                {description}
              </motion.p>
            ) : (
              <p className="text-[11px] text-gray-500 mt-1 leading-normal font-semibold truncate max-w-[400px]">
                {description}
              </p>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
};
export default TimelineEvent;
