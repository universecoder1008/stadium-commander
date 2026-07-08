import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Radio, Search } from "lucide-react";
import TimelineEvent from "./TimelineEvent";
import type { EventData } from "../types/api";

interface TimelineProps {
  events: EventData[];
}

export const Timeline: React.FC<TimelineProps> = React.memo(({ events }) => {
  const [filter, setFilter] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>(" ");
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const [, setTick] = useState(0);

  // Parse safe trim search state
  const normalizedSearch = searchQuery.trim().toLowerCase();

  // Force re-renders periodically to keep relative time calculations fresh
  useEffect(() => {
    const timer = setInterval(() => {
      setTick((t) => t + 1);
    }, 10000);
    return () => clearInterval(timer);
  }, []);

  // Auto-scroll to top when a filter changes or events list updates
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [filter, events, normalizedSearch]);

  const filterButtons = [
    { label: "All", category: "All" },
    { label: "Crowd", category: "Crowd" },
    { label: "Transport", category: "Transport" },
    { label: "Medical", category: "Medical" },
    { label: "Weather", category: "Weather" },
    { label: "Volunteers", category: "Volunteer" },
    { label: "AI", category: "AI Commander" }
  ];

  const filteredEvents = events.filter((e) => {
    const matchesFilter =
      filter === "All" ||
      e.category === filter ||
      (filter === "Volunteers" && e.category === "Volunteer") ||
      (filter === "AI" && e.category === "AI Commander");

    const matchesSearch =
      e.title.toLowerCase().includes(normalizedSearch) ||
      e.description.toLowerCase().includes(normalizedSearch);

    return matchesFilter && matchesSearch;
  });

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 hover:border-blue-500/10 transition-all duration-300 flex flex-col h-[500px]">
      {/* Header Panel */}
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4 border-b border-gray-800/80 pb-4 select-none">
        <div>
          <h2 className="text-sm font-black tracking-wider text-gray-200 uppercase font-mono flex items-center gap-2">
            <Radio className="w-4.5 h-4.5 text-blue-500 animate-pulse" />
            Live Operations Event Feed
          </h2>
          <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-0.5 font-mono">
            FIFA Stadium Incident Telemetry Dispatch Logs
          </p>
        </div>

        {/* Toolbar: Category Filters and Quick Search Input */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Quick Search Input */}
          <div className="relative flex items-center">
            <Search className="w-3.5 h-3.5 text-gray-650 absolute left-2.5 pointer-events-none" />
            <input
              type="text"
              value={searchQuery === " " ? "" : searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search dispatches..."
              aria-label="Search incident dispatch logs"
              className="pl-8 pr-3 py-1 bg-gray-950/80 border border-gray-800 rounded-lg text-2xs font-mono text-gray-200 placeholder-gray-650 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30 transition-all w-[180px]"
            />
          </div>

          {/* Categories Tab Selector buttons */}
          <div className="flex flex-wrap items-center gap-1 bg-gray-950/80 p-1 border border-gray-850 rounded-lg">
            {filterButtons.map((btn) => (
              <button
                key={btn.label}
                onClick={() => {
                  setFilter(btn.category);
                  setExpandedIndex(null);
                }}
                aria-label={`Filter incident stream by ${btn.label}`}
                className={`px-2.5 py-0.5 rounded text-[9px] font-black font-mono tracking-wider uppercase transition-all duration-200 cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-500/40 ${
                  filter === btn.category || (btn.category === "Volunteer" && filter === "Volunteers") || (btn.category === "AI Commander" && filter === "AI")
                    ? "bg-blue-600 text-white glow-blue"
                    : "text-gray-500 hover:text-gray-300"
                }`}
              >
                {btn.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Operations Event Stream List */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto mt-4 pr-2 space-y-3 scrollbar-thin"
      >
        <AnimatePresence mode="popLayout">
          {filteredEvents.length > 0 ? (
            filteredEvents.map((event, idx) => {
              // Mark the very first item as newest event
              const isNewest = idx === 0;

              return (
                <TimelineEvent
                  key={event.timestampMs + event.title}
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
              className="flex flex-col items-center justify-center h-full text-center text-gray-600 font-mono text-xs uppercase tracking-wider select-none animate-fade-in"
            >
              No timeline dispatches match search query.
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
});

export default Timeline;
