import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Radio } from "lucide-react";
import TimelineEvent from "./TimelineEvent";
import type { EventData } from "./TimelineEvent";

interface TimelineProps {
  events: EventData[];
}

export const Timeline: React.FC<TimelineProps> = ({ events }) => {
  const [filter, setFilter] = useState<string>("All");
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to top when a filter changes or events list updates
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [filter, events]);

  const filterButtons = [
    { label: "All", category: "All" },
    { label: "Crowd", category: "Crowd" },
    { label: "Transport", category: "Transport" },
    { label: "Medical", category: "Medical" },
    { label: "Weather", category: "Weather" },
    { label: "Volunteer", category: "Volunteer" },
    { label: "AI", category: "AI Commander" }
  ];

  const filteredEvents = events.filter((e) => {
    if (filter === "All") return true;
    return e.category === filter;
  });

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 hover:border-blue-500/10 transition-all duration-300 flex flex-col h-[500px]">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-800/80 pb-4 select-none">
        <div>
          <h2 className="text-sm font-black tracking-wider text-gray-200 uppercase font-mono flex items-center gap-2">
            <Radio className="w-4.5 h-4.5 text-blue-500 animate-pulse" />
            Live Operations Timeline
          </h2>
          <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-0.5">
            Realtime Incident & Signals Stream Registry
          </p>
        </div>

        {/* Filter Toolbar Button Groups */}
        <div className="flex flex-wrap items-center gap-1.5 bg-gray-950/80 p-1 border border-gray-850 rounded-lg">
          {filterButtons.map((btn) => (
            <button
              key={btn.label}
              onClick={() => {
                setFilter(btn.category);
                setExpandedIndex(null);
              }}
              className={`px-3 py-1 rounded text-[10px] font-black font-mono tracking-wider uppercase transition-all duration-200 cursor-pointer ${
                filter === btn.category
                  ? "bg-blue-600 text-white glow-blue"
                  : "text-gray-500 hover:text-gray-300"
              }`}
            >
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      {/* Scrollable Timeline Stream */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto mt-4 pr-2 space-y-3 scrollbar-thin"
      >
        <AnimatePresence mode="popLayout">
          {filteredEvents.length > 0 ? (
            filteredEvents.map((event, idx) => {
              // The newest event is always the first index in the current visible list
              const isNewest = idx === 0;

              return (
                <TimelineEvent
                  key={event.time}
                  event={event}
                  isNewest={isNewest}
                  isExpanded={expandedIndex === idx}
                  onToggle={() => setExpandedIndex(expandedIndex === idx ? null : idx)}
                />
              );
            })
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center h-full text-center text-gray-600 font-mono text-xs uppercase tracking-wider select-none"
            >
              No timeline dispatches in this category.
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
export default Timeline;
