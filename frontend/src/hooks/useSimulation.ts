import { useState, useEffect, useCallback } from "react";
import { api } from "../services/api";
import type {
  SimulatorStatus,
  CommanderResponse,
  CombinedSituationReport,
  EventData,
  ToastData,
  EventPriority,
} from "../types/api";

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
  const [toasts, setToasts] = useState<ToastData[]>([]);
  const [latencyMs, setLatencyMs] = useState<number>(45);

  // Add toast notification helper with individual self-destruct timers
  const addToast = useCallback((message: string, type: ToastData["type"] = "info") => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // Retrieve current simulator status
  const fetchStatus = useCallback(async () => {
    const t0 = Date.now();
    try {
      const data = await api.getStatus();
      setStatus(data);
      setLatencyMs(Date.now() - t0);
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
      addToast(msg, "error");
    }
  }, [decision, addToast]);

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
      timestampMs: Date.now(),
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
    const t0 = Date.now();
    try {
      const resDecision = await api.simulate();
      setDecision(resDecision);

      const updatedStatus = await api.getStatus();
      setStatus(updatedStatus);
      setLatencyMs(Date.now() - t0);

      const report = updatedStatus.latest_report;
      if (report) {
        // 1. Append to timeline list
        addTimelineEvent(report, resDecision);

        // 2. Trigger multi-toasts alerts
        addToast(`Simulation advanced: ${report.match_phase} phase started`, "success");
        addToast(`AI Recommendation updated: ${resDecision.top_risk}`, "info");

        if (report.weather && report.weather.risk !== "LOW") {
          addToast(
            `Weather Warning: ${report.weather.prediction.expected_operational_impact}`,
            "warning"
          );
        }
        if (report.medical && (report.medical.risk !== "LOW" || report.medical.prediction.resource_shortage)) {
          addToast("Medical Alert: High first aid response load detected!", "warning");
        }
        if (report.transport && report.transport.risk !== "LOW") {
          addToast(`Transport Alert: Parking occupies ${report.transport.parking_occupancy_percent.toFixed(0)}%`, "warning");
        }
      }

      setConnectionHealthy(true);
    } catch (err: any) {
      console.error("Simulation run failed:", err);
      const msg = "Timeline progression failed. Please retry.";
      setError(msg);
      addToast(msg, "error");
      setIsAutoSimulating(false);
    } finally {
      setLoading(false);
    }
  }, [addTimelineEvent, addToast]);

  // Start simulation loop
  const startSimulation = useCallback(() => {
    setIsAutoSimulating(true);
    addToast("Simulation auto-run started (5s interval)", "success");
  }, [addToast]);

  // Pause simulation loop
  const pauseSimulation = useCallback(() => {
    setIsAutoSimulating(false);
    addToast("Simulation auto-run paused", "info");
  }, [addToast]);

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
      
      // Keep initial system start log on reset
      setEvents([
        {
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          timestampMs: Date.now(),
          category: "System",
          title: "Simulation Started",
          description: "FastAPI operational sensors online. Telemetry streams successfully established.",
          priority: "LOW",
        },
      ]);

      setIsAutoSimulating(false);
      await fetchStatus();
      addToast("Simulation timeline reset successfully", "success");
    } catch (err: any) {
      console.error("Reset simulation failed:", err);
      const msg = "Reset failed. Please check backend connection.";
      setError(msg);
      addToast(msg, "error");
    } finally {
      setLoading(false);
    }
  }, [fetchStatus, addToast]);

  // Boot telemetry event on first mounting
  useEffect(() => {
    setEvents([
      {
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        timestampMs: Date.now(),
        category: "System",
        title: "Simulation Started",
        description: "FastAPI operational sensors online. Telemetry streams successfully established.",
        priority: "LOW",
      },
    ]);
  }, []);

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
    toasts,
    setLiveMode,
    fetchStatus,
    simulateTimeline,
    startSimulation,
    pauseSimulation,
    resetSimulation,
    dismissToast,
    latencyMs,
  };
};

export default useSimulation;
