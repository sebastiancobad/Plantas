import { useState } from "react";
import { thermoApi } from "../services/api";

interface Component {
  name: string;
  mole_fraction: number;
}

const AVAILABLE_COMPONENTS = [
  "methane", "ethane", "propane", "n-butane", "i-butane", "n-pentane",
  "i-pentane", "n-hexane", "n-heptane", "n-octane", "benzene", "toluene",
  "ethylbenzene", "water", "hydrogen", "nitrogen", "oxygen", "CO2",
  "H2S", "ammonia", "methanol", "ethanol", "acetone", "acetic_acid",
];

export default function ThermoPage() {
  const [components, setComponents] = useState<Component[]>([
    { name: "methane", mole_fraction: 0.7 },
    { name: "ethane", mole_fraction: 0.2 },
    { name: "propane", mole_fraction: 0.1 },
  ]);
  const [temperature, setTemperature] = useState("300");
  const [pressure, setPressure] = useState("101325");
  const [eosModel, setEosModel] = useState<"PR" | "SRK">("PR");
  const [phase, setPhase] = useState<"auto" | "vapor" | "liquid">("auto");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addComponent = () => {
    setComponents([...components, { name: "methane", mole_fraction: 0 }]);
  };

  const removeComponent = (idx: number) => {
    setComponents(components.filter((_, i) => i !== idx));
  };

  const updateComponent = (idx: number, field: keyof Component, value: string | number) => {
    const updated = [...components];
    if (field === "mole_fraction") {
      updated[idx] = { ...updated[idx], [field]: Number(value) };
    } else {
      updated[idx] = { ...updated[idx], [field]: value as string };
    }
    setComponents(updated);
  };

  const totalFraction = components.reduce((sum, c) => sum + c.mole_fraction, 0);

  const handleCalculate = async () => {
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const res = await thermoApi.calculateProperties({
        components,
        temperature_K: Number(temperature),
        pressure_Pa: Number(pressure),
        eos_model: eosModel,
        phase,
      });
      setResults(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Calculation failed";
      setError(typeof (err as Record<string, unknown>)?.response === "object"
        ? JSON.stringify(((err as Record<string, unknown>).response as Record<string, unknown>)?.data)
        : msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-breadcrumb">Modules <span>/ Thermodynamic Properties</span></div>
        <h1>Thermodynamic Properties</h1>
        <p>Calculate mixture properties using Peng-Robinson or SRK equation of state.</p>
      </div>

      <div className="module-layout">
        {/* Input Panel */}
        <div className="card">
          <div className="card-header">
            <h2>Input Parameters</h2>
            <span className="badge badge-info">EOS Calculation</span>
          </div>

          {/* Components Table */}
          <div style={{ marginBottom: 20 }}>
            <div className="flex items-center justify-between mb-16">
              <label className="form-label" style={{ margin: 0 }}>Components</label>
              <button className="btn btn-secondary btn-sm" onClick={addComponent}>+ Add</button>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Component</th>
                  <th>Mole Fraction</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {components.map((c, i) => (
                  <tr key={i}>
                    <td>
                      <select
                        className="form-select"
                        value={c.name}
                        onChange={(e) => updateComponent(i, "name", e.target.value)}
                      >
                        {AVAILABLE_COMPONENTS.map((name) => (
                          <option key={name} value={name}>{name}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <input
                        className="form-input"
                        type="number"
                        step="0.01"
                        min="0"
                        max="1"
                        value={c.mole_fraction}
                        onChange={(e) => updateComponent(i, "mole_fraction", e.target.value)}
                      />
                    </td>
                    <td>
                      {components.length > 1 && (
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => removeComponent(i)}
                          style={{ padding: "0 8px", minWidth: 28 }}
                        >
                          &times;
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ fontSize: 11, marginTop: 6, color: Math.abs(totalFraction - 1) < 0.01 ? "var(--success)" : "var(--error)" }}>
              Total: {totalFraction.toFixed(4)} {Math.abs(totalFraction - 1) < 0.01 ? "(valid)" : "(must sum to 1.0)"}
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Temperature <span className="unit">(K)</span></label>
              <input className="form-input" type="number" value={temperature} onChange={(e) => setTemperature(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Pressure <span className="unit">(Pa)</span></label>
              <input className="form-input" type="number" value={pressure} onChange={(e) => setPressure(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">EOS Model</label>
              <select className="form-select" value={eosModel} onChange={(e) => setEosModel(e.target.value as "PR" | "SRK")}>
                <option value="PR">Peng-Robinson</option>
                <option value="SRK">Soave-Redlich-Kwong</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Phase</label>
              <select className="form-select" value={phase} onChange={(e) => setPhase(e.target.value as "auto" | "vapor" | "liquid")}>
                <option value="auto">Auto-detect</option>
                <option value="vapor">Vapor</option>
                <option value="liquid">Liquid</option>
              </select>
            </div>
          </div>

          <div className="mt-24">
            <button
              className="btn btn-primary"
              onClick={handleCalculate}
              disabled={loading || Math.abs(totalFraction - 1) > 0.01}
            >
              {loading ? <><span className="spinner" /> Calculating...</> : "Calculate Properties"}
            </button>
          </div>

          {error && <div style={{ marginTop: 12, padding: 12, background: "var(--error-light)", borderRadius: "var(--radius-sm)", color: "var(--error)", fontSize: 12 }}>{error}</div>}
        </div>

        {/* Results Panel */}
        <div className="card">
          <div className="card-header">
            <h2>Results</h2>
            {results && <span className="badge badge-success">Calculated</span>}
          </div>

          {!results ? (
            <div className="empty-state">
              <div className="icon">&#x2697;</div>
              <p>Configure the mixture and click Calculate to see thermodynamic properties.</p>
            </div>
          ) : (
            <div className="results-grid">
              <div className="result-item highlight">
                <div className="label">Phase</div>
                <div className="value" style={{ fontSize: 16 }}>{(results as Record<string, unknown>).phase as string}</div>
              </div>
              <div className="result-item">
                <div className="label">Density</div>
                <div className="value">{Number((results as Record<string, unknown>).density_kg_m3).toFixed(2)}<span className="unit">kg/m&sup3;</span></div>
              </div>
              <div className="result-item">
                <div className="label">Mol. Weight</div>
                <div className="value">{Number((results as Record<string, unknown>).molecular_weight_g_mol).toFixed(2)}<span className="unit">g/mol</span></div>
              </div>
              <div className="result-item">
                <div className="label">Compressibility Z</div>
                <div className="value">{Number((results as Record<string, unknown>).compressibility_Z).toFixed(4)}</div>
              </div>
              <div className="result-item">
                <div className="label">Viscosity</div>
                <div className="value">{Number((results as Record<string, unknown>).viscosity_Pa_s).toExponential(3)}<span className="unit">Pa&middot;s</span></div>
              </div>
              <div className="result-item">
                <div className="label">Thermal Cond.</div>
                <div className="value">{Number((results as Record<string, unknown>).thermal_conductivity_W_mK).toFixed(4)}<span className="unit">W/mK</span></div>
              </div>
              <div className="result-item">
                <div className="label">Cp</div>
                <div className="value">{Number((results as Record<string, unknown>).heat_capacity_cp_J_molK).toFixed(2)}<span className="unit">J/mol&middot;K</span></div>
              </div>
              <div className="result-item">
                <div className="label">Molar Density</div>
                <div className="value">{Number((results as Record<string, unknown>).molar_density_mol_m3).toFixed(1)}<span className="unit">mol/m&sup3;</span></div>
              </div>
              <div className="result-item">
                <div className="label">H Departure</div>
                <div className="value">{Number((results as Record<string, unknown>).enthalpy_departure_J_mol).toFixed(1)}<span className="unit">J/mol</span></div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
