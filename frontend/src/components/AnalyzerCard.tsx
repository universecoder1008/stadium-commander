import React from "react";
import { motion } from "framer-motion";
import { Clock } from "lucide-react";
import RiskBadge from "./RiskBadge";

interface AnalyzerCardProps {
  name: string;
  risk: "LOW" | "MEDIUM" | "HIGH";
  status: string;
  icon: React.ReactNode;
  lastUpdated: string;
}

export const AnalyzerCard: React.FC<AnalyzerCardProps> = ({
  name,
  risk,
  status,
  icon,
  lastUpdated
}) => {
  // Animation configurations
  const cardVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  return (
    <motion.div
      variants={cardVariants}
      whileHover={{ y: -6, transition: { duration: 0.2, ease: "easeInOut" } }}
      className="bg-slate-900/50 backdrop-blur-md border border-gray-800/80 rounded-2xl p-5 shadow-lg flex flex-col justify-between h-[230px] hover:border-blue-500/30 transition-colors duration-300 font-sans"
    >
      <div>
        {/* Top: Icon & Analyzer Name */}
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gray-950/80 rounded-lg border border-gray-800 text-gray-400 group-hover:text-blue-400">
            {icon}
          </div>
          <h3 className="text-xs font-black tracking-wider text-gray-200 uppercase font-mono">
            {name}
          </h3>
        </div>

        {/* Center: Large Risk Badge */}
        <div className="my-5 flex items-center justify-start">
          <RiskBadge risk={risk} />
        </div>

        {/* Bottom: Short AI Status */}
        <p className="text-2xs text-gray-300 leading-relaxed font-semibold pl-1">
          &ldquo;{status}&rdquo;
        </p>
      </div>

      {/* Footer: Last Updated timestamp */}
      <div className="border-t border-gray-900/60 pt-3 flex items-center justify-between text-[10px] text-gray-500 font-mono select-none">
        <span className="flex items-center gap-1">
          <Clock className="w-3.5 h-3.5 text-gray-600" />
          UPDATED
        </span>
        <span>{lastUpdated}</span>
      </div>
    </motion.div>
  );
};
export default AnalyzerCard;
