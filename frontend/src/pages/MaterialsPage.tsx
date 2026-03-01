import { useState } from "react";
import { materialsApi } from "../services/api";

export default function MaterialsPage() {
  const [tab, setTab] = useState<"select" | "co2" | "h2s">("select");
  const [designTemp, setDesignTemp] = useState("100");
  const [minTemp, setMinTemp] = useState("-29");
  const [designPressure, setDesignPressure] = useState("10");
  const [co2Pp, setCo2Pp] = useState("0.5");
  const [h2sPp, setH2sPp] = useState("0.01");
  const [pH, setPH] = useState("6.5");
  const [chloride, setChloride] = useState("50");
  const [serviceType, setServiceType] = useState("general");
  const [co2Temp, setCo2Temp] = useState("60");
  const [co2Pressure, setCo2Pressure] = useState("2.0");
  const [co2pH, setCo2pH] = useState("5.5");
  const [h2sPress, setH2sPress] = useState("0.05");
  const [h2spH, setH2spH] = useState("4.0");
  const [h2sTemp, setH2sTemp] = useState("40");
  const [h2sMaterial, setH2sMaterial] = useState("carbon_steel_A106B");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      let res;
      if (tab === "select") {
        res = await materialsApi.selectMaterial({
          design_temperature_C: Number(designTemp), minimum_temperature_C: Number(minTemp),
          design_pressure_barg: Number(designPressure), co2_partial_pressure_bar: Number(co2Pp),
          h2s_partial_pressure_bar: Number(h2sPp), pH: Number(pH), chloride_ppm: Number(chloride),
          service_type: serviceType,
        });
      } else if (tab === "co2") {
        res = await materialsApi.co2Corrosion({
          temperature_C: Number(co2Temp), co2_partial_pressure_bar: Number(co2Pressure), pH: Number(co2pH),
        });
      } else {
        res = await materialsApi.h2sSourCheck({
          h2s_partial_pressure_bar: Number(h2sPress), pH: Number(h2spH), temperature_C: Number(h2sTemp),
          material_key: h2sMaterial,
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
        <div className="page-breadcrumb">Modules <span>/ Material Selection</span></div>
        <h1>Material Selection & Metallurgy</h1>
        <p>Corrosion analysis, NACE MR0175 screening, and alloy recommendation.</p>
      </div>

      <div className="tabs">
        <button className={`tab ${tab === "select" ? "active" : ""}`} onClick={() => { setTab("select"); setResults(null); }}>Material Selection</button>
        <button className={`tab ${tab === "co2" ? "active" : ""}`} onClick={() => { setTab("co2"); setResults(null); }}>CO&#x2082; Corrosion</button>
        <button className={`tab ${tab === "h2s" ? "active" : ""}`} onClick={() => { setTab("h2s"); setResults(null); }}>H&#x2082;S Sour Check</button>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>Input Parameters</h2></div>
          {tab === "select" && (
            <div className="form-grid">
              <div className="form-group"><label className="form-label">Design Temp <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={designTemp} onChange={(e) => setDesignTemp(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Min Temp <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={minTemp} onChange={(e) => setMinTemp(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Design Pressure <span className="unit">(barg)</span></label><input className="form-input" type="number" value={designPressure} onChange={(e) => setDesignPressure(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">CO&#x2082; PP <span className="unit">(bar)</span></label><input className="form-input" type="number" step="0.1" value={co2Pp} onChange={(e) => setCo2Pp(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">H&#x2082;S PP <span className="unit">(bar)</span></label><input className="form-input" type="number" step="0.001" value={h2sPp} onChange={(e) => setH2sPp(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">pH</label><input className="form-input" type="number" step="0.1" value={pH} onChange={(e) => setPH(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Chloride <span className="unit">(ppm)</span></label><input className="form-input" type="number" value={chloride} onChange={(e) => setChloride(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Service Type</label>
                <select className="form-select" value={serviceType} onChange={(e) => setServiceType(e.target.value)}>
                  <option value="general">General</option><option value="sour">Sour Service</option><option value="high_temp">High Temperature</option>
                </select>
              </div>
            </div>
          )}
          {tab === "co2" && (
            <div className="form-grid">
              <div className="form-group"><label className="form-label">Temperature <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={co2Temp} onChange={(e) => setCo2Temp(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">CO&#x2082; Partial Pressure <span className="unit">(bar)</span></label><input className="form-input" type="number" step="0.1" value={co2Pressure} onChange={(e) => setCo2Pressure(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">pH</label><input className="form-input" type="number" step="0.1" value={co2pH} onChange={(e) => setCo2pH(e.target.value)} /></div>
            </div>
          )}
          {tab === "h2s" && (
            <div className="form-grid">
              <div className="form-group"><label className="form-label">H&#x2082;S PP <span className="unit">(bar)</span></label><input className="form-input" type="number" step="0.01" value={h2sPress} onChange={(e) => setH2sPress(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">pH</label><input className="form-input" type="number" step="0.1" value={h2spH} onChange={(e) => setH2spH(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Temperature <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={h2sTemp} onChange={(e) => setH2sTemp(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Material</label>
                <select className="form-select" value={h2sMaterial} onChange={(e) => setH2sMaterial(e.target.value)}>
                  <option value="carbon_steel_A106B">Carbon Steel A106B</option>
                  <option value="carbon_steel_A516_70">Carbon Steel A516-70</option>
                  <option value="ss_304">SS 304</option><option value="ss_316L">SS 316L</option>
                  <option value="duplex_2205">Duplex 2205</option><option value="inconel_625">Inconel 625</option>
                </select>
              </div>
            </div>
          )}
          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleCalculate} disabled={loading}>
              {loading ? <><span className="spinner" /> Analyzing...</> : tab === "select" ? "Select Material" : tab === "co2" ? "Calc Corrosion Rate" : "Check Sour Service"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>Results</h2>{results && <span className="badge badge-success">Complete</span>}</div>
          {!results ? (
            <div className="empty-state"><div className="icon">&#x1F6E1;</div><p>Run the analysis to see material recommendations.</p></div>
          ) : tab === "select" ? (
            <>
              {(results as Record<string, unknown>).recommended && (() => {
                const rec = (results as Record<string, unknown>).recommended as Record<string, unknown>;
                const props = rec.properties as Record<string, unknown> | undefined;
                return (
                  <>
                    <div style={{ padding: 16, background: "var(--primary-subtle)", border: "1px solid rgba(79,107,246,.15)", borderRadius: "var(--radius-sm)", marginBottom: 16 }}>
                      <div style={{ fontSize: 11, fontWeight: 600, color: "var(--primary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 4 }}>Recommended Material</div>
                      <div style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)" }}>{String(rec.name)}</div>
                      <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>UNS: {String(rec.UNS)} &middot; {String(rec.category)} &middot; Score: {String(rec.score)}/100</div>
                    </div>
                    {props && (
                      <div className="results-grid">
                        <div className="result-item"><div className="label">Yield Strength</div><div className="value">{String(props.yield_MPa)}<span className="unit">MPa</span></div></div>
                        <div className="result-item"><div className="label">Tensile Strength</div><div className="value">{String(props.tensile_MPa)}<span className="unit">MPa</span></div></div>
                        <div className="result-item"><div className="label">Max Temp</div><div className="value">{String(props.max_temp_C)}<span className="unit">&deg;C</span></div></div>
                        <div className="result-item"><div className="label">Cost Factor</div><div className="value">{String(rec.cost_factor)}<span className="unit">x</span></div></div>
                      </div>
                    )}
                    {rec.notes && (rec.notes as string[]).length > 0 && (
                      <div className="mt-16" style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                        {(rec.notes as string[]).map((n, i) => <div key={i} style={{ marginBottom: 4 }}>&#x2022; {n}</div>)}
                      </div>
                    )}
                  </>
                );
              })()}
            </>
          ) : tab === "co2" ? (
            <div className="results-grid">
              <div className="result-item highlight"><div className="label">Corrosion Rate</div><div className="value">{Number((results as Record<string, unknown>).corrosion_rate_mm_yr).toFixed(2)}<span className="unit">mm/yr</span></div></div>
              <div className="result-item"><div className="label">Severity</div><div className="value" style={{ fontSize: 14, textTransform: "capitalize" }}>{String((results as Record<string, unknown>).severity)}</div></div>
              <div className="result-item"><div className="label">Model</div><div className="value" style={{ fontSize: 14 }}>{String((results as Record<string, unknown>).model)}</div></div>
            </div>
          ) : (
            <div className="results-grid">
              <div className={`result-item ${(results as Record<string, unknown>).acceptable ? "success" : "warning"}`}><div className="label">Acceptable</div><div className="value">{(results as Record<string, unknown>).acceptable ? "Yes" : "No"}</div></div>
              <div className="result-item"><div className="label">NACE Region</div><div className="value">{String((results as Record<string, unknown>).nace_region)}</div></div>
              <div className="result-item highlight"><div className="label">Severity</div><div className="value" style={{ fontSize: 14, textTransform: "capitalize" }}>{String((results as Record<string, unknown>).severity).replace(/_/g, " ")}</div></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
