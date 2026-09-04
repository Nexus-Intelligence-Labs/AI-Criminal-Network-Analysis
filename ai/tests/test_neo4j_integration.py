import os

import pytest

from entity_resolution.store import EntityStore
from entity_resolution.resolver import EntityResolver

from graph.neo4j_writer import Neo4jGraphWriter

from pipelines.unified_pipeline import UnifiedPipeline

from models.schemas import Relationship


class IntegrationRelationshipExtractor:
    """
    Deterministic relationship extractor used for the
    real Neo4j integration test.

    This avoids loading Gemma while still exercising
    relationship validation and graph construction.
    """

    def extract(
        self,
        text,
        source_record,
    ):
        return [
            Relationship(
                source="Rahul Sharma",
                relationship="CALLED",
                target="Priya Singh",
                timestamp="2026-09-05T10:30:00",
                source_record=source_record,
                confidence=0.95,
            )
        ]


class IntegrationNLP:
    """
    Deterministic NLP result for the Neo4j integration test.

    The Neo4j integration test should verify graph behavior
    independently from model availability.
    """

    def process(
        self,
        text,
        source_id,
    ):
        return {
            "source": source_id,
            "text": text,
            "entities": [
                {
                    "entity_id": "INTEGRATION_E001",
                    "entity_type": "PERSON",
                    "name": "Rahul Sharma",
                    "source": source_id,
                    "confidence": 0.98,
                },
                {
                    "entity_id": "INTEGRATION_E002",
                    "entity_type": "PERSON",
                    "name": "Priya Singh",
                    "source": source_id,
                    "confidence": 0.97,
                },
            ],
        }


class IntegrationSimilarity:
    """
    Deterministic similarity engine for integration testing.

    Rahul Sharma and Priya Singh are deliberately treated
    as different entities.
    """

    def multi_field_similarity(
        self,
        entity1,
        entity2,
    ):
        if (
            entity1["name"]
            == entity2["name"]
        ):
            score = 1.0
        else:
            score = 0.10

        return {
            "field_scores": {
                "name": score,
            },
            "combined_score": score,
        }


class IntegrationConfidenceScorer:
    """Confidence classifier for the integration test."""

    def classify(self, score):
        if score >= 0.90:
            return "HIGH"

        if score >= 0.70:
            return "REVIEW"

        return "LOW"


class IntegrationEventExtractor:
    """Create a deterministic CALL event."""

    def extract(
        self,
        text,
        source_record,
        entities=None,
    ):
        from models.schemas import Event

        participants = []

        for entity in entities or []:

            entity_type = entity.get(
                "entity_type"
            )

            if hasattr(
                entity_type,
                "value"
            ):
                entity_type = entity_type.value

            if entity_type != "PERSON":
                continue

            name = entity.get("name")

            if name and name in text:
                participants.append(name)

        return [
            Event(
                event_type="CALL",
                timestamp="2026-09-05T10:30:00",
                participants=participants,
                source_record=source_record,
                confidence=0.90,
            )
        ]


def create_pipeline():
    """Create a deterministic integration-test pipeline."""

    resolver = EntityResolver(
        similarity=IntegrationSimilarity(),
        confidence_scorer=(
            IntegrationConfidenceScorer()
        ),
    )

    return UnifiedPipeline(
        nlp_pipeline=IntegrationNLP(),
        relationship_extractor=(
            IntegrationRelationshipExtractor()
        ),
        event_extractor=(
            IntegrationEventExtractor()
        ),
        entity_resolver=resolver,
        entity_store=EntityStore(),
    )


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


def delete_integration_data(
    writer,
    source_record,
):
    """
    Remove only the nodes created by this integration test.

    Entity nodes store provenance in the `source` property,
    while Event nodes store provenance in `source_record`.

    Both are checked so the cleanup is complete.
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
    MATCH (e:Entity {
        entity_id: $entity_id
    })

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


def query_relationship(
    writer,
    source_id,
    target_id,
):
    """Return a relationship between two canonical entities."""

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
        r.source_record AS source_record,
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


def query_event(
    writer,
    event_id,
):
    """Return an event node."""

    query = """
    MATCH (e:Event {
        event_id: $event_id
    })

    RETURN
        e.event_id AS event_id,
        e.event_type AS event_type,
        e.source_record AS source_record,
        e.confidence AS confidence
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(
            query,
            event_id=event_id,
        )

        return result.single()


def query_event_participants(
    writer,
    event_id,
):
    """Return canonical IDs connected to an event."""

    query = """
    MATCH (
        p:Entity
    )-[r:INVOLVED_IN]->(
        e:Event {
            event_id: $event_id
        }
    )

    RETURN
        p.entity_id AS entity_id
    ORDER BY p.entity_id
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(
            query,
            event_id=event_id,
        )

        return [
            record["entity_id"]
            for record in result
        ]


def test_real_neo4j_fir_end_to_end():
    """
    Test the complete FIR -> pipeline -> canonical ID ->
    graph adapter -> Neo4j flow.
    """

    source_record = (
        "INTEGRATION_FIR_001"
    )

    writer = create_writer()

    try:
        # Clean up only previous test data.
        delete_integration_data(
            writer,
            source_record,
        )

        # Create pipeline.
        pipeline = create_pipeline()

        # Process FIR.
        result = pipeline.process(
            "fir",
            {
                "source_record": source_record,
                "text": (
                    "Rahul Sharma called "
                    "Priya Singh."
                ),
            },
        )

        # Verify pipeline output.
        assert result[
            "record_type"
        ] == "fir"

        assert result[
            "source_record"
        ] == source_record

        assert len(
            result["entities"]
        ) == 2

        assert len(
            result["relationships"]
        ) == 1

        assert len(
            result["events"]
        ) == 1

        # Verify canonical IDs.
        entity_ids = {
            entity["entity_id"]
            for entity in result[
                "entities"
            ]
        }

        assert (
            "INTEGRATION_E001"
            in entity_ids
        )

        assert (
            "INTEGRATION_E002"
            in entity_ids
        )

        # Verify graph data.
        graph_data = result[
            "graph_data"
        ]

        assert len(
            graph_data["entities"]
        ) == 2

        assert len(
            graph_data["relationships"]
        ) == 1

        assert len(
            graph_data["events"]
        ) == 1

        relationship = graph_data[
            "relationships"
        ][0]

        assert (
            relationship[
                "source_entity_id"
            ]
            == "INTEGRATION_E001"
        )

        assert (
            relationship[
                "target_entity_id"
            ]
            == "INTEGRATION_E002"
        )

        # Write to real Neo4j.
        write_result = pipeline.neo4j_writer

        assert write_result is None

        write_result = writer.write_extraction(
            graph_data["entities"],
            graph_data["relationships"],
            graph_data["events"],
        )

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
            ] == 1
        )

        # Verify entity E001.
        rahul = query_entity(
            writer,
            "INTEGRATION_E001",
        )

        assert rahul is not None

        assert (
            rahul["entity_id"]
            == "INTEGRATION_E001"
        )

        assert (
            rahul["name"]
            == "Rahul Sharma"
        )

        assert (
            rahul["entity_type"]
            == "PERSON"
        )

        # Verify entity E002.
        priya = query_entity(
            writer,
            "INTEGRATION_E002",
        )

        assert priya is not None

        assert (
            priya["entity_id"]
            == "INTEGRATION_E002"
        )

        assert (
            priya["name"]
            == "Priya Singh"
        )

        # Verify relationship.
        relationship = query_relationship(
            writer,
            "INTEGRATION_E001",
            "INTEGRATION_E002",
        )

        assert relationship is not None

        assert (
            relationship[
                "source_id"
            ]
            == "INTEGRATION_E001"
        )

        assert (
            relationship[
                "target_id"
            ]
            == "INTEGRATION_E002"
        )

        assert (
            relationship[
                "relationship"
            ]
            == "CALLED"
        )

        assert (
            relationship[
                "source_record"
            ]
            == source_record
        )

        assert (
            relationship[
                "confidence"
            ] == 0.95
        )

        # Verify event.
        event_id = (
            f"EVENT_{source_record}_1"
        )

        event = query_event(
            writer,
            event_id,
        )

        assert event is not None

        assert (
            event["event_type"]
            == "CALL"
        )

        assert (
            event["source_record"]
            == source_record
        )

        assert (
            event["confidence"]
            == 0.90
        )

        # Verify event participants.
        participants = (
            query_event_participants(
                writer,
                event_id,
            )
        )

        assert participants == [
            "INTEGRATION_E001",
            "INTEGRATION_E002",
        ]

    finally:
        # Always remove both Entity and Event nodes
        # associated with this integration source.
        delete_integration_data(
            writer,
            source_record,
        )

        writer.close()