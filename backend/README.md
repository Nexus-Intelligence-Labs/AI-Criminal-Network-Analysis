# Backend

FastAPI backend for the AI-Powered Criminal Network Analysis System.

## Responsibilities

The backend is responsible for:

- REST API endpoints
- Authentication and authorization
- Communication between the frontend, AI pipeline, graph database, and PostgreSQL
- Request validation
- Business logic
- Investigator-facing data retrieval

## Planned Technologies

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Neo4j Python Driver
- Pytest

## Structure

```text
backend/
├── app/
│   ├── api/          API routes
│   ├── core/         Configuration and security
│   ├── db/           Database connections
│   ├── models/       Database models
│   ├── schemas/      Pydantic schemas
│   └── services/     Business logic
└── tests/            Backend tests
