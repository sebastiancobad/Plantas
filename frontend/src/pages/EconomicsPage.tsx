import { useState } from "react";
import { economicsApi } from "../services/api";

interface EquipmentItem { tag: string; type: string; material: string; size_value: number; size_unit: string; size_param: string; }

export default function EconomicsPage() {
  const [projectName, setProjectName] = useState("New Chemical Plant");
  const [locationFactor, setLocationFactor] = useState("1.0");
  const [baseYear, setBaseYear] = useState("2020");
  const [targetYear, setTargetYear] = useState("2026");
  const [contingency, setContingency] = useState("15");
  const [engineering, setEngineering] = useState("12");
  const [discountRate, setDiscountRate] = useState("0.10");
  const [lifetime, setLifetime] = useState("20");
  const [revenue, setRevenue] = useState("5000000");
  const [equipmentList, setEquipmentList] = useState<EquipmentItem[]>([
    { tag: "E-101", type: "shell_and_tube_heat_exchanger", material: "carbon_steel", size_value: 50, size_unit: "m2", size_param: "area" },
    { tag: "P-101", type: "centrifugal_pump", material: "carbon_steel", size_value: 15, size_unit: "kW", size_param: "power" },
    { tag: "V-101", type: "pressure_vessel", material: "carbon_steel", size_value: 10, size_unit: "m3", size_param: "volume" },
  ]);
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addEquipment = () => setEquipmentList([...equipmentList, { tag: "", type: "pressure_vessel", material: "carbon_steel", size_value: 1, size_unit: "m3", size_param: "volume" }]);

  const handleEvaluate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      const res = await economicsApi.fullEvaluation({
        capex: {
          project_name: projectName, location_factor: Number(locationFactor),
          base_year: Number(baseYear), target_year: Number(targetYear),
          equipment_list: equipmentList.map((e) => ({
            tag: e.tag, type: e.type, material: e.material,
            size_parameter: { value: e.size_value, unit: e.size_unit, parameter_name: e.size_param },
            cost_source: "correlations",
          })),
          contingency_percent: Number(contingency),
          engineering_fee_percent: Number(engineering),
        },
        discount_rate: Number(discountRate),
        project_lifetime_years: Number(lifetime),
        annual_revenue_usd: Number(revenue),
      });
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  const capex = results ? (results as Record<string, unknown>).capex as Record<string, unknown> | undefined : undefined;
  const costSummary = capex ? capex.cost_summary as Record<string, unknown> | undefined : undefined;
  const npvData = results ? (results as Record<string, unknown>).npv_analysis as Record<string, unknown> | undefined : undefined;
  const eqCosts = capex ? capex.equipment_costs as Record<string, unknown>[] | undefined : undefined;

  const fmt = (n: number) => n >= 1e6 ? `${(n / 1e6).toFixed(2)}M` : n >= 1e3 ? `${(n / 1e3).toFixed(0)}K` : n.toFixed(0);

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Economic Evaluation</span></div>
        <h1>Economic Evaluation</h1>
        <p>CAPEX estimation with CEPCI escalation, Lang factors, and NPV/IRR analysis.</p>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>Project Data</h2></div>

          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group full-width"><label className="form-label">Project Name</label><input className="form-input" value={projectName} onChange={(e) => setProjectName(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Location Factor</label><input className="form-input" type="number" step="0.1" value={locationFactor} onChange={(e) => setLocationFactor(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Base Year</label><input className="form-input" type="number" value={baseYear} onChange={(e) => setBaseYear(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Target Year</label><input className="form-input" type="number" value={targetYear} onChange={(e) => setTargetYear(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Contingency <span className="unit">(%)</span></label><input className="form-input" type="number" value={contingency} onChange={(e) => setContingency(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Engineering Fee <span className="unit">(%)</span></label><input className="form-input" type="number" value={engineering} onChange={(e) => setEngineering(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Discount Rate</label><input className="form-input" type="number" step="0.01" value={discountRate} onChange={(e) => setDiscountRate(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Project Lifetime <span className="unit">(yr)</span></label><input className="form-input" type="number" value={lifetime} onChange={(e) => setLifetime(e.target.value)} /></div>
            <div className="form-group"><label className="form-label">Annual Revenue <span className="unit">(USD)</span></label><input className="form-input" type="number" value={revenue} onChange={(e) => setRevenue(e.target.value)} /></div>
          </div>

          <div className="flex items-center justify-between mb-16">
            <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Equipment List</h3>
            <button className="btn btn-secondary btn-sm" onClick={addEquipment}>+ Add</button>
          </div>
          <div style={{ overflowX: "auto" }}>
            <table className="data-table" style={{ marginBottom: 20 }}>
              <thead><tr><th>Tag</th><th>Type</th><th>Material</th><th>Size</th><th>Unit</th><th></th></tr></thead>
              <tbody>
                {equipmentList.map((eq, i) => (
                  <tr key={i}>
                    <td><input className="form-input" value={eq.tag} style={{ width: 70 }} onChange={(e) => { const u = [...equipmentList]; u[i] = { ...eq, tag: e.target.value }; setEquipmentList(u); }} /></td>
                    <td><select className="form-select" value={eq.type} onChange={(e) => { const u = [...equipmentList]; u[i] = { ...eq, type: e.target.value }; setEquipmentList(u); }}>
                      <option value="shell_and_tube_heat_exchanger">S&T Heat Exchanger</option>
                      <option value="centrifugal_pump">Centrifugal Pump</option>
                      <option value="pressure_vessel">Pressure Vessel</option>
                      <option value="distillation_column">Distillation Column</option>
                      <option value="compressor">Compressor</option>
                      <option value="storage_tank">Storage Tank</option>
                    </select></td>
                    <td><select className="form-select" value={eq.material} onChange={(e) => { const u = [...equipmentList]; u[i] = { ...eq, material: e.target.value }; setEquipmentList(u); }}>
                      <option value="carbon_steel">Carbon Steel</option><option value="stainless_steel_304">SS 304</option><option value="stainless_steel_316">SS 316</option>
                    </select></td>
                    <td><input className="form-input" type="number" style={{ width: 70 }} value={eq.size_value} onChange={(e) => { const u = [...equipmentList]; u[i] = { ...eq, size_value: Number(e.target.value) }; setEquipmentList(u); }} /></td>
                    <td><input className="form-input" style={{ width: 50 }} value={eq.size_unit} onChange={(e) => { const u = [...equipmentList]; u[i] = { ...eq, size_unit: e.target.value }; setEquipmentList(u); }} /></td>
                    <td><button className="btn btn-secondary btn-sm" onClick={() => setEquipmentList(equipmentList.filter((_, j) => j !== i))} style={{ padding: "0 8px" }}>&times;</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleEvaluate} disabled={loading}>
              {loading ? <><span className="spinner" /> Evaluating...</> : "Run Economic Evaluation"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>Results</h2>{costSummary && <span className="badge badge-success">Complete</span>}</div>
          {!costSummary ? (
            <div className="empty-state"><div className="icon">&#x1F4B0;</div><p>Enter project data and equipment list to evaluate economics.</p></div>
          ) : (
            <>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Cost Summary</h3>
              <div className="results-grid" style={{ marginBottom: 20 }}>
                <div className="result-item"><div className="label">Equipment Cost</div><div className="value">${fmt(Number(costSummary.total_equipment_cost_usd))}</div></div>
                <div className="result-item"><div className="label">Lang Factor</div><div className="value">{Number(costSummary.lang_factor).toFixed(2)}</div></div>
                <div className="result-item"><div className="label">Installed Cost</div><div className="value">${fmt(Number(costSummary.total_installed_cost_usd))}</div></div>
                <div className="result-item highlight"><div className="label">Total CAPEX</div><div className="value">${fmt(Number(costSummary.total_capital_cost_usd))}</div></div>
              </div>

              {eqCosts && eqCosts.length > 0 && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Equipment Breakdown</h3>
                  <table className="data-table" style={{ marginBottom: 20 }}>
                    <thead><tr><th>Tag</th><th>Base Cost</th><th>Installed Cost</th></tr></thead>
                    <tbody>
                      {eqCosts.map((eq, i) => (
                        <tr key={i}>
                          <td className="font-mono">{String(eq.tag)}</td>
                          <td>${Number(eq.base_cost_usd).toLocaleString()}</td>
                          <td>${Number(eq.installed_cost_usd).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              )}

              {npvData && (
                <>
                  <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>NPV / IRR Analysis</h3>
                  <div className="results-grid">
                    <div className={`result-item ${Number(npvData.npv_usd) > 0 ? "success" : "warning"}`}>
                      <div className="label">NPV</div>
                      <div className="value">${fmt(Number(npvData.npv_usd))}</div>
                    </div>
                    {npvData.irr_percent != null && (
                      <div className="result-item highlight"><div className="label">IRR</div><div className="value">{Number(npvData.irr_percent).toFixed(1)}<span className="unit">%</span></div></div>
                    )}
                    {npvData.simple_payback_years != null && (
                      <div className="result-item"><div className="label">Payback</div><div className="value">{Number(npvData.simple_payback_years).toFixed(1)}<span className="unit">yr</span></div></div>
                    )}
                    <div className="result-item"><div className="label">Annual Cash Flow</div><div className="value">${fmt(Number(npvData.annual_cash_flow_usd))}</div></div>
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
