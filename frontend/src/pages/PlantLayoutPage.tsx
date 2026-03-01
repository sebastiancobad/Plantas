import { useState } from "react";
import { plantLayoutApi } from "../services/api";

interface EquipmentEntry { tag: string; type: string; }

export default function PlantLayoutPage() {
  const [equipment, setEquipment] = useState<EquipmentEntry[]>([
    { tag: "V-101", type: "pressure_vessel" },
    { tag: "F-101", type: "fired_heater" },
    { tag: "T-101", type: "storage_tank_flammable" },
    { tag: "P-101", type: "pump" },
  ]);
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addEquipment = () => setEquipment([...equipment, { tag: "", type: "pressure_vessel" }]);

  const handleGenerate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      const eqPayload = equipment.map((e) => ({
        tag: e.tag, type: e.type,
        distance_to: Object.fromEntries(equipment.filter((o) => o.tag !== e.tag).map((o) => [o.tag, 20])),
      }));
      const res = await plantLayoutApi.generateLayout({ equipment: eqPayload });
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  const spacingResults = results ? (results as Record<string, unknown>).spacing_results as Record<string, unknown>[] | undefined : undefined;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Plant Layout</span></div>
        <h1>Plant Layout & Location</h1>
        <p>API 2510 spacing tables and plot plan area estimation.</p>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>Equipment List</h2></div>

          <div className="flex items-center justify-between mb-16">
            <span className="text-sm text-muted">Define equipment to check minimum spacing per API 2510.</span>
            <button className="btn btn-secondary btn-sm" onClick={addEquipment}>+ Add</button>
          </div>
          <table className="data-table" style={{ marginBottom: 16 }}>
            <thead><tr><th>Tag</th><th>Equipment Type</th><th></th></tr></thead>
            <tbody>
              {equipment.map((eq, i) => (
                <tr key={i}>
                  <td><input className="form-input" value={eq.tag} onChange={(e) => { const u = [...equipment]; u[i] = { ...eq, tag: e.target.value }; setEquipment(u); }} /></td>
                  <td><select className="form-select" value={eq.type} onChange={(e) => { const u = [...equipment]; u[i] = { ...eq, type: e.target.value }; setEquipment(u); }}>
                    <option value="pressure_vessel">Pressure Vessel</option>
                    <option value="fired_heater">Fired Heater</option>
                    <option value="storage_tank_flammable">Storage Tank (Flammable)</option>
                    <option value="pump">Pump</option>
                    <option value="compressor">Compressor</option>
                    <option value="cooling_tower">Cooling Tower</option>
                    <option value="control_room">Control Room</option>
                    <option value="flare">Flare</option>
                  </select></td>
                  <td><button className="btn btn-secondary btn-sm" onClick={() => setEquipment(equipment.filter((_, j) => j !== i))} style={{ padding: "0 8px" }}>&times;</button></td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
              {loading ? <><span className="spinner" /> Checking...</> : "Check Spacing"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>Spacing Results</h2>{spacingResults && <span className="badge badge-success">Checked</span>}</div>
          {!spacingResults ? (
            <div className="empty-state"><div className="icon">&#x1F3D7;</div><p>Define equipment and check spacing compliance.</p></div>
          ) : (
            <>
              {results && (results as Record<string, unknown>).plot_plan_area_m2 && (
                <div className="result-item highlight" style={{ marginBottom: 16 }}>
                  <div className="label">Estimated Plot Area</div>
                  <div className="value">{Number((results as Record<string, unknown>).plot_plan_area_m2).toFixed(0)}<span className="unit">m&sup2;</span></div>
                </div>
              )}
              <table className="data-table">
                <thead><tr><th>Equipment A</th><th>Equipment B</th><th>Min (m)</th><th>Actual (m)</th><th>Status</th></tr></thead>
                <tbody>
                  {spacingResults.map((r, i) => (
                    <tr key={i}>
                      <td className="font-mono">{String(r.equipment_a)}</td>
                      <td className="font-mono">{String(r.equipment_b)}</td>
                      <td>{Number(r.minimum_distance_m).toFixed(1)}</td>
                      <td>{Number(r.actual_distance_m).toFixed(1)}</td>
                      <td><span className={`badge ${String(r.status) === "PASS" ? "badge-success" : "badge-error"}`}>{String(r.status)}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {results && (results as Record<string, unknown>).recommendations && (
                <div className="mt-16" style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                  {((results as Record<string, unknown>).recommendations as string[]).map((r, i) => <div key={i} style={{ marginTop: 4 }}>&#x2022; {r}</div>)}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
