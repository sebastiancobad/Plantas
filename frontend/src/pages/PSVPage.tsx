import { useState } from "react";
import { psvApi } from "../services/api";

export default function PSVPage() {
  const [reliefType, setReliefType] = useState("gas");
  const [massFlow, setMassFlow] = useState("5000");
  const [tempK, setTempK] = useState("400");
  const [molWeight, setMolWeight] = useState("28");
  const [compZ, setCompZ] = useState("0.95");
  const [kRatio, setKRatio] = useState("1.4");
  const [volFlow, setVolFlow] = useState("10");
  const [liquidDensity, setLiquidDensity] = useState("900");
  const [viscCp, setViscCp] = useState("1.0");
  const [setPressure, setSetPressure] = useState("1500");
  const [backPressure, setBackPressure] = useState("101");
  const [valveType, setValveType] = useState("conventional");
  const [ruptureDisk, setRuptureDisk] = useState(false);
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      const payload: Record<string, unknown> = {
        relief_type: reliefType, set_pressure_kPa: Number(setPressure),
        back_pressure_kPa: Number(backPressure), valve_type: valveType, rupture_disk: ruptureDisk,
      };
      if (reliefType === "gas") {
        payload.mass_flow_kg_hr = Number(massFlow); payload.temperature_K = Number(tempK);
        payload.molecular_weight = Number(molWeight); payload.compressibility_Z = Number(compZ);
        payload.k_ratio = Number(kRatio);
      } else {
        payload.volume_flow_m3_hr = Number(volFlow); payload.density_kg_m3 = Number(liquidDensity);
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

  const orifice = results ? (results as Record<string, unknown>).selected_orifice as Record<string, unknown> | undefined : undefined;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Safety Relief Valves</span></div>
        <h1>Safety Relief Valve Sizing</h1>
        <p>API 520/521 sizing for gas, liquid, and fire case scenarios.</p>
      </div>

      <div className="tabs">
        <button className={`tab ${reliefType === "gas" ? "active" : ""}`} onClick={() => setReliefType("gas")}>Gas / Vapor</button>
        <button className={`tab ${reliefType === "liquid" ? "active" : ""}`} onClick={() => setReliefType("liquid")}>Liquid</button>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>Valve Input</h2></div>

          {reliefType === "gas" ? (
            <div className="form-grid" style={{ marginBottom: 20 }}>
              <div className="form-group"><label className="form-label">Mass Flow <span className="unit">(kg/hr)</span></label><input className="form-input" type="number" value={massFlow} onChange={(e) => setMassFlow(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Temperature <span className="unit">(K)</span></label><input className="form-input" type="number" value={tempK} onChange={(e) => setTempK(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Molecular Weight</label><input className="form-input" type="number" value={molWeight} onChange={(e) => setMolWeight(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Z (compressibility)</label><input className="form-input" type="number" step="0.01" value={compZ} onChange={(e) => setCompZ(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">k (Cp/Cv)</label><input className="form-input" type="number" step="0.01" value={kRatio} onChange={(e) => setKRatio(e.target.value)} /></div>
            </div>
          ) : (
            <div className="form-grid" style={{ marginBottom: 20 }}>
              <div className="form-group"><label className="form-label">Volume Flow <span className="unit">(m&sup3;/hr)</span></label><input className="form-input" type="number" value={volFlow} onChange={(e) => setVolFlow(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Density <span className="unit">(kg/m&sup3;)</span></label><input className="form-input" type="number" value={liquidDensity} onChange={(e) => setLiquidDensity(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Viscosity <span className="unit">(cP)</span></label><input className="form-input" type="number" step="0.1" value={viscCp} onChange={(e) => setViscCp(e.target.value)} /></div>
            </div>
          )}

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Valve Configuration</h3>
          <div className="form-grid">
            <div className="form-group"><label className="form-label">Set Pressure <span className="unit">(kPa)</span></label><input className="form-input" type="number" value={setPressure} onChange={(e) => setSetPressure(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Back Pressure <span className="unit">(kPa)</span></label><input className="form-input" type="number" value={backPressure} onChange={(e) => setBackPressure(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Valve Type</label>
              <select className="form-select" value={valveType} onChange={(e) => setValveType(e.target.value)}>
                <option value="conventional">Conventional</option><option value="balanced_bellows">Balanced Bellows</option>
              </select>
            </div>
            <div className="form-group"><label className="form-label">Rupture Disk</label>
              <select className="form-select" value={ruptureDisk ? "yes" : "no"} onChange={(e) => setRuptureDisk(e.target.value === "yes")}>
                <option value="no">No</option><option value="yes">Yes</option>
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
          <div className="card-header"><h2>Sizing Results</h2>{orifice && <span className="badge badge-success">Sized</span>}</div>
          {!results ? (
            <div className="empty-state"><div className="icon">&#x26A0;</div><p>Specify relief conditions and click Size PSV.</p></div>
          ) : (
            <div className="results-grid">
              <div className="result-item highlight"><div className="label">Required Area</div><div className="value">{Number((results as Record<string, unknown>).required_area_mm2).toFixed(1)}<span className="unit">mm&sup2;</span></div></div>
              {orifice && (
                <>
                  <div className="result-item highlight"><div className="label">Selected Orifice</div><div className="value" style={{ fontSize: 24 }}>{String(orifice.designation)}</div></div>
                  <div className="result-item"><div className="label">Orifice Area</div><div className="value">{Number(orifice.area_mm2).toFixed(1)}<span className="unit">mm&sup2;</span></div></div>
                </>
              )}
              <div className="result-item"><div className="label">Flow Type</div><div className="value" style={{ fontSize: 14, textTransform: "capitalize" }}>{String((results as Record<string, unknown>).flow_type)}</div></div>
              <div className="result-item"><div className="label">Relief Rate</div><div className="value">{Number((results as Record<string, unknown>).relief_rate_kg_hr).toFixed(0)}<span className="unit">kg/hr</span></div></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
