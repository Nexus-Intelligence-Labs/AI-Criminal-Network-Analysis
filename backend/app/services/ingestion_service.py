"""Safe, auditable ingestion of small structured source records.

The repository does not yet have a migration system or a stable AI service
boundary in the backend.  This service therefore persists the accepted source
records and provenance as immutable JSON job artifacts, while keeping parsing
and validation deterministic and ready for a future pipeline adapter.
"""

import csv
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.schemas.ingestion import (
    IngestionPreview,
    IngestionRequest,
    ValidationIssue,
)
from app.db.neo4j import get_neo4j_driver

AI_ROOT = Path(__file__).resolve().parents[3] / "ai"
if str(AI_ROOT) not in sys.path:
    sys.path.append(str(AI_ROOT))

SUPPORTED_EXTENSIONS = {".csv", ".json", ".txt"}
MAX_CONTENT_BYTES = 5 * 1024 * 1024
ARTIFACT_ROOT = Path(__file__).resolve().parents[3] / "data" / "ingestion"


def _parse(request: IngestionRequest) -> tuple[list[str], list[dict[str, object]], list[ValidationIssue]]:
    suffix = Path(request.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        return [], [], [ValidationIssue(message="Unsupported file type; use CSV, JSON, or TXT.")]

    if len(request.content.encode("utf-8")) > MAX_CONTENT_BYTES:
        return [], [], [ValidationIssue(message="Source file exceeds the 5 MiB limit.")]

    if suffix == ".csv":
        reader = csv.DictReader(io.StringIO(request.content))
        columns = reader.fieldnames or []
        rows = [dict(row) for row in reader]
    elif suffix == ".json":
        try:
            payload = json.loads(request.content)
        except json.JSONDecodeError:
            return [], [], [ValidationIssue(message="JSON source is malformed.")]
        if isinstance(payload, dict):
            rows = [payload]
        elif isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
            rows = payload
        else:
            return [], [], [ValidationIssue(message="JSON must contain an object or an array of objects.")]
        columns = sorted({key for row in rows for key in row})
    else:
        rows = [{"text": line} for line in request.content.splitlines() if line.strip()]
        columns = ["text"]

    issues: list[ValidationIssue] = []
    if not rows:
        issues.append(ValidationIssue(message="Source contains no records."))
    for index, row in enumerate(rows, start=1):
        if not any(str(value).strip() for value in row.values() if value is not None):
            issues.append(ValidationIssue(row=index, message="Record is empty."))
    return columns, rows, issues


def preview(request: IngestionRequest) -> IngestionPreview:
    columns, rows, issues = _parse(request)
    return IngestionPreview(
        filename=request.filename,
        case_id=request.case_id,
        source_type=request.source_type,
        columns=columns,
        rows=rows[:100],
        issues=issues,
        provenance={
            "source_filename": request.filename,
            "source_type": request.source_type,
            "case_id": request.case_id,
            "record_count": len(rows),
            "previewed_at": datetime.now(timezone.utc).isoformat(),
        },
    )


def _canonical_graph(rows: list[dict[str, object]], request: IngestionRequest, job_id: str) -> dict[str, list[dict[str, object]]]:
    """Map supported source rows to the existing Entity/RELATED ontology."""
    entities: dict[str, dict[str, object]] = {}
    relationships: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        source_record = str(row.get("source_record") or f"{request.filename}:row-{index}")
        if request.source_type.lower() == "cdr" and row.get("caller") and row.get("receiver"):
            from pipelines.cdr_processor import CDRProcessor

            record = CDRProcessor().process({**row, "source_record": source_record})
            caller_id = f"PHONE_{record.caller}"
            receiver_id = f"PHONE_{record.receiver}"
            graph = {
                "entities": [
                    {"entity_id": caller_id, "entity_type": "PHONE", "name": record.caller, "source": source_record, "confidence": 1.0},
                    {"entity_id": receiver_id, "entity_type": "PHONE", "name": record.receiver, "source": source_record, "confidence": 1.0},
                ],
                "relationships": [{
                    "relationship_id": f"REL_{source_record}_1",
                    "source_entity_id": caller_id,
                    "target_entity_id": receiver_id,
                    "relationship": "CALLED",
                    "timestamp": record.timestamp,
                    "source_record": source_record,
                    "confidence": 1.0,
                }],
            }
        elif request.source_type.lower() == "financial" and row.get("sender") and row.get("receiver"):
            from pipelines.financial_processor import FinancialProcessor

            record = FinancialProcessor().process({**row, "source_record": source_record})
            sender_id = f"PARTY_{record.sender}"
            receiver_id = f"PARTY_{record.receiver}"
            graph = {
                "entities": [
                    {"entity_id": sender_id, "entity_type": "PERSON", "name": record.sender, "source": source_record, "confidence": 1.0},
                    {"entity_id": receiver_id, "entity_type": "PERSON", "name": record.receiver, "source": source_record, "confidence": 1.0},
                ],
                "relationships": [{
                    "relationship_id": f"REL_{source_record}_1",
                    "source_entity_id": sender_id,
                    "target_entity_id": receiver_id,
                    "relationship": "TRANSFERRED_TO",
                    "timestamp": record.timestamp,
                    "source_record": source_record,
                    "confidence": 1.0,
                }],
            }
        else:
            # Explicit deterministic fallback for generic rows when heavyweight
            # model dependencies are not configured in the backend environment.
            text = str(row.get("text") or row.get("name") or "").strip()
            ai_entities: list[dict[str, object]] = []
            if request.source_type.lower() == "fir" and text:
                try:
                    from nlp.pipeline import NLPPipeline

                    ai_entities = NLPPipeline().process(text, source_record)["entities"]
                except (ImportError, OSError, RuntimeError):
                    ai_entities = []
            names = [value for value in re.split(r"\s+(?:communicated with|contacted|met)\s+", text, maxsplit=1) if value]
            if len(names) < 2:
                names = [str(row[key]).strip() for key in ("source", "target") if row.get(key)]
            if not names:
                continue
            graph = {
                "entities": [
                    {"entity_id": str(entity.get("entity_id") or f"IMPORT_{job_id}_{index}_{position}"), "entity_type": str(entity.get("entity_type") or "PERSON"), "name": str(entity.get("name") or name), "source": source_record, "confidence": float(entity.get("confidence") or 0.5)}
                    for position, (name, entity) in enumerate(zip(names, ai_entities or [{} for _ in names]), start=1)
                ],
                "relationships": [],
                "events": [],
            }
            if len(names) >= 2:
                graph["relationships"].append({
                    "relationship_id": f"REL_{job_id}_{index}",
                    "source_entity_id": graph["entities"][0]["entity_id"],
                    "target_entity_id": graph["entities"][1]["entity_id"],
                    "relationship": str(row.get("relationship") or "RELATED"),
                    "timestamp": str(row.get("timestamp") or ""),
                    "source_record": source_record,
                    "confidence": 0.5,
                })
        for entity in graph["entities"]:
            entity = dict(entity)
            entity.update({"case_id": request.case_id, "job_id": job_id, "source_record": source_record})
            entities[str(entity["entity_id"])] = entity
        for relationship in graph["relationships"]:
            relationship = dict(relationship)
            relationship.update({"case_id": request.case_id, "job_id": job_id})
            relationships.append(relationship)
    return {"entities": list(entities.values()), "relationships": relationships}


def _write_graph(graph: dict[str, list[dict[str, object]]]) -> tuple[int, int]:
    driver = get_neo4j_driver()
    with driver.session() as session:
        entity_result = session.run(
            """
            UNWIND $entities AS entity
            MERGE (node:Entity {entity_id: entity.entity_id})
            SET node.entity_type = entity.entity_type,
                node.name = entity.name,
                node.case_id = entity.case_id,
                node.job_id = entity.job_id,
                node.source = entity.source,
                node.source_record = entity.source_record,
                node.confidence = entity.confidence,
                node.updated_at = datetime()
            RETURN count(node) AS count
            """,
            entities=graph["entities"],
        ).single()
        relationship_result = session.run(
            """
            UNWIND $relationships AS relationship
            MATCH (source:Entity {entity_id: relationship.source_entity_id})
            MATCH (target:Entity {entity_id: relationship.target_entity_id})
            MERGE (source)-[edge:RELATED {relationship_id: relationship.relationship_id}]->(target)
            SET edge.relationship = relationship.relationship,
                edge.case_id = relationship.case_id,
                edge.job_id = relationship.job_id,
                edge.source_record = relationship.source_record,
                edge.timestamp = relationship.timestamp,
                edge.confidence = relationship.confidence
            RETURN count(edge) AS count
            """,
            relationships=graph["relationships"],
        ).single()
    return int(entity_result["count"]), int(relationship_result["count"])


def import_records(request: IngestionRequest) -> tuple[str, IngestionPreview, str, dict[str, int]]:
    result = preview(request)
    _, rows, issues = _parse(request)
    job_id = str(uuid4())
    status = "completed" if not issues else "rejected"
    artifact_dir = ARTIFACT_ROOT / job_id
    artifact_dir.mkdir(parents=True, exist_ok=False)
    artifact_path = artifact_dir / "records.json"
    graph = _canonical_graph(rows, request, job_id)
    entities_written, relationships_written = _write_graph(graph)
    artifact_path.write_text(
        json.dumps(
            {
                "job_id": job_id,
                "status": status,
                "request": request.model_dump(),
                "records_received": len(rows),
                "records_parsed": len(rows),
                "records_rejected": len(issues),
                "rows": rows,
                "graph": {
                    "entities_extracted": len(graph["entities"]),
                    "relationships_extracted": len(graph["relationships"]),
                    "entities_written": entities_written,
                    "relationships_written": relationships_written,
                },
                "provenance": result.provenance,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return job_id, result, str(artifact_path.relative_to(ARTIFACT_ROOT.parent)), {
        "entities_written": entities_written,
        "relationships_written": relationships_written,
    }


def get_job(job_id: str) -> dict[str, object] | None:
    artifact_path = ARTIFACT_ROOT / job_id / "records.json"
    if not artifact_path.is_file():
        return None
    return json.loads(artifact_path.read_text(encoding="utf-8"))
