/**
 * ChemScale — Main Application Shell.
 *
 * Defines the top-level layout and routing structure.
 * Each engineering module gets its own route and lazy-loaded page.
 */

import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

function Sidebar() {
  const modules = [
    { path: "/", label: "Dashboard" },
    { path: "/thermo", label: "Thermodynamic Properties" },
    { path: "/heat-exchangers", label: "Heat Exchanger Design" },
    { path: "/economics", label: "Economic Evaluation" },
    { path: "/piping", label: "Pipe Sizing" },
    { path: "/pumps", label: "Pump Selection" },
    { path: "/separators", label: "Phase Separators" },
    { path: "/distillation", label: "Distillation Column" },
    { path: "/psv", label: "Safety Relief Valves" },
  ];

  return (
    <nav style={{ width: 240, borderRight: "1px solid #e0e0e0", padding: 16 }}>
      <h2 style={{ fontSize: 18, marginBottom: 24 }}>ChemScale</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {modules.map((m) => (
          <li key={m.path} style={{ marginBottom: 8 }}>
            <Link to={m.path} style={{ textDecoration: "none", color: "#1a73e8" }}>
              {m.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

function Dashboard() {
  return (
    <div>
      <h1>ChemScale Dashboard</h1>
      <p>Chemical Engineering Design &amp; Sizing Platform</p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginTop: 24 }}>
        <div style={{ padding: 16, border: "1px solid #e0e0e0", borderRadius: 8 }}>
          <h3>Thermo Engine</h3>
          <p>PR &amp; SRK EOS, NRTL, UNIQUAC</p>
          <p>27 compounds available</p>
        </div>
        <div style={{ padding: 16, border: "1px solid #e0e0e0", borderRadius: 8 }}>
          <h3>Heat Exchanger</h3>
          <p>Shell &amp; tube design, Kern/Bell-Delaware</p>
          <p>TEMA / ASME VIII / API 660</p>
        </div>
        <div style={{ padding: 16, border: "1px solid #e0e0e0", borderRadius: 8 }}>
          <h3>Economics</h3>
          <p>CAPEX, OPEX, NPV, IRR</p>
          <p>CEPCI 2000-2026</p>
        </div>
      </div>
    </div>
  );
}

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div>
      <h1>{title}</h1>
      <p>Module under development — see ARCHITECTURE.md for the roadmap.</p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar />
        <main style={{ flex: 1, padding: 24 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/thermo" element={<PlaceholderPage title="Thermodynamic Properties" />} />
            <Route path="/heat-exchangers" element={<PlaceholderPage title="Heat Exchanger Design" />} />
            <Route path="/economics" element={<PlaceholderPage title="Economic Evaluation" />} />
            <Route path="/piping" element={<PlaceholderPage title="Pipe Sizing & Hydraulics" />} />
            <Route path="/pumps" element={<PlaceholderPage title="Pump Selection & Sizing" />} />
            <Route path="/separators" element={<PlaceholderPage title="Phase Separators" />} />
            <Route path="/distillation" element={<PlaceholderPage title="Distillation Column Design" />} />
            <Route path="/psv" element={<PlaceholderPage title="Safety Relief Valves" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
