import React from "react";

interface LegendProps {
  lowCount: number;
  mediumCount: number;
  highCount: number;
  unknownCount: number;
}

export const Legend: React.FC<LegendProps> = ({
  lowCount,
  mediumCount,
  highCount,
  unknownCount
}) => {
  const legendItems = [
    { label: "Low Risk", color: "bg-emerald-500 shadow-emerald-500/40", count: lowCount },
    { label: "Medium Risk", color: "bg-amber-500 shadow-amber-500/40", count: mediumCount },
    { label: "High Risk", color: "bg-rose-500 shadow-rose-500/40 animate-pulse", count: highCount },
    { label: "Inactive", color: "bg-gray-600 shadow-gray-600/40", count: unknownCount }
  ];

  return (
    <div 
      aria-label="Stadium Risk Map Legend"
      className="flex flex-wrap items-center gap-4 text-3xs font-mono font-bold text-gray-400 uppercase tracking-wider select-none bg-gray-950/40 px-3 py-1.5 rounded-lg border border-gray-800/80 shadow-inner"
    >
      {legendItems.map((item, idx) => (
        <div key={idx} className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full shadow-md ${item.color}`} />
          <span>{item.label} ({item.count})</span>
        </div>
      ))}
    </div>
  );
};

export default Legend;
