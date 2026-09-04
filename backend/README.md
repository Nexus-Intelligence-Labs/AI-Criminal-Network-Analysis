# Backend

Initial FastAPI backend foundation for the AI Criminal Network Analysis system.
It provides the API boundary, configuration, database connection factories,
validation schemas, and service placeholders. Domain workflows will be added
without coupling route handlers directly to database clients.

## Setup

Python 3.14 is recommended.

```powershell
cd backend
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The application reads configuration from environment variables. Database
services are not contacted while importing the application, so the API can be
started before PostgreSQL or Neo4j is available. Set the variables listed in
`app/core/config.py` before using database-backed features.

## Run

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Visit:

- `http://127.0.0.1:8000/health` for the health response
- `http://127.0.0.1:8000/docs` for the OpenAPI/Swagger UI

Run tests from `backend/`:

```powershell
python -m pytest
```

## Structure

```text
backend/
├── app/
│   ├── api/          FastAPI router and route modules
│   ├── core/         Configuration and logging
│   ├── db/           PostgreSQL and Neo4j infrastructure
│   ├── models/       SQLAlchemy model placeholders
│   ├── schemas/      Pydantic request/response schemas
│   └── services/     Domain service interfaces/placeholders
├── tests/            Backend tests
├── requirements.txt  Runtime and test dependencies
└── README.md
```
