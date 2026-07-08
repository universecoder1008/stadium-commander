import React from "react";

export const Legend: React.FC = () => {
  const legendItems = [
    { label: "Low Risk", color: "bg-emerald-500 shadow-emerald-500/50" },
    { label: "Medium Risk", color: "bg-amber-500 shadow-amber-500/50" },
    { label: "High Risk", color: "bg-rose-500 shadow-rose-500/50 animate-pulse" },
    { label: "Inactive", color: "bg-gray-600 shadow-gray-600/50" }
  ];

  return (
    <div className="flex flex-wrap items-center gap-4 text-3xs font-mono font-bold text-gray-500 uppercase tracking-widest select-none">
      {legendItems.map((item, idx) => (
        <div key={idx} className="flex items-center gap-1.5">
          <span className={`w-2.5 h-2.5 rounded-full shadow-sm ${item.color}`} />
          <span>{item.label}</span>
        </div>
      ))}
    </div>
  );
};
export default Legend;
