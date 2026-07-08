import React from "react";
import { motion } from "framer-motion";
import clsx from "clsx";

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "UNKNOWN";

interface StadiumZoneProps {
  name: string;
  risk: RiskLevel;
  status: string;
  onClick: () => void;
  isSelected: boolean;
  positionClass: string;
}

export const StadiumZone: React.FC<StadiumZoneProps> = ({
  name,
  risk,
  status,
  onClick,
  isSelected,
  positionClass
}) => {
  const isHigh = risk === "HIGH";

  // Position-wise colors
  const getColors = () => {
    switch (risk) {
      case "HIGH":
        return {
          bg: "bg-rose-950/30 border-rose-500/40 text-rose-300",
          glow: "hover:shadow-rose-500/20 hover:border-rose-400",
          dot: "bg-rose-400"
        };
      case "MEDIUM":
        return {
          bg: "bg-amber-950/30 border-amber-500/40 text-amber-300",
          glow: "hover:shadow-amber-500/20 hover:border-amber-400",
          dot: "bg-amber-400"
        };
      case "LOW":
        return {
          bg: "bg-emerald-950/30 border-emerald-500/40 text-emerald-300",
          glow: "hover:shadow-emerald-500/20 hover:border-emerald-400",
          dot: "bg-emerald-400"
        };
      default:
        return {
          bg: "bg-gray-900/40 border-gray-800 text-gray-400",
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
      whileHover={{ scale: 1.03, transition: { duration: 0.15 } }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={clsx(
        "absolute p-2.5 rounded-xl border backdrop-blur-md text-3xs font-mono font-bold tracking-wider flex items-center gap-2 transition-all duration-300 shadow-md cursor-pointer select-none",
        positionClass,
        colors.bg,
        colors.glow,
        {
          "ring-2 ring-blue-500/50 border-blue-400 shadow-lg": isSelected
        }
      )}
      title={`${name}: ${status}`}
    >
      {/* Risk indicator status circle */}
      <motion.span
        animate={isHigh ? {
          scale: [1, 1.3, 1],
          opacity: [1, 0.6, 1]
        } : {}}
        transition={isHigh ? {
          duration: 1.5,
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
};
export default StadiumZone;
