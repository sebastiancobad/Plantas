import { useState } from "react";
import { processSafetyApi } from "../services/api";

export default function ProcessSafetyPage() {
  const [tab, setTab] = useState<"dow" | "hazop">("dow");
  // Dow F&EI
  const [materialName, setMaterialName] = useState("methane");
  const [replacementCost, setReplacementCost] = useState("1000000");
  const [exothermic, setExothermic] = useState(false);
  const [flammable, setFlammable] = useState(true);
  const [enclosed, setEnclosed] = useState(false);
  const [toxicMaterials, setToxicMaterials] = useState(false);
  const [operatingTempC, setOperatingTempC] = useState("150");
  const [operatingPressBarg, setOperatingPressBarg] = useState("10");
  const [flammableQtyKg, setFlammableQtyKg] = useState("5000");
  const [corrosion, setCorrosion] = useState(false);
  // HAZOP
  const [nodeDesc, setNodeDesc] = useState("Feed Heater E-101 shell side");
  const [designIntent, setDesignIntent] = useState("Heat crude oil from 25C to 150C using HP steam");
  const [parameters, setParameters] = useState("flow,temperature,pressure,level");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      let res;
      if (tab === "dow") {
        res = await processSafetyApi.calculateDowFEI({
          material_name: materialName,
          replacement_cost_usd: Number(replacementCost),
          general_process_hazards: {
            exothermic_reaction: exothermic,
            flammable_material: flammable,
            enclosed_unit: enclosed,
          },
          special_process_hazards: {
            toxic_materials: toxicMaterials,
            operating_temperature_C: Number(operatingTempC),
            operating_pressure_barg: Number(operatingPressBarg),
            flammable_quantity_kg: Number(flammableQtyKg),
            corrosion_erosion: corrosion,
          },
        });
      } else {
        res = await processSafetyApi.generateHAZOP({
          node_description: nodeDesc,
          design_intent: designIntent,
          parameters: parameters.split(",").map((s) => s.trim()),
        });
      }
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  // Dow F&EI response fields
  const fei = results?.fire_explosion_index as number | undefined;
  const hazardDegree = results?.degree_of_hazard as string | undefined;
  const materialFactor = results?.material_factor as number | undefined;
  const f1 = results?.general_process_hazard_factor_F1 as number | undefined;
  const f2 = results?.special_process_hazard_factor_F2 as number | undefined;
  const f3 = results?.unit_hazard_factor_F3 as number | undefined;
  const radiusM = results?.radius_of_exposure_m as number | undefined;
  const lossEstimate = results?.loss_estimate as Record<string, number> | undefined;

  // HAZOP response fields
  const hazopWorksheet = results?.worksheet as Record<string, unknown>[] | undefined;
  const hazopNode = results?.node as string | undefined;
  const worksheetEntries = results?.worksheet_entries as number | undefined;
  const caseStudies = results?.case_studies_relevant as Record<string, unknown>[] | undefined;

  const hazardColor = (degree: string) => {
    if (degree === "Light") return "badge-success";
    if (degree === "Moderate") return "badge-info";
    return "badge-error";
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
                <select className="form-select" value={materialName} onChange={(e) => setMaterialName(e.target.value)}>
                  {["methane", "ethane", "propane", "benzene", "toluene", "hydrogen", "ethylene", "ammonia", "hydrogen_sulfide"].map((m) => <option key={m} value={m}>{m.replace(/_/g, " ")}</option>)}
                </select>
              </div>
              <div className="form-group"><label className="form-label">Replacement Cost <span className="unit">(USD)</span></label><input className="form-input" type="number" value={replacementCost} onChange={(e) => setReplacementCost(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Operating Temp <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={operatingTempC} onChange={(e) => setOperatingTempC(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Operating Pressure <span className="unit">(barg)</span></label><input className="form-input" type="number" value={operatingPressBarg} onChange={(e) => setOperatingPressBarg(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Flammable Qty <span className="unit">(kg)</span></label><input className="form-input" type="number" value={flammableQtyKg} onChange={(e) => setFlammableQtyKg(e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Exothermic Reaction</label>
                <select className="form-select" value={exothermic ? "yes" : "no"} onChange={(e) => setExothermic(e.target.value === "yes")}><option value="no">No</option><option value="yes">Yes</option></select>
              </div>
              <div className="form-group"><label className="form-label">Flammable Material</label>
                <select className="form-select" value={flammable ? "yes" : "no"} onChange={(e) => setFlammable(e.target.value === "yes")}><option value="yes">Yes</option><option value="no">No</option></select>
              </div>
              <div className="form-group"><label className="form-label">Enclosed Unit</label>
                <select className="form-select" value={enclosed ? "yes" : "no"} onChange={(e) => setEnclosed(e.target.value === "yes")}><option value="no">No</option><option value="yes">Yes</option></select>
              </div>
              <div className="form-group"><label className="form-label">Toxic Materials</label>
                <select className="form-select" value={toxicMaterials ? "yes" : "no"} onChange={(e) => setToxicMaterials(e.target.value === "yes")}><option value="no">No</option><option value="yes">Yes</option></select>
              </div>
              <div className="form-group"><label className="form-label">Corrosion/Erosion</label>
                <select className="form-select" value={corrosion ? "yes" : "no"} onChange={(e) => setCorrosion(e.target.value === "yes")}><option value="no">No</option><option value="yes">Yes</option></select>
              </div>
            </div>
          ) : (
            <div className="form-grid">
              <div className="form-group full-width"><label className="form-label">Node Description</label><input className="form-input" value={nodeDesc} onChange={(e) => setNodeDesc(e.target.value)} /></div>
              <div className="form-group full-width"><label className="form-label">Design Intent</label><input className="form-input" value={designIntent} onChange={(e) => setDesignIntent(e.target.value)} /></div>
              <div className="form-group full-width"><label className="form-label">Parameters <span className="unit">(comma-separated)</span></label><input className="form-input" value={parameters} onChange={(e) => setParameters(e.target.value)} /></div>
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
            <div className="empty-state"><div className="icon">&#x26A0;</div><p>{tab === "dow" ? "Enter process data to calculate the Fire & Explosion Index." : "Define the HAZOP node to generate a worksheet."}</p></div>
          ) : tab === "dow" && fei != null ? (
            <>
              <div className="results-grid" style={{ marginBottom: 16 }}>
                <div className="result-item"><div className="label">Material Factor</div><div className="value">{Number(materialFactor).toFixed(1)}</div></div>
                <div className="result-item"><div className="label">F<sub>1</sub> (General)</div><div className="value">{Number(f1).toFixed(2)}</div></div>
                <div className="result-item"><div className="label">F<sub>2</sub> (Special)</div><div className="value">{Number(f2).toFixed(2)}</div></div>
                <div className="result-item"><div className="label">F<sub>3</sub> (Unit Hazard)</div><div className="value">{Number(f3).toFixed(2)}</div></div>
                <div className="result-item highlight"><div className="label">Fire & Explosion Index</div><div className="value">{Number(fei).toFixed(1)}</div></div>
                <div className={`result-item`}>
                  <div className="label">Degree of Hazard</div>
                  <div className="value"><span className={`badge ${hazardColor(String(hazardDegree))}`}>{String(hazardDegree)}</span></div>
                </div>
                {radiusM != null && (
                  <div className="result-item"><div className="label">Exposure Radius</div><div className="value">{Number(radiusM).toFixed(1)}<span className="unit">m</span></div></div>
                )}
              </div>
              {lossEstimate && (
                <div style={{ marginTop: 12 }}>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 8 }}>Loss Estimate</h3>
                  <div className="results-grid">
                    <div className="result-item"><div className="label">Max Probable Property Damage</div><div className="value">${Number(lossEstimate.maximum_probable_property_damage_usd).toLocaleString()}</div></div>
                    <div className="result-item"><div className="label">Probable Loss (with credits)</div><div className="value">${Number(lossEstimate.probable_loss_with_credits_usd).toLocaleString()}</div></div>
                  </div>
                </div>
              )}
            </>
          ) : hazopWorksheet ? (
            <>
              {hazopNode && (
                <div style={{ marginBottom: 12, fontSize: 13 }}>
                  <strong>Node:</strong> {hazopNode}
                  {worksheetEntries != null && <span style={{ color: "var(--text-tertiary)", marginLeft: 12 }}>{worksheetEntries} entries</span>}
                </div>
              )}
              <div style={{ maxHeight: 500, overflowY: "auto" }}>
                {hazopWorksheet.map((row, i) => (
                  <div key={i} style={{ padding: 14, borderBottom: "1px solid var(--border-light)" }}>
                    <div className="flex items-center gap-8 mb-16">
                      <span className="badge badge-info">{String(row.guideword)}</span>
                      <span style={{ fontSize: 12, color: "var(--text-tertiary)" }}>{String(row.parameter)}</span>
                      <span style={{ fontSize: 13, fontWeight: 600 }}>{String(row.deviation)}</span>
                    </div>
                    <div style={{ fontSize: 12, color: "var(--text-secondary)", display: "grid", gap: 6 }}>
                      <div><strong>Causes:</strong> {String(row.possible_causes)}</div>
                      <div><strong>Consequences:</strong> {String(row.consequences)}</div>
                      <div><strong>Safeguards:</strong> {String(row.safeguards)}</div>
                      <div><strong>Recommendations:</strong> {String(row.recommendations)}</div>
                    </div>
                  </div>
                ))}
              </div>
              {caseStudies && caseStudies.length > 0 && (
                <div style={{ marginTop: 16, padding: 12, background: "var(--info-light)", borderRadius: "var(--radius-sm)" }}>
                  <strong style={{ fontSize: 12, color: "var(--info)" }}>Relevant Case Studies:</strong>
                  {caseStudies.map((cs, i) => (
                    <div key={i} style={{ marginTop: 8, fontSize: 12, color: "var(--text-secondary)" }}>
                      <strong>{String(cs.title)}</strong> ({String(cs.location)}) &mdash; {String(cs.casualties)}
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
