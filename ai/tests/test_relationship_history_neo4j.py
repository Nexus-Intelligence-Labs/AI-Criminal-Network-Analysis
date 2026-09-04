import os

import pytest

from graph.graph_adapter import GraphAdapter
from graph.neo4j_writer import Neo4jGraphWriter

from pipelines.cdr_processor import CDRProcessor


def create_writer():
    """Create Neo4j writer from environment variables."""

    uri = os.getenv(
        "NEO4J_URI",
        "bolt://localhost:7687",
    )

    username = os.getenv(
        "NEO4J_USERNAME",
        "neo4j",
    )

    password = os.getenv(
        "NEO4J_PASSWORD",
        "",
    )

    if not password:
        pytest.fail(
            "NEO4J_PASSWORD is not set."
        )

    return Neo4jGraphWriter(
        uri=uri,
        username=username,
        password=password,
    )


def delete_test_data(
    writer,
):
    """Delete only data created by this test."""

    writer.connect()

    query = """
    MATCH (n)
    WHERE n.source IN [
        "HISTORY_CDR_001",
        "HISTORY_CDR_002"
    ]
       OR n.source_record IN [
        "HISTORY_CDR_001",
        "HISTORY_CDR_002"
    ]
       OR n.entity_id IN [
        "PHONE_+919876543210",
        "PHONE_+919988776655",
        "PHONE_9876543210",
        "PHONE_9988776655"
    ]
    DETACH DELETE n
    """

    with writer.driver.session() as session:
        session.run(query)


def query_history(
    writer,
):
    """
    Return all CALLED relationships between the two
    normalized test phone entities.
    """

    query = """
    MATCH (
        source:Entity {
            entity_id: "PHONE_+919876543210"
        }
    )-[r:RELATED {
        relationship: "CALLED"
    }]->(
        target:Entity {
            entity_id: "PHONE_+919988776655"
        }
    )

    RETURN
        r.relationship_id AS relationship_id,
        r.relationship AS relationship,
        r.timestamp AS timestamp,
        r.source_record AS source_record,
        r.duration AS duration

    ORDER BY r.timestamp
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(query)

        return [
            {
                "relationship_id": record[
                    "relationship_id"
                ],
                "relationship": record[
                    "relationship"
                ],
                "timestamp": record[
                    "timestamp"
                ],
                "source_record": record[
                    "source_record"
                ],
                "duration": record[
                    "duration"
                ],
            }
            for record in result
        ]


def count_relationships(
    writer,
):
    """Count all test relationships."""

    query = """
    MATCH (
        source:Entity
    )-[r:RELATED {
        relationship: "CALLED"
    }]->(
        target:Entity
    )

    WHERE r.source_record IN [
        "HISTORY_CDR_001",
        "HISTORY_CDR_002"
    ]

    RETURN count(r) AS count
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(query)

        return result.single()["count"]


def test_neo4j_preserves_relationship_history():
    """
    Verify that two separate CDR records between the same
    caller and receiver become two separate relationships.
    """

    writer = create_writer()

    try:
        # --------------------------------------------------
        # 1. Clean previous test data
        # --------------------------------------------------

        delete_test_data(
            writer
        )

        # --------------------------------------------------
        # 2. Create the REAL CDR processor
        # --------------------------------------------------

        cdr_processor = CDRProcessor()

        adapter = GraphAdapter()

        # --------------------------------------------------
        # 3. Process first CDR through the real pipeline
        # --------------------------------------------------

        first_record = cdr_processor.process(
            {
                "caller": "9876543210",
                "receiver": "9988776655",
                "timestamp": (
                    "2026-09-05T10:00:00"
                ),
                "duration": 120,
                "source_record": (
                    "HISTORY_CDR_001"
                ),
            }
        )

        # --------------------------------------------------
        # 4. Verify first record normalization
        # --------------------------------------------------

        assert first_record.caller == (
            "+919876543210"
        )

        assert first_record.receiver == (
            "+919988776655"
        )

        # --------------------------------------------------
        # 5. Convert first record to graph data
        # --------------------------------------------------

        first_graph = adapter.adapt_cdr(
            first_record
        )

        # --------------------------------------------------
        # 6. Process second CDR through the real pipeline
        # --------------------------------------------------

        second_record = cdr_processor.process(
            {
                "caller": "9876543210",
                "receiver": "9988776655",
                "timestamp": (
                    "2026-09-05T14:30:00"
                ),
                "duration": 300,
                "source_record": (
                    "HISTORY_CDR_002"
                ),
            }
        )

        # --------------------------------------------------
        # 7. Verify second record normalization
        # --------------------------------------------------

        assert second_record.caller == (
            "+919876543210"
        )

        assert second_record.receiver == (
            "+919988776655"
        )

        # --------------------------------------------------
        # 8. Convert second record to graph data
        # --------------------------------------------------

        second_graph = adapter.adapt_cdr(
            second_record
        )

        # --------------------------------------------------
        # 9. Verify different relationship IDs
        # --------------------------------------------------

        first_relationship = (
            first_graph[
                "relationships"
            ][0]
        )

        second_relationship = (
            second_graph[
                "relationships"
            ][0]
        )

        assert (
            first_relationship[
                "relationship_id"
            ]
            == "REL_HISTORY_CDR_001_1"
        )

        assert (
            second_relationship[
                "relationship_id"
            ]
            == "REL_HISTORY_CDR_002_1"
        )

        assert (
            first_relationship[
                "relationship_id"
            ]
            != second_relationship[
                "relationship_id"
            ]
        )

        # --------------------------------------------------
        # 10. Verify both records point to the same
        #     canonical phone IDs
        # --------------------------------------------------

        assert (
            first_relationship[
                "source_entity_id"
            ]
            == "PHONE_+919876543210"
        )

        assert (
            first_relationship[
                "target_entity_id"
            ]
            == "PHONE_+919988776655"
        )

        assert (
            second_relationship[
                "source_entity_id"
            ]
            == "PHONE_+919876543210"
        )

        assert (
            second_relationship[
                "target_entity_id"
            ]
            == "PHONE_+919988776655"
        )

        # --------------------------------------------------
        # 11. Write first record
        # --------------------------------------------------

        first_result = (
            writer.write_extraction(
                first_graph["entities"],
                first_graph[
                    "relationships"
                ],
                first_graph["events"],
            )
        )

        assert (
            first_result[
                "entities_created"
            ] == 2
        )

        assert (
            first_result[
                "relationships_created"
            ] == 1
        )

        # --------------------------------------------------
        # 12. Write second record
        # --------------------------------------------------

        second_result = (
            writer.write_extraction(
                second_graph["entities"],
                second_graph[
                    "relationships"
                ],
                second_graph["events"],
            )
        )

        assert (
            second_result[
                "entities_created"
            ] == 2
        )

        assert (
            second_result[
                "relationships_created"
            ] == 1
        )

        # --------------------------------------------------
        # 13. Verify TWO relationships exist
        # --------------------------------------------------

        assert (
            count_relationships(
                writer
            )
            == 2
        )

        history = query_history(
            writer
        )

        assert len(history) == 2

        # --------------------------------------------------
        # 14. Verify first historical record
        # --------------------------------------------------

        assert (
            history[0][
                "relationship_id"
            ]
            == "REL_HISTORY_CDR_001_1"
        )

        assert (
            history[0][
                "relationship"
            ]
            == "CALLED"
        )

        assert (
            history[0][
                "source_record"
            ]
            == "HISTORY_CDR_001"
        )

        assert (
            history[0][
                "timestamp"
            ]
            == "2026-09-05T10:00:00"
        )

        assert (
            history[0][
                "duration"
            ]
            == 120
        )

        # --------------------------------------------------
        # 15. Verify second historical record
        # --------------------------------------------------

        assert (
            history[1][
                "relationship_id"
            ]
            == "REL_HISTORY_CDR_002_1"
        )

        assert (
            history[1][
                "relationship"
            ]
            == "CALLED"
        )

        assert (
            history[1][
                "source_record"
            ]
            == "HISTORY_CDR_002"
        )

        assert (
            history[1][
                "timestamp"
            ]
            == "2026-09-05T14:30:00"
        )

        assert (
            history[1][
                "duration"
            ]
            == 300
        )

        # --------------------------------------------------
        # 16. Re-ingest first record
        # --------------------------------------------------
        #
        # The relationship ID is identical, so Neo4j
        # should update the existing record instead of
        # creating a duplicate.
        # --------------------------------------------------

        repeat_result = (
            writer.write_extraction(
                first_graph["entities"],
                first_graph[
                    "relationships"
                ],
                first_graph["events"],
            )
        )

        assert (
            repeat_result[
                "relationships_created"
            ] == 1
        )

        # --------------------------------------------------
        # 17. Verify history still contains exactly
        #     TWO relationships
        # --------------------------------------------------

        assert (
            count_relationships(
                writer
            )
            == 2
        )

        repeated_history = query_history(
            writer
        )

        assert len(
            repeated_history
        ) == 2

        # --------------------------------------------------
        # 18. Verify both historical records survived
        # --------------------------------------------------

        relationship_ids = {
            item[
                "relationship_id"
            ]
            for item in repeated_history
        }

        assert (
            relationship_ids
            == {
                "REL_HISTORY_CDR_001_1",
                "REL_HISTORY_CDR_002_1",
            }
        )

    finally:
        # --------------------------------------------------
        # 19. Clean up test data
        # --------------------------------------------------

        delete_test_data(
            writer
        )

        writer.close()