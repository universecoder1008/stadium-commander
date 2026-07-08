import { useState, useCallback } from "react";
import { api } from "../services/api";
import type { CombinedSituationReport, CommanderResponse } from "../types/api";

export const useCommander = () => {
  const [decision, setDecision] = useState<CommanderResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Directly analyze a consolidated situation report
  const analyzeReport = useCallback(async (report: CombinedSituationReport) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.analyze(report);
      setDecision(data);
      return data;
    } catch (err: any) {
      console.error("Direct report analysis failed:", err);
      setError("Commander reasoning request failed.");
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    decision,
    loading,
    error,
    analyzeReport,
  };
};

export default useCommander;
