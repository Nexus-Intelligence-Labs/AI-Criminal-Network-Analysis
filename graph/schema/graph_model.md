# SIH AI Criminal Network Analysis
## Neo4j Graph Model

## Overview

The graph database stores criminal investigation entities and the relationships between them.

PostgreSQL is the Source of Truth.

Neo4j is used for:

- Graph traversal
- Link analysis
- Community detection
- Centrality analysis
- Suspicious pattern detection
- Visualization

---

# Node Labels

Every node has the base label:

:Entity

Additional labels:

- Person
- Organization
- Phone
- BankAccount
- Vehicle
- Device
- Email
- Address
- SocialAccount
- Document
- Evidence
- Location

Example:

(:Entity:Person)

---

# Entity Properties

| Property | Type | Required |
|----------|------|----------|
| entity_id | String | Yes |
| case_id | String | Yes |
| entity_type | String | Yes |
| name | String | Yes |
| source | String | Yes |
| source_record | String | Optional |
| confidence | Float | Yes |
| created_at | DateTime | Yes |
| updated_at | DateTime | Yes |

---

# Relationship Types

- CALLED
- MESSAGED
- EMAILED
- TRANSFERRED_TO
- ASSOCIATED_WITH
- OWNS
- USES
- LOCATED_AT
- VISITED
- EMPLOYED_BY
- MEMBER_OF
- RELATED_TO
- REGISTERED_TO
- LINKED_TO
- COMMUNICATED_WITH

---

# Relationship Properties

| Property | Type |
|----------|------|
| relationship_id | String |
| case_id | String |
| source_record | String |
| confidence | Float |
| weight | Float |
| timestamp | DateTime |
| created_at | DateTime |

---

# Analytics Properties

These are computed later by the analytics service.

- risk_score
- suspicion_score
- pagerank
- betweenness
- degree
- community_id

---

# Architecture

Raw Data / AI

↓

FastAPI

↓

PostgreSQL

↓

Graph Loader

↓

Neo4j

↓

Analytics + Visualization