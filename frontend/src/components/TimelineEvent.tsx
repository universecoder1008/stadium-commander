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
import type { EventData } from "../types/api";

interface TimelineEventProps {
  event: EventData;
  isNewest: boolean;
  isExpanded: boolean;
  onToggle: () => void;
}

const getRelativeTime = (timestampMs: number, defaultTime: string) => {
  if (!timestampMs) return defaultTime;
  const diff = Date.now() - timestampMs;
  const sec = Math.floor(diff / 1000);
  if (sec < 5) return "Just now";
  if (sec < 60) return `${sec}s ago`;
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m ago`;
  return defaultTime;
};

export const TimelineEvent: React.FC<TimelineEventProps> = React.memo(({
  event,
  isNewest,
  isExpanded,
  onToggle
}) => {
  const { time, timestampMs, category, title, description, priority } = event;

  const displayTime = getRelativeTime(timestampMs, time);

  // Category Icon & Emoji Mapping
  const getCategoryDetails = () => {
    switch (category) {
      case "Crowd":
        return { emoji: "🚨", icon: <Users className="w-3.5 h-3.5 text-blue-400" /> };
      case "Transport":
        return { emoji: "🚇", icon: <Bus className="w-3.5 h-3.5 text-indigo-400" /> };
      case "Medical":
        return { emoji: "🚑", icon: <HeartPulse className="w-3.5 h-3.5 text-rose-400" /> };
      case "Weather":
        return { emoji: "🌧", icon: <CloudRain className="w-3.5 h-3.5 text-amber-400" /> };
      case "Volunteer":
        return { emoji: "👥", icon: <UserCheck className="w-3.5 h-3.5 text-emerald-400" /> };
      case "AI Commander":
        return { emoji: "🤖", icon: <Cpu className="w-3.5 h-3.5 text-violet-400" /> };
      default:
        return { emoji: "⚽", icon: <Terminal className="w-3.5 h-3.5 text-gray-400" /> };
    }
  };

  const categoryDetails = getCategoryDetails();

  // Left accent border based on severity
  const getSeverityStyle = () => {
    const p = (priority || "LOW").toUpperCase();
    switch (p) {
      case "CRITICAL":
        return {
          border: "border-l-4 border-l-rose-600",
          badge: "bg-rose-600 text-white border-rose-600"
        };
      case "HIGH":
        return {
          border: "border-l-4 border-l-rose-500",
          badge: "text-rose-400 border-rose-500/30 bg-rose-950/20"
        };
      case "MEDIUM":
        return {
          border: "border-l-4 border-l-amber-500",
          badge: "text-amber-400 border-amber-500/30 bg-amber-950/20"
        };
      default: // LOW
        return {
          border: "border-l-4 border-l-emerald-500",
          badge: "text-emerald-400 border-emerald-500/30 bg-emerald-950/20"
        };
    }
  };

  const severityStyle = getSeverityStyle();

  return (
    <motion.div
      layout="position"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.35 }}
      whileHover={{
        y: -2,
        boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.2)",
        borderColor: "rgba(59, 130, 246, 0.3)"
      }}
      onClick={onToggle}
      className={clsx(
        "bg-slate-900/40 backdrop-blur-md border rounded-2xl p-4 flex gap-4 cursor-pointer select-none transition-all duration-300",
        severityStyle.border,
        {
          "border-blue-500/40 shadow-lg shadow-blue-500/5 ring-1 ring-blue-500/10": isNewest,
          "border-gray-800/80": !isNewest,
        }
      )}
    >
      {/* Category Icon and Vertical Line Trace */}
      <div className="flex flex-col items-center gap-1.5 select-none">
        <div className="w-8 h-8 rounded-lg bg-gray-950 border border-gray-800 flex items-center justify-center relative shrink-0">
          <span className="absolute -top-1.5 -left-1.5 text-xs">
            {categoryDetails.emoji}
          </span>
          {categoryDetails.icon}
          
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
            <span className="text-blue-400 font-bold tracking-wider">{displayTime}</span>
            <span className="text-gray-500 font-bold uppercase tracking-wider">
              {category}
            </span>
          </div>

          <span
            className={clsx(
              "px-2 py-0.5 rounded border text-[9px] font-black uppercase tracking-wider",
              severityStyle.badge
            )}
          >
            {priority}
          </span>
        </div>

        <div>
          <h4 className="text-xs font-black text-gray-100 uppercase tracking-wide flex items-center justify-between">
            {title}
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-gray-500 shrink-0" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500 shrink-0" />
            )}
          </h4>
          
          {/* Smooth expanded description details */}
          <AnimatePresence initial={false}>
            {isExpanded ? (
              <motion.p
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25 }}
                className="text-[11px] text-gray-400 mt-2 leading-relaxed font-semibold overflow-hidden select-text"
              >
                {description}
              </motion.p>
            ) : (
              description && (
                <p className="text-[11px] text-gray-500 mt-1 leading-normal font-semibold truncate max-w-[400px]">
                  {description}
                </p>
              )
            )}
          </AnimatePresence>
        </div>

      </div>
    </motion.div>
  );
});

export default TimelineEvent;
