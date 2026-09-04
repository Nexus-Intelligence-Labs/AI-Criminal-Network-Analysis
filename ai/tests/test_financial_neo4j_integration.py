import os

import pytest

from entity_resolution.resolver import EntityResolver
from entity_resolution.store import EntityStore

from graph.graph_adapter import GraphAdapter
from graph.neo4j_writer import Neo4jGraphWriter

from pipelines.financial_processor import FinancialProcessor


class FinancialSimilarity:
    """
    Deterministic similarity engine for the Financial
    -> Neo4j integration test.

    Entity names are used as the identifier in this test.
    """

    def multi_field_similarity(
        self,
        entity1,
        entity2,
    ):
        name1 = (
            entity1.get("name", "")
            .strip()
            .lower()
        )

        name2 = (
            entity2.get("name", "")
            .strip()
            .lower()
        )

        if name1 == name2:
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


class FinancialConfidenceScorer:
    """Confidence classifier for the financial integration test."""

    def classify(self, score):
        if score >= 0.90:
            return "HIGH"

        if score >= 0.70:
            return "REVIEW"

        return "LOW"


def create_resolver():
    """Create a deterministic entity resolver."""

    return EntityResolver(
        similarity=FinancialSimilarity(),
        confidence_scorer=FinancialConfidenceScorer(),
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


def delete_financial_data(
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


def query_transfer_relationship(
    writer,
    source_id,
    target_id,
):
    """Return the TRANSFERRED_TO relationship."""

    query = """
    MATCH (
        source:Entity {
            entity_id: $source_id
        }
    )-[r:RELATED {
        relationship: "TRANSFERRED_TO"
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
        r.amount AS amount,
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


def count_financial_entities(
    writer,
    source_record,
):
    """Count financial entities created for this source."""

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


def count_financial_relationships(
    writer,
    source_record,
):
    """Count financial relationships created for this source."""

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


def test_real_financial_to_neo4j_end_to_end():
    """
    Test the complete:

    Financial Transaction
    -> Financial Processor
    -> Entity Resolution
    -> Graph Adapter
    -> Neo4j

    flow using a real Neo4j database.
    """

    source_record = (
        "INTEGRATION_FINANCIAL_001"
    )

    writer = create_writer()

    try:
        # --------------------------------------------------
        # 1. Clean previous integration-test data
        # --------------------------------------------------

        delete_financial_data(
            writer,
            source_record,
        )

        # --------------------------------------------------
        # 2. Create the financial processor
        # --------------------------------------------------

        financial_processor = (
            FinancialProcessor()
        )

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
        # 5. Process a real financial transaction
        # --------------------------------------------------

        financial_input = {
            "sender": "Rahul Sharma",
            "receiver": "Priya Singh",
            "amount": 25000,
            "timestamp": (
                "2026-09-05T12:00:00"
            ),
            "source_record": source_record,
        }

        transaction = (
            financial_processor.process(
                financial_input
            )
        )

        # --------------------------------------------------
        # 6. Verify financial processing
        # --------------------------------------------------

        assert transaction.sender == (
            "Rahul Sharma"
        )

        assert transaction.receiver == (
            "Priya Singh"
        )

        assert transaction.amount == 25000.0

        assert transaction.timestamp == (
            "2026-09-05T12:00:00"
        )

        assert transaction.source_record == (
            source_record
        )

        # --------------------------------------------------
        # 7. Convert transaction to graph data
        # --------------------------------------------------

        graph_data = (
            graph_adapter.adapt_financial(
                transaction
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
            == "PARTY_Rahul Sharma"
        )

        assert (
            graph_data["entities"][1][
                "entity_id"
            ]
            == "PARTY_Priya Singh"
        )

        assert (
            graph_data["entities"][0][
                "entity_type"
            ]
            == "PERSON"
        )

        assert (
            graph_data["entities"][1][
                "entity_type"
            ]
            == "PERSON"
        )

        assert (
            graph_data["entities"][0][
                "name"
            ]
            == "Rahul Sharma"
        )

        assert (
            graph_data["entities"][1][
                "name"
            ]
            == "Priya Singh"
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
            == "PARTY_Rahul Sharma"
        )

        assert (
            relationship[
                "target_entity_id"
            ]
            == "PARTY_Priya Singh"
        )

        assert (
            relationship[
                "relationship"
            ]
            == "TRANSFERRED_TO"
        )

        assert (
            relationship[
                "timestamp"
            ]
            == "2026-09-05T12:00:00"
        )

        assert (
            relationship[
                "source_record"
            ]
            == source_record
        )

        assert (
            relationship[
                "amount"
            ]
            == 25000.0
        )

        # --------------------------------------------------
        # 10. Resolve financial entities
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
                "PARTY_Rahul Sharma"
            )
            is not None
        )

        assert (
            entity_store.get_entity(
                "PARTY_Priya Singh"
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
            count_financial_entities(
                writer,
                source_record,
            )
        )

        assert entity_count == 2

        # --------------------------------------------------
        # 16. Verify relationship count
        # --------------------------------------------------

        relationship_count = (
            count_financial_relationships(
                writer,
                source_record,
            )
        )

        assert relationship_count == 1

        # --------------------------------------------------
        # 17. Query sender from Neo4j
        # --------------------------------------------------

        sender = query_entity(
            writer,
            "PARTY_Rahul Sharma",
        )

        assert sender is not None

        assert (
            sender["entity_id"]
            == "PARTY_Rahul Sharma"
        )

        assert (
            sender["entity_type"]
            == "PERSON"
        )

        assert (
            sender["name"]
            == "Rahul Sharma"
        )

        assert (
            sender["source"]
            == source_record
        )

        assert (
            sender["confidence"]
            == 1.0
        )

        # --------------------------------------------------
        # 18. Query receiver from Neo4j
        # --------------------------------------------------

        receiver = query_entity(
            writer,
            "PARTY_Priya Singh",
        )

        assert receiver is not None

        assert (
            receiver["entity_id"]
            == "PARTY_Priya Singh"
        )

        assert (
            receiver["entity_type"]
            == "PERSON"
        )

        assert (
            receiver["name"]
            == "Priya Singh"
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
        # 19. Query TRANSFERRED_TO relationship
        # --------------------------------------------------

        neo4j_relationship = (
            query_transfer_relationship(
                writer,
                "PARTY_Rahul Sharma",
                "PARTY_Priya Singh",
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
            == "PARTY_Rahul Sharma"
        )

        assert (
            neo4j_relationship[
                "target_id"
            ]
            == "PARTY_Priya Singh"
        )

        assert (
            neo4j_relationship[
                "relationship"
            ]
            == "TRANSFERRED_TO"
        )

        assert (
            neo4j_relationship[
                "timestamp"
            ]
            == "2026-09-05T12:00:00"
        )

        assert (
            neo4j_relationship[
                "source_record"
            ]
            == source_record
        )

        assert (
            neo4j_relationship[
                "amount"
            ]
            == 25000.0
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

        delete_financial_data(
            writer,
            source_record,
        )

        writer.close()