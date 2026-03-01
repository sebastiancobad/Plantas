import { useState } from "react";
import { distillationApi } from "../services/api";

export default function DistillationPage() {
  const [moleFracs, setMoleFracs] = useState("0.3,0.3,0.4");
  const [feedQuality, setFeedQuality] = useState("1.0");
  const [molarFlow, setMolarFlow] = useState("100");
  const [lkIndex, setLkIndex] = useState("0");
  const [hkIndex, setHkIndex] = useState("1");
  const [relVols, setRelVols] = useState("2.5,1.0,0.4");
  const [distPurity, setDistPurity] = useState("0.95");
  const [btmPurity, setBtmPurity] = useState("0.95");
  const [refluxFactor, setRefluxFactor] = useState("1.3");
  const [liquidDensity, setLiquidDensity] = useState("750");
  const [vaporDensity, setVaporDensity] = useState("3.0");
  const [surfTension, setSurfTension] = useState("0.02");
  const [avgMw, setAvgMw] = useState("58");
  const [internalType, setInternalType] = useState("tray");
  const [trayType, setTrayType] = useState("sieve");
  const [packingType, setPackingType] = useState("pall_rings_50mm");
  const [traySpacing, setTraySpacing] = useState("0.61");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      const res = await distillationApi.designColumn({
        feed: {
          mole_fractions: moleFracs.split(",").map(Number),
          feed_quality: Number(feedQuality),
          molar_flow_mol_s: Number(molarFlow),
        },
        light_key_index: Number(lkIndex), heavy_key_index: Number(hkIndex),
        relative_volatilities: relVols.split(",").map(Number),
        distillate_lk_purity: Number(distPurity), bottoms_hk_purity: Number(btmPurity),
        reflux_ratio_factor: Number(refluxFactor),
        liquid_density_kg_m3: Number(liquidDensity), vapor_density_kg_m3: Number(vaporDensity),
        surface_tension_N_m: Number(surfTension), avg_molecular_weight: Number(avgMw),
        internal_type: internalType, tray_type: trayType, packing_type: packingType,
        tray_spacing_m: Number(traySpacing),
      });
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  const sc = results ? (results as Record<string, unknown>).shortcut_design as Record<string, unknown> | undefined : undefined;
  const col = results ? (results as Record<string, unknown>).column_design as Record<string, unknown> | undefined : undefined;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Distillation Column</span></div>
        <h1>Distillation Column Design</h1>
        <p>Fenske-Underwood-Gilliland shortcut method with tray/packing selection.</p>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>Feed & Specifications</h2></div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Feed</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group full-width"><label className="form-label">Mole Fractions <span className="unit">(comma-separated)</span></label><input className="form-input" value={moleFracs} onChange={(e) => setMoleFracs(e.target.value)} placeholder="0.3,0.3,0.4" /></div>
            <div className="form-group"><label className="form-label">Feed Quality <span className="unit">(1=sat. liq.)</span></label><input className="form-input" type="number" step="0.1" value={feedQuality} onChange={(e) => setFeedQuality(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Molar Flow <span className="unit">(mol/s)</span></label><input className="form-input" type="number" value={molarFlow} onChange={(e) => setMolarFlow(e.target.value)} /></div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Key Components</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Light Key Index</label><input className="form-input" type="number" min="0" value={lkIndex} onChange={(e) => setLkIndex(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Heavy Key Index</label><input className="form-input" type="number" min="0" value={hkIndex} onChange={(e) => setHkIndex(e.target.value)} /></div>
            <div className="form-group full-width"><label className="form-label">Relative Volatilities <span className="unit">(comma-separated)</span></label><input className="form-input" value={relVols} onChange={(e) => setRelVols(e.target.value)} placeholder="2.5,1.0,0.4" /></div>
            <div className="form-group"><label className="form-label">Distillate LK Purity</label><input className="form-input" type="number" step="0.01" value={distPurity} onChange={(e) => setDistPurity(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Bottoms HK Purity</label><input className="form-input" type="number" step="0.01" value={btmPurity} onChange={(e) => setBtmPurity(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">R/R<sub>min</sub> Factor</label><input className="form-input" type="number" step="0.1" value={refluxFactor} onChange={(e) => setRefluxFactor(e.target.value)} /></div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Physical Properties</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Liquid Density <span className="unit">(kg/m&sup3;)</span></label><input className="form-input" type="number" value={liquidDensity} onChange={(e) => setLiquidDensity(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Vapor Density <span className="unit">(kg/m&sup3;)</span></label><input className="form-input" type="number" step="0.1" value={vaporDensity} onChange={(e) => setVaporDensity(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Surface Tension <span className="unit">(N/m)</span></label><input className="form-input" type="number" step="0.001" value={surfTension} onChange={(e) => setSurfTension(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Avg MW <span className="unit">(g/mol)</span></label><input className="form-input" type="number" value={avgMw} onChange={(e) => setAvgMw(e.target.value)} /></div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Internals</h3>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Internal Type</label>
              <select className="form-select" value={internalType} onChange={(e) => setInternalType(e.target.value)}>
                <option value="tray">Tray</option><option value="packing">Packing</option>
              </select>
            </div>
            {internalType === "tray" ? (
              <>
                <div className="form-group"><label className="form-label">Tray Type</label>
                  <select className="form-select" value={trayType} onChange={(e) => setTrayType(e.target.value)}>
                    <option value="sieve">Sieve</option><option value="valve">Valve</option><option value="bubble_cap">Bubble Cap</option>
                  </select>
                </div>
                <div className="form-group"><label className="form-label">Tray Spacing <span className="unit">(m)</span></label><input className="form-input" type="number" step="0.01" value={traySpacing} onChange={(e) => setTraySpacing(e.target.value)} /></div>
              </>
            ) : (
              <div className="form-group"><label className="form-label">Packing Type</label>
                <select className="form-select" value={packingType} onChange={(e) => setPackingType(e.target.value)}>
                  <option value="pall_rings_50mm">Pall Rings 50mm</option><option value="raschig_rings_25mm">Raschig Rings 25mm</option>
                  <option value="mellapak_250Y">Mellapak 250Y</option><option value="intalox_saddles">Intalox Saddles</option>
                </select>
              </div>
            )}
          </div>

          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleCalculate} disabled={loading}>
              {loading ? <><span className="spinner" /> Designing...</> : "Design Column"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>Design Results</h2>{sc && <span className="badge badge-success">Designed</span>}</div>
          {!sc ? (
            <div className="empty-state"><div className="icon">&#x1F3ED;</div><p>Specify feed and separation requirements to design the column.</p></div>
          ) : (
            <>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Shortcut Design (FUG)</h3>
              <div className="results-grid" style={{ marginBottom: 20 }}>
                <div className="result-item"><div className="label">N<sub>min</sub> (Fenske)</div><div className="value">{Number(sc.N_min).toFixed(1)}</div></div>
                <div className="result-item"><div className="label">R<sub>min</sub> (Underwood)</div><div className="value">{Number(sc.R_min).toFixed(3)}</div></div>
                <div className="result-item highlight"><div className="label">R<sub>actual</sub></div><div className="value">{Number(sc.R_actual).toFixed(3)}</div></div>
                <div className="result-item highlight"><div className="label">N<sub>actual</sub></div><div className="value">{Number(sc.N_actual).toFixed(1)}<span className="unit">stages</span></div></div>
              </div>

              {col && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Column Dimensions</h3>
                  <div className="results-grid" style={{ marginBottom: 20 }}>
                    <div className="result-item highlight"><div className="label">Diameter</div><div className="value">{Number(col.diameter_m).toFixed(2)}<span className="unit">m</span></div></div>
                    <div className="result-item highlight"><div className="label">Height</div><div className="value">{Number(col.height_m).toFixed(1)}<span className="unit">m</span></div></div>
                    <div className={`result-item ${Number(col.percent_flood) < 80 ? "success" : "warning"}`}>
                      <div className="label">% Flood</div>
                      <div className="value">{Number(col.percent_flood).toFixed(1)}<span className="unit">%</span></div>
                    </div>
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
