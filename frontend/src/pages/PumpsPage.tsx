import { useState } from "react";
import { pumpsApi } from "../services/api";

export default function PumpsPage() {
  const [density, setDensity] = useState("1000");
  const [viscosity, setViscosity] = useState("0.001");
  const [vaporPressure, setVaporPressure] = useState("3170");
  const [designFlow, setDesignFlow] = useState("0.01");
  const [ratedFactor, setRatedFactor] = useState("1.10");
  const [suctionPressure, setSuctionPressure] = useState("101325");
  const [suctionHead, setSuctionHead] = useState("2.0");
  const [suctionLoss, setSuctionLoss] = useState("0.5");
  const [dischargePressure, setDischargePressure] = useState("500000");
  const [dischargeHead, setDischargeHead] = useState("20.0");
  const [speed, setSpeed] = useState("2950");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCalculate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      const res = await pumpsApi.sizePump({
        fluid: { density_kg_m3: Number(density), viscosity_Pa_s: Number(viscosity), vapor_pressure_Pa: Number(vaporPressure) },
        flow: { design_flow_m3_s: Number(designFlow), rated_factor: Number(ratedFactor) },
        suction: { pressure_Pa: Number(suctionPressure), static_head_m: Number(suctionHead), friction_loss_m: Number(suctionLoss) },
        discharge: { pressure_Pa: Number(dischargePressure), static_head_m: Number(dischargeHead) },
        speed_rpm: Number(speed),
      });
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  const op = results ? (results as Record<string, unknown>).operating_point as Record<string, unknown> | undefined : undefined;
  const npsh = results ? (results as Record<string, unknown>).npsh_analysis as Record<string, unknown> | undefined : undefined;
  const pump = results ? (results as Record<string, unknown>).pump_selection as Record<string, unknown> | undefined : undefined;
  const motor = results ? (results as Record<string, unknown>).motor_sizing as Record<string, unknown> | undefined : undefined;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Pump Selection</span></div>
        <h1>Pump Selection & Sizing</h1>
        <p>System head curves, NPSH analysis, and motor sizing per API 610.</p>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>Input Parameters</h2></div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Fluid Properties</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Density <span className="unit">(kg/m&sup3;)</span></label><input className="form-input" type="number" value={density} onChange={(e) => setDensity(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Viscosity <span className="unit">(Pa&middot;s)</span></label><input className="form-input" type="number" step="0.0001" value={viscosity} onChange={(e) => setViscosity(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Vapor Pressure <span className="unit">(Pa)</span></label><input className="form-input" type="number" value={vaporPressure} onChange={(e) => setVaporPressure(e.target.value)} /></div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Flow</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Design Flow <span className="unit">(m&sup3;/s)</span></label><input className="form-input" type="number" step="0.001" value={designFlow} onChange={(e) => setDesignFlow(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Rated Factor</label><input className="form-input" type="number" step="0.01" value={ratedFactor} onChange={(e) => setRatedFactor(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Speed <span className="unit">(rpm)</span></label><input className="form-input" type="number" value={speed} onChange={(e) => setSpeed(e.target.value)} /></div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Suction Side</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Pressure <span className="unit">(Pa)</span></label><input className="form-input" type="number" value={suctionPressure} onChange={(e) => setSuctionPressure(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Static Head <span className="unit">(m)</span></label><input className="form-input" type="number" step="0.1" value={suctionHead} onChange={(e) => setSuctionHead(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Friction Loss <span className="unit">(m)</span></label><input className="form-input" type="number" step="0.1" value={suctionLoss} onChange={(e) => setSuctionLoss(e.target.value)} /></div>
          </div>

          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Discharge Side</h3>
          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Pressure <span className="unit">(Pa)</span></label><input className="form-input" type="number" value={dischargePressure} onChange={(e) => setDischargePressure(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Static Head <span className="unit">(m)</span></label><input className="form-input" type="number" step="0.1" value={dischargeHead} onChange={(e) => setDischargeHead(e.target.value)} /></div>
          </div>

          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleCalculate} disabled={loading}>
              {loading ? <><span className="spinner" /> Sizing...</> : "Size Pump"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>Results</h2>{op && <span className="badge badge-success">Sized</span>}</div>
          {!op ? (
            <div className="empty-state"><div className="icon">&#x2699;</div><p>Enter pump system data and click Size Pump.</p></div>
          ) : (
            <>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Operating Point</h3>
              <div className="results-grid" style={{ marginBottom: 20 }}>
                <div className="result-item highlight"><div className="label">Head</div><div className="value">{Number(op.head_m).toFixed(1)}<span className="unit">m</span></div></div>
                <div className="result-item highlight"><div className="label">Power</div><div className="value">{Number(op.power_kW).toFixed(2)}<span className="unit">kW</span></div></div>
                <div className="result-item"><div className="label">Flow</div><div className="value">{(Number(op.flow_m3_s) * 3600).toFixed(1)}<span className="unit">m&sup3;/h</span></div></div>
              </div>

              {npsh && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>NPSH Analysis</h3>
                  <div className="results-grid" style={{ marginBottom: 20 }}>
                    <div className="result-item"><div className="label">NPSH Available</div><div className="value">{Number(npsh.npsh_available_m).toFixed(2)}<span className="unit">m</span></div></div>
                    <div className="result-item"><div className="label">NPSH Required</div><div className="value">{Number(npsh.npsh_required_m).toFixed(2)}<span className="unit">m</span></div></div>
                    <div className={`result-item ${Number(npsh.margin_m) > 0 ? "success" : "warning"}`}>
                      <div className="label">Margin</div>
                      <div className="value">{Number(npsh.margin_m).toFixed(2)}<span className="unit">m</span></div>
                    </div>
                  </div>
                </>
              )}

              {pump && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Pump Selection</h3>
                  <div className="results-grid" style={{ marginBottom: 20 }}>
                    <div className="result-item"><div className="label">Type</div><div className="value" style={{ fontSize: 14, textTransform: "capitalize" }}>{String(pump.type).replace(/_/g, " ")}</div></div>
                    <div className="result-item"><div className="label">Specific Speed</div><div className="value">{Number(pump.specific_speed).toFixed(0)}</div></div>
                    <div className="result-item"><div className="label">Efficiency</div><div className="value">{(Number(pump.efficiency) * 100).toFixed(1)}<span className="unit">%</span></div></div>
                  </div>
                </>
              )}

              {motor && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Motor Sizing</h3>
                  <div className="results-grid">
                    <div className="result-item highlight"><div className="label">Motor Power</div><div className="value">{Number(motor.power_kW).toFixed(1)}<span className="unit">kW</span></div></div>
                    <div className="result-item"><div className="label">Frame</div><div className="value">{Number(motor.frame_hp).toFixed(0)}<span className="unit">HP</span></div></div>
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
