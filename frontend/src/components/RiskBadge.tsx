import React from "react";
import { motion } from "framer-motion";
import clsx from "clsx";

interface RiskBadgeProps {
  risk: "LOW" | "MEDIUM" | "HIGH";
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ risk }) => {
  const normalized = risk.toUpperCase();
  const isHigh = normalized === "HIGH";

  const badgeStyles = clsx(
    "px-3 py-1 text-xs font-black tracking-wider rounded-full border uppercase inline-flex items-center gap-1.5 shadow-sm transition-all duration-300",
    {
      "bg-emerald-950/40 text-emerald-400 border-emerald-500/30":
        normalized === "LOW",
      "bg-amber-950/40 text-amber-400 border-amber-500/30":
        normalized === "MEDIUM",
      "bg-rose-950/40 text-rose-400 border-rose-500/30":
        isHigh,
    }
  );

  return (
    <motion.span
      animate={isHigh ? {
        scale: [1, 1.05, 1],
        boxShadow: [
          "0 0 0 0px rgba(239, 68, 68, 0.4)",
          "0 0 0 6px rgba(239, 68, 68, 0)",
          "0 0 0 0px rgba(239, 68, 68, 0)"
        ]
      } : {}}
      transition={isHigh ? {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      } : undefined}
      className={badgeStyles}
    >
      <span
        className={clsx("w-1.5 h-1.5 rounded-full", {
          "bg-emerald-400": normalized === "LOW",
          "bg-amber-400": normalized === "MEDIUM",
          "bg-rose-400": isHigh,
        })}
      />
      {normalized}
    </motion.span>
  );
};
export default RiskBadge;
