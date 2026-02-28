# ChemScale — Architecture Design Document

> **Version:** 0.1.0
> **Status:** Stakeholder Review
> **Author:** Lead Architect / Sr. Chemical Process Engineer
> **Date:** 2026-02-28

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Tech Stack & High-Level Architecture](#2-tech-stack--high-level-architecture)
3. [Core System Foundations](#3-core-system-foundations)
4. [The Calculation Pipeline](#4-the-calculation-pipeline)
5. [Module Catalog](#5-module-catalog)
6. [Phased Development Roadmap](#6-phased-development-roadmap)
7. [Proof of Concept — Deep Dive](#7-proof-of-concept--deep-dive)
8. [Security, Compliance & Standards](#8-security-compliance--standards)
9. [Deployment Architecture](#9-deployment-architecture)

---

## 1. Executive Summary

**ChemScale** is a cloud-native, modular Chemical Engineering Design and Sizing
platform. It replaces fragmented spreadsheets and legacy tools with a unified,
standards-compliant system covering equipment sizing, thermodynamic analysis,
safety evaluation, and economic assessment.

The platform is built around two non-negotiable foundations:

| Foundation | Purpose |
|---|---|
| **Thermodynamic & Physical Property Engine** | Peng-Robinson, SRK, NRTL, UNIQUAC EOS/activity models for dynamic mixture property calculation |
| **Component Database** | DIPPR-style structured chemical property repository with 400+ compounds |

These foundations feed **12 integrated engineering modules** that span the full
lifecycle of process plant design — from pipe sizing to CAPEX estimation.

---

## 2. Tech Stack & High-Level Architecture

### 2.1 Technology Selection Rationale

| Layer | Technology | Justification |
|---|---|---|
| **Backend API** | Python 3.12 + FastAPI | Dominant language in scientific computing; async I/O for concurrent requests; automatic OpenAPI docs |
| **Computation Engine** | NumPy, SciPy, CoolProp | Battle-tested numerical solvers; CoolProp for reference-quality fluid properties |
| **Task Queue** | Celery + Redis | Offloads heavy iterative calculations (distillation convergence, rigorous HX rating) to background workers |
| **Database** | PostgreSQL 16 | ACID compliance for engineering data integrity; JSONB for flexible equipment datasheets |
| **Cache** | Redis | Sub-millisecond caching of repeated thermo lookups (VLE, enthalpy) |
| **Frontend** | React 18 + TypeScript | Component-based UI; rich ecosystem for charting (Recharts) and CAD-like layout (React Flow) |
| **State Management** | Zustand | Lightweight, avoids Redux boilerplate for engineering form state |
| **API Communication** | REST (JSON) + WebSocket | REST for CRUD; WebSocket for real-time convergence progress on iterative solvers |
| **Containerization** | Docker + Docker Compose | Reproducible local dev; identical prod images |
| **Cloud Deployment** | AWS (ECS Fargate) | Serverless containers; auto-scaling compute for burst thermo calculations |
| **CI/CD** | GitHub Actions | Integrated with the repository; test → lint → build → deploy pipeline |
| **Unit System** | Pint (Python) | Eliminates unit conversion errors — the single largest source of engineering mistakes |

### 2.2 High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + TS)                         │
│  ┌─────────┐  ┌───────────┐  ┌──────────┐  ┌─────────────────────┐  │
│  │ Dashbrd │  │ Module UI │  │ Datasheet│  │  P&ID Canvas        │  │
│  │  Page   │  │   Forms   │  │  Viewer  │  │  (React Flow)       │  │
│  └────┬────┘  └─────┬─────┘  └────┬─────┘  └──────────┬──────────┘  │
│       └──────────────┴─────────────┴───────────────────┘             │
│                              │  REST / WebSocket                     │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────────┐
│                     API GATEWAY (FastAPI)                             │
│                              │                                       │
│  ┌───────────┐  ┌────────────┴──────────┐  ┌──────────────────────┐  │
│  │  Auth &   │  │   /api/v1/...         │  │   WebSocket          │  │
│  │  RBAC     │  │   Module Endpoints    │  │   Progress Channel   │  │
│  └───────────┘  └────────────┬──────────┘  └──────────────────────┘  │
│                              │                                       │
│  ┌───────────────────────────┼───────────────────────────────────────┤
│  │              SERVICE LAYER (Business Logic)                       │
│  │                           │                                       │
│  │  ┌─────────────────────── ┼ ─────────────────────────────┐       │
│  │  │     CALCULATION PIPELINE ORCHESTRATOR                  │       │
│  │  │                        │                               │       │
│  │  │  ┌─────────────┐  ┌───┴────────┐  ┌───────────────┐  │       │
│  │  │  │ INPUT       │  │ THERMO     │  │ MODULE        │  │       │
│  │  │  │ VALIDATION  │→ │ ENGINE     │→ │ CALCULATOR    │  │       │
│  │  │  │ (Pydantic)  │  │ (EOS/Act.) │  │ (HX, Pump..) │  │       │
│  │  │  └─────────────┘  └────────────┘  └───────┬───────┘  │       │
│  │  │                                           │           │       │
│  │  │                                   ┌───────┴───────┐   │       │
│  │  │                                   │ DATASHEET     │   │       │
│  │  │                                   │ GENERATOR     │   │       │
│  │  │                                   └───────────────┘   │       │
│  │  └───────────────────────────────────────────────────────┘       │
│  └───────────────────────────────────────────────────────────────────┤
│                              │                                       │
│  ┌───────────┐  ┌────────────┴──────────┐  ┌──────────────────────┐  │
│  │  Redis    │  │   PostgreSQL          │  │   Celery Workers     │  │
│  │  Cache    │  │   (Components, Eqp.)  │  │   (Heavy Compute)    │  │
│  └───────────┘  └───────────────────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.3 Backend Package Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI application factory
│   ├── core/
│   │   ├── config.py              # Environment & settings
│   │   └── units.py               # Pint unit registry
│   ├── api/v1/
│   │   ├── router.py              # Central router aggregation
│   │   └── endpoints/
│   │       ├── thermo.py          # Thermodynamic property queries
│   │       ├── components.py      # Chemical component CRUD
│   │       ├── heat_exchangers.py # Module 6
│   │       ├── economics.py       # Module 12
│   │       ├── piping.py          # Module 1
│   │       ├── separators.py      # Module 4
│   │       ├── pumps.py           # Module 5
│   │       ├── distillation.py    # Module 7
│   │       ├── psv.py             # Module 8
│   │       └── ...                # Other modules
│   ├── models/
│   │   ├── component.py           # SQLAlchemy ORM: chemical components
│   │   ├── equipment.py           # SQLAlchemy ORM: equipment datasheets
│   │   └── project.py             # SQLAlchemy ORM: project metadata
│   ├── schemas/
│   │   ├── thermo.py              # Pydantic: thermo request/response
│   │   ├── heat_exchanger.py      # Pydantic: HX I/O
│   │   ├── economics.py           # Pydantic: econ I/O
│   │   └── ...
│   ├── services/
│   │   ├── thermo/
│   │   │   ├── eos.py             # Peng-Robinson, SRK implementations
│   │   │   ├── activity.py        # NRTL, UNIQUAC implementations
│   │   │   └── properties.py      # Mixture property calculator
│   │   ├── components/
│   │   │   └── database.py        # Component lookup service
│   │   └── modules/
│   │       ├── heat_exchanger.py   # HX design engine
│   │       ├── economics.py        # Economic evaluation engine
│   │       ├── piping.py           # Pipe sizing engine
│   │       └── ...
│   ├── db/
│   │   └── database.py            # Engine, session, Base
│   └── utils/
│       └── constants.py           # Gas constant, standard conditions
├── tests/
│   ├── test_thermo.py
│   ├── test_heat_exchanger.py
│   └── test_economics.py
└── requirements.txt
```

---

## 3. Core System Foundations

### 3.1 Thermodynamic & Physical Property Engine

This is the **heartbeat** of ChemScale. Every engineering module depends on
accurate fluid properties — density, viscosity, enthalpy, fugacity, VLE.

#### 3.1.1 Equations of State (EOS)

| Model | Use Case | Key Equation |
|---|---|---|
| **Peng-Robinson (PR)** | Hydrocarbon systems, refinery gas plants | `P = RT/(V-b) - a·α(T)/[V(V+b) + b(V-b)]` |
| **Soave-Redlich-Kwong (SRK)** | Gas processing, lighter hydrocarbons | `P = RT/(V-b) - a·α(T)/[V(V+b)]` |

Both are implemented as cubic EOS solvers using Cardano's method for the
compressibility factor `Z`, with generalized mixing rules (van der Waals
one-fluid) for multi-component systems.

#### 3.1.2 Activity Coefficient Models

| Model | Use Case |
|---|---|
| **NRTL** | Strongly non-ideal liquid mixtures (alcohol-water, azeotropes) |
| **UNIQUAC** | Size-asymmetric molecules, polymer systems |

These models provide liquid-phase activity coefficients `γᵢ` for VLE
calculations using the γ-φ approach: `yᵢ·φᵢ·P = xᵢ·γᵢ·Pᵢˢᵃᵗ`.

#### 3.1.3 Property Calculation Services

```
Flash Calculations:    TP-flash, PH-flash, bubble/dew point
Transport Properties:  Viscosity (Lucas), thermal conductivity (Stiel-Thodos)
Mixture Rules:         Kay's rule (pseudocritical), Wilke (viscosity mixing)
```

#### 3.1.4 Caching Strategy

Thermo calculations are **expensive** (iterative VLE solves can take 50-200ms).
Redis caches results keyed by `hash(components, T, P, composition)` with a 1-hour TTL.
Cache hit rates of 60-80% are expected for parametric studies.

### 3.2 Component Database

Structured after DIPPR, the component database stores:

| Property Category | Examples | Storage |
|---|---|---|
| **Critical Properties** | Tc, Pc, ω (acentric factor), Vc | Scalar columns |
| **Temperature Correlations** | Cp(T), μ(T), λ(T), Pvap(T) | JSONB (coefficient arrays) |
| **Binary Interaction Params** | kᵢⱼ (PR/SRK), τᵢⱼ (NRTL), uᵢⱼ (UNIQUAC) | Relational join table |
| **Safety Data** | Autoignition temp, LEL/UEL, IDLH | Scalar columns |
| **Material Compatibility** | Corrosion rates with common alloys | JSONB |

The database ships pre-seeded with **400+ compounds** commonly encountered in
oil & gas, petrochemical, and chemical manufacturing.

---

## 4. The Calculation Pipeline

Every engineering calculation in ChemScale follows a **uniform 5-stage pipeline**.
This ensures consistency, traceability, and auditability across all 12 modules.

```
  ┌─────────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
  │  STAGE 1    │    │  STAGE 2    │    │  STAGE 3     │    │  STAGE 4    │    │  STAGE 5     │
  │             │    │             │    │              │    │             │    │              │
  │  User Input │ →  │  Thermo     │ →  │  Module      │ →  │  Standards  │ →  │  Datasheet   │
  │  Validation │    │  Engine     │    │  Calculator  │    │  Compliance │    │  Output      │
  │             │    │             │    │              │    │             │    │              │
  └─────────────┘    └─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
       │                   │                   │                   │                  │
   Pydantic            EOS/Activity        Engineering         API/ASME/TEMA      JSON + PDF
   schema              models              correlations        limit checks       generation
   validation          VLE, ρ, μ, h        & solvers           & warnings
```

### Stage-by-Stage Walkthrough (Heat Exchanger Example)

**Stage 1 — Input Validation:**
User submits process conditions via `POST /api/v1/heat-exchangers/design`.
Pydantic validates all fields: flow rates > 0, temperatures in valid ranges,
component fractions sum to 1.0 (±0.001 tolerance).

**Stage 2 — Thermodynamic Engine:**
The pipeline calls the thermo service to compute:
- Shell-side & tube-side fluid densities at inlet/outlet conditions
- Viscosities (for Reynolds number → heat transfer coefficients)
- Specific heats and enthalpies (for duty verification: Q = ṁ·Cp·ΔT)
- Thermal conductivities (for Nusselt correlations)

Properties are cached in Redis. If a prior identical lookup exists, it is
returned in <1ms instead of recomputing.

**Stage 3 — Module Calculator:**
The heat exchanger engine uses the thermo properties to:
- Calculate LMTD (or ε-NTU if crossflow)
- Estimate the overall U from Kern or Bell-Delaware correlations
- Compute required area: A = Q / (U · LMTD · Ft)
- Select tube count, pitch, shell diameter from TEMA standards

**Stage 4 — Standards Compliance:**
The result is checked against:
- TEMA mechanical limits (tube wall thickness, baffle spacing)
- ASME Sec. VIII pressure vessel design rules
- API 660 (shell & tube) or API 661 (air coolers) guidelines
- Velocity limits: tube-side < 3 m/s for CW, shell-side per TEMA tables

Warnings or errors are generated for any violations.

**Stage 5 — Datasheet Output:**
The validated result is serialized as:
- JSON response (for frontend rendering)
- Optionally a PDF datasheet conforming to PIP standards

---

## 5. Module Catalog

| # | Module | Key Standards | Core Algorithms |
|---|---|---|---|
| 1 | Pipe Sizing & Hydraulics | ASME B31.3, API 14E | Darcy-Weisbach, Colebrook-White, Beggs-Brill (multiphase) |
| 2 | Material Selection | NACE MR0175, API 571 | de Waard-Milliams (CO₂), NACE sour service curves |
| 3 | Plant Layout | API 2510, NFPA 30 | Spacing tables, separation distance matrices |
| 4 | Phase Separators | API 12J, GPSA | Souders-Brown, droplet settling (Stokes' law), retention time |
| 5 | Pump Selection | API 610, HI Standards | Affinity laws, system curve vs. pump curve intersection, NPSH margin |
| 6 | Heat Exchanger Design | TEMA, ASME VIII, API 660/661 | Kern, Bell-Delaware, ε-NTU, Colburn j-factor |
| 7 | Distillation Column | GPSA, Sulzer/Koch packing data | McCabe-Thiele, Fenske-Underwood-Gilliland, stage-by-stage |
| 8 | Safety Relief Valves | API 520/521, ASME VIII | Orifice sizing (gas/liquid/two-phase), fire case per API 521 |
| 9 | Process Safety | OSHA PSM, EPA RMP | Dow F&EI, HAZOP templates, consequence modeling |
| 10 | Advanced Process Control | ISA-5.1, ISA-95 | PID tuning (Ziegler-Nichols), cascade/FF/MPC selection |
| 11 | P&ID Development | ISA 5.1, PIP PIC001 | Symbol library, automated line numbering |
| 12 | Economic Evaluation | AACE, CEPCI | Six-tenths rule, Lang factors, discounted cash flow |

---

## 6. Phased Development Roadmap

### Phase 1 — MVP Foundation (Months 1-4)

> **Goal:** Working thermodynamic engine + 3 most-requested modules + frontend shell.

| Sprint | Deliverable |
|---|---|
| 1-2 | Thermodynamic Engine (PR, SRK EOS) + Component Database (200 compounds) |
| 3-4 | Module 1: Pipe Sizing & Hydraulics (single-phase + two-phase) |
| 5-6 | Module 5: Pump Selection & Sizing (centrifugal focus) |
| 7-8 | Module 6: Heat Exchanger Design (shell & tube, conceptual + rating) |
| 9-10 | Frontend shell: dashboard, module forms, result visualization |
| 11-12 | Module 12: Economic Evaluation (CAPEX estimation, utility costing) |
| 13-14 | Integration testing, CI/CD pipeline, staging deployment |

**Phase 1 Exit Criteria:**
- User can design a pump + piping + HX system end-to-end
- CAPEX estimate generated automatically from equipment sizes
- All thermo results validated against NIST/DIPPR within ±2%

### Phase 2 — Separation & Safety (Months 5-8)

> **Goal:** Cover the critical separation and safety engineering workflows.

| Sprint | Deliverable |
|---|---|
| 15-16 | Module 4: Phase Separators (2-phase + 3-phase, horizontal/vertical) |
| 17-18 | Module 7: Distillation Column Design (shortcut + rigorous) |
| 19-20 | Module 8: Safety Relief Valves (API 520/521 sizing) |
| 21-22 | Activity Coefficient Models (NRTL, UNIQUAC) for non-ideal VLE |
| 23-24 | Module 2: Material Selection & Metallurgy (corrosion calculators) |
| 25-26 | End-to-end integration: distillation → condenser (HX) → reflux pump → PSV |

**Phase 2 Exit Criteria:**
- Full distillation column design with condenser/reboiler HX sizing
- PSV sizing for all standard overpressure scenarios
- Material recommendations based on process conditions

### Phase 3 — Plant Design & Intelligence (Months 9-12)

> **Goal:** Complete the platform with layout, P&ID, APC, and safety modules.

| Sprint | Deliverable |
|---|---|
| 27-28 | Module 3: Plant Layout & Location (spacing tables, plot plan) |
| 29-30 | Module 11: P&ID Development (ISA symbol library, auto-generation) |
| 31-32 | Module 9: Process Safety & Industrial Hygiene (HAZOP templates) |
| 33-34 | Module 10: Advanced Process Control (control strategy selection) |
| 35-36 | Cross-module integration: full plant design workflow |
| 37-38 | PDF datasheet generation, report export, audit trail |
| 39-40 | Performance optimization, load testing, production hardening |

**Phase 3 Exit Criteria:**
- User can design an entire process unit from PFD to cost estimate
- P&ID auto-generated from equipment connections
- HAZOP worksheet pre-populated from process conditions

---

## 7. Proof of Concept — Deep Dive

### 7.1 Module 6: Heat Exchanger Design

#### 7.1.1 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/heat-exchangers/design` | Run conceptual or rigorous HX design |
| `POST` | `/api/v1/heat-exchangers/rate` | Rate an existing HX geometry |
| `GET`  | `/api/v1/heat-exchangers/{id}` | Retrieve a saved HX datasheet |
| `GET`  | `/api/v1/heat-exchangers/tema-types` | List available TEMA shell/head types |

#### 7.1.2 JSON Input — Design Mode

```json
{
  "calculation_mode": "design",
  "exchanger_type": "shell_and_tube",
  "tema_type": "AES",

  "hot_side": {
    "fluid_name": "crude_oil_mix",
    "components": [
      {"name": "n-hexane",  "mole_fraction": 0.35},
      {"name": "n-heptane", "mole_fraction": 0.40},
      {"name": "n-octane",  "mole_fraction": 0.25}
    ],
    "mass_flow_rate":    {"value": 50000, "unit": "kg/hr"},
    "inlet_temperature": {"value": 150,   "unit": "degC"},
    "outlet_temperature":{"value": 90,    "unit": "degC"},
    "inlet_pressure":    {"value": 5.0,   "unit": "barg"},
    "fouling_resistance":{"value": 0.00035, "unit": "m2*K/W"},
    "placement": "shell"
  },

  "cold_side": {
    "fluid_name": "cooling_water",
    "components": [
      {"name": "water", "mole_fraction": 1.0}
    ],
    "mass_flow_rate":    {"value": 80000, "unit": "kg/hr"},
    "inlet_temperature": {"value": 30,    "unit": "degC"},
    "outlet_temperature":{"value": 45,    "unit": "degC"},
    "inlet_pressure":    {"value": 4.0,   "unit": "barg"},
    "fouling_resistance":{"value": 0.00018, "unit": "m2*K/W"},
    "placement": "tube"
  },

  "mechanical_constraints": {
    "max_shell_diameter":  {"value": 1500, "unit": "mm"},
    "tube_od":             {"value": 19.05, "unit": "mm"},
    "tube_bwg":            14,
    "tube_length":         {"value": 6096, "unit": "mm"},
    "tube_pitch_ratio":    1.25,
    "tube_layout_angle":   30,
    "baffle_cut_percent":  25,
    "tube_material":       "carbon_steel",
    "shell_material":      "carbon_steel",
    "design_pressure":     {"value": 10.0, "unit": "barg"},
    "design_temperature":  {"value": 200,  "unit": "degC"}
  },

  "options": {
    "correlation_method": "bell_delaware",
    "include_vibration_check": true,
    "include_pressure_drop": true
  }
}
```

#### 7.1.3 Expected JSON Output — Design Result

```json
{
  "status": "success",
  "calculation_id": "hx-2026-00142",
  "warnings": [
    "Shell-side velocity (0.42 m/s) is below recommended minimum (0.5 m/s). Consider reducing baffle spacing."
  ],

  "thermal_results": {
    "duty":              {"value": 2847.5, "unit": "kW"},
    "lmtd":             {"value": 48.3,   "unit": "K"},
    "correction_factor_ft": 0.87,
    "effective_mtd":     {"value": 42.0,   "unit": "K"},
    "overall_u_clean":   {"value": 485.2,  "unit": "W/m2/K"},
    "overall_u_dirty":   {"value": 362.1,  "unit": "W/m2/K"},
    "required_area":     {"value": 187.4,  "unit": "m2"},
    "excess_area_percent": 12.3,
    "shell_side_htc":    {"value": 1250.0, "unit": "W/m2/K"},
    "tube_side_htc":     {"value": 5200.0, "unit": "W/m2/K"}
  },

  "hydraulic_results": {
    "shell_side_pressure_drop": {"value": 0.45, "unit": "bar"},
    "tube_side_pressure_drop":  {"value": 0.32, "unit": "bar"},
    "shell_side_velocity":      {"value": 0.42, "unit": "m/s"},
    "tube_side_velocity":       {"value": 1.85, "unit": "m/s"}
  },

  "mechanical_summary": {
    "tema_designation":  "AES",
    "shell_id":          {"value": 1050, "unit": "mm"},
    "tube_count":        620,
    "tube_passes":       2,
    "baffle_count":      18,
    "baffle_spacing":    {"value": 320, "unit": "mm"},
    "tube_sheet_thickness": {"value": 45, "unit": "mm"}
  },

  "vibration_check": {
    "natural_frequency_hz": 42.5,
    "vortex_shedding_hz":  18.2,
    "fluidelastic_ratio":  0.65,
    "status": "PASS"
  },

  "compliance": {
    "tema_check":  "PASS",
    "asme_viii":   "PASS",
    "api_660":     "PASS",
    "velocity_limits": "WARNING — shell side below minimum"
  }
}
```

### 7.2 Module 12: Economic Evaluation & Industrial Utilities

#### 7.2.1 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/economics/capex` | Estimate capital cost of equipment |
| `POST` | `/api/v1/economics/opex` | Estimate annual operating cost |
| `POST` | `/api/v1/economics/utilities` | Calculate utility demand and cost |
| `GET`  | `/api/v1/economics/cepci/{year}` | Get CEPCI index for a given year |
| `POST` | `/api/v1/economics/evaluate` | Full economic evaluation (CAPEX + OPEX + NPV) |

#### 7.2.2 JSON Input — CAPEX Estimation

```json
{
  "project_name": "Crude Oil Stabilizer Unit",
  "location_factor": 1.15,
  "base_year": 2020,
  "target_year": 2026,

  "equipment_list": [
    {
      "tag": "E-101",
      "type": "shell_and_tube_heat_exchanger",
      "material": "carbon_steel",
      "design_pressure_barg": 10.0,
      "size_parameter": {"value": 187.4, "unit": "m2", "parameter_name": "area"},
      "base_cost_usd": null,
      "cost_source": "correlations"
    },
    {
      "tag": "P-101A/B",
      "type": "centrifugal_pump",
      "material": "stainless_steel_316",
      "design_pressure_barg": 15.0,
      "size_parameter": {"value": 75, "unit": "kW", "parameter_name": "driver_power"},
      "base_cost_usd": null,
      "cost_source": "correlations"
    },
    {
      "tag": "V-101",
      "type": "vertical_pressure_vessel",
      "material": "carbon_steel",
      "design_pressure_barg": 8.0,
      "size_parameter": {"value": 15.0, "unit": "m3", "parameter_name": "volume"},
      "base_cost_usd": null,
      "cost_source": "correlations"
    }
  ],

  "lang_factor_method": "detailed",
  "contingency_percent": 15.0,
  "engineering_fee_percent": 12.0
}
```

#### 7.2.3 JSON Input — Utility Demand

```json
{
  "utilities": {
    "steam": {
      "consumers": [
        {"tag": "E-102", "duty_kW": 1500, "steam_pressure": "LP", "description": "Reboiler"}
      ]
    },
    "cooling_water": {
      "consumers": [
        {"tag": "E-101", "duty_kW": 2847.5, "delta_t_degC": 15, "description": "Crude cooler"}
      ]
    },
    "instrument_air": {
      "consumers": [
        {"tag": "FCV-101", "flow_nm3_hr": 5.0, "description": "Flow control valve"},
        {"tag": "LCV-101", "flow_nm3_hr": 3.0, "description": "Level control valve"}
      ]
    },
    "electricity": {
      "consumers": [
        {"tag": "P-101A", "power_kW": 75, "operating_hours": 8400}
      ]
    }
  },
  "unit_costs": {
    "lp_steam_per_ton": 25.0,
    "mp_steam_per_ton": 35.0,
    "hp_steam_per_ton": 45.0,
    "cooling_water_per_m3": 0.05,
    "electricity_per_kWh": 0.08,
    "instrument_air_per_nm3": 0.02
  }
}
```

#### 7.2.4 Expected JSON Output — CAPEX Result

```json
{
  "status": "success",
  "calculation_id": "econ-2026-00087",

  "cepci": {
    "base_year": 2020,
    "base_index": 596.2,
    "target_year": 2026,
    "target_index": 823.5,
    "escalation_factor": 1.381
  },

  "equipment_costs": [
    {
      "tag": "E-101",
      "type": "shell_and_tube_heat_exchanger",
      "base_cost_usd": 85200,
      "escalated_cost_usd": 117660,
      "material_factor": 1.0,
      "pressure_factor": 1.15,
      "installed_cost_usd": 135310
    },
    {
      "tag": "P-101A/B",
      "type": "centrifugal_pump",
      "base_cost_usd": 42000,
      "escalated_cost_usd": 58002,
      "material_factor": 2.1,
      "pressure_factor": 1.1,
      "installed_cost_usd": 133954
    },
    {
      "tag": "V-101",
      "type": "vertical_pressure_vessel",
      "base_cost_usd": 28500,
      "escalated_cost_usd": 39359,
      "material_factor": 1.0,
      "pressure_factor": 1.2,
      "installed_cost_usd": 47231
    }
  ],

  "cost_summary": {
    "total_equipment_cost_usd": 316495,
    "lang_factor": 4.28,
    "total_installed_cost_usd": 1354599,
    "engineering_fee_usd": 162552,
    "contingency_usd": 203190,
    "total_capital_cost_usd": 1720341,
    "location_adjusted_usd": 1978392
  },

  "utility_demand_summary": {
    "lp_steam_ton_hr": 2.45,
    "cooling_water_m3_hr": 163.5,
    "instrument_air_nm3_hr": 8.0,
    "electricity_kW": 75.0,
    "annual_utility_cost_usd": 295400
  }
}
```

#### 7.2.5 Expected JSON Output — OPEX Result

```json
{
  "status": "success",
  "annual_opex": {
    "raw_materials_usd": 0,
    "utilities_usd": 295400,
    "labor_usd": 480000,
    "maintenance_usd": 68022,
    "insurance_usd": 34011,
    "overhead_usd": 192000,
    "total_annual_opex_usd": 1069433
  },
  "unit_production_cost": {
    "value": 12.85,
    "unit": "USD/bbl"
  }
}
```

---

## 8. Security, Compliance & Standards

| Area | Implementation |
|---|---|
| **Authentication** | JWT-based auth with RBAC (Viewer, Engineer, Admin) |
| **Data Integrity** | All calculations are immutable — saved with input hash for audit |
| **Calculation Audit** | Every result stores: input hash, software version, timestamp, user ID |
| **Standards Traceability** | Each compliance check references the specific clause (e.g., "TEMA R-2.31") |
| **Unit Safety** | All internal calculations use SI. Conversion happens only at I/O boundary |

---

## 9. Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     AWS Cloud                            │
│                                                          │
│   ┌──────────────┐     ┌────────────────────────────┐   │
│   │ CloudFront   │────→│  S3 (React Frontend)       │   │
│   │ (CDN)        │     └────────────────────────────┘   │
│   └──────┬───────┘                                      │
│          │                                               │
│   ┌──────┴───────┐     ┌────────────────────────────┐   │
│   │  ALB         │────→│  ECS Fargate (API)          │   │
│   │  (Load Bal.) │     │  2-8 tasks (auto-scaling)   │   │
│   └──────────────┘     └──────────┬─────────────────┘   │
│                                   │                      │
│          ┌────────────────────────┼──────────────┐      │
│          │                        │              │      │
│   ┌──────┴───────┐  ┌────────────┴───┐  ┌───────┴──┐  │
│   │ RDS Postgres │  │ ElastiCache    │  │ ECS      │  │
│   │ (Multi-AZ)   │  │ (Redis)        │  │ Workers  │  │
│   └──────────────┘  └────────────────┘  └──────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Scaling Strategy:**
- API containers scale horizontally on CPU/memory thresholds
- Celery workers scale on queue depth (0 → 10 workers in 60s)
- PostgreSQL: read replicas for component database queries
- Redis: cluster mode for high-throughput thermo cache
