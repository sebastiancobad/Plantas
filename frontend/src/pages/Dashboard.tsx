import { Link } from "react-router-dom";

const MODULES = [
  {
    path: "/thermo",
    title: "Thermodynamic Properties",
    desc: "PR & SRK EOS, NRTL, UNIQUAC activity models with 27+ compounds and DIPPR correlations.",
    tag: "Core",
    color: "#4F6BF6",
  },
  {
    path: "/piping",
    title: "Pipe Sizing & Hydraulics",
    desc: "Darcy-Weisbach pressure drop, Colebrook-White friction factor, API 14E erosional velocity.",
    tag: "Mechanical",
    color: "#10B981",
  },
  {
    path: "/materials",
    title: "Material Selection",
    desc: "12 alloys, CO\u2082/H\u2082S corrosion, NACE MR0175 sour service screening.",
    tag: "Mechanical",
    color: "#10B981",
  },
  {
    path: "/separators",
    title: "Phase Separators",
    desc: "2-phase & 3-phase, horizontal/vertical, Souders-Brown, demister sizing.",
    tag: "Process",
    color: "#8B5CF6",
  },
  {
    path: "/pumps",
    title: "Pump Selection & Sizing",
    desc: "System curves, NPSH analysis, affinity laws, centrifugal vs PD selection.",
    tag: "Mechanical",
    color: "#10B981",
  },
  {
    path: "/heat-exchangers",
    title: "Heat Exchanger Design",
    desc: "Shell & tube design via Kern method, LMTD correction, TEMA/ASME compliance.",
    tag: "Process",
    color: "#8B5CF6",
  },
  {
    path: "/distillation",
    title: "Distillation Column",
    desc: "Fenske-Underwood-Gilliland shortcut, tray/packing selection, flooding analysis.",
    tag: "Process",
    color: "#8B5CF6",
  },
  {
    path: "/psv",
    title: "Safety Relief Valves",
    desc: "API 520/521 sizing for gas, liquid, and fire case scenarios with orifice selection.",
    tag: "Safety",
    color: "#EF4444",
  },
  {
    path: "/process-safety",
    title: "Process Safety",
    desc: "Dow F&EI calculation, HAZOP worksheet generation, historical case studies.",
    tag: "Safety",
    color: "#EF4444",
  },
  {
    path: "/apc",
    title: "Advanced Process Control",
    desc: "PID tuning (Ziegler-Nichols, Cohen-Coon, Lambda), control strategy selection.",
    tag: "Control",
    color: "#F59E0B",
  },
  {
    path: "/pid",
    title: "P&ID Development",
    desc: "ISA 5.1 symbol library, automated line numbering, P&ID drawing data export.",
    tag: "Control",
    color: "#F59E0B",
  },
  {
    path: "/plant-layout",
    title: "Plant Layout",
    desc: "API 2510 spacing tables, plot plan area estimation, and equipment placement.",
    tag: "Planning",
    color: "#F59E0B",
  },
  {
    path: "/economics",
    title: "Economic Evaluation",
    desc: "CAPEX (CEPCI, Lang factors), OPEX estimation, NPV/IRR analysis.",
    tag: "Economics",
    color: "#06B6D4",
  },
];

export default function Dashboard() {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Chemical Engineering Design & Sizing Platform</p>
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-label">Total Modules</div>
          <div className="stat-value">13</div>
          <div className="stat-sub">Engineering tools</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Process Design</div>
          <div className="stat-value">3</div>
          <div className="stat-sub">Separators, HX, Distillation</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Safety & Compliance</div>
          <div className="stat-value">2</div>
          <div className="stat-sub">PSV, Process Safety</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Standards</div>
          <div className="stat-value">8+</div>
          <div className="stat-sub">API, TEMA, ASME, NACE</div>
        </div>
      </div>

      <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16, color: "var(--text-primary)" }}>
        Engineering Modules
      </h2>

      <div className="module-grid">
        {MODULES.map((m) => (
          <Link key={m.path} to={m.path} style={{ textDecoration: "none", color: "inherit" }}>
            <div className="module-card">
              <div className="flex items-center justify-between">
                <span
                  className="module-tag"
                  style={{ color: m.color }}
                >
                  {m.tag}
                </span>
              </div>
              <h3>{m.title}</h3>
              <p>{m.desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
