import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import ThermoPage from "./pages/ThermoPage";
import PipingPage from "./pages/PipingPage";
import MaterialsPage from "./pages/MaterialsPage";
import PlantLayoutPage from "./pages/PlantLayoutPage";
import SeparatorsPage from "./pages/SeparatorsPage";
import PumpsPage from "./pages/PumpsPage";
import HeatExchangerPage from "./pages/HeatExchangerPage";
import DistillationPage from "./pages/DistillationPage";
import PSVPage from "./pages/PSVPage";
import ProcessSafetyPage from "./pages/ProcessSafetyPage";
import APCPage from "./pages/APCPage";
import PIDPage from "./pages/PIDPage";
import EconomicsPage from "./pages/EconomicsPage";

const NAV_SECTIONS = [
  {
    label: "Overview",
    items: [
      { path: "/", label: "Dashboard", icon: "\u25A6" },
    ],
  },
  {
    label: "Core",
    items: [
      { path: "/thermo", label: "Thermodynamics", icon: "\u2697" },
      { path: "/piping", label: "Pipe Sizing", icon: "\u2502" },
      { path: "/materials", label: "Materials", icon: "\u25C8" },
    ],
  },
  {
    label: "Process Design",
    items: [
      { path: "/separators", label: "Phase Separators", icon: "\u2261" },
      { path: "/pumps", label: "Pump Sizing", icon: "\u2699" },
      { path: "/heat-exchangers", label: "Heat Exchangers", icon: "\u21C4" },
      { path: "/distillation", label: "Distillation", icon: "\u2AE8" },
    ],
  },
  {
    label: "Safety",
    items: [
      { path: "/psv", label: "Relief Valves", icon: "\u26A0" },
      { path: "/process-safety", label: "Process Safety", icon: "\u1F6E1" },
    ],
  },
  {
    label: "Control & Planning",
    items: [
      { path: "/apc", label: "Process Control", icon: "\u2248" },
      { path: "/pid", label: "P&ID Development", icon: "\u2B21" },
      { path: "/plant-layout", label: "Plant Layout", icon: "\u229E" },
    ],
  },
  {
    label: "Economics",
    items: [
      { path: "/economics", label: "Economic Eval.", icon: "\u0024" },
    ],
  },
];

function Sidebar() {
  const location = useLocation();
  return (
    <nav className="sidebar">
      <div className="sidebar-brand">
        <h1>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2" />
            <path d="M8.5 2h7" />
            <path d="M7 16.5h10" />
          </svg>
          ChemScale
        </h1>
        <p>Engineering Platform</p>
      </div>
      <div className="sidebar-nav">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            <div className="sidebar-section">{section.label}</div>
            {section.items.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-item ${isActive ? "active" : ""}`}
                >
                  <span className="nav-icon">{item.icon}</span>
                  {item.label}
                </Link>
              );
            })}
          </div>
        ))}
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/thermo" element={<ThermoPage />} />
            <Route path="/piping" element={<PipingPage />} />
            <Route path="/materials" element={<MaterialsPage />} />
            <Route path="/plant-layout" element={<PlantLayoutPage />} />
            <Route path="/separators" element={<SeparatorsPage />} />
            <Route path="/pumps" element={<PumpsPage />} />
            <Route path="/heat-exchangers" element={<HeatExchangerPage />} />
            <Route path="/distillation" element={<DistillationPage />} />
            <Route path="/psv" element={<PSVPage />} />
            <Route path="/process-safety" element={<ProcessSafetyPage />} />
            <Route path="/apc" element={<APCPage />} />
            <Route path="/pid" element={<PIDPage />} />
            <Route path="/economics" element={<EconomicsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
