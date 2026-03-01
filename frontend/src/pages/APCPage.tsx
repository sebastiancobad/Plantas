import { useState } from "react";
import { apcApi } from "../services/api";

export default function APCPage() {
  const [tab, setTab] = useState<"tune" | "strategy">("tune");
  const [gain, setGain] = useState("1.5");
  const [tau, setTau] = useState("60");
  const [theta, setTheta] = useState("10");
  const [loopType, setLoopType] = useState("PID");
  const [lambdaFactor, setLambdaFactor] = useState("3.0");
  const [unitType, setUnitType] = useState("heat_exchanger");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      let res;
      if (tab === "tune") {
        res = await apcApi.tunePID({
          process_gain: Number(gain),
          time_constant_s: Number(tau),
          dead_time_s: Number(theta),
          controller_type: loopType,
          lambda_factor: Number(lambdaFactor),
        });
      } else {
        res = await apcApi.getControlStrategy({ unit_type: unitType });
      }
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  // Extract tuning results - backend returns { tuning_results: { ziegler_nichols, cohen_coon, lambda_imc } }
  const tuningResults = results?.tuning_results as Record<string, Record<string, unknown>> | undefined;
  const processModel = results?.process_model as Record<string, unknown> | undefined;
  const recommendation = results?.recommendation as string | undefined;

  // Extract strategy results - backend returns { strategy: { primary, enhanced, advanced, typical_loops } }
  const strategy = results?.strategy as Record<string, unknown> | undefined;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Advanced Process Control</span></div>
        <h1>Advanced Process Control</h1>
        <p>PID tuning and control strategy selection for process equipment.</p>
      </div>

      <div className="tabs">
        <button className={`tab ${tab === "tune" ? "active" : ""}`} onClick={() => { setTab("tune"); setResults(null); }}>PID Tuning</button>
        <button className={`tab ${tab === "strategy" ? "active" : ""}`} onClick={() => { setTab("strategy"); setResults(null); }}>Control Strategy</button>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>{tab === "tune" ? "Process Model (FOPDT)" : "Unit Operation"}</h2></div>
          {tab === "tune" ? (
            <div className="form-grid">
              <div className="form-group"><label className="form-label">Process Gain K</label><input className="form-input" type="number" step="0.1" value={gain} onChange={(e) => setGain(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Time Constant &tau; <span className="unit">(s)</span></label><input className="form-input" type="number" value={tau} onChange={(e) => setTau(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Dead Time &theta; <span className="unit">(s)</span></label><input className="form-input" type="number" value={theta} onChange={(e) => setTheta(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Controller Type</label>
                <select className="form-select" value={loopType} onChange={(e) => setLoopType(e.target.value)}>
                  <option value="P">P</option><option value="PI">PI</option><option value="PID">PID</option>
                </select>
              </div>
              <div className="form-group"><label className="form-label">Lambda Factor</label><input className="form-input" type="number" step="0.5" value={lambdaFactor} onChange={(e) => setLambdaFactor(e.target.value)} /></div>
            </div>
          ) : (
            <div className="form-grid">
              <div className="form-group full-width"><label className="form-label">Unit Operation Type</label>
                <select className="form-select" value={unitType} onChange={(e) => setUnitType(e.target.value)}>
                  <option value="heat_exchanger">Heat Exchanger</option>
                  <option value="distillation_column">Distillation Column</option>
                  <option value="reactor">Reactor</option>
                  <option value="compressor">Compressor</option>
                  <option value="separator">Separator</option>
                  <option value="pump">Pump</option>
                  <option value="fired_heater">Fired Heater</option>
                </select>
              </div>
            </div>
          )}
          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleCalculate} disabled={loading}>
              {loading ? <><span className="spinner" /> Calculating...</> : tab === "tune" ? "Tune PID" : "Get Strategy"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>Results</h2>{results && <span className="badge badge-success">Complete</span>}</div>
          {!results ? (
            <div className="empty-state"><div className="icon">&#x1F39B;</div><p>{tab === "tune" ? "Enter FOPDT model parameters to compute PID gains." : "Select unit type to see recommended control strategies."}</p></div>
          ) : tab === "tune" && tuningResults ? (
            <>
              {processModel && (
                <div className="results-grid" style={{ marginBottom: 20 }}>
                  <div className="result-item"><div className="label">Dead Time Ratio</div><div className="value">{Number(processModel.dead_time_ratio).toFixed(3)}</div></div>
                  <div className="result-item"><div className="label">Controllability</div><div className="value" style={{ fontSize: 14, textTransform: "capitalize" }}>{String(processModel.controllability).replace(/_/g, " ")}</div></div>
                </div>
              )}

              {Object.entries(tuningResults).map(([method, params]) => (
                <div key={method} style={{ marginBottom: 16 }}>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 8 }}>{String(params.method || method).replace(/_/g, " ")}</h3>
                  <div className="results-grid">
                    <div className="result-item highlight"><div className="label">K<sub>c</sub></div><div className="value">{Number(params.Kc).toFixed(3)}</div></div>
                    {params.Ti != null && <div className="result-item highlight"><div className="label">T<sub>i</sub></div><div className="value">{Number(params.Ti).toFixed(2)}<span className="unit">s</span></div></div>}
                    {params.Td != null && <div className="result-item highlight"><div className="label">T<sub>d</sub></div><div className="value">{Number(params.Td).toFixed(2)}<span className="unit">s</span></div></div>}
                  </div>
                </div>
              ))}

              {recommendation && (
                <div style={{ marginTop: 8, padding: 12, background: "var(--info-light)", borderRadius: "var(--radius-sm)", fontSize: 12, color: "var(--info)" }}>
                  <strong>Recommendation:</strong> {recommendation}
                </div>
              )}
            </>
          ) : strategy ? (
            <>
              <div style={{ marginBottom: 16, display: "grid", gap: 8 }}>
                <div className="result-item"><div className="label">Primary Strategy</div><div className="value" style={{ fontSize: 13, lineHeight: 1.5 }}>{String(strategy.primary)}</div></div>
                <div className="result-item"><div className="label">Enhanced Strategy</div><div className="value" style={{ fontSize: 13, lineHeight: 1.5 }}>{String(strategy.enhanced)}</div></div>
                <div className="result-item highlight"><div className="label">Advanced Strategy</div><div className="value" style={{ fontSize: 13, lineHeight: 1.5 }}>{String(strategy.advanced)}</div></div>
              </div>
              {strategy.typical_loops && (
                <table className="data-table">
                  <thead><tr><th>Tag</th><th>Variable</th><th>Manipulated</th><th>Type</th></tr></thead>
                  <tbody>
                    {(strategy.typical_loops as Record<string, unknown>[]).map((loop, i) => (
                      <tr key={i}><td>{String(loop.tag)}</td><td>{String(loop.variable)}</td><td>{String(loop.manipulated)}</td><td><span className="badge badge-info">{String(loop.type)}</span></td></tr>
                    ))}
                  </tbody>
                </table>
              )}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
