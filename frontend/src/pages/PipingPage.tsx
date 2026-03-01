import { useState } from "react";
import { pipingApi } from "../services/api";

interface Fitting { type: string; count: number; }

const FITTING_TYPES = [
  "elbow_90_lr", "elbow_90_sr", "elbow_45", "tee_run", "tee_branch",
  "gate_valve", "globe_valve", "check_valve", "ball_valve", "butterfly_valve",
  "reducer", "expander", "entrance_sharp", "exit",
];

export default function PipingPage() {
  const [mode, setMode] = useState<"size" | "check">("size");
  const [density, setDensity] = useState("1000");
  const [viscosity, setViscosity] = useState("0.001");
  const [massFlow, setMassFlow] = useState("5.0");
  const [fluidPhase, setFluidPhase] = useState("liquid");
  const [material, setMaterial] = useState("carbon_steel");
  const [schedule, setSchedule] = useState("40");
  const [length, setLength] = useState("100");
  const [elevation, setElevation] = useState("0");
  const [npsInches, setNpsInches] = useState("4");
  const [maxDp, setMaxDp] = useState("2.0");
  const [fittings, setFittings] = useState<Fitting[]>([
    { type: "elbow_90_lr", count: 4 },
    { type: "gate_valve", count: 2 },
  ]);
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addFitting = () => setFittings([...fittings, { type: "elbow_90_lr", count: 1 }]);
  const removeFitting = (i: number) => setFittings(fittings.filter((_, idx) => idx !== i));

  const handleCalculate = async () => {
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const payload: Record<string, unknown> = {
        mode,
        fluid: { density_kg_m3: Number(density), viscosity_Pa_s: Number(viscosity), mass_flow_kg_s: Number(massFlow), phase: fluidPhase },
        pipe: { material, schedule, length_m: Number(length), elevation_change_m: Number(elevation), ...(mode === "check" ? { nps_inches: Number(npsInches) } : {}) },
        fittings,
        max_pressure_drop_bar: Number(maxDp),
      };
      const res = await pipingApi.sizePipe(payload);
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data)
        : msg);
    } finally {
      setLoading(false);
    }
  };

  const pipe = results && (mode === "size"
    ? (results as Record<string, unknown>).selected_pipe as Record<string, unknown> | undefined
    : (results as Record<string, unknown>).hydraulics as Record<string, unknown> | undefined);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Pipe Sizing & Hydraulics</span></div>
        <h1>Pipe Sizing & Hydraulics</h1>
        <p>Darcy-Weisbach pressure drop with Colebrook-White friction factor.</p>
      </div>

      <div className="tabs">
        <button className={`tab ${mode === "size" ? "active" : ""}`} onClick={() => setMode("size")}>Auto Size</button>
        <button className={`tab ${mode === "check" ? "active" : ""}`} onClick={() => setMode("check")}>Check Existing</button>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header">
            <h2>Fluid & Pipe Data</h2>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Fluid Properties</h3>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Density <span className="unit">(kg/m&sup3;)</span></label>
              <input className="form-input" type="number" value={density} onChange={(e) => setDensity(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Viscosity <span className="unit">(Pa&middot;s)</span></label>
              <input className="form-input" type="number" step="0.0001" value={viscosity} onChange={(e) => setViscosity(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Mass Flow <span className="unit">(kg/s)</span></label>
              <input className="form-input" type="number" value={massFlow} onChange={(e) => setMassFlow(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Phase</label>
              <select className="form-select" value={fluidPhase} onChange={(e) => setFluidPhase(e.target.value)}>
                <option value="liquid">Liquid</option>
                <option value="vapor">Vapor / Gas</option>
                <option value="two_phase">Two-Phase</option>
              </select>
            </div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", margin: "20px 0 12px" }}>Pipe Configuration</h3>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Material</label>
              <select className="form-select" value={material} onChange={(e) => setMaterial(e.target.value)}>
                <option value="carbon_steel">Carbon Steel</option>
                <option value="stainless_steel">Stainless Steel</option>
                <option value="pvc">PVC</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Schedule</label>
              <select className="form-select" value={schedule} onChange={(e) => setSchedule(e.target.value)}>
                <option value="40">Schedule 40</option>
                <option value="80">Schedule 80</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Length <span className="unit">(m)</span></label>
              <input className="form-input" type="number" value={length} onChange={(e) => setLength(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Elevation Change <span className="unit">(m)</span></label>
              <input className="form-input" type="number" value={elevation} onChange={(e) => setElevation(e.target.value)} />
            </div>
            {mode === "check" && (
              <div className="form-group">
                <label className="form-label">NPS <span className="unit">(inches)</span></label>
                <input className="form-input" type="number" value={npsInches} onChange={(e) => setNpsInches(e.target.value)} />
              </div>
            )}
            {mode === "size" && (
              <div className="form-group">
                <label className="form-label">Max \u0394P <span className="unit">(bar)</span></label>
                <input className="form-input" type="number" step="0.1" value={maxDp} onChange={(e) => setMaxDp(e.target.value)} />
              </div>
            )}
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", margin: "20px 0 12px" }}>Fittings</h3>
          <table className="data-table" style={{ marginBottom: 8 }}>
            <thead><tr><th>Fitting Type</th><th>Count</th><th></th></tr></thead>
            <tbody>
              {fittings.map((f, i) => (
                <tr key={i}>
                  <td>
                    <select className="form-select" value={f.type} onChange={(e) => {
                      const u = [...fittings]; u[i] = { ...f, type: e.target.value }; setFittings(u);
                    }}>
                      {FITTING_TYPES.map((t) => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
                    </select>
                  </td>
                  <td><input className="form-input" type="number" min="1" value={f.count} onChange={(e) => {
                    const u = [...fittings]; u[i] = { ...f, count: Number(e.target.value) }; setFittings(u);
                  }} /></td>
                  <td><button className="btn btn-secondary btn-sm" onClick={() => removeFitting(i)} style={{ padding: "0 8px" }}>&times;</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className="btn btn-secondary btn-sm" onClick={addFitting}>+ Add Fitting</button>

          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleCalculate} disabled={loading}>
              {loading ? <><span className="spinner" /> Calculating...</> : mode === "size" ? "Size Pipe" : "Check Hydraulics"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header">
            <h2>Results</h2>
            {pipe && <span className="badge badge-success">Calculated</span>}
          </div>
          {!pipe ? (
            <div className="empty-state">
              <div className="icon">&#x1F6E0;</div>
              <p>Configure fluid and pipe parameters, then run the calculation.</p>
            </div>
          ) : (
            <>
              {results && (results as Record<string, unknown>).warnings && ((results as Record<string, unknown>).warnings as string[]).length > 0 && (
                <div style={{ marginBottom: 16, padding: 10, background: "var(--warning-light)", borderRadius: "var(--radius-sm)", fontSize: 12, color: "var(--warning)" }}>
                  {((results as Record<string, unknown>).warnings as string[]).map((w: string, i: number) => <div key={i}>{w}</div>)}
                </div>
              )}
              <div className="results-grid">
                {mode === "size" && (
                  <div className="result-item highlight">
                    <div className="label">Selected NPS</div>
                    <div className="value">{String((pipe as Record<string, unknown>).nps_inches)}<span className="unit">in</span></div>
                  </div>
                )}
                <div className="result-item">
                  <div className="label">Velocity</div>
                  <div className="value">{Number((pipe as Record<string, unknown>).velocity_m_s ?? (pipe as Record<string, unknown>).velocity_m_s).toFixed(2)}<span className="unit">m/s</span></div>
                </div>
                <div className="result-item">
                  <div className="label">Reynolds Number</div>
                  <div className="value" style={{ fontSize: 16 }}>{Number((pipe as Record<string, unknown>).reynolds ?? (pipe as Record<string, unknown>).reynolds_number).toFixed(0)}</div>
                </div>
                <div className="result-item">
                  <div className="label">Friction Factor</div>
                  <div className="value" style={{ fontSize: 16 }}>{Number((pipe as Record<string, unknown>).friction_factor ?? (pipe as Record<string, unknown>).friction_factor_darcy).toFixed(5)}</div>
                </div>
                <div className="result-item">
                  <div className="label">\u0394P Friction</div>
                  <div className="value">{Number((pipe as Record<string, unknown>).dp_friction_bar).toFixed(3)}<span className="unit">bar</span></div>
                </div>
                <div className="result-item">
                  <div className="label">\u0394P Fittings</div>
                  <div className="value">{Number((pipe as Record<string, unknown>).dp_fittings_bar).toFixed(3)}<span className="unit">bar</span></div>
                </div>
                <div className="result-item">
                  <div className="label">\u0394P Elevation</div>
                  <div className="value">{Number((pipe as Record<string, unknown>).dp_elevation_bar).toFixed(3)}<span className="unit">bar</span></div>
                </div>
                <div className="result-item highlight">
                  <div className="label">\u0394P Total</div>
                  <div className="value">{Number((pipe as Record<string, unknown>).dp_total_bar).toFixed(3)}<span className="unit">bar</span></div>
                </div>
              </div>
              {mode === "size" && (
                <div className="mt-16 flex gap-8">
                  {Boolean((pipe as Record<string, unknown>).velocity_ok) && <span className="badge badge-success">Velocity OK</span>}
                  {Boolean((pipe as Record<string, unknown>).dp_ok) && <span className="badge badge-success">{"\u0394P OK"}</span>}
                  {!((pipe as Record<string, unknown>).velocity_ok) && <span className="badge badge-warning">Velocity Warning</span>}
                  {!((pipe as Record<string, unknown>).dp_ok) && <span className="badge badge-warning">{"\u0394P Exceeded"}</span>}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
