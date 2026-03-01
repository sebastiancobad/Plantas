import { useState } from "react";
import { psvApi } from "../services/api";

export default function PSVPage() {
  const [fluidPhase, setFluidPhase] = useState("vapor");
  const [scenario, setScenario] = useState("blocked_outlet");
  const [massFlow, setMassFlow] = useState("5000");
  const [tempK, setTempK] = useState("400");
  const [molWeight, setMolWeight] = useState("28");
  const [compZ, setCompZ] = useState("0.95");
  const [kRatio, setKRatio] = useState("1.3");
  const [volFlow, setVolFlow] = useState("10");
  const [liquidDensity, setLiquidDensity] = useState("800");
  const [viscCp, setViscCp] = useState("1.0");
  const [setPressureVal, setSetPressureVal] = useState("1000");
  const [backPressure, setBackPressure] = useState("101.325");
  const [valveType, setValveType] = useState("conventional");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      const payload: Record<string, unknown> = {
        scenario,
        fluid_phase: fluidPhase,
        set_pressure_kPa: Number(setPressureVal),
        back_pressure_kPa: Number(backPressure),
        valve_type: valveType,
      };
      if (fluidPhase === "vapor" || fluidPhase === "gas") {
        payload.relief_rate_kg_hr = Number(massFlow);
        payload.relieving_temperature_K = Number(tempK);
        payload.molecular_weight = Number(molWeight);
        payload.compressibility_Z = Number(compZ);
        payload.cp_cv_ratio = Number(kRatio);
      } else {
        payload.relief_rate_m3_hr = Number(volFlow);
        payload.density_kg_m3 = Number(liquidDensity);
        payload.viscosity_cP = Number(viscCp);
      }
      const res = await psvApi.sizePSV(payload);
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  const sizing = results?.valve_sizing as Record<string, unknown> | undefined;
  const orifice = sizing?.selected_orifice as Record<string, unknown> | undefined;
  const spec = results?.valve_specification as Record<string, unknown> | undefined;
  const compliance = results?.compliance as Record<string, unknown> | undefined;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Safety Relief Valves</span></div>
        <h1>Safety Relief Valve Sizing</h1>
        <p>API 520/521 sizing for gas, liquid, and fire case scenarios.</p>
      </div>

      <div className="tabs">
        <button className={`tab ${fluidPhase === "vapor" ? "active" : ""}`} onClick={() => setFluidPhase("vapor")}>Gas / Vapor</button>
        <button className={`tab ${fluidPhase === "liquid" ? "active" : ""}`} onClick={() => setFluidPhase("liquid")}>Liquid</button>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>Valve Input</h2></div>

          {fluidPhase === "vapor" ? (
            <div className="form-grid" style={{ marginBottom: 20 }}>
              <div className="form-group"><label className="form-label">Relief Rate <span className="unit">(kg/hr)</span></label><input className="form-input" type="number" value={massFlow} onChange={(e) => setMassFlow(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Relieving Temp <span className="unit">(K)</span></label><input className="form-input" type="number" value={tempK} onChange={(e) => setTempK(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Molecular Weight</label><input className="form-input" type="number" value={molWeight} onChange={(e) => setMolWeight(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Z (compressibility)</label><input className="form-input" type="number" step="0.01" value={compZ} onChange={(e) => setCompZ(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Cp/Cv ratio</label><input className="form-input" type="number" step="0.01" value={kRatio} onChange={(e) => setKRatio(e.target.value)} /></div>
            </div>
          ) : (
            <div className="form-grid" style={{ marginBottom: 20 }}>
              <div className="form-group"><label className="form-label">Relief Rate <span className="unit">(m&sup3;/hr)</span></label><input className="form-input" type="number" value={volFlow} onChange={(e) => setVolFlow(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Density <span className="unit">(kg/m&sup3;)</span></label><input className="form-input" type="number" value={liquidDensity} onChange={(e) => setLiquidDensity(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Viscosity <span className="unit">(cP)</span></label><input className="form-input" type="number" step="0.1" value={viscCp} onChange={(e) => setViscCp(e.target.value)} /></div>
            </div>
          )}

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Valve Configuration</h3>
          <div className="form-grid">
            <div className="form-group"><label className="form-label">Scenario</label>
              <select className="form-select" value={scenario} onChange={(e) => setScenario(e.target.value)}>
                <option value="blocked_outlet">Blocked Outlet</option>
                <option value="fire">Fire Case</option>
                <option value="control_valve_failure">Control Valve Failure</option>
                <option value="tube_rupture">Tube Rupture</option>
              </select>
            </div>
            <div className="form-group"><label className="form-label">Set Pressure <span className="unit">(kPa abs)</span></label><input className="form-input" type="number" value={setPressureVal} onChange={(e) => setSetPressureVal(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Back Pressure <span className="unit">(kPa abs)</span></label><input className="form-input" type="number" value={backPressure} onChange={(e) => setBackPressure(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Valve Type</label>
              <select className="form-select" value={valveType} onChange={(e) => setValveType(e.target.value)}>
                <option value="conventional">Conventional</option><option value="balanced_bellows">Balanced Bellows</option>
              </select>
            </div>
          </div>

          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleCalculate} disabled={loading}>
              {loading ? <><span className="spinner" /> Sizing...</> : "Size PSV"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>Sizing Results</h2>{sizing && <span className="badge badge-success">Sized</span>}</div>
          {!sizing ? (
            <div className="empty-state"><div className="icon">&#x26A0;</div><p>Specify relief conditions and click Size PSV.</p></div>
          ) : (
            <>
              <div className="results-grid" style={{ marginBottom: 16 }}>
                <div className="result-item highlight"><div className="label">Required Area</div><div className="value">{Number(sizing.required_area_mm2).toFixed(1)}<span className="unit">mm&sup2;</span></div></div>
                {orifice && (
                  <>
                    <div className="result-item highlight"><div className="label">Selected Orifice</div><div className="value" style={{ fontSize: 24 }}>{String(orifice.designation)}</div></div>
                    <div className="result-item"><div className="label">Orifice Area</div><div className="value">{Number(orifice.area_mm2).toFixed(1)}<span className="unit">mm&sup2;</span></div></div>
                  </>
                )}
                <div className="result-item"><div className="label">Flow Type</div><div className="value" style={{ fontSize: 14, textTransform: "capitalize" }}>{String(sizing.flow_type)}</div></div>
                <div className="result-item"><div className="label">Relief Rate</div><div className="value">{Number(sizing.relief_rate_kg_hr).toFixed(0)}<span className="unit">kg/hr</span></div></div>
              </div>

              {spec && (
                <div className="results-grid" style={{ marginBottom: 16 }}>
                  <div className="result-item"><div className="label">Back Pressure</div><div className="value">{Number(spec.backpressure_percent).toFixed(1)}<span className="unit">%</span></div></div>
                  <div className="result-item"><div className="label">Kb Correction</div><div className="value">{Number(spec.Kb_correction).toFixed(3)}</div></div>
                  <div className="result-item"><div className="label">Relieving Pressure</div><div className="value">{Number(spec.relieving_pressure_kPa).toFixed(0)}<span className="unit">kPa</span></div></div>
                </div>
              )}

              {compliance && (
                <div className="flex gap-8" style={{ flexWrap: "wrap" }}>
                  {Object.entries(compliance).map(([k, v]) => (
                    <span key={k} className={`badge ${String(v) === "PASS" ? "badge-success" : "badge-info"}`}>
                      {k.replace(/_/g, " ").toUpperCase()}: {String(v)}
                    </span>
                  ))}
                </div>
              )}

              {results?.warnings && (results.warnings as string[]).length > 0 && (
                <div className="mt-16" style={{ fontSize: 12, color: "var(--warning)" }}>
                  {(results.warnings as string[]).map((w, i) => <div key={i}>&#x26A0; {w}</div>)}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
