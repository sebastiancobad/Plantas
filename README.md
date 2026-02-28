# ChemScale

**Chemical Engineering Design & Sizing Platform**

A cloud-native, modular application for end-to-end chemical process design —
from thermodynamic property calculations to equipment sizing and economic evaluation.

## Quick Start

```bash
# Start all services (API, PostgreSQL, Redis)
docker-compose up -d

# API documentation available at:
# http://localhost:8000/docs    (Swagger UI)
# http://localhost:8000/redoc   (ReDoc)
```

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full design document including:
- Tech stack and high-level architecture
- 5-stage calculation pipeline
- Phased development roadmap (3 phases, 12 modules)
- Proof-of-concept deep dives for Heat Exchanger Design and Economic Evaluation

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Computation | NumPy, SciPy, CoolProp |
| Database | PostgreSQL 16 |
| Cache | Redis |
| Frontend | React 18, TypeScript, Vite |
| Containers | Docker, Docker Compose |

## Project Structure

```
├── ARCHITECTURE.md              # Full architecture design document
├── Dockerfile                   # Multi-stage Docker build
├── docker-compose.yml           # Local development stack
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── core/                # Config, units
│   │   ├── api/v1/endpoints/    # REST API endpoints
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic I/O schemas
│   │   ├── services/
│   │   │   ├── thermo/          # EOS, activity models, property calculator
│   │   │   ├── components/      # Chemical component database
│   │   │   └── modules/         # Engineering calculation engines
│   │   ├── db/                  # Database session management
│   │   └── utils/               # Constants, helpers
│   ├── tests/                   # Pytest test suite
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.tsx              # Application shell + routing
    │   ├── services/api.ts      # API client
    │   └── main.tsx             # Entry point
    ├── package.json
    └── tsconfig.json
```

## Implemented Modules (Phase 1 MVP)

### Core Foundations
- **Thermodynamic Engine**: Peng-Robinson & SRK equations of state, NRTL & UNIQUAC activity models
- **Component Database**: 27 compounds with critical properties (Tc, Pc, ω, Mw)

### Module 6 — Heat Exchanger Design
- Shell & tube design (Kern method)
- LMTD + Ft correction factor
- Tube count estimation, shell selection from TEMA series
- Standards compliance (TEMA, ASME VIII, API 660)
- Vibration analysis check

### Module 12 — Economic Evaluation
- CAPEX: Cost correlations, CEPCI escalation (2000–2026), material/pressure factors, Lang factors
- Utilities: Steam, cooling water, instrument air, electricity demand
- OPEX: Labor, maintenance, insurance, overhead
- NPV / IRR analysis

## API Endpoints

| Method | Endpoint | Module |
|---|---|---|
| `POST` | `/api/v1/thermo/properties` | Thermodynamic properties |
| `GET` | `/api/v1/thermo/components` | Component database |
| `POST` | `/api/v1/heat-exchangers/design` | HX design |
| `GET` | `/api/v1/heat-exchangers/tema-types` | TEMA type catalog |
| `POST` | `/api/v1/economics/capex` | CAPEX estimation |
| `POST` | `/api/v1/economics/utilities` | Utility demand |
| `POST` | `/api/v1/economics/opex` | OPEX estimation |
| `POST` | `/api/v1/economics/evaluate` | Full economic evaluation |
| `GET` | `/api/v1/economics/cepci/{year}` | CEPCI lookup |

## Running Tests

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v
```

## Standards Compliance

ASME, API 520/521/610/660/661, TEMA, ISA 5.1, NACE MR0175, PIP, AACE
