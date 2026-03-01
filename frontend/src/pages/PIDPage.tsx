import { useState } from "react";
import { pidApi } from "../services/api";

interface Equipment { tag: string; type: string; description: string; x: number; y: number; }
interface Instrument { measured_variable: string; function: string; loop_number: number; location: string; }

export default function PIDPage() {
  const [unitNumber, setUnitNumber] = useState("100");
  const [equipment, setEquipment] = useState<Equipment[]>([
    { tag: "V-101", type: "vessel", description: "Feed Drum", x: 100, y: 200 },
    { tag: "P-101A/B", type: "pump", description: "Feed Pump", x: 300, y: 200 },
    { tag: "E-101", type: "heat_exchanger", description: "Feed Preheater", x: 500, y: 200 },
  ]);
  const [instruments, setInstruments] = useState<Instrument[]>([
    { measured_variable: "L", function: "IC", loop_number: 101, location: "field" },
    { measured_variable: "P", function: "IC", loop_number: 102, location: "control_room" },
    { measured_variable: "T", function: "IC", loop_number: 103, location: "control_room" },
  ]);
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addEquipment = () => setEquipment([...equipment, { tag: "", type: "vessel", description: "", x: 100, y: 100 }]);
  const addInstrument = () => setInstruments([...instruments, { measured_variable: "T", function: "IC", loop_number: 100, location: "field" }]);

  const handleGenerate = async () => {
    setLoading(true); setError(""); setResults(null);
    try {
      const res = await pidApi.generatePID({ unit_number: unitNumber, equipment, instruments, lines: [] });
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Generation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data) : msg);
    } finally { setLoading(false); }
  };

  const pidData = results ? (results as Record<string, unknown>).pid_data as Record<string, unknown> | undefined : undefined;

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ P&ID Development</span></div>
        <h1>P&ID Development</h1>
        <p>ISA 5.1 symbol library, instrument tagging, and line numbering.</p>
      </div>

      <div className="module-layout">
        <div className="card">
          <div className="card-header"><h2>P&ID Input</h2></div>

          <div className="form-grid" style={{ marginBottom: 20 }}>
            <div className="form-group"><label className="form-label">Unit Number</label><input className="form-input" value={unitNumber} onChange={(e) => setUnitNumber(e.target.value)} /></div>
          </div>

          <div className="flex items-center justify-between mb-16">
            <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Equipment</h3>
            <button className="btn btn-secondary btn-sm" onClick={addEquipment}>+ Add</button>
          </div>
          <table className="data-table" style={{ marginBottom: 20 }}>
            <thead><tr><th>Tag</th><th>Type</th><th>Description</th><th></th></tr></thead>
            <tbody>
              {equipment.map((eq, i) => (
                <tr key={i}>
                  <td><input className="form-input" value={eq.tag} onChange={(e) => { const u = [...equipment]; u[i] = { ...eq, tag: e.target.value }; setEquipment(u); }} /></td>
                  <td><select className="form-select" value={eq.type} onChange={(e) => { const u = [...equipment]; u[i] = { ...eq, type: e.target.value }; setEquipment(u); }}>
                    <option value="vessel">Vessel</option><option value="pump">Pump</option><option value="compressor">Compressor</option>
                    <option value="heat_exchanger">Heat Exchanger</option><option value="reactor">Reactor</option><option value="column">Column</option>
                  </select></td>
                  <td><input className="form-input" value={eq.description} onChange={(e) => { const u = [...equipment]; u[i] = { ...eq, description: e.target.value }; setEquipment(u); }} /></td>
                  <td><button className="btn btn-secondary btn-sm" onClick={() => setEquipment(equipment.filter((_, j) => j !== i))} style={{ padding: "0 8px" }}>&times;</button></td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="flex items-center justify-between mb-16">
            <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Instruments</h3>
            <button className="btn btn-secondary btn-sm" onClick={addInstrument}>+ Add</button>
          </div>
          <table className="data-table" style={{ marginBottom: 20 }}>
            <thead><tr><th>Variable</th><th>Function</th><th>Loop #</th><th>Location</th><th></th></tr></thead>
            <tbody>
              {instruments.map((inst, i) => (
                <tr key={i}>
                  <td><select className="form-select" value={inst.measured_variable} onChange={(e) => { const u = [...instruments]; u[i] = { ...inst, measured_variable: e.target.value }; setInstruments(u); }}>
                    <option value="T">Temperature</option><option value="P">Pressure</option><option value="F">Flow</option><option value="L">Level</option>
                  </select></td>
                  <td><select className="form-select" value={inst.function} onChange={(e) => { const u = [...instruments]; u[i] = { ...inst, function: e.target.value }; setInstruments(u); }}>
                    <option value="IC">Indicating Controller</option><option value="I">Indicator</option><option value="T">Transmitter</option>
                  </select></td>
                  <td><input className="form-input" type="number" value={inst.loop_number} onChange={(e) => { const u = [...instruments]; u[i] = { ...inst, loop_number: Number(e.target.value) }; setInstruments(u); }} /></td>
                  <td><select className="form-select" value={inst.location} onChange={(e) => { const u = [...instruments]; u[i] = { ...inst, location: e.target.value }; setInstruments(u); }}>
                    <option value="field">Field</option><option value="control_room">Control Room</option>
                  </select></td>
                  <td><button className="btn btn-secondary btn-sm" onClick={() => setInstruments(instruments.filter((_, j) => j !== i))} style={{ padding: "0 8px" }}>&times;</button></td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="mt-24">
            <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
              {loading ? <><span className="spinner" /> Generating...</> : "Generate P&ID Data"}
            </button>
          </div>
          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        <div className="card">
          <div className="card-header"><h2>P&ID Output</h2>{pidData && <span className="badge badge-success">Generated</span>}</div>
          {!pidData ? (
            <div className="empty-state"><div className="icon">&#x1F4CB;</div><p>Define equipment and instruments, then generate the P&ID data.</p></div>
          ) : (
            <>
              <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Equipment Nodes</h3>
              <table className="data-table" style={{ marginBottom: 20 }}>
                <thead><tr><th>ID</th><th>Type</th><th>Label</th><th>Description</th></tr></thead>
                <tbody>
                  {((pidData as Record<string, unknown>).equipment_nodes as Record<string, unknown>[])?.map((n, i) => (
                    <tr key={i}><td className="font-mono">{String(n.id)}</td><td>{String(n.type)}</td><td>{String(n.label)}</td><td>{String(n.description)}</td></tr>
                  ))}
                </tbody>
              </table>

              <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 12 }}>Instrument Tags</h3>
              <table className="data-table">
                <thead><tr><th>Tag</th><th>Type</th><th>ID</th></tr></thead>
                <tbody>
                  {((pidData as Record<string, unknown>).instrument_nodes as Record<string, unknown>[])?.map((n, i) => (
                    <tr key={i}><td className="font-mono">{String(n.tag)}</td><td>{String(n.type)}</td><td>{String(n.id)}</td></tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
