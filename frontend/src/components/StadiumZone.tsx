import React from "react";
import { motion } from "framer-motion";
import clsx from "clsx";

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "UNKNOWN";

interface StadiumZoneProps {
  name: string;
  risk: RiskLevel;
  status: string;
  onClick: () => void;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
  isSelected: boolean;
  positionClass: string;
}

export const StadiumZone: React.FC<StadiumZoneProps> = React.memo(({
  name,
  risk,
  status,
  onClick,
  onMouseEnter,
  onMouseLeave,
  isSelected,
  positionClass
}) => {
  const isHigh = risk === "HIGH";

  // Position-wise colors
  const getColors = () => {
    switch (risk) {
      case "HIGH":
        return {
          bg: "bg-rose-950/40 border-rose-500/50 text-rose-300",
          glow: "hover:shadow-rose-500/30 hover:border-rose-400",
          dot: "bg-rose-400"
        };
      case "MEDIUM":
        return {
          bg: "bg-amber-950/40 border-amber-500/50 text-amber-300",
          glow: "hover:shadow-amber-500/30 hover:border-amber-400",
          dot: "bg-amber-400"
        };
      case "LOW":
        return {
          bg: "bg-emerald-950/40 border-emerald-500/50 text-emerald-300",
          glow: "hover:shadow-emerald-500/30 hover:border-emerald-400",
          dot: "bg-emerald-400"
        };
      default:
        return {
          bg: "bg-gray-900/50 border-gray-800 text-gray-400",
          glow: "hover:shadow-gray-700/20 hover:border-gray-700",
          dot: "bg-gray-600"
        };
    }
  };

  const colors = getColors();

  return (
    <motion.button
      variants={{
        hidden: { opacity: 0, scale: 0.9 },
        visible: { opacity: 1, scale: 1 }
      }}
      animate={isHigh ? {
        boxShadow: [
          "0 0 0 0px rgba(239, 68, 68, 0.4)",
          "0 0 0 10px rgba(239, 68, 68, 0)",
          "0 0 0 0px rgba(239, 68, 68, 0.4)"
        ]
      } : {}}
      transition={isHigh ? {
        duration: 2.0,
        repeat: Infinity,
        ease: "easeInOut"
      } : { duration: 0.3 }}
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      aria-label={`Zone ${name}, risk: ${risk}, status: ${status}`}
      className={clsx(
        "absolute p-2.5 rounded-xl border backdrop-blur-md text-3xs font-mono font-bold tracking-wider flex items-center gap-2 transition-all duration-300 shadow-md cursor-pointer select-none focus:outline-none focus:ring-2 focus:ring-blue-500/50",
        positionClass,
        colors.bg,
        colors.glow,
        {
          "ring-2 ring-blue-500/60 border-blue-400 shadow-lg": isSelected
        }
      )}
      title={`${name}: ${status}`}
    >
      {/* Risk indicator status circle */}
      <motion.span
        animate={isHigh ? {
          scale: [1, 1.4, 1],
          opacity: [1, 0.5, 1]
        } : {}}
        transition={isHigh ? {
          duration: 1.2,
          repeat: Infinity,
          ease: "easeInOut"
        } : undefined}
        className={clsx("w-2 h-2 rounded-full shrink-0", colors.dot)}
      />
      
      <div className="text-left">
        <div className="uppercase leading-none">{name}</div>
        <div className="text-[8px] opacity-60 mt-0.5 uppercase tracking-widest truncate max-w-[80px]">
          {status}
        </div>
      </div>
    </motion.button>
  );
});

export default StadiumZone;
