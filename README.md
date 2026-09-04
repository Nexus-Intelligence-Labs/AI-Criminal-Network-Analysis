# AI-Powered Criminal Network Analysis System

> AI-powered Investigative Intelligence Graph for Smart India Hackathon.

An investigative intelligence platform designed to transform fragmented structured and unstructured crime-related information into a connected, searchable, and explainable criminal intelligence network.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Project Goal](#project-goal)
- [Why This System](#why-this-system)
- [Core Pipeline](#core-pipeline)
- [System Architecture](#system-architecture)
- [Core Capabilities](#core-capabilities)
- [Investigative Intelligence Graph](#investigative-intelligence-graph)
- [Graph Analytics](#graph-analytics)
- [Anomaly Detection](#anomaly-detection)
- [Explainable Intelligence](#explainable-intelligence)
- [Investigator Dashboard](#investigator-dashboard)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Data Architecture](#data-architecture)
- [Backend Architecture](#backend-architecture)
- [Security Architecture](#security-architecture)
- [Development Environment](#development-environment)
- [Local Setup](#local-setup)
- [Running the Database Infrastructure](#running-the-database-infrastructure)
- [Running the Backend](#running-the-backend)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Git and Contribution Workflow](#git-and-contribution-workflow)
- [Team Structure](#team-structure)
- [Development Principles](#development-principles)
- [Data Privacy and Security](#data-privacy-and-security)
- [Project Roadmap](#project-roadmap)
- [Current Project Status](#current-project-status)
- [License](#license)

---

# Overview

Modern criminal investigations often involve large volumes of fragmented information collected from many different sources.

Relevant information may be distributed across:

- First Information Reports (FIRs)
- criminal histories
- intelligence reports
- call-detail records
- financial records
- surveillance information
- vehicle records
- organizational information
- social intelligence
- case and evidence records

These sources may contain incomplete, duplicated, inconsistent, or differently formatted representations of the same real-world entity.

The purpose of this system is to combine these heterogeneous sources and transform them into a unified investigative intelligence environment.

The platform combines:

```text
Data Engineering
        +
AI / NLP
        +
Entity Resolution
        +
Knowledge Graphs
        +
Graph Analytics
        +
Anomaly Detection
        +
Backend Services
        +
Security
        +
Investigator UI
```

The result is intended to help investigators move from isolated records toward connected intelligence.

---

# Problem Statement

## Smart India Hackathon — Problem Statement 26189

**AI-Powered Criminal Network Analysis System**

The project addresses the challenge of analyzing fragmented criminal intelligence and discovering connections between people, organizations, vehicles, locations, communications, financial activity, cases, and other investigative entities.

Traditional tabular systems are effective for storing individual records, but relationships across thousands of records can be difficult to discover manually.

This system aims to provide an intelligence-analysis layer that connects these records and makes relationships, networks, patterns, anomalies, and supporting evidence easier to investigate.

---

# Project Goal

Build an investigative intelligence platform that:

- integrates structured and unstructured crime-related data
- cleans and normalizes heterogeneous sources
- extracts entities using AI/NLP
- extracts relationships from unstructured information
- resolves references to the same real-world entity
- constructs a unified knowledge graph
- performs graph and network analysis
- detects potentially significant anomalies and patterns
- connects analytical results to supporting evidence
- provides explainable investigative intelligence
- exposes functionality through a backend API
- provides an interactive investigator dashboard
- incorporates authentication, authorization, and audit controls

---

# Why This System

A conventional database can answer questions such as:

```text
"Show records belonging to Person A."
```

An investigative graph can help answer questions such as:

```text
"Who is Person A connected to?"

"Which organization connects these two individuals?"

"Which people share communication or financial relationships?"

"What entities form the central part of this network?"

"What unusual patterns exist around this case?"

"What evidence supports this relationship?"
```

The objective is not simply to collect more data.

The objective is to make relationships across the data easier to understand.

---

# Core Pipeline

```text
Raw Data
   │
   ▼
Data Ingestion
   │
   ▼
Cleaning
   │
   ▼
Normalization
   │
   ▼
AI / NLP Extraction
   │
   ├── Entity Extraction
   ├── Relationship Extraction
   └── Information Extraction
   │
   ▼
Entity Resolution
   │
   ▼
Standardized Intelligence
   │
   ▼
Knowledge Graph Construction
   │
   ▼
Graph Analytics
   │
   ▼
Anomaly Detection
   │
   ▼
Explainable Intelligence
   │
   ▼
FastAPI Backend
   │
   ▼
Investigator Dashboard
```

---

# System Architecture

At a high level, the system is divided into several cooperating layers.

```text
┌─────────────────────────────────────────────┐
│              DATA SOURCES                   │
│                                             │
│ FIRs | CDR | Financial | Surveillance      │
│ Criminal History | Vehicles | Reports       │
│ Social Intelligence | Organizations        │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│           DATA ENGINEERING LAYER            │
│                                             │
│ Ingestion → Cleaning → Normalization       │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│               AI / NLP LAYER                │
│                                             │
│ Entity Extraction                           │
│ Relationship Extraction                     │
│ Entity Resolution                           │
│ Embeddings / Similarity                     │
│ Transformer Models                          │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│             INTELLIGENCE LAYER              │
│                                             │
│ Standardized Entities + Relationships       │
└───────────────┬─────────────────┬───────────┘
                │                 │
                ▼                 ▼
        ┌──────────────┐   ┌──────────────┐
        │ PostgreSQL   │   │    Neo4j     │
        │              │   │              │
        │ Structured   │   │ Graph Data   │
        │ Application  │   │ Relationships│
        │ Data         │   │ Networks     │
        └──────┬───────┘   └──────┬───────┘
               │                  │
               └────────┬─────────┘
                        ▼
┌─────────────────────────────────────────────┐
│               FASTAPI BACKEND               │
│                                             │
│ API Routing                                 │
│ Search                                      │
│ Cases                                       │
│ Evidence                                    │
│ Graph Operations                            │
│ Analytics                                   │
│ Alerts                                      │
│ Authentication                              │
│ Authorization                               │
│ Audit Logging                               │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│           INVESTIGATOR DASHBOARD            │
│                                             │
│ Search | Graph | Cases | Evidence          │
│ Timelines | Alerts | Analytics              │
└─────────────────────────────────────────────┘
```

---

# Core Capabilities

## Data Integration

The platform is designed to process information from multiple intelligence domains.

Examples include:

- FIRs
- criminal histories
- CDR information
- financial records
- surveillance records
- vehicle records
- organizations
- intelligence reports
- social intelligence

Each source may have its own schema and terminology.

The data engineering layer is responsible for making these sources usable by the downstream AI and graph systems.

---

## Entity Extraction

AI/NLP components identify meaningful entities from unstructured sources.

Possible entities include:

- Person
- Organization
- Vehicle
- Phone
- Account
- Location
- Case
- Evidence
- Event
- Address

Example:

```text
"Rahul met Sameer in Delhi using vehicle DL01AB1234."

                  │
                  ▼

Person: Rahul
Person: Sameer
Location: Delhi
Vehicle: DL01AB1234
```

---

## Relationship Extraction

Relationships between extracted entities can be inferred from textual or structured sources.

Example:

```text
Rahul
  │
  ├── MET ──────────► Sameer
  │
  └── USED ─────────► Vehicle
                           │
                           └── LOCATED_IN ───► Delhi
```

The final relationship vocabulary will be defined by the graph schema and data contracts.

---

## Entity Resolution

Different records may refer to the same real-world entity.

For example:

```text
Record A:
Raj Kumar

Record B:
R. Kumar

Record C:
Raj K.

Record D:
Raj Kumar, Delhi
```

Entity resolution attempts to determine whether these records represent the same entity.

Potential techniques include:

- deterministic matching
- identifier matching
- fuzzy matching
- semantic similarity
- embeddings
- contextual comparison
- confidence scoring

The result is a standardized entity representation.

---

# Investigative Intelligence Graph

Neo4j is used to represent relationships between entities.

Example graph:

```text
                    ┌──────────────┐
                    │ Organization │
                    └──────┬───────┘
                           │ MEMBER_OF
                           │
                    ┌──────▼───────┐
                    │    Person    │
                    └───┬────┬─────┘
                        │    │
               KNOWS    │    │ OWNS
                        │    │
              ┌─────────▼┐   ▼
              │  Person  │ Vehicle
              └────┬─────┘
                   │
              INVOLVED_IN
                   │
                   ▼
                Case
```

The graph is intended to preserve relationships rather than reducing every piece of intelligence to isolated rows.

---

# Graph Analytics

The graph-analysis layer is designed to support investigation-oriented questions such as:

- shortest paths
- relationship traversal
- connected components
- centrality analysis
- community detection
- network clustering
- high-connectivity entities
- relationship pattern detection

Potential analytical metrics include:

- degree centrality
- betweenness centrality
- closeness centrality
- connected components
- community / cluster identification

The exact algorithms used will depend on the investigation workflow and graph scale.

---

# Anomaly Detection

The system is intended to identify potentially significant patterns that may deserve investigator attention.

Examples could include:

- unusually dense relationships
- unexpected network connections
- sudden changes in relationship patterns
- unusual communication structures
- anomalous transaction relationships
- entities behaving differently from normal network patterns

Anomaly detection is intended to be an investigative aid.

It should not be treated as an automatic determination of criminality.

---

# Explainable Intelligence

Analytical results should be accompanied by understandable supporting context.

Instead of returning only:

```text
"High-risk entity"
```

the system should aim to provide:

```text
Entity
   │
   ├── connected to Person A
   ├── connected to Organization B
   ├── associated with Vehicle C
   ├── involved in Case D
   └── relationship supported by Evidence E
```

This helps investigators understand:

- why a result appeared
- what relationships produced it
- which records support the result
- how the entities are connected
- what confidence or supporting context is available

---

# Investigator Dashboard

The frontend is intended to provide an investigator-focused interface.

Planned functionality includes:

## Search

Search across entities, cases, relationships, evidence, and intelligence records.

## Graph Exploration

Interactively explore:

- people
- organizations
- vehicles
- locations
- cases
- relationships
- network clusters

## Case Investigation

View information associated with a specific investigation.

## Timeline Exploration

Understand how events and relationships evolve over time.

## Alerts

Surface potentially significant analytical findings.

## Analytics

Present graph statistics and investigation-oriented metrics.

## Evidence

Connect analytical relationships with underlying supporting records.

---

# Technology Stack

## Frontend

- React
- Vite
- TypeScript
- Tailwind CSS
- shadcn/ui
- Cytoscape.js
- Recharts
- Axios

### Frontend responsibilities

The frontend provides the investigator-facing experience, including:

- dashboards
- search
- graph visualization
- filtering
- timelines
- case interfaces
- alerts
- analytics

---

## Backend

- Python
- FastAPI
- Pydantic
- Pydantic Settings
- SQLAlchemy
- PostgreSQL

### Backend responsibilities

- API routing
- request validation
- database access
- graph integration
- application services
- search
- case management
- evidence handling
- analytics
- alerts
- authentication
- authorization

---

## AI / NLP

- spaCy
- Hugging Face Transformers
- Sentence Transformers
- PyTorch
- scikit-learn

### AI responsibilities

- entity extraction
- relationship extraction
- entity resolution
- semantic similarity
- embeddings
- NLP inference
- model experimentation

GPU-intensive workloads are primarily expected to occur in this layer.

---

## Graph

- Neo4j
- Cypher
- Neo4j Graph Data Science
- NetworkX

### Graph responsibilities

- graph schema
- relationship representation
- graph querying
- network analysis
- graph analytics
- path analysis
- clustering

---

## DevOps

- Docker
- Docker Compose
- GitHub Actions

### Development infrastructure

Docker Compose provides reproducible local infrastructure for:

- PostgreSQL
- Neo4j

Application code remains synchronized through GitHub rather than through Docker or Portainer.

---

# Repository Structure

```text
AI-Criminal-Network-Analysis/
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── pull_request_template.md
│   └── workflows/
│
├── ai/
│   ├── entity_resolution/
│   ├── models/
│   ├── nlp/
│   ├── pipelines/
│   ├── relationship_extraction/
│   ├── tests/
│   └── README.md
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── README.md
│   └── requirements.txt
│
├── data/
│   ├── cdr/
│   ├── criminal_history/
│   ├── financial/
│   ├── fir/
│   ├── intelligence_reports/
│   ├── organizations/
│   ├── social/
│   ├── surveillance/
│   └── vehicles/
│
├── docs/
│   ├── api/
│   ├── architecture/
│   ├── data-contracts/
│   └── decisions/
│
├── frontend/
│
├── graph/
│   ├── analytics/
│   ├── loaders/
│   ├── queries/
│   ├── schema/
│   ├── tests/
│   └── README.md
│
├── scripts/
│   ├── ingestion/
│   ├── seed/
│   └── utilities/
│
├── tests/
│   ├── fixtures/
│   └── integration/
│
├── .env.example
├── .gitignore
└── README.md
```

---

# Data Architecture

The system uses two complementary databases.

## PostgreSQL

PostgreSQL stores structured application-level data.

Potential examples:

- users
- cases
- evidence metadata
- audit logs
- structured application records

Development version:

```text
PostgreSQL 18.6
```

---

## Neo4j

Neo4j stores graph-native intelligence.

Potential graph data includes:

- entities
- relationships
- investigation networks
- paths
- graph patterns

Development version:

```text
Neo4j 2026.07.1
```

---

## Why PostgreSQL + Neo4j?

The two systems serve different purposes.

```text
PostgreSQL
    │
    ├── Structured application data
    ├── Users
    ├── Cases
    ├── Evidence metadata
    └── Audit data


Neo4j
    │
    ├── Entities
    ├── Relationships
    ├── Networks
    ├── Paths
    └── Graph analytics
```

This separation allows relational workloads and graph workloads to be handled independently.

---

# Backend Architecture

The backend follows a layered FastAPI structure.

```text
API Routes
    │
    ▼
Services
    │
    ├───────────────┐
    ▼               ▼
PostgreSQL       Neo4j
    │               │
    └───────┬───────┘
            ▼
       Application
        Response
```

Current API domains include:

- health
- entities
- relationships
- graph
- search
- alerts
- cases
- timelines
- evidence
- analytics

Security functionality will be integrated into this existing backend rather than implemented as a separate backend.

---

# Security Architecture

Security is being developed as a dedicated cross-cutting concern.

Planned capabilities include:

- password hashing
- authentication
- JWT authentication
- JWT verification
- current-user dependency
- role-based access control
- API authorization
- security middleware
- audit logging
- secret management
- security hardening
- security testing

Password hashing uses:

```text
pwdlib + Argon2
```

JWT functionality uses:

```text
PyJWT
```

Passwords must never be stored in plaintext.

Secrets must never be committed to Git.

The `.env` file is intentionally excluded from version control.

---

# Security Development Roadmap

Security is intentionally implemented incrementally:

```text
Password Hashing
        │
        ▼
User Security Fields
        │
        ▼
Authentication / Login
        │
        ▼
JWT Creation + Verification
        │
        ▼
Current User Dependency
        │
        ▼
RBAC
        │
        ▼
Protected Endpoints
        │
        ▼
Audit Logging
        │
        ▼
Security Hardening
        │
        ▼
Security Testing
```

---

# Development Environment

The current development environment is based around:

- Python 3.14
- Node.js
- npm
- Git
- Docker
- Docker Compose
- PostgreSQL
- Neo4j

Additional developer tooling includes:

- VS Code / Antigravity
- DBeaver
- Portainer
- Ruff
- pytest
- ESLint
- Prettier
- SonarQube for IDE

---

# Local Setup

## 1. Clone the repository

```bash
git clone git@github.com:Nexus-Intelligence-Labs/AI-Criminal-Network-Analysis.git

cd AI-Criminal-Network-Analysis
```

---

## 2. Configure environment variables

Create your local environment file:

```bash
cp .env.example .env
```

Update the values for your local setup.

Never commit `.env`.

---

## 3. Create the backend virtual environment

```bash
cd backend

python -m venv .venv
```

Activate it:

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

---

## 4. Install backend dependencies

```bash
python -m pip install -r requirements.txt
```

---

# Running the Database Infrastructure

From the project root:

```bash
docker compose up -d
```

Check the containers:

```bash
docker compose ps
```

The local development stack includes:

```text
PostgreSQL
Neo4j
```

Stop the services:

```bash
docker compose down
```

Avoid deleting database volumes unless intentionally resetting local database data.

---

# Running the Full Stack with Docker

To run the API, PostgreSQL, and Neo4j consistently on any computer with
Docker Desktop installed, copy `.env.example` to `.env`, set secure local
passwords, then run from the repository root:

```bash
docker compose up --build -d
```

The API is available at `http://localhost:8000` and its Swagger documentation
is available at `http://localhost:8000/docs`. Neo4j Browser is available at
`http://localhost:7474`.

For another device on the same network, use the Docker host's LAN IP instead
of `localhost` (for example, `http://192.168.1.20:8000/docs`) and allow port
8000 through that host's firewall. A publicly accessible URL requires deploying
this Compose stack to a server or cloud platform; do not expose the database
ports publicly.

---

# PostgreSQL Development Access

PostgreSQL is exposed locally on:

```text
localhost:5432
```

DBeaver can be used as the primary graphical PostgreSQL development tool.

---

# Neo4j Development Access

Neo4j Browser:

```text
http://localhost:7474
```

Bolt:

```text
bolt://localhost:7687
```

Neo4j Browser can be used to inspect the graph and execute Cypher queries.

---

# Running the Backend

From:

```text
backend/
```

with the virtual environment activated:

```bash
uvicorn app.main:app --reload
```

The backend runs on the configured application port.

FastAPI's interactive API documentation can be used to inspect the available routes during development.

---

# Testing

Backend tests use pytest.

Run the complete backend test suite:

```bash
pytest
```

Run a specific test:

```bash
pytest tests/test_health.py
```

Tests should be added alongside new functionality.

Security features should include both successful and failure-path tests.

---

# Code Quality

Python code uses Ruff for linting and formatting.

Check Python code:

```bash
ruff check backend
```

Format Python code:

```bash
ruff format backend
```

Frontend code uses ESLint and Prettier.

The project aims to keep changes focused and reviewable rather than introducing large unrelated formatting changes.

---

# Git and Contribution Workflow

`main` is protected.

Direct pushes to `main` are not part of the development workflow.

Expected workflow:

```text
Latest main
    │
    ▼
Feature branch
    │
    ▼
Implementation
    │
    ▼
Testing
    │
    ▼
Review diff
    │
    ▼
Commit
    │
    ▼
Push branch
    │
    ▼
Pull Request
    │
    ▼
Teammate approval
    │
    ▼
Resolve conversations
    │
    ▼
Squash merge
```

Example:

```bash
git switch main
git pull origin main

git switch -c feature/my-feature
```

Review changes:

```bash
git status
git diff
```

Stage only intended files:

```bash
git add path/to/file
```

Commit:

```bash
git commit -m "feat: describe change"
```

Push:

```bash
git push -u origin feature/my-feature
```

Never use:

```bash
git add .
```

blindly in a project containing secrets or generated files.

---

# Team Structure

The project is divided into three working groups.

## Group 1 — Data + AI

### Person 5 — Data Engineering

Responsibilities:

- data ingestion
- cleaning
- normalization
- dataset preparation
- raw source processing
- standardized intelligence preparation

### Person 3 — AI / NLP

Responsibilities:

- entity extraction
- relationship extraction
- entity resolution
- NLP pipelines
- embeddings
- transformer models
- inference
- model experimentation

---

## Group 2 — Graph + Backend

### Person 4 — Graph / Network Analytics

Responsibilities:

- Neo4j
- graph schema
- nodes and relationships
- Cypher
- graph analytics
- network analysis
- centrality
- clustering
- path analysis

### Person 2 — Backend + DevOps / Integration

Responsibilities:

- FastAPI
- backend APIs
- service layer
- PostgreSQL
- Neo4j integration
- Docker
- DevOps
- deployment
- system integration

---

## Group 3 — Frontend + Security

### Person 1 — Frontend / UI-UX

Responsibilities:

- React
- UI/UX
- investigator dashboard
- search
- filtering
- graph visualization
- timelines
- investigation workflows

### Person 6 — Security + Backend Support

Responsibilities:

- authentication
- password hashing
- JWT
- RBAC
- API security
- security middleware
- secrets management
- audit logging
- security hardening
- security testing
- backend security integration

---

# Development Principles

## Modular ownership

Each group owns a technical domain while integration happens through shared contracts.

## Incremental development

Features should be implemented in small, testable stages.

## Reproducibility

Docker Compose and pinned infrastructure versions help developers reproduce the same local database environment.

## Security by design

Security should be incorporated during development instead of being treated as a final deployment step.

## Explainability

Analytical findings should be connected to understandable relationships, evidence, and supporting context.

## Minimal destructive changes

Existing functionality should not be rewritten unless there is a concrete reason.

---

# Data Privacy and Security

This project is intended for intelligence-analysis scenarios.

Do not commit real sensitive law-enforcement information to the repository.

Development data should be:

- synthetic
- anonymized
- appropriately licensed
- publicly usable
- or otherwise authorized for development purposes

Never commit:

- `.env`
- database passwords
- JWT secrets
- API keys
- cloud credentials
- private keys
- production data

Because the repository is public, every committed file should be treated as publicly accessible.

---

# Project Roadmap

```text
Phase 1
Repository + Infrastructure
        │
        ▼
Phase 2
Backend + Database Foundations
        │
        ▼
Phase 3
Data Engineering
        │
        ▼
Phase 4
AI / NLP
        │
        ▼
Phase 5
Knowledge Graph
        │
        ▼
Phase 6
Graph Analytics + Anomaly Detection
        │
        ▼
Phase 7
Security + Authentication
        │
        ▼
Phase 8
Investigator Dashboard
        │
        ▼
Phase 9
System Integration
        │
        ▼
Phase 10
Testing + Hardening
        │
        ▼
Phase 11
Demonstration / Deployment
```

---

# Current Project Status

> This section should be updated as features are completed.

## Infrastructure

- [x] GitHub organization
- [x] Repository structure
- [x] Team structure
- [x] Protected `main`
- [x] Pull request workflow
- [x] Docker environment
- [x] PostgreSQL development environment
- [x] Neo4j development environment
- [x] Environment variable template

## Backend

- [x] FastAPI foundation
- [x] PostgreSQL integration foundation
- [x] Neo4j integration foundation
- [x] API route structure
- [x] Initial database models
- [x] Initial schemas
- [x] Initial service layer

## Security

- [x] Security dependency foundation
- [ ] Password hashing integration
- [ ] User authentication
- [ ] JWT authentication
- [ ] Current-user dependency
- [ ] RBAC
- [ ] Protected API endpoints
- [ ] Audit logging integration
- [ ] Security hardening
- [ ] Security test suite

## AI / NLP

- [ ] Data ingestion pipeline
- [ ] Entity extraction
- [ ] Relationship extraction
- [ ] Entity resolution
- [ ] Embedding pipeline
- [ ] Production model integration

## Graph

- [ ] Final graph ontology
- [ ] Graph loaders
- [ ] Production graph construction
- [ ] Graph analytics
- [ ] Advanced investigation queries
- [ ] Anomaly detection

## Frontend

- [ ] Investigator dashboard
- [ ] Authentication UI
- [ ] Entity search
- [ ] Graph visualization
- [ ] Case workflows
- [ ] Timeline views
- [ ] Alert interface

---

# Documentation

Additional technical documentation is organized under:

```text
docs/
├── api/
├── architecture/
├── data-contracts/
└── decisions/
```

Component-specific documentation is available in:

```text
ai/README.md
backend/README.md
graph/README.md
```

---

# License

A project license has not yet been selected.

---

# Project Status

**Active Development**

This repository represents an actively evolving Smart India Hackathon project.

The architecture, graph ontology, AI pipelines, APIs, security controls, and investigator interface are being developed incrementally.

---
