import React from "react";
import { Trophy, Activity, Radio, RefreshCw } from "lucide-react";

interface NavbarProps {
  currentPhase: string;
  liveMode: boolean;
  setLiveMode: (live: boolean) => void;
  connectionHealthy: boolean;
  onRefresh: () => void;
  loading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentPhase,
  liveMode,
  setLiveMode,
  connectionHealthy,
  onRefresh,
  loading
}) => {
  return (
    <nav className="h-16 border-b border-gray-800 bg-gray-950 px-6 flex items-center justify-between z-50">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-blue-600/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
          <Trophy className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-md font-black tracking-wider text-gray-100 uppercase font-mono">
              Stadium Commander
            </h1>
            <span className="text-[9px] font-black px-1.5 py-0.5 rounded border border-blue-500/20 bg-blue-500/5 text-blue-400 uppercase tracking-wider font-mono">
              Mission Control
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs font-mono">
        {/* Live Mode Toggle Switch */}
        <div className="flex items-center gap-2 border border-gray-800 bg-gray-900/40 px-3 py-1.5 rounded-lg select-none">
          <label className="text-[10px] text-gray-500 font-bold uppercase tracking-wider cursor-pointer flex items-center gap-2">
            <input
              type="checkbox"
              checked={liveMode}
              onChange={(e) => setLiveMode(e.target.checked)}
              className="accent-blue-500 cursor-pointer w-3.5 h-3.5"
            />
            Live mode (5s)
          </label>
        </div>

        {/* Network status */}
        <div
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-[10px] font-black tracking-wider uppercase transition-colors duration-300 ${
            connectionHealthy
              ? "bg-emerald-950/20 text-emerald-400 border-emerald-500/20"
              : "bg-rose-950/20 text-rose-400 border-rose-500/20 animate-pulse"
          }`}
        >
          <Radio className="w-3.5 h-3.5" />
          {connectionHealthy ? "ONLINE" : "OFFLINE"}
        </div>

        {/* Match status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-800 bg-gray-900/60">
          <Activity className="w-3.5 h-3.5 text-blue-400" />
          <span className="text-gray-500 font-bold uppercase">Phase:</span>
          <span className="text-gray-200 font-bold uppercase">{currentPhase}</span>
        </div>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          disabled={loading}
          className="p-1.5 border border-gray-800 bg-gray-900 hover:bg-gray-850 text-gray-400 hover:text-gray-200 rounded-lg disabled:opacity-50 transition-all flex items-center justify-center cursor-pointer"
          title="Manual refresh"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-400" : ""}`} />
        </button>
      </div>
    </nav>
  );
};
export default Navbar;
