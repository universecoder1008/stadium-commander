export interface Prediction {
  gate?: string;
  issue?: string;
  eta_minutes?: number;
}

export interface CrowdResponse {
  risk: string;
  confidence: number;
  predictions: Prediction[];
  reasoning: string[];
}

export interface TransportPrediction {
  remaining_spectators: number;
  estimated_arrival_minutes: number;
}

export interface TransportResponse {
  risk: string;
  confidence: number;
  parking_occupancy_percent: number;
  metro_status: string;
  bus_status: string;
  arrival_prediction: TransportPrediction;
  reasoning: string[];
}

export interface MedicalPrediction {
  predicted_incidents: number;
  resource_shortage: boolean;
  estimated_response_time: number;
}

export interface MedicalResponse {
  risk: string;
  confidence: number;
  ambulance_utilization_percent: number;
  medical_staff_utilization_percent: number;
  prediction: MedicalPrediction;
  reasoning: string[];
}

export interface WeatherPrediction {
  expected_operational_impact: string;
  expected_delay_minutes: number;
  recommendation: string;
}

export interface WeatherResponse {
  risk: string;
  confidence: number;
  weather_status: string;
  prediction: WeatherPrediction;
  reasoning: string[];
}

export interface VolunteerPrediction {
  expected_shortage: number;
  recommended_redeployment: string;
  predicted_response_time: number;
}

export interface VolunteerResponse {
  risk: string;
  confidence: number;
  volunteer_utilization_percent: number;
  coverage_percent: number;
  prediction: VolunteerPrediction;
  reasoning: string[];
}

export interface CombinedSituationReport {
  timestamp: string;
  match_phase: string;
  crowd?: CrowdResponse;
  transport?: TransportResponse;
  medical?: MedicalResponse;
  weather?: WeatherResponse;
  volunteer?: VolunteerResponse;
  system_status: "NORMAL" | "WARNING" | "CRITICAL";
  version: string;
  analyzers_completed: string[];
  analyzers_failed: Record<string, string>;
  processing_time_ms: number;
}

export interface CommanderResponse {
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  top_risk: string;
  summary: string;
  actions: string[];
  estimated_impact: string;
  confidence: number;
}

export interface SimulatorStatus {
  current_phase: string;
  phase_index: number;
  total_phases: number;
  latest_report: CombinedSituationReport | null;
}
