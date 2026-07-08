import axios from "axios";

import type {
  CombinedSituationReport,
  CommanderResponse,
  SimulatorStatus,
} from "../types/api";

// -------------------------------------------------------------
// Axios Reusable Client Setup
// -------------------------------------------------------------

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export const api = {
  /**
   * Fetches service status and root configuration.
   */
  async getRoot() {
    const response = await apiClient.get("/");
    return response.data;
  },

  /**
   * Fetches application health checks.
   */
  async getHealth() {
    const response = await apiClient.get("/health");
    return response.data;
  },

  /**
   * Queries the current active timeline phase and latest situation report.
   */
  async getStatus(): Promise<SimulatorStatus> {
    const response = await apiClient.get<SimulatorStatus>("/status");
    return response.data;
  },

  /**
   * Advances the simulation timeline index and triggers the analysis loop.
   */
  async simulate(): Promise<CommanderResponse> {
    const response = await apiClient.post<CommanderResponse>("/simulate");
    return response.data;
  },

  /**
   * Direct trigger for Commander Agent analysis on an existing situation report.
   */
  async analyze(report: CombinedSituationReport): Promise<CommanderResponse> {
    const response = await apiClient.post<CommanderResponse>("/analyze", report);
    return response.data;
  },
};

export default api;
