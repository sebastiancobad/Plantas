/**
 * ChemScale — Main Application Shell.
 *
 * Full-featured layout with navigation for all 12 engineering modules.
 */

import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";

const MODULES = [
  { path: "/", label: "Dashboard", icon: "grid" },
  { path: "/thermo", label: "Thermodynamic Properties", icon: "flame" },
  { path: "/piping", label: "Pipe Sizing & Hydraulics", icon: "pipe" },
  { path: "/materials", label: "Material Selection", icon: "shield" },
  { path: "/plant-layout", label: "Plant Layout", icon: "layout" },
  { path: "/separators", label: "Phase Separators", icon: "layers" },
  { path: "/pumps", label: "Pump Selection", icon: "pump" },
  { path: "/heat-exchangers", label: "Heat Exchanger Design", icon: "transfer" },
  { path: "/distillation", label: "Distillation Column", icon: "column" },
  { path: "/psv", label: "Safety Relief Valves", icon: "valve" },
  { path: "/process-safety", label: "Process Safety", icon: "alert" },
  { path: "/apc", label: "Advanced Process Control", icon: "sliders" },
  { path: "/pid", label: "P&ID Development", icon: "diagram" },
  { path: "/economics", label: "Economic Evaluation", icon: "dollar" },
];

function Sidebar() {
  const location = useLocation();
  return (
    <nav style={{ width: 260, borderRight: "1px solid #e0e0e0", padding: "16px 0",
                  background: "#fafafa", minHeight: "100vh", overflowY: "auto" }}>
      <div style={{ padding: "0 16px 16px", borderBottom: "1px solid #e0e0e0", marginBottom: 8 }}>
        <h2 style={{ fontSize: 20, margin: 0, color: "#1a73e8", fontWeight: 700 }}>ChemScale</h2>
        <p style={{ fontSize: 11, color: "#666", margin: "4px 0 0" }}>Chemical Engineering Platform</p>
      </div>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {MODULES.map((m) => {
          const isActive = location.pathname === m.path;
          return (
            <li key={m.path}>
              <Link to={m.path} style={{
                display: "block", padding: "8px 16px", textDecoration: "none",
                color: isActive ? "#1a73e8" : "#333", fontSize: 13,
                background: isActive ? "#e8f0fe" : "transparent",
                borderLeft: isActive ? "3px solid #1a73e8" : "3px solid transparent",
                fontWeight: isActive ? 600 : 400,
              }}>
                {m.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

function Dashboard() {
  const modules = [
    { title: "Thermo Engine", desc: "PR & SRK EOS, NRTL, UNIQUAC — 27+ compounds with DIPPR correlations" },
    { title: "Pipe Sizing", desc: "Darcy-Weisbach, Colebrook-White, API 14E erosional velocity" },
    { title: "Materials", desc: "12 alloys, CO₂/H₂S corrosion, NACE MR0175 screening" },
    { title: "Plant Layout", desc: "API 2510 spacing tables, plot plan estimation" },
    { title: "Phase Separators", desc: "2/3-phase, horizontal/vertical, Souders-Brown" },
    { title: "Pump Sizing", desc: "System curves, NPSH, affinity laws, motor selection" },
    { title: "Heat Exchangers", desc: "Shell & tube, Kern method, TEMA/ASME compliance" },
    { title: "Distillation", desc: "FUG shortcut, tray/packing selection, flooding check" },
    { title: "Safety Valves", desc: "API 520/521 gas/liquid/fire case, orifice selection" },
    { title: "Process Safety", desc: "Dow F&EI, HAZOP templates, case studies" },
    { title: "APC", desc: "PID tuning (Z-N, Cohen-Coon, Lambda), control strategies" },
    { title: "Economics", desc: "CAPEX, OPEX, CEPCI escalation, NPV/IRR analysis" },
  ];
  return (
    <div>
      <h1 style={{ fontSize: 28, marginBottom: 8 }}>ChemScale Dashboard</h1>
      <p style={{ color: "#555", marginBottom: 24 }}>Chemical Engineering Design & Sizing Platform — 12 Integrated Modules</p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 16 }}>
        {modules.map((m) => (
          <div key={m.title} style={{ padding: 16, border: "1px solid #e0e0e0", borderRadius: 8, background: "#fff" }}>
            <h3 style={{ fontSize: 15, margin: "0 0 6px", color: "#1a73e8" }}>{m.title}</h3>
            <p style={{ fontSize: 12, color: "#666", margin: 0 }}>{m.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function ModulePage({ title, endpoint, description }: { title: string; endpoint: string; description: string }) {
  return (
    <div>
      <h1 style={{ fontSize: 24, marginBottom: 8 }}>{title}</h1>
      <p style={{ color: "#555", marginBottom: 16 }}>{description}</p>
      <div style={{ padding: 16, background: "#f5f5f5", borderRadius: 8, marginBottom: 16 }}>
        <p style={{ fontSize: 13, margin: 0 }}>
          <strong>API Endpoint:</strong>{" "}
          <code style={{ background: "#e0e0e0", padding: "2px 6px", borderRadius: 4 }}>
            POST /api/v1{endpoint}
          </code>
        </p>
        <p style={{ fontSize: 12, color: "#666", marginTop: 8, marginBottom: 0 }}>
          See <a href="/docs" target="_blank" rel="noopener noreferrer">API Documentation</a> for full input/output schema.
        </p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh", fontFamily: "'Inter', -apple-system, sans-serif" }}>
        <Sidebar />
        <main style={{ flex: 1, padding: 32, maxWidth: 1200, overflowY: "auto" }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/thermo" element={<ModulePage title="Thermodynamic Properties" endpoint="/thermo/properties" description="Calculate mixture properties using PR/SRK EOS and NRTL/UNIQUAC activity models." />} />
            <Route path="/piping" element={<ModulePage title="Pipe Sizing & Hydraulics" endpoint="/piping/size" description="Darcy-Weisbach pressure drop, Colebrook-White friction factor, pipe schedule selection." />} />
            <Route path="/materials" element={<ModulePage title="Material Selection & Metallurgy" endpoint="/materials/select" description="CO₂/H₂S corrosion calculators, NACE MR0175 sour service screening, alloy recommendation." />} />
            <Route path="/plant-layout" element={<ModulePage title="Plant Layout & Location" endpoint="/plant-layout/generate" description="API 2510 spacing tables, plot plan area estimation, wind direction analysis." />} />
            <Route path="/separators" element={<ModulePage title="Phase Separator Sizing" endpoint="/separators/design" description="2-phase/3-phase separator design with Souders-Brown, demister sizing, retention time." />} />
            <Route path="/pumps" element={<ModulePage title="Pump Selection & Sizing" endpoint="/pumps/design" description="System head curves, NPSH analysis, centrifugal vs PD selection, motor sizing." />} />
            <Route path="/heat-exchangers" element={<ModulePage title="Heat Exchanger Design" endpoint="/heat-exchangers/design" description="Shell & tube design via Kern method, LMTD correction, TEMA/ASME/API 660 compliance." />} />
            <Route path="/distillation" element={<ModulePage title="Distillation Column Design" endpoint="/distillation/design" description="Fenske-Underwood-Gilliland shortcut, tray/packing selection, flooding analysis." />} />
            <Route path="/psv" element={<ModulePage title="Safety Relief Valves" endpoint="/psv/size" description="API 520/521 sizing for gas, liquid, and fire case scenarios. Standard orifice selection." />} />
            <Route path="/process-safety" element={<ModulePage title="Process Safety & Industrial Hygiene" endpoint="/process-safety/dow-fei" description="Dow F&EI calculation, HAZOP worksheet generation, case study database." />} />
            <Route path="/apc" element={<ModulePage title="Advanced Process Control" endpoint="/apc/tune-pid" description="PID tuning (Ziegler-Nichols, Cohen-Coon, Lambda), control strategy selection." />} />
            <Route path="/pid" element={<ModulePage title="P&ID Development" endpoint="/pid/generate" description="ISA 5.1 symbol library, automated line numbering, P&ID drawing data export." />} />
            <Route path="/economics" element={<ModulePage title="Economic Evaluation" endpoint="/economics/evaluate" description="CAPEX (CEPCI, Lang factors), OPEX, utility demand, NPV/IRR analysis." />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
