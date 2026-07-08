import React from "react";
import Navbar from "../components/Navbar";

interface MainLayoutProps {
  children: React.ReactNode;
  navbarProps: {
    currentPhase: string;
    liveMode: boolean;
    setLiveMode: (live: boolean) => void;
    connectionHealthy: boolean;
    onRefresh: () => void;
    loading: boolean;
  };
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children, navbarProps }) => {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col font-sans selection:bg-blue-500/20">
      <Navbar {...navbarProps} />
      <main className="flex-1 w-full max-w-7xl mx-auto px-6 py-6 overflow-y-auto">
        {children}
      </main>
      <footer className="border-t border-gray-900 bg-gray-950 py-4 text-center text-[9px] text-gray-600 font-mono tracking-wider">
        FIFA WORLD CUP QATAR © 2026 OPERATIONS HUB. ALL SENSORS SYNCED.
      </footer>
    </div>
  );
};
export default MainLayout;
