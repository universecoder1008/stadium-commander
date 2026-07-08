import React from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon: React.ReactNode;
  trend?: string;
  trendType?: "up" | "down" | "neutral";
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtext,
  icon,
  trend,
  trendType = "neutral",
}) => {
  return (
    <div className="bg-card border border-gray-800/80 rounded-xl p-4 flex items-center justify-between transition-all duration-300 hover:border-blue-500/40 hover:shadow-lg hover:shadow-blue-500/5 group">
      <div>
        <p className="text-gray-400 text-xs font-semibold tracking-wider uppercase group-hover:text-blue-400 transition-colors">
          {title}
        </p>
        <h3 className="text-2xl font-bold text-gray-100 mt-1 tracking-tight">
          {value}
        </h3>
        {subtext && <p className="text-gray-500 text-xs mt-0.5">{subtext}</p>}
        {trend && (
          <p
            className={`text-xs mt-1.5 font-medium flex items-center gap-1 ${
              trendType === "up"
                ? "text-emerald-400"
                : trendType === "down"
                ? "text-rose-400"
                : "text-gray-400"
            }`}
          >
            {trend}
          </p>
        )}
      </div>
      <div className="p-3 bg-gray-900/60 rounded-xl border border-gray-800/50 group-hover:border-blue-500/20 text-gray-400 group-hover:text-blue-400 group-hover:scale-105 transition-all">
        {icon}
      </div>
    </div>
  );
};
export default MetricCard;
