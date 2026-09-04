# AI-Powered Criminal Network Analysis System

## Overview

AI-Criminal-Network-Analysis is a multi-component investigation platform
foundation. It combines:

- a FastAPI backend with PostgreSQL and Neo4j connection layers;
- Python NLP, entity-resolution, relationship, event, and ingestion pipelines;
- graph loading, querying, and early network analytics code; and
- a React investigator dashboard with graph exploration and mock investigative
  workflows.

The repository is currently a development-stage system. The backend security
foundation is implemented, while most domain endpoints and the dashboard data
flows remain incomplete or demo-only. This README describes the code that
exists today; planned capabilities are explicitly labelled.

### Status legend

- ✅ **Implemented** — present in the repository and supported by the current
  implementation.
- 🟡 **Mock/demo** — interactive or representative UI/data only; not connected
  to persistent backend workflows.
- 🟠 **Partially integrated** — meaningful code exists, but important
  integration, persistence, or operational pieces are still missing.
- 🔴 **Not implemented / blocked** — planned, unavailable, or currently blocked
  by a known defect or missing integration.

## Problem Statement

Investigative records can contain people, organizations, phones, vehicles,
financial activity, communications, events, and relationships spread across
multiple sources. The project provides a place to normalize those records,
extract structured intelligence, resolve identities, store network context,
and expose investigation-oriented views.

## Project Goals

1. Normalize heterogeneous investigative records.
2. Extract entities, relationships, and events with source traceability.
3. Resolve references to the same real-world entity.
4. Represent relationships in a Neo4j knowledge graph.
5. Support graph queries and network analytics.
6. Provide a protected investigator-facing API and dashboard.
7. Keep uncertain or model-generated results reviewable and explainable.

## Current Scope at a Glance

| Area | Current state |
| --- | --- |
| Backend API | FastAPI routes and security foundation; most domain handlers are placeholders |
| PostgreSQL | SQLAlchemy models and connection factory; no migration system |
| Neo4j | Driver, writers, loaders, queries, and graph service code; schema/integration is incomplete |
| AI/NLP | Working modules for extraction, resolution, structured processors, and pipeline orchestration |
| Graph analytics | Early degree/PageRank/Louvain code; graph analytics modules currently have syntax errors |
| Frontend | React/Vite investigator UI using local mock data |
| Frontend authentication | Development-only mock session; not connected to backend JWT login |
| End-to-end integration | Not complete |
| Production readiness | Not claimed |

## System Architecture

The intended repository flow is:

```text
Source records
    |
    v
AI preprocessing and structured processors
    |
    +--> NER / entity extraction
    +--> relationship and event extraction
    +--> entity resolution
    |
    v
Graph adapter / Neo4j writer
    |
    v
Neo4j graph queries and analytics
    |
    v
FastAPI API
    |
    v
React investigator dashboard
```

The flow is not yet a single production pipeline. AI writers, graph schema
conventions, backend graph queries, and frontend data services still require
integration work.

## Repository Structure

```text
.
├── ai/                 NLP, entity resolution, pipelines, AI tests
├── backend/            FastAPI application, models, schemas, services, tests
├── data/               Source-category placeholders and data documentation
├── docs/               Architecture, API, data-contract, and decision notes
├── frontend/           React/Vite investigator dashboard
├── graph/              Neo4j queries, loaders, services, analytics, schema
├── scripts/            Reserved ingestion, seed, and utility locations
├── tests/              Repository-level test placeholder area
├── .env.example        Development environment variable template
└── docker-compose.yml  PostgreSQL and Neo4j development services
```

The source-category directories under `data/` and the subdirectories under
`scripts/` currently contain placeholders rather than a complete ingestion
deployment.

## Technology Stack

### Backend

- Python 3.12+ (the checked-in development environment uses Python 3.14)
- FastAPI
- Pydantic v2 and `pydantic-settings`
- Uvicorn
- SQLAlchemy 2
- `psycopg`
- Neo4j Python driver
- PyJWT
- `pwdlib` with Argon2
- pytest and HTTPX

### AI / NLP

- spaCy and `en_core_web_sm`
- Hugging Face Transformers
- Sentence Transformers
- PyTorch
- pandas, NumPy, scikit-learn
- NetworkX
- RapidFuzz / python-Levenshtein / thefuzz

The AI requirements file does not currently declare every import used by the
repository. In particular, Neo4j and `google-genai` are used by some AI
modules but are not listed in `ai/requirements.txt`; install them explicitly
in the AI environment when exercising those modules.

### Frontend

- React 19
- TypeScript
- Vite 6
- React Router 7
- Tailwind CSS
- Radix UI / shadcn-style primitives
- Lucide React
- Cytoscape.js
- Recharts

## Data Architecture

### PostgreSQL

The backend defines SQLAlchemy models for:

- `User`: username, password hash, creation time;
- `AuditLog`: security action, actor, JSON details, timestamp;
- `Case`: case identifier, title, status, description, timestamp; and
- `Evidence`: identifier, case, type, source, and collection timestamp.

The PostgreSQL URL is constructed from `POSTGRES_*` settings. A session and
engine factory exist, but the repository does not contain Alembic migrations,
schema lifecycle management, or complete domain persistence workflows.

### Neo4j

Neo4j is used by:

- `ai/graph/neo4j_writer.py` for AI-derived entities, relationships, and events;
- `graph/loaders/` for graph synchronization and synthetic/demo loading;
- `graph/services/graph_query_service.py` for case graphs, neighbors, and
  shortest paths; and
- `backend/app/db/neo4j.py` and the backend graph service.

The documented graph model describes typed `Entity` nodes, case identifiers,
timestamps, evidence/source metadata, and relationship types. There is no
executable schema/migration/index setup. The AI writer currently uses generic
`:Entity` nodes and `RELATED` relationships, while backend queries and graph
documentation expect case-aware and typed relationships. This mismatch must be
resolved before claiming end-to-end graph correctness.

## Backend Architecture

The application entry point is `backend/app/main.py` and registers
`backend/app/api/router.py`.

### Registered routes

| Route | Status |
| --- | --- |
| `GET /health` | Implemented health response |
| `POST /api/auth/login` | Implemented database-backed login |
| `GET /api/entities/` | Protected placeholder |
| `GET /api/relationships/` | Protected placeholder |
| `GET /api/graph/{case_id}` | Delegates to graph service |
| `GET /api/graph/neighbors/{entity_id}` | Delegates to graph service |
| `GET /api/graph/shortest-path` | Delegates to graph service |
| `GET /api/search/` | Protected placeholder |
| `GET /api/alerts/` | Protected placeholder |
| `GET /api/cases/` | Protected placeholder |
| `GET /api/timelines/` | Protected placeholder |
| `GET /api/evidence/` | Protected placeholder |
| `GET /api/analytics/` | Protected placeholder |

Most domain route handlers currently return a not-implemented response. The
graph route ordering should also be reviewed so the literal `shortest-path`
route cannot be captured by `/{case_id}`.

`backend/realtime_api.py` is a separate, unregistered FastAPI application for
CDR, financial, and FIR ingestion. It initializes a global AI pipeline and is
not the application registered by `backend/app/main.py`.

## Security Architecture

### Implemented backend controls

- Password hashing and verification use Argon2 through `pwdlib`.
- Login verifies the database user and issues a signed JWT.
- JWTs contain `sub`, `iat`, and `exp` claims.
- JWT verification uses a server-controlled HS256 allowlist.
- `JWT_SECRET` must be non-empty and at least 32 UTF-8 bytes.
- Production rejects known insecure placeholder secrets.
- Token lifetime is positive and capped at seven days.
- Protected routes resolve the current user from a bearer token.
- Invalid or missing credentials receive generic authentication failures.
- Login success/failure, authentication failure, and authorization denial audit
  events are represented by the audit service.
- Role helper dependencies exist and return 403 for denied roles.

### Security limitations

The `User` model does not have a persisted role column, and existing routes
primarily use `get_current_user` rather than role-specific guards. There is no
refresh/revocation mechanism, registration flow, password-reset backend,
rate-limiting layer, security middleware, or migration-managed authorization
policy. The separate `realtime_api.py` is not equivalent to the secured main
API and should not be exposed without additional hardening.

### Authentication architecture

The frontend and backend authentication flows are currently separate:

```text
Frontend /login
    |
    v
mockAuthService
    |
    v
localStorage or sessionStorage session
    |
    v
RequireAuth protects dashboard routes
```

```text
POST /api/auth/login
    |
    v
FastAPI auth route
    |
    v
Argon2 password verification
    |
    v
JWT access token
    |
    v
Bearer-protected backend routes
```

`frontend/src/services/auth/mockAuthService.ts` accepts any non-empty
email/password pair. `frontend/src/pages/Login.tsx` requires an email-shaped
identifier. The frontend does not call `/api/auth/login`, does not store a
backend JWT, and does not attach `Authorization` headers. `VITE_API_BASE_URL`
is present in `.env.example` but is not currently used by frontend API code.

## AI / NLP Architecture

### Preprocessing and extraction

`ai/nlp/preprocessor.py` performs Unicode normalization, whitespace cleanup,
and limited Indian `+91` phone formatting. It is not an OCR, language
detection, sentence segmentation, or full provenance system.

`ai/nlp/entity_extractor.py` combines:

- spaCy `en_core_web_sm` NER;
- hard-coded spaCy EntityRuler patterns;
- Hugging Face `dslim/bert-base-NER`;
- Indian phone and vehicle regular expressions; and
- heuristic de-duplication.

The current extraction is primarily English/model and pattern based. It has
limited domain coverage and does not provide a complete date extraction
implementation.

### Entity resolution

`ai/entity_resolution/` supports in-memory and Neo4j-backed stores. Matching
is same-type and combines fuzzy string similarity, phone/address/organization
fields, and `all-MiniLM-L6-v2` embeddings. Results are categorized with
high/review/low thresholds and persistent identities use UUID canonical IDs.

There is no complete blocking/indexing strategy, alias-management system,
calibration workflow, human-review persistence, or probabilistic model.
Embeddings are computed synchronously during comparison; there is no standalone
vector pipeline or vector index.

### Relationships, events, and pipelines

- Gemini-backed relationship extraction returns validated structured JSON from
  an allowlisted relationship vocabulary and requires `GEMINI_API_KEY`.
- Event extraction currently uses keyword presence for call, transfer, travel,
  meeting, and location categories; it does not fully recover event arguments,
  timestamps, amounts, or evidence spans.
- CDR and financial processors normalize and validate structured records.
- The unified pipeline accepts `cdr`, `financial`, and `fir` records, resolves
  entities, adapts graph data, validates relationships, extracts events, and
  can write to Neo4j.

Model initialization, external Gemini access, Neo4j availability, and missing
AI dependency declarations affect which pipeline paths can run locally.

## Knowledge Graph and Analytics

### Implemented building blocks

- Cypher query files for entity/relationship creation, case graphs, neighbors,
  and shortest paths.
- `GraphQueryService` that loads those queries and executes them through a
  Neo4j driver.
- `GraphService` used by the backend graph routes.
- Synthetic/demo graph generators and a relationship generator.
- Early degree-centrality and PageRank code.
- Louvain community detection code that expects an existing GDS projection
  named `criminalGraph`.

### Current defects and gaps

The current checkout does not compile cleanly:

- `graph/analytics/centrality.py` has unindented method bodies.
- `graph/loaders/graph_loader.py` contains an unterminated/malformed
  triple-quoted query and indentation errors.

The graph tests directory contains no substantive tests. There is no graph
projection lifecycle, no implemented betweenness/similarity/anomaly/influence
analytics, and no executable schema migration or index setup. Synthetic
loaders use development credentials, can clear data destructively, and are not
production ingestion tooling.

## Frontend / Investigator Dashboard

The frontend is a React/Vite application with one `BrowserRouter`, providers
for theme and authentication, a `RequireAuth` boundary, Tailwind styling,
Radix/shadcn-style components, Cytoscape graph visualization, and Recharts
charts.

### Public routes

- `/login`
- `/forgot-password`
- `/reset-password`
- `/access-request`
- `/session-expired`
- `/unauthorized`

### Protected routes

- `/dashboard`
- `/cases`
- `/search`
- `/entities`
- `/entities/:entityId`
- `/graph`
- `/timeline`
- `/evidence`
- `/alerts`
- `/analytics`
- `/settings`
- `/investigations`
- `/reviews`
- `/saved-queries`
- `/alert-rules`

Unknown paths redirect to `/dashboard`. The frontend has no matching
`/cases/:caseId` route even though an entity-detail navigation path refers to
case detail; that route should be added or the navigation corrected.

### User-facing workflows

| Workflow | Current implementation |
| --- | --- |
| Login and session gate | Local mock session and protected routing |
| Dashboard | Local graph metrics, risk/activity panels, and quick actions |
| Cases/entities/evidence/timeline/alerts | UI pages backed by local mock datasets |
| Graph | Cytoscape graph, filters, layouts, search, hop-depth control, and demo explanations |
| Investigations | Local investigation selector, graph, entity inspector, evidence/assistant/notes/cross-case panels |
| AI review | Local entity-resolution and extraction accept/reject queue |
| Saved queries | Local create/run/duplicate/delete state |
| Alert rules | Local rule-builder state |
| Analytics | Local charts and selectable demo analysis scopes |
| Settings | Frontend settings UI |

These workflows are useful interaction prototypes, not backend-connected
investigation records.

## Investigative Workflow Status

| Capability | Status | Meaning |
| --- | --- | --- |
| Investigation workspace | 🟡 Frontend/demo | Interactive local workspace; no persistence/API |
| Multi-hop graph controls | 🟡 Frontend/demo | Controls affect the demo UI; backend query integration is pending |
| Shortest-path UI | 🟠 Partial | Backend query exists; no complete connected frontend workflow |
| Relationship explanation | 🟡 Frontend/demo | Local explanation panel and mock reasoning |
| Evidence/provenance | 🟡 Frontend/demo | Local evidence records and provenance display |
| AI assistant | 🟡 Frontend/demo | Local canned responses/citations; no model service call |
| Entity-resolution review | 🟡 Frontend/demo | Local accept/reject queue |
| AI extraction review | 🟡 Frontend/demo | Local accept/reject queue |
| Cross-case analysis | 🟡 Frontend/demo | Mock shared-entity comparison |
| Network comparison/change detection | 🔴 Planned | No connected change-detection implementation |
| Temporal graph | 🟡 Frontend/demo | Local timeline control; no temporal backend query |
| Saved queries | 🟡 Frontend/demo | In-memory local state |
| Advanced search/query builder | 🟡 Frontend/demo | Local query-builder controls |
| Investigator notes | 🟡 Frontend/demo | Local UI state; no persistence |
| Alert-rule builder | 🟡 Frontend/demo | Local UI state; no alert execution |
| “Why am I seeing this?” | 🟡 Frontend/demo | Local explainability panel |
| Analytics workspace | 🟡 Frontend/demo | Local chart data and filters |
| Dashboard insights | 🟡 Frontend/demo | Local metrics and mock graph |

## Mock and Demo Data

The following frontend areas use files under `frontend/src/mocks/` or local
component state:

- graph nodes and relationships;
- cases and entities;
- evidence and relationships;
- dashboard metrics;
- investigations and cross-case comparisons;
- assistant responses and citations;
- review queues;
- saved queries and alert rules.

The sidebar labels the application as demo mode. No mock record should be
interpreted as a live case, real alert, verified intelligence, or model
decision.

## Local Development Setup

### Prerequisites

- Git
- Docker and Docker Compose
- Python 3.12+ (Python 3.14 is used by the checked-in environments)
- Node.js and npm

### Clone and environment

```bash
git clone <repository-url>
cd AI-Criminal-Network-Analysis
cp .env.example .env
```

Replace development placeholder secrets before using shared or production
environments. In particular, `JWT_SECRET` must be at least 32 UTF-8 bytes and
must not be a known placeholder in production.

## Running Infrastructure

`docker-compose.yml` provisions PostgreSQL and Neo4j:

```bash
docker compose up -d
docker compose ps
docker compose down
```

Services and ports:

- PostgreSQL: configured host port, container port 5432;
- Neo4j Bolt: 7687; and
- Neo4j browser/HTTP: 7474.

The compose file uses named volumes for PostgreSQL and Neo4j data. The
application does not currently run migrations automatically.

## Running the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

On Windows, activate with the shell-specific command for the created virtual
environment. The API provides:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

The application requires `JWT_SECRET` during settings initialization. Database
connections are created through the configured factories, but most domain
routes are not implemented yet.

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Other available scripts:

```bash
npm run typecheck
npm run lint
npm run build
npm run preview
```

The current frontend can be explored without a running backend because its
authentication and dashboard data are local demo implementations.

## Running the AI / NLP Code

```bash
cd ai
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest tests/
```

Some modules additionally import `neo4j` and `google-genai`, which are not
declared in `ai/requirements.txt`. Neo4j integration tests require a reachable
Neo4j instance and appropriate environment variables. Gemini tests require
`GEMINI_API_KEY` and may be skipped or unavailable without external access.

## Testing

### Backend

```bash
cd backend
python -m pytest
```

The backend suite covers health, models, authentication, JWT validation,
protected routes, authorization dependencies, audit logging, and security
hardening. The historical development baseline was 143 passing tests; rerun
the command above for the current checkout rather than treating that number
as a permanent guarantee.

### AI/NLP

```bash
cd ai
python -m pytest tests/
```

The suite includes preprocessing, NER, processors, entity resolution,
relationship parsing, events, adapters, writers, and pipeline tests. Several
tests are infrastructure- or API-dependent.

### Graph and integration

The `graph/tests/` directory currently has no substantive test suite.
Neo4j-dependent AI integration tests require running infrastructure and
credentials. Graph compilation currently fails on the syntax defects described
above.

### Frontend

There are no frontend unit-test files currently present. The available
validation commands are:

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

The frontend has previously passed these commands with two existing
Fast Refresh warnings from shared UI primitive exports. Vite may also report a
large JavaScript bundle warning.

## Dependency and Configuration Notes

Important environment variables are documented in `.env.example`:

| Variable group | Purpose |
| --- | --- |
| `POSTGRES_*` | PostgreSQL connection and container configuration |
| `NEO4J_*` | Neo4j connection and container configuration |
| `BACKEND_*` | Backend bind host and port |
| `VITE_API_BASE_URL` | Intended frontend API base URL; currently unused |
| `JWT_SECRET` | Required backend signing secret |
| `JWT_ALGORITHM` | Backend JWT algorithm, restricted to HS256 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Backend access-token lifetime |

Do not commit `.env` files or real credentials. Synthetic graph scripts still
contain development credential assumptions and should not be used as-is for
shared environments.

## Current Implementation Status

| Subsystem | Status | Evidence / limitation |
| --- | --- | --- |
| Architecture | 🟠 Partially integrated | Components exist but are not one end-to-end production flow |
| Backend API | 🟠 Partially integrated | FastAPI and route registration exist; most domain routes are placeholders |
| PostgreSQL | 🟠 Partially integrated | Models/factory exist; no migrations or full persistence |
| Neo4j | 🟠 Partially integrated | Driver/query/writer code exists; ontology and synchronization disagree |
| Graph analytics | 🔴 Blocked | Current centrality/loader syntax errors; GDS lifecycle absent |
| AI/NLP | 🟠 Partially integrated | Multiple working modules; external models/services and provenance remain incomplete |
| Entity resolution | 🟠 Partially integrated | Similarity and canonical IDs exist; no durable review/calibration workflow |
| Security | ✅ Implemented foundation | Backend Argon2/JWT/bearer/audit hardening exists; broader controls remain |
| Frontend | 🟡 Frontend/demo | React application and protected UI routes exist |
| Dashboard | 🟡 Frontend/demo | Metrics and graph use local data |
| Investigative workflows | 🟡 Frontend/demo | Interactive prototypes, not persisted investigations |
| Backend ↔ frontend | 🔴 Not integrated | Frontend does not call API or attach JWTs |
| AI ↔ frontend | 🔴 Not integrated | Review and assistant screens use local mocks |
| Neo4j ↔ frontend | 🔴 Not integrated | Graph visualization uses frontend mock graph data |
| End-to-end integration | 🔴 Planned | Requires API, persistence, graph, and AI wiring |
| Testing | 🟠 Partial | Backend/AI suites exist; graph/frontend unit coverage is limited |
| Deployment | 🔴 Development only | Compose is local infrastructure, not a production deployment |
| Production readiness | 🔴 Not claimed | Security and integration gaps remain |

## Roadmap

The next work should be driven by the actual gaps:

1. Fix graph module syntax errors and add graph tests.
2. Establish executable Neo4j constraints, indexes, and projection lifecycle.
3. Reconcile AI writer, graph loader, schema, and backend query ontology,
   including `case_id`, typed relationships, and source provenance.
4. Add PostgreSQL migrations and complete domain persistence services.
5. Connect frontend authentication to `/api/auth/login`, JWT storage, token
   expiry handling, and bearer requests.
6. Replace frontend mocks with authenticated API services incrementally.
7. Add durable investigations, evidence, notes, saved queries, reviews, and
   alert rules.
8. Add retries, batching, model caching, observability, and queue-based
   ingestion for AI pipelines.
9. Add frontend tests, graph tests, API integration tests, and infrastructure
   test profiles.
10. Remove hard-coded credentials and define a deployment/security process.
11. Reduce the frontend bundle and add production build/deployment automation.

## Responsible and Explainable Intelligence

The project is intended to keep extracted intelligence traceable to source
records and to avoid unsupported inference. Current implementation does not
yet provide complete provenance spans, calibrated confidence, durable human
review, or production auditability for every AI-derived graph change.

The frontend assistant, explanations, evidence panels, and review queues are
explicitly local demo workflows. They must not be presented as authoritative
model conclusions or live investigative intelligence.

## Contributing and Git Workflow

Use focused branches and review changes before merging:

```bash
git status
git diff --check
```

Keep credentials and generated environments out of commits. Changes that
affect authentication, graph ontology, AI provenance, or data retention should
include tests and documentation updates.

## License

No project license file is currently present in the repository. Add and
document a license before distributing the software.
