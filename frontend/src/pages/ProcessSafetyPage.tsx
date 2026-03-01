import { useState } from "react";
import { processSafetyApi } from "../services/api";

export default function ProcessSafetyPage() {
  const [tab, setTab] = useState<"dow" | "hazop">("dow");
  // Dow F&EI
  const [material, setMaterial] = useState("methane");
  const [unitTemp, setUnitTemp] = useState("150");
  const [pressureBarg, setPressureBarg] = useState("10");
  const [volumeL, setVolumeL] = useState("5000");
  const [exothermic, setExothermic] = useState(false);
  const [flammable, setFlammable] = useState(true);
  const [reactivity, setReactivity] = useState("2");
  const [toxicity, setToxicity] = useState("3");
  // HAZOP
  const [nodeName, setNodeName] = useState("Feed Heater E-101");
  const [processDesc, setProcessDesc] = useState("Feed preheater heating crude oil from 25C to 150C using HP steam");
  const [keyParams, setKeyParams] = useState("Temperature,Pressure,Flow,Level");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      let res;
      if (tab === "dow") {
        res = await processSafetyApi.calculateDowFEI({
          material, process_unit_temperature_C: Number(unitTemp),
          pressure_barg: Number(pressureBarg), volume_liters: Number(volumeL),
          general_process_hazards: { exothermic_reaction: exothermic, flammable_material: flammable },
          special_process_hazards: { reactivity: Number(reactivity), toxicity: Number(toxicity), corrosion: 1 },
        });
      } else {
        res = await processSafetyApi.generateHAZOP({
          node_name: nodeName, process_description: processDesc,
          key_parameters: keyParams.split(",").map((s) => s.trim()),
        });
      }
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Process Safety</span></div>
        <h1>Process Safety & Industrial Hygiene</h1>
        <p>Dow F&EI calculation and HAZOP worksheet generation.</p>
      </div>

      <div className="tabs">
        <button className={`tab ${tab === "dow" ? "active" : ""}`} onClick={() => { setTab("dow"); setResults(null); }}>Dow F&EI</button>
        <button className={`tab ${tab === "hazop" ? "active" : ""}`} onClick={() => { setTab("hazop"); setResults(null); }}>HAZOP Generator</button>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>{tab === "dow" ? "Dow F&EI Input" : "HAZOP Node Input"}</h2></div>
          {tab === "dow" ? (
            <div className="form-grid">
              <div className="form-group"><label className="form-label">Material</label>
                <select className="form-select" value={material} onChange={(e) => setMaterial(e.target.value)}>
                  {["methane", "ethane", "propane", "benzene", "toluene", "hydrogen", "ethylene", "ammonia"].map((m) => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>
              <div className="form-group"><label className="form-label">Temperature <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={unitTemp} onChange={(e) => setUnitTemp(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Pressure <span className="unit">(barg)</span></label><input className="form-input" type="number" value={pressureBarg} onChange={(e) => setPressureBarg(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Volume <span className="unit">(L)</span></label><input className="form-input" type="number" value={volumeL} onChange={(e) => setVolumeL(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Exothermic Reaction</label>
                <select className="form-select" value={exothermic ? "yes" : "no"} onChange={(e) => setExothermic(e.target.value === "yes")}><option value="no">No</option><option value="yes">Yes</option></select>
              </div>
              <div className="form-group"><label className="form-label">Flammable Material</label>
                <select className="form-select" value={flammable ? "yes" : "no"} onChange={(e) => setFlammable(e.target.value === "yes")}><option value="yes">Yes</option><option value="no">No</option></select>
              </div>
              <div className="form-group"><label className="form-label">Reactivity <span className="unit">(0-10)</span></label><input className="form-input" type="number" min="0" max="10" value={reactivity} onChange={(e) => setReactivity(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Toxicity <span className="unit">(0-10)</span></label><input className="form-input" type="number" min="0" max="10" value={toxicity} onChange={(e) => setToxicity(e.target.value)} /></div>
            </div>
          ) : (
            <div className="form-grid">
              <div className="form-group full-width"><label className="form-label">Node Name</label><input className="form-input" value={nodeName} onChange={(e) => setNodeName(e.target.value)} /></div>
              <div className="form-group full-width"><label className="form-label">Process Description</label><input className="form-input" value={processDesc} onChange={(e) => setProcessDesc(e.target.value)} /></div>
              <div className="form-group full-width"><label className="form-label">Key Parameters <span className="unit">(comma-separated)</span></label><input className="form-input" value={keyParams} onChange={(e) => setKeyParams(e.target.value)} /></div>
            </div>
          )}
          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleCalculate} disabled={loading}>
              {loading ? <><span className="spinner" /> Calculating...</> : tab === "dow" ? "Calculate F&EI" : "Generate HAZOP"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>Results</h2>{results && <span className="badge badge-success">Complete</span>}</div>
          {!results ? (
            <div className="empty-state"><div className="icon">&#x1F6E1;</div><p>{tab === "dow" ? "Enter process data to calculate the Fire & Explosion Index." : "Define the HAZOP node to generate a worksheet."}</p></div>
          ) : tab === "dow" ? (
            <>
              <div className="results-grid" style={{ marginBottom: 16 }}>
                <div className="result-item"><div className="label">Material Factor</div><div className="value">{Number((results as Record<string, unknown>).material_factor).toFixed(1)}</div></div>
                <div className="result-item"><div className="label">Base F&EI</div><div className="value">{Number((results as Record<string, unknown>).base_fei).toFixed(1)}</div></div>
                <div className="result-item highlight"><div className="label">Adjusted F&EI</div><div className="value">{Number((results as Record<string, unknown>).adjusted_fei).toFixed(1)}</div></div>
                <div className={`result-item ${["light"].includes(String((results as Record<string, unknown>).fire_probability_category)) ? "success" : "warning"}`}>
                  <div className="label">Fire Category</div>
                  <div className="value" style={{ fontSize: 14, textTransform: "capitalize" }}>{String((results as Record<string, unknown>).fire_probability_category)}</div>
                </div>
              </div>
              {(results as Record<string, unknown>).recommendations && (
                <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                  <strong style={{ color: "var(--text-primary)" }}>Recommendations:</strong>
                  {((results as Record<string, unknown>).recommendations as string[]).map((r, i) => <div key={i} style={{ marginTop: 4 }}>&#x2022; {r}</div>)}
                </div>
              )}
            </>
          ) : (
            <div style={{ maxHeight: 500, overflowY: "auto" }}>
              {((results as Record<string, unknown>).hazop_worksheet as Record<string, unknown>[])?.map((row, i) => (
                <div key={i} style={{ padding: 14, borderBottom: "1px solid var(--border-light)" }}>
                  <div className="flex items-center gap-8 mb-16">
                    <span className="badge badge-info">{String(row.guideword)}</span>
                    <span style={{ fontSize: 13, fontWeight: 600 }}>{String(row.deviation)}</span>
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)", display: "grid", gap: 6 }}>
                    <div><strong>Causes:</strong> {(row.possible_causes as string[]).join("; ")}</div>
                    <div><strong>Consequences:</strong> {(row.consequences as string[]).join("; ")}</div>
                    <div><strong>Safeguards:</strong> {(row.safeguards as string[]).join("; ")}</div>
                    <div><strong>Recommendations:</strong> {(row.recommendations as string[]).join("; ")}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
