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

// ── Pipe Sizing & Hydraulics ──────────────────────────────────────

export const pipingApi = {
  sizePipe: (data: Record<string, unknown>) =>
    api.post("/piping/size", data),
  getSchedules: () => api.get("/piping/schedules"),
  getRoughness: () => api.get("/piping/roughness"),
};

// ── Material Selection ───────────────────────────────────────────

export const materialsApi = {
  selectMaterial: (data: Record<string, unknown>) =>
    api.post("/materials/select", data),
  co2Corrosion: (data: Record<string, unknown>) =>
    api.post("/materials/co2-corrosion", data),
  h2sSourCheck: (data: Record<string, unknown>) =>
    api.post("/materials/h2s-check", data),
  getMaterials: () => api.get("/materials/list"),
};

// ── Plant Layout ─────────────────────────────────────────────────

export const plantLayoutApi = {
  generateLayout: (data: Record<string, unknown>) =>
    api.post("/plant-layout/generate", data),
  getSpacing: (eq1: string, eq2: string) =>
    api.get(`/plant-layout/spacing?equipment1=${eq1}&equipment2=${eq2}`),
};

// ── Phase Separators ─────────────────────────────────────────────

export const separatorsApi = {
  designSeparator: (data: Record<string, unknown>) =>
    api.post("/separators/design", data),
  getKFactors: () => api.get("/separators/k-factors"),
};

// ── Pump Selection ───────────────────────────────────────────────

export const pumpsApi = {
  sizePump: (data: Record<string, unknown>) =>
    api.post("/pumps/design", data),
  getMotorSizes: () => api.get("/pumps/motor-sizes"),
};

// ── Heat Exchanger Design ─────────────────────────────────────────

export const heatExchangerApi = {
  design: (data: Record<string, unknown>) =>
    api.post("/heat-exchangers/design", data),
  getTemTypes: () => api.get("/heat-exchangers/tema-types"),
};

// ── Distillation Column ──────────────────────────────────────────

export const distillationApi = {
  designColumn: (data: Record<string, unknown>) =>
    api.post("/distillation/design", data),
  getTrayTypes: () => api.get("/distillation/tray-types"),
  getPackingTypes: () => api.get("/distillation/packing-types"),
};

// ── Safety Relief Valves (PSV) ───────────────────────────────────

export const psvApi = {
  sizePSV: (data: Record<string, unknown>) =>
    api.post("/psv/size", data),
  getOrifices: () => api.get("/psv/orifices"),
};

// ── Process Safety ───────────────────────────────────────────────

export const processSafetyApi = {
  calculateDowFEI: (data: Record<string, unknown>) =>
    api.post("/process-safety/dow-fei", data),
  generateHAZOP: (data: Record<string, unknown>) =>
    api.post("/process-safety/hazop", data),
  getCaseStudies: () => api.get("/process-safety/case-studies"),
  getISDChecklist: () => api.get("/process-safety/isd-checklist"),
};

// ── Advanced Process Control ─────────────────────────────────────

export const apcApi = {
  tunePID: (data: Record<string, unknown>) =>
    api.post("/apc/tune-pid", data),
  getControlStrategy: (unitOp: string) =>
    api.get(`/apc/control-strategy/${unitOp}`),
};

// ── P&ID Development ─────────────────────────────────────────────

export const pidApi = {
  generatePID: (data: Record<string, unknown>) =>
    api.post("/pid/generate", data),
  getSymbols: () => api.get("/pid/symbols"),
  getLetterCodes: () => api.get("/pid/letter-codes"),
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
