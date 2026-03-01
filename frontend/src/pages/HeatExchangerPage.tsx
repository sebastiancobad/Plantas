import { useState } from "react";
import { heatExchangerApi } from "../services/api";

export default function HeatExchangerPage() {
  const [temaType, setTemaType] = useState("AES");
  const [hotFluid, setHotFluid] = useState("Process stream");
  const [hotComponent, setHotComponent] = useState("benzene");
  const [hotFlow, setHotFlow] = useState("5.0");
  const [hotTin, setHotTin] = useState("150");
  const [hotTout, setHotTout] = useState("80");
  const [hotP, setHotP] = useState("5");
  const [hotFouling, setHotFouling] = useState("0.0002");
  const [coldFluid, setColdFluid] = useState("Cooling water");
  const [coldComponent, setColdComponent] = useState("water");
  const [coldFlow, setColdFlow] = useState("10.0");
  const [coldTin, setColdTin] = useState("25");
  const [coldTout, setColdTout] = useState("45");
  const [coldP, setColdP] = useState("3");
  const [coldFouling, setColdFouling] = useState("0.0002");
  const [tubeOd, setTubeOd] = useState("19.05");
  const [tubeLength, setTubeLength] = useState("6096");
  const [pitchRatio, setPitchRatio] = useState("1.25");
  const [layoutAngle, setLayoutAngle] = useState("30");
  const [baffleCut, setBaffleCut] = useState("25");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      const res = await heatExchangerApi.design({
        calculation_mode: "design", exchanger_type: "shell_and_tube", tema_type: temaType,
        hot_side: {
          fluid_name: hotFluid,
          components: [{ name: hotComponent, mole_fraction: 1.0 }],
          mass_flow_rate: { value: Number(hotFlow), unit: "kg/s" },
          inlet_temperature: { value: Number(hotTin), unit: "degC" },
          outlet_temperature: { value: Number(hotTout), unit: "degC" },
          inlet_pressure: { value: Number(hotP), unit: "bar" },
          fouling_resistance: { value: Number(hotFouling), unit: "m2*K/W" },
          placement: "shell",
        },
        cold_side: {
          fluid_name: coldFluid,
          components: [{ name: coldComponent, mole_fraction: 1.0 }],
          mass_flow_rate: { value: Number(coldFlow), unit: "kg/s" },
          inlet_temperature: { value: Number(coldTin), unit: "degC" },
          outlet_temperature: { value: Number(coldTout), unit: "degC" },
          inlet_pressure: { value: Number(coldP), unit: "bar" },
          fouling_resistance: { value: Number(coldFouling), unit: "m2*K/W" },
          placement: "tube",
        },
        mechanical_constraints: {
          tube_od: { value: Number(tubeOd), unit: "mm" },
          tube_length: { value: Number(tubeLength), unit: "mm" },
          tube_pitch_ratio: Number(pitchRatio),
          tube_layout_angle: Number(layoutAngle),
          baffle_cut_percent: Number(baffleCut),
        },
      });
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  const thermal = results ? (results as Record<string, unknown>).thermal_results as Record<string, unknown> | undefined : undefined;
  const hydraulic = results ? (results as Record<string, unknown>).hydraulic_results as Record<string, unknown> | undefined : undefined;
  const mech = results ? (results as Record<string, unknown>).mechanical_summary as Record<string, unknown> | undefined : undefined;
  const compliance = results ? (results as Record<string, unknown>).compliance as Record<string, unknown> | undefined : undefined;

  const val = (obj: Record<string, unknown> | undefined, key: string): number => {
    if (!obj || !obj[key]) return 0;
    const v = obj[key] as Record<string, unknown>;
    return typeof v === "object" && v.value !== undefined ? Number(v.value) : Number(v);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Heat Exchanger Design</span></div>
        <h1>Heat Exchanger Design</h1>
        <p>Shell & tube design using Kern method with TEMA/ASME/API 660 compliance.</p>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>Design Input</h2></div>

          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group">
              <label className="form-label">TEMA Type</label>
              <select className="form-select" value={temaType} onChange={(e) => setTemaType(e.target.value)}>
                <option value="AES">AES - Split Ring Floating Head</option>
                <option value="BEM">BEM - Fixed Tubesheet</option>
                <option value="AEU">AEU - U-Tube Bundle</option>
              </select>
            </div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Hot Side (Shell)</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Fluid Name</label><input className="form-input" value={hotFluid} onChange={(e) => setHotFluid(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Component</label>
              <select className="form-select" value={hotComponent} onChange={(e) => setHotComponent(e.target.value)}>
                {["benzene", "toluene", "methane", "ethane", "propane", "n-butane", "n-pentane", "n-hexane", "n-heptane", "n-octane", "water", "ethanol", "methanol", "acetone", "hydrogen", "nitrogen", "oxygen", "carbon_dioxide", "ammonia"].map((c) => <option key={c} value={c}>{c.replace(/_/g, " ")}</option>)}
              </select>
            </div>
            <div className="form-group"><label className="form-label">Mass Flow <span className="unit">(kg/s)</span></label><input className="form-input" type="number" step="0.1" value={hotFlow} onChange={(e) => setHotFlow(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">T<sub>in</sub> <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={hotTin} onChange={(e) => setHotTin(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">T<sub>out</sub> <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={hotTout} onChange={(e) => setHotTout(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Pressure <span className="unit">(bar)</span></label><input className="form-input" type="number" step="0.5" value={hotP} onChange={(e) => setHotP(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Fouling <span className="unit">(m&sup2;K/W)</span></label><input className="form-input" type="number" step="0.0001" value={hotFouling} onChange={(e) => setHotFouling(e.target.value)} /></div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Cold Side (Tube)</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Fluid Name</label><input className="form-input" value={coldFluid} onChange={(e) => setColdFluid(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Component</label>
              <select className="form-select" value={coldComponent} onChange={(e) => setColdComponent(e.target.value)}>
                {["water", "benzene", "toluene", "methane", "ethane", "propane", "n-butane", "n-pentane", "n-hexane", "n-heptane", "n-octane", "ethanol", "methanol", "acetone", "hydrogen", "nitrogen", "oxygen", "carbon_dioxide", "ammonia"].map((c) => <option key={c} value={c}>{c.replace(/_/g, " ")}</option>)}
              </select>
            </div>
            <div className="form-group"><label className="form-label">Mass Flow <span className="unit">(kg/s)</span></label><input className="form-input" type="number" step="0.1" value={coldFlow} onChange={(e) => setColdFlow(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">T<sub>in</sub> <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={coldTin} onChange={(e) => setColdTin(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">T<sub>out</sub> <span className="unit">(&deg;C)</span></label><input className="form-input" type="number" value={coldTout} onChange={(e) => setColdTout(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Pressure <span className="unit">(bar)</span></label><input className="form-input" type="number" step="0.5" value={coldP} onChange={(e) => setColdP(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Fouling <span className="unit">(m&sup2;K/W)</span></label><input className="form-input" type="number" step="0.0001" value={coldFouling} onChange={(e) => setColdFouling(e.target.value)} /></div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Mechanical</h3>
          <div className="form-grid">
            <div className="form-group"><label className="form-label">Tube OD <span className="unit">(mm)</span></label><input className="form-input" type="number" step="0.01" value={tubeOd} onChange={(e) => setTubeOd(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Tube Length <span className="unit">(mm)</span></label><input className="form-input" type="number" value={tubeLength} onChange={(e) => setTubeLength(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Pitch Ratio</label><input className="form-input" type="number" step="0.05" value={pitchRatio} onChange={(e) => setPitchRatio(e.target.value)} /></div>
            <div className="form-group">
              <label className="form-label">Layout Angle</label>
              <select className="form-select" value={layoutAngle} onChange={(e) => setLayoutAngle(e.target.value)}>
                <option value="30">30&deg; (Triangular)</option><option value="45">45&deg; (Rotated Square)</option>
                <option value="60">60&deg;</option><option value="90">90&deg; (Square)</option>
              </select>
            </div>
            <div className="form-group"><label className="form-label">Baffle Cut <span className="unit">(%)</span></label><input className="form-input" type="number" value={baffleCut} onChange={(e) => setBaffleCut(e.target.value)} /></div>
          </div>

          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleCalculate} disabled={loading}>
              {loading ? <><span className="spinner" /> Designing...</> : "Design Heat Exchanger"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>Results</h2>{thermal && <span className="badge badge-success">Designed</span>}</div>
          {!thermal ? (
            <div className="empty-state"><div className="icon">&#x1F525;</div><p>Enter heat exchanger parameters and run the design.</p></div>
          ) : (
            <>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Thermal</h3>
              <div className="results-grid" style={{ marginBottom: 20 }}>
                <div className="result-item highlight"><div className="label">Duty</div><div className="value">{val(thermal, "duty").toFixed(0)}<span className="unit">kW</span></div></div>
                <div className="result-item"><div className="label">LMTD</div><div className="value">{val(thermal, "lmtd").toFixed(1)}<span className="unit">K</span></div></div>
                <div className="result-item"><div className="label">F<sub>t</sub></div><div className="value">{Number(thermal.correction_factor_ft).toFixed(3)}</div></div>
                <div className="result-item highlight"><div className="label">Required Area</div><div className="value">{val(thermal, "required_area").toFixed(1)}<span className="unit">m&sup2;</span></div></div>
                <div className="result-item"><div className="label">Actual Area</div><div className="value">{val(thermal, "actual_area").toFixed(1)}<span className="unit">m&sup2;</span></div></div>
                <div className="result-item success"><div className="label">Excess Area</div><div className="value">{Number(thermal.excess_area_percent).toFixed(1)}<span className="unit">%</span></div></div>
                <div className="result-item"><div className="label">U (clean)</div><div className="value">{val(thermal, "overall_u_clean").toFixed(0)}<span className="unit">W/m&sup2;K</span></div></div>
                <div className="result-item"><div className="label">U (dirty)</div><div className="value">{val(thermal, "overall_u_dirty").toFixed(0)}<span className="unit">W/m&sup2;K</span></div></div>
              </div>

              {hydraulic && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Hydraulic</h3>
                  <div className="results-grid" style={{ marginBottom: 20 }}>
                    <div className="result-item"><div className="label">Shell &Delta;P</div><div className="value">{val(hydraulic, "shell_side_pressure_drop").toFixed(3)}<span className="unit">bar</span></div></div>
                    <div className="result-item"><div className="label">Tube &Delta;P</div><div className="value">{val(hydraulic, "tube_side_pressure_drop").toFixed(3)}<span className="unit">bar</span></div></div>
                    <div className="result-item"><div className="label">Shell Velocity</div><div className="value">{val(hydraulic, "shell_side_velocity").toFixed(2)}<span className="unit">m/s</span></div></div>
                    <div className="result-item"><div className="label">Tube Velocity</div><div className="value">{val(hydraulic, "tube_side_velocity").toFixed(2)}<span className="unit">m/s</span></div></div>
                  </div>
                </>
              )}

              {mech && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Mechanical</h3>
                  <div className="results-grid" style={{ marginBottom: 20 }}>
                    <div className="result-item"><div className="label">TEMA</div><div className="value" style={{ fontSize: 14 }}>{String(mech.tema_designation)}</div></div>
                    <div className="result-item"><div className="label">Shell ID</div><div className="value">{val(mech, "shell_id").toFixed(0)}<span className="unit">mm</span></div></div>
                    <div className="result-item"><div className="label">Tube Count</div><div className="value">{String(mech.tube_count)}</div></div>
                    <div className="result-item"><div className="label">Tube Passes</div><div className="value">{String(mech.tube_passes)}</div></div>
                    <div className="result-item"><div className="label">Baffles</div><div className="value">{String(mech.baffle_count)}</div></div>
                  </div>
                </>
              )}

              {compliance && (
                <div className="mt-16 flex gap-8" style={{ flexWrap: "wrap" }}>
                  {Object.entries(compliance).map(([k, v]) => (
                    <span key={k} className={`badge ${String(v).toLowerCase().includes("pass") || String(v).toLowerCase().includes("ok") ? "badge-success" : "badge-warning"}`}>
                      {k.replace(/_/g, " ")}: {String(v)}
                    </span>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
