import os

import pytest

from app.db.neo4j import get_neo4j_driver
from app.schemas.ingestion import IngestionRequest
from app.services.graph_service import GraphService
from app.services.ingestion_service import _canonical_graph, _write_graph


pytestmark = pytest.mark.skipif(
    not os.getenv("NEO4J_PASSWORD"),
    reason="Set NEO4J_PASSWORD to run the real Neo4j ingestion integration test.",
)


def test_ingestion_writes_and_reads_real_neo4j_graph():
    case_id = "TEST-E2E-NEO4J"
    request = IngestionRequest(
        filename="synthetic-cdr.csv",
        content="caller,receiver,timestamp,duration\n9876543210,9123456789,2026-01-01,30\n",
        case_id=case_id,
        source_type="cdr",
    )
    graph = _canonical_graph(
        [{"caller": "9876543210", "receiver": "9123456789", "timestamp": "2026-01-01", "duration": "30"}],
        request,
        "TEST-E2E-JOB",
    )

    try:
        assert _write_graph(graph) == (2, 1)
        result = GraphService().get_case_graph(case_id)
        assert len(result["nodes"]) == 2
        assert len(result["edges"]) == 1
        assert result["edges"][0]["type"] == "CALLED"
    finally:
        with get_neo4j_driver().session() as session:
            session.run(
                "MATCH (node:Entity {case_id: $case_id}) DETACH DELETE node",
                case_id=case_id,
            ).consume()
