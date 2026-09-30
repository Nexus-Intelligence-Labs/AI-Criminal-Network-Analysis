# Development Setup

## Local host-backed development

Use the host environment when Uvicorn runs directly on the workstation:

```bash
cp .env.host.example .env
docker compose up -d postgres neo4j
backend/.venv/bin/python scripts/seed/seed_dev_user.py
PYTHONPATH=backend backend/.venv/bin/python -m uvicorn app.main:app \
  --host 127.0.0.1 --port 8010 --reload
```

The host configuration uses `POSTGRES_HOST=127.0.0.1` and
`NEO4J_URI=bolt://127.0.0.1:7687`. The Compose service names `postgres` and
`neo4j` are only resolvable by processes running inside the Compose network.

Run the frontend against the real API:

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8010 \
VITE_AUTH_MODE=api \
VITE_GRAPH_MODE=api \
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173/login` and use the development credentials entered
by the seed command. The seed command is idempotent and refuses to replace an
existing username.

After login, open `/ingestion`, upload a synthetic CDR CSV, import it, and use
the result link to open `/graph?case=<case_id>`. A minimal fixture is:

```csv
caller,receiver,timestamp,duration
demo-caller,demo-receiver,2026-01-01T12:00:00Z,60
```

For a backend container, use `.env.docker.example` with
`POSTGRES_HOST=postgres`, `POSTGRES_PORT=5432`, and
`NEO4J_URI=bolt://neo4j:7687`.

## Prerequisites

Each developer should have:

- Git
- GitHub account
- VS Code
- Docker Desktop
- Python 3.12+
- Node.js LTS

## Clone Repository

```bash
git clone <repository-url>
cd AI-Criminal-Network-Analysis
