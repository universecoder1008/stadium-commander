import { useState, useEffect, useCallback } from "react";
import { api } from "../services/api";
import type { SimulatorStatus, CommanderResponse, CombinedSituationReport } from "../types/api";

export type EventCategory =
  | "Crowd"
  | "Transport"
  | "Medical"
  | "Weather"
  | "Volunteer"
  | "AI Commander"
  | "System";

export type EventPriority = "LOW" | "MEDIUM" | "HIGH";

export interface EventData {
  time: string;
  category: EventCategory;
  title: string;
  description: string;
  priority: EventPriority;
}

export const useSimulation = () => {
  const [status, setStatus] = useState<SimulatorStatus>({
    current_phase: "T-120",
    phase_index: 0,
    total_phases: 8,
    latest_report: null,
  });
  const [decision, setDecision] = useState<CommanderResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [liveMode, setLiveMode] = useState<boolean>(false);
  const [connectionHealthy, setConnectionHealthy] = useState<boolean>(true);
  const [isAutoSimulating, setIsAutoSimulating] = useState<boolean>(false);
  const [events, setEvents] = useState<EventData[]>([]);
  const [toast, setToast] = useState<{ message: string; type: "error" | "success" } | null>(null);

  // Helper to trigger custom toast notifications
  const showToast = useCallback((message: string, type: "error" | "success" = "error") => {
    setToast({ message, type });
  }, []);

  // Dismiss toast
  const dismissToast = useCallback(() => {
    setToast(null);
  }, []);

  // Retrieve current simulator status
  const fetchStatus = useCallback(async () => {
    try {
      const data = await api.getStatus();
      setStatus(data);
      setConnectionHealthy(true);
      setError(null);

      // If we have a latest report but no decision in memory yet, do a check to analyze it
      if (data.latest_report && !decision) {
        try {
          const resDecision = await api.analyze(data.latest_report);
          setDecision(resDecision);
        } catch (err) {
          console.error("Failed to analyze latest report on initial sync:", err);
        }
      }
    } catch (err: any) {
      console.error("Failed to fetch simulator status:", err);
      setConnectionHealthy(false);
      const msg = "Failed to sync with backend server. Is it online?";
      setError(msg);
      showToast(msg, "error");
    }
  }, [decision, showToast]);

  // Create timeline event helper
  const addTimelineEvent = useCallback((report: CombinedSituationReport, dec: CommanderResponse) => {
    const priorityMap: Record<string, EventPriority> = {
      LOW: "LOW",
      MEDIUM: "MEDIUM",
      HIGH: "HIGH",
      CRITICAL: "HIGH",
    };

    const newEvent: EventData = {
      time: report.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      category: "AI Commander",
      title: `Match Phase Advanced: ${report.match_phase}`,
      description: `AI Commander Priority: ${dec.priority}. Top Risk Vector: ${dec.top_risk}. Summary: ${dec.summary}`,
      priority: priorityMap[dec.priority] || "LOW",
    };

    setEvents((prev) => [newEvent, ...prev]);
  }, []);

  // Advance simulation phase
  const simulateTimeline = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const resDecision = await api.simulate();
      setDecision(resDecision);

      const updatedStatus = await api.getStatus();
      setStatus(updatedStatus);

      if (updatedStatus.latest_report) {
        addTimelineEvent(updatedStatus.latest_report, resDecision);
      }

      setConnectionHealthy(true);
    } catch (err: any) {
      console.error("Simulation run failed:", err);
      const msg = "Timeline progression failed. Please retry.";
      setError(msg);
      showToast(msg, "error");
      setIsAutoSimulating(false);
    } finally {
      setLoading(false);
    }
  }, [addTimelineEvent, showToast]);

  // Start simulation loop
  const startSimulation = useCallback(() => {
    setIsAutoSimulating(true);
  }, []);

  // Pause simulation loop
  const pauseSimulation = useCallback(() => {
    setIsAutoSimulating(false);
  }, []);

  // Reset simulation by advancing timeline to wrap around back to index 0
  const resetSimulation = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let currentStatus = await api.getStatus();
      let safetyCounter = 0;
      while (currentStatus.phase_index !== 0 && safetyCounter < 10) {
        await api.simulate();
        currentStatus = await api.getStatus();
        safetyCounter++;
      }
      setDecision(null);
      setEvents([]);
      setIsAutoSimulating(false);
      await fetchStatus();
      showToast("Simulation reset successfully", "success");
    } catch (err: any) {
      console.error("Reset simulation failed:", err);
      const msg = "Reset failed. Please check backend connection.";
      setError(msg);
      showToast(msg, "error");
    } finally {
      setLoading(false);
    }
  }, [fetchStatus, showToast]);

  // Auto-dismiss toast
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => {
        setToast(null);
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  // Polling for liveMode
  useEffect(() => {
    fetchStatus();

    let intervalId: any;
    if (liveMode) {
      intervalId = setInterval(() => {
        fetchStatus();
      }, 5000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [liveMode, fetchStatus]);

  // Simulation interval for Auto Simulation
  useEffect(() => {
    let timer: any;
    if (isAutoSimulating && !loading && !error) {
      timer = setTimeout(() => {
        simulateTimeline();
      }, 5000);
    }
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [isAutoSimulating, loading, error, simulateTimeline]);

  return {
    status,
    decision,
    loading,
    error,
    liveMode,
    connectionHealthy,
    isAutoSimulating,
    events,
    toast,
    setLiveMode,
    fetchStatus,
    simulateTimeline,
    startSimulation,
    pauseSimulation,
    resetSimulation,
    dismissToast,
  };
};

export default useSimulation;
