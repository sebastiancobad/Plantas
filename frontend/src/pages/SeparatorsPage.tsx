import { useState } from "react";
import { separatorsApi } from "../services/api";

export default function SeparatorsPage() {
  const [sepType, setSepType] = useState("two_phase");
  const [orientation, setOrientation] = useState("horizontal");
  const [fluidType, setFluidType] = useState("crude_oil");
  const [gasDensity, setGasDensity] = useState("50");
  const [gasFlow, setGasFlow] = useState("1.0");
  const [gasVisc, setGasVisc] = useState("0.000015");
  const [oilDensity, setOilDensity] = useState("800");
  const [oilFlow, setOilFlow] = useState("0.01");
  const [oilVisc, setOilVisc] = useState("0.005");
  const [waterDensity, setWaterDensity] = useState("1020");
  const [waterFlow, setWaterFlow] = useState("0.005");
  const [pressure, setPressure] = useState("10");
  const [temperature, setTemperature] = useState("40");
  const [droplet, setDroplet] = useState("150");
  const [demister, setDemister] = useState(true);
  const [ldRatio, setLdRatio] = useState("4.0");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      const payload: Record<string, unknown> = {
        separator_type: sepType, orientation, fluid_type: fluidType,
        gas_phase: { density_kg_m3: Number(gasDensity), actual_flow_m3_s: Number(gasFlow), viscosity_Pa_s: Number(gasVisc) },
        oil_phase: { density_kg_m3: Number(oilDensity), flow_m3_s: Number(oilFlow), viscosity_Pa_s: Number(oilVisc) },
        operating_pressure_barg: Number(pressure), operating_temperature_C: Number(temperature),
        droplet_diameter_micron: Number(droplet), demister, LD_ratio: Number(ldRatio),
      };
      if (sepType === "three_phase") {
        payload.water_phase = { density_kg_m3: Number(waterDensity), flow_m3_s: Number(waterFlow) };
      }
      const res = await separatorsApi.designSeparator(payload);
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  const vessel = results ? (results as Record<string, unknown>).vessel_geometry as Record<string, unknown> | undefined : undefined;
  const gasCap = results ? (results as Record<string, unknown>).gas_capacity as Record<string, unknown> | undefined : undefined;
  const nozzles = results ? (results as Record<string, unknown>).nozzles as Record<string, unknown> | undefined : undefined;
  const demisterRes = results ? (results as Record<string, unknown>).demister as Record<string, unknown> | undefined : undefined;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Phase Separators</span></div>
        <h1>Phase Separator Sizing</h1>
        <p>2-phase & 3-phase separator design with Souders-Brown correlation.</p>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>Design Input</h2></div>

          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group">
              <label className="form-label">Separator Type</label>
              <select className="form-select" value={sepType} onChange={(e) => setSepType(e.target.value)}>
                <option value="two_phase">Two-Phase</option>
                <option value="three_phase">Three-Phase</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Orientation</label>
              <select className="form-select" value={orientation} onChange={(e) => setOrientation(e.target.value)}>
                <option value="horizontal">Horizontal</option>
                <option value="vertical">Vertical</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Fluid Type</label>
              <select className="form-select" value={fluidType} onChange={(e) => setFluidType(e.target.value)}>
                <option value="crude_oil">Crude Oil</option>
                <option value="light_oil">Light Oil</option>
                <option value="default">Default</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">L/D Ratio</label>
              <input className="form-input" type="number" step="0.5" value={ldRatio} onChange={(e) => setLdRatio(e.target.value)} />
            </div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Gas Phase</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Density <span className="unit">(kg/m&sup3;)</span></label><input className="form-input" type="number" value={gasDensity} onChange={(e) => setGasDensity(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Flow <span className="unit">(m&sup3;/s)</span></label><input className="form-input" type="number" step="0.1" value={gasFlow} onChange={(e) => setGasFlow(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Viscosity <span className="unit">(Pa&middot;s)</span></label><input className="form-input" type="number" step="0.000001" value={gasVisc} onChange={(e) => setGasVisc(e.target.value)} /></div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Oil Phase</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Density <span className="unit">(kg/m&sup3;)</span></label><input className="form-input" type="number" value={oilDensity} onChange={(e) => setOilDensity(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Flow <span className="unit">(m&sup3;/s)</span></label><input className="form-input" type="number" step="0.001" value={oilFlow} onChange={(e) => setOilFlow(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Viscosity <span className="unit">(Pa&middot;s)</span></label><input className="form-input" type="number" step="0.001" value={oilVisc} onChange={(e) => setOilVisc(e.target.value)} /></div>
          </div>

          {sepType === "three_phase" && (
            <>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Water Phase</h3>
              <div className="form-grid" style={{ marginBottom: 20 }}>
                <div className="form-group"><label className="form-label">Density <span className="unit">(kg/m&sup3;)</span></label><input className="form-input" type="number" value={waterDensity} onChange={(e) => setWaterDensity(e.target.value)} /></div>
                <div className="form-group"><label className="form-label">Flow <span className="unit">(m&sup3;/s)</span></label><input className="form-input" type="number" step="0.001" value={waterFlow} onChange={(e) => setWaterFlow(e.target.value)} /></div>
              </div>
            </>
          )}

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Operating Conditions</h3>
          <div className="form-grid">
            <div className="form-group"><label className="form-label">Pressure <span className="unit">(barg)</span></label><input className="form-input" type="number" value={pressure} onChange={(e) => setPressure(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Temperature <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={temperature} onChange={(e) => setTemperature(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Droplet Size <span className="unit">(&mu;m)</span></label><input className="form-input" type="number" value={droplet} onChange={(e) => setDroplet(e.target.value)} /></div>
            <div className="form-group">
              <label className="form-label">Demister Pad</label>
              <select className="form-select" value={demister ? "yes" : "no"} onChange={(e) => setDemister(e.target.value === "yes")}>
                <option value="yes">Yes</option><option value="no">No</option>
              </select>
            </div>
          </div>

          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleCalculate} disabled={loading}>
              {loading ? <><span className="spinner" /> Designing...</> : "Design Separator"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>Design Results</h2>{vessel && <span className="badge badge-success">Complete</span>}</div>
          {!vessel ? (
            <div className="empty-state"><div className="icon">&#x2B21;</div><p>Configure separator parameters and run the design calculation.</p></div>
          ) : (
            <>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Vessel Geometry</h3>
              <div className="results-grid" style={{ marginBottom: 20 }}>
                <div className="result-item highlight"><div className="label">Diameter</div><div className="value">{Number(vessel.diameter_m).toFixed(2)}<span className="unit">m</span></div></div>
                <div className="result-item highlight"><div className="label">Length</div><div className="value">{Number(vessel.length_m).toFixed(2)}<span className="unit">m</span></div></div>
                <div className="result-item"><div className="label">L/D Ratio</div><div className="value">{Number(vessel.LD_ratio).toFixed(1)}</div></div>
                <div className="result-item"><div className="label">Volume</div><div className="value">{Number(vessel.vessel_volume_m3).toFixed(2)}<span className="unit">m&sup3;</span></div></div>
              </div>
              {gasCap && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Gas Capacity</h3>
                  <div className="results-grid" style={{ marginBottom: 20 }}>
                    <div className="result-item"><div className="label">K (Souders-Brown)</div><div className="value">{Number(gasCap.souders_brown_K).toFixed(3)}</div></div>
                    <div className="result-item"><div className="label">Max Gas Vel.</div><div className="value">{Number(gasCap.max_gas_velocity_m_s).toFixed(2)}<span className="unit">m/s</span></div></div>
                    <div className="result-item"><div className="label">Actual Gas Vel.</div><div className="value">{Number(gasCap.actual_gas_velocity_m_s).toFixed(2)}<span className="unit">m/s</span></div></div>
                  </div>
                </>
              )}
              {nozzles && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Nozzle Sizes</h3>
                  <div className="results-grid" style={{ marginBottom: 20 }}>
                    <div className="result-item"><div className="label">Gas Inlet</div><div className="value">{Number(nozzles.gas_inlet_mm).toFixed(0)}<span className="unit">mm</span></div></div>
                    <div className="result-item"><div className="label">Gas Outlet</div><div className="value">{Number(nozzles.gas_outlet_mm).toFixed(0)}<span className="unit">mm</span></div></div>
                    <div className="result-item"><div className="label">Liquid Outlet</div><div className="value">{Number(nozzles.liquid_outlet_mm).toFixed(0)}<span className="unit">mm</span></div></div>
                  </div>
                </>
              )}
              {demisterRes && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Demister</h3>
                  <div className="results-grid">
                    <div className="result-item"><div className="label">Type</div><div className="value" style={{ fontSize: 14 }}>{String(demisterRes.type).replace(/_/g, " ")}</div></div>
                    <div className="result-item"><div className="label">Diameter</div><div className="value">{Number(demisterRes.diameter_m).toFixed(2)}<span className="unit">m</span></div></div>
                  </div>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
