import os

import pytest

from entity_resolution.resolver import EntityResolver
from entity_resolution.store import EntityStore

from graph.graph_adapter import GraphAdapter
from graph.neo4j_writer import Neo4jGraphWriter

from pipelines.cdr_processor import CDRProcessor


class CDRSimilarity:
    """
    Deterministic similarity engine for the CDR -> Neo4j
    integration test.

    Phone numbers are treated as strong identifiers.
    """

    def multi_field_similarity(
        self,
        entity1,
        entity2,
    ):
        phone1 = entity1.get("name", "")
        phone2 = entity2.get("name", "")

        normalized1 = self._normalize_phone(phone1)
        normalized2 = self._normalize_phone(phone2)

        if normalized1 == normalized2:
            return {
                "field_scores": {
                    "name": 1.0,
                },
                "combined_score": 1.0,
            }

        return {
            "field_scores": {
                "name": 0.10,
            },
            "combined_score": 0.10,
        }

    @staticmethod
    def _normalize_phone(phone):
        """Normalize Indian phone numbers."""

        value = "".join(
            character
            for character in str(phone)
            if character.isdigit()
        )

        if value.startswith("91") and len(value) == 12:
            value = value[2:]

        if value.startswith("0") and len(value) == 11:
            value = value[1:]

        return value


class CDRConfidenceScorer:
    """Confidence classifier for the CDR integration test."""

    def classify(self, score):
        if score >= 0.90:
            return "HIGH"

        if score >= 0.70:
            return "REVIEW"

        return "LOW"


def create_resolver():
    """Create a deterministic entity resolver."""

    return EntityResolver(
        similarity=CDRSimilarity(),
        confidence_scorer=CDRConfidenceScorer(),
    )


def create_writer():
    """Create a Neo4j writer using environment variables."""

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


def delete_cdr_data(
    writer,
    source_record,
):
    """
    Delete only the nodes created by this integration test.
    """

    writer.connect()

    query = """
    MATCH (n)
    WHERE n.source = $source_record
       OR n.source_record = $source_record
    DETACH DELETE n
    """

    with writer.driver.session() as session:
        session.run(
            query,
            source_record=source_record,
        )


def query_entity(
    writer,
    entity_id,
):
    """Return an entity by canonical ID."""

    query = """
    MATCH (
        e:Entity {
            entity_id: $entity_id
        }
    )

    RETURN
        e.entity_id AS entity_id,
        e.entity_type AS entity_type,
        e.name AS name,
        e.source AS source,
        e.confidence AS confidence
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(
            query,
            entity_id=entity_id,
        )

        return result.single()


def query_called_relationship(
    writer,
    source_id,
    target_id,
):
    """Return the CALLED relationship between two entities."""

    query = """
    MATCH (
        source:Entity {
            entity_id: $source_id
        }
    )-[r:RELATED {
        relationship: "CALLED"
    }]->(
        target:Entity {
            entity_id: $target_id
        }
    )

    RETURN
        source.entity_id AS source_id,
        target.entity_id AS target_id,
        r.relationship AS relationship,
        r.timestamp AS timestamp,
        r.source_record AS source_record,
        r.duration AS duration,
        r.confidence AS confidence
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(
            query,
            source_id=source_id,
            target_id=target_id,
        )

        return result.single()


def count_cdr_entities(
    writer,
    source_record,
):
    """Count CDR entities created for this source record."""

    query = """
    MATCH (e:Entity)
    WHERE e.source = $source_record

    RETURN count(e) AS count
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(
            query,
            source_record=source_record,
        )

        record = result.single()

        return record["count"]


def count_cdr_relationships(
    writer,
    source_record,
):
    """Count CDR relationships created for this source record."""

    query = """
    MATCH (
        source:Entity
    )-[r:RELATED]->(
        target:Entity
    )

    WHERE r.source_record = $source_record

    RETURN count(r) AS count
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(
            query,
            source_record=source_record,
        )

        record = result.single()

        return record["count"]


def test_real_cdr_to_neo4j_end_to_end():
    """
    Test the complete:

    CDR
    -> CDR Processor
    -> Entity Resolution
    -> Graph Adapter
    -> Neo4j

    flow using a real Neo4j database.
    """

    source_record = (
        "INTEGRATION_CDR_001"
    )

    writer = create_writer()

    try:
        # --------------------------------------------------
        # 1. Clean previous integration-test data
        # --------------------------------------------------

        delete_cdr_data(
            writer,
            source_record,
        )

        # --------------------------------------------------
        # 2. Create the CDR processor
        # --------------------------------------------------

        cdr_processor = CDRProcessor()

        # --------------------------------------------------
        # 3. Create the entity resolver
        # --------------------------------------------------

        resolver = create_resolver()

        entity_store = EntityStore()

        # --------------------------------------------------
        # 4. Create the graph adapter
        # --------------------------------------------------

        graph_adapter = GraphAdapter()

        # --------------------------------------------------
        # 5. Process a real CDR record
        # --------------------------------------------------

        cdr_input = {
            "caller": "9876543210",
            "receiver": "9988776655",
            "timestamp": (
                "2026-09-05T11:00:00"
            ),
            "duration": 120,
            "source_record": source_record,
        }

        record = cdr_processor.process(
            cdr_input
        )

        # --------------------------------------------------
        # 6. Verify CDR processing
        # --------------------------------------------------

        assert record.caller == (
            "+919876543210"
        )

        assert record.receiver == (
            "+919988776655"
        )

        assert record.timestamp == (
            "2026-09-05T11:00:00"
        )

        assert record.duration == 120

        assert record.source_record == (
            source_record
        )

        # --------------------------------------------------
        # 7. Convert CDR to graph data
        # --------------------------------------------------

        graph_data = (
            graph_adapter.adapt_cdr(
                record
            )
        )

        # --------------------------------------------------
        # 8. Verify graph entities
        # --------------------------------------------------

        assert len(
            graph_data["entities"]
        ) == 2

        assert (
            graph_data["entities"][0][
                "entity_id"
            ]
            == "PHONE_+919876543210"
        )

        assert (
            graph_data["entities"][1][
                "entity_id"
            ]
            == "PHONE_+919988776655"
        )

        assert (
            graph_data["entities"][0][
                "entity_type"
            ]
            == "PHONE"
        )

        assert (
            graph_data["entities"][1][
                "entity_type"
            ]
            == "PHONE"
        )

        assert (
            graph_data["entities"][0][
                "name"
            ]
            == "+919876543210"
        )

        assert (
            graph_data["entities"][1][
                "name"
            ]
            == "+919988776655"
        )

        # --------------------------------------------------
        # 9. Verify graph relationship
        # --------------------------------------------------

        assert len(
            graph_data["relationships"]
        ) == 1

        relationship = graph_data[
            "relationships"
        ][0]

        assert (
            relationship[
                "source_entity_id"
            ]
            == "PHONE_+919876543210"
        )

        assert (
            relationship[
                "target_entity_id"
            ]
            == "PHONE_+919988776655"
        )

        assert (
            relationship[
                "relationship"
            ]
            == "CALLED"
        )

        assert (
            relationship[
                "timestamp"
            ]
            == "2026-09-05T11:00:00"
        )

        assert (
            relationship[
                "source_record"
            ]
            == source_record
        )

        assert (
            relationship[
                "duration"
            ]
            == 120
        )

        # --------------------------------------------------
        # 10. Resolve CDR entities
        # --------------------------------------------------

        resolved_entities = []

        for entity in graph_data[
            "entities"
        ]:

            result = resolver.resolve_entity(
                entity,
                entity_store,
            )

            assert result["action"] == (
                "CREATE"
            )

            resolved_entities.append(
                result["canonical_entity"]
            )

        # --------------------------------------------------
        # 11. Verify canonical entity store
        # --------------------------------------------------

        assert len(
            entity_store
        ) == 2

        assert (
            entity_store.get_entity(
                "PHONE_+919876543210"
            )
            is not None
        )

        assert (
            entity_store.get_entity(
                "PHONE_+919988776655"
            )
            is not None
        )

        # --------------------------------------------------
        # 12. Replace graph entities with
        #     resolved canonical entities
        # --------------------------------------------------

        graph_data["entities"] = (
            resolved_entities
        )

        # --------------------------------------------------
        # 13. Write graph to real Neo4j
        # --------------------------------------------------

        write_result = (
            writer.write_extraction(
                graph_data["entities"],
                graph_data[
                    "relationships"
                ],
                graph_data.get(
                    "events",
                    [],
                ),
            )
        )

        # --------------------------------------------------
        # 14. Verify Neo4j write result
        # --------------------------------------------------

        assert (
            write_result[
                "entities_created"
            ] == 2
        )

        assert (
            write_result[
                "relationships_created"
            ] == 1
        )

        assert (
            write_result[
                "events_created"
            ] == 0
        )

        # --------------------------------------------------
        # 15. Verify entity count in Neo4j
        # --------------------------------------------------

        entity_count = (
            count_cdr_entities(
                writer,
                source_record,
            )
        )

        assert entity_count == 2

        # --------------------------------------------------
        # 16. Verify relationship count
        # --------------------------------------------------

        relationship_count = (
            count_cdr_relationships(
                writer,
                source_record,
            )
        )

        assert relationship_count == 1

        # --------------------------------------------------
        # 17. Query caller from Neo4j
        # --------------------------------------------------

        caller = query_entity(
            writer,
            "PHONE_+919876543210",
        )

        assert caller is not None

        assert (
            caller["entity_id"]
            == "PHONE_+919876543210"
        )

        assert (
            caller["entity_type"]
            == "PHONE"
        )

        assert (
            caller["name"]
            == "+919876543210"
        )

        assert (
            caller["source"]
            == source_record
        )

        assert (
            caller["confidence"]
            == 1.0
        )

        # --------------------------------------------------
        # 18. Query receiver from Neo4j
        # --------------------------------------------------

        receiver = query_entity(
            writer,
            "PHONE_+919988776655",
        )

        assert receiver is not None

        assert (
            receiver["entity_id"]
            == "PHONE_+919988776655"
        )

        assert (
            receiver["entity_type"]
            == "PHONE"
        )

        assert (
            receiver["name"]
            == "+919988776655"
        )

        assert (
            receiver["source"]
            == source_record
        )

        assert (
            receiver["confidence"]
            == 1.0
        )

        # --------------------------------------------------
        # 19. Query CALLED relationship
        # --------------------------------------------------

        neo4j_relationship = (
            query_called_relationship(
                writer,
                "PHONE_+919876543210",
                "PHONE_+919988776655",
            )
        )

        assert (
            neo4j_relationship
            is not None
        )

        assert (
            neo4j_relationship[
                "source_id"
            ]
            == "PHONE_+919876543210"
        )

        assert (
            neo4j_relationship[
                "target_id"
            ]
            == "PHONE_+919988776655"
        )

        assert (
            neo4j_relationship[
                "relationship"
            ]
            == "CALLED"
        )

        assert (
            neo4j_relationship[
                "timestamp"
            ]
            == "2026-09-05T11:00:00"
        )

        assert (
            neo4j_relationship[
                "source_record"
            ]
            == source_record
        )

        assert (
            neo4j_relationship[
                "duration"
            ]
            == 120
        )

        assert (
            neo4j_relationship[
                "confidence"
            ]
            == 1.0
        )

    finally:
        # --------------------------------------------------
        # 20. Clean up integration-test data
        # --------------------------------------------------

        delete_cdr_data(
            writer,
            source_record,
        )

        writer.close()