/**
 * ChemScale API Client.
 *
 * Centralized HTTP client for all backend communication.
 * Every module-specific service file imports and uses this client.
 */

import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60000, // 60s for heavy thermo calculations
});

// ── Thermodynamic Properties ──────────────────────────────────────

export interface ComponentInput {
  name: string;
  mole_fraction: number;
}

export interface ThermoPropertyRequest {
  components: ComponentInput[];
  temperature_K: number;
  pressure_Pa: number;
  eos_model?: "PR" | "SRK";
  phase?: "auto" | "vapor" | "liquid";
}

export const thermoApi = {
  calculateProperties: (data: ThermoPropertyRequest) =>
    api.post("/thermo/properties", data),

  getComponents: () => api.get("/thermo/components"),
};

// ── Heat Exchanger Design ─────────────────────────────────────────

export const heatExchangerApi = {
  design: (data: Record<string, unknown>) =>
    api.post("/heat-exchangers/design", data),

  getTemTypes: () => api.get("/heat-exchangers/tema-types"),
};

// ── Economic Evaluation ───────────────────────────────────────────

export const economicsApi = {
  estimateCapex: (data: Record<string, unknown>) =>
    api.post("/economics/capex", data),

  estimateUtilities: (data: Record<string, unknown>) =>
    api.post("/economics/utilities", data),

  estimateOpex: (data: Record<string, unknown>) =>
    api.post("/economics/opex", data),

  getCepci: (year: number) => api.get(`/economics/cepci/${year}`),

  fullEvaluation: (data: Record<string, unknown>) =>
    api.post("/economics/evaluate", data),
};

export default api;
