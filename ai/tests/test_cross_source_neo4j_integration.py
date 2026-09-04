import os

import pytest

from entity_resolution.resolver import EntityResolver
from entity_resolution.store import EntityStore

from graph.graph_adapter import GraphAdapter
from graph.neo4j_writer import Neo4jGraphWriter

from models.schemas import Event, Relationship

from pipelines.cdr_processor import CDRProcessor
from pipelines.financial_processor import FinancialProcessor

from pipelines.unified_pipeline import UnifiedPipeline


class CrossSourceSimilarity:
    """
    Deterministic similarity engine for the complete
    FIR + CDR + Financial cross-source integration test.
    """

    def multi_field_similarity(
        self,
        entity1,
        entity2,
    ):
        type1 = entity1.get(
            "entity_type"
        )

        type2 = entity2.get(
            "entity_type"
        )

        if type1 != type2:
            return {
                "field_scores": {
                    "name": 0.0,
                },
                "combined_score": 0.0,
            }

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

        # Exact identifier/name match.
        if name1 == name2:
            return {
                "field_scores": {
                    "name": 1.0,
                },
                "combined_score": 1.0,
            }

        # Similar person name without an exact match.
        if {
            name1,
            name2,
        } == {
            "rahul sharma",
            "rahul s.",
        }:
            return {
                "field_scores": {
                    "name": 0.80,
                },
                "combined_score": 0.80,
            }

        return {
            "field_scores": {
                "name": 0.10,
            },
            "combined_score": 0.10,
        }


class CrossSourceConfidenceScorer:
    """Confidence classifier for the integration test."""

    def classify(self, score):
        if score >= 0.90:
            return "HIGH"

        if score >= 0.70:
            return "REVIEW"

        return "LOW"


class CrossSourceNLP:
    """
    Deterministic FIR NLP component.

    The FIR contains Rahul Sharma, Priya Singh,
    and Rahul's phone number.
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
                    "entity_id": "FIR_CROSS_E001",
                    "entity_type": "PERSON",
                    "name": "Rahul Sharma",
                    "source": source_id,
                    "confidence": 0.98,
                },
                {
                    "entity_id": "FIR_CROSS_E002",
                    "entity_type": "PERSON",
                    "name": "Priya Singh",
                    "source": source_id,
                    "confidence": 0.97,
                },
                {
                    "entity_id": "FIR_CROSS_E003",
                    "entity_type": "PHONE",
                    "name": "+919876543210",
                    "source": source_id,
                    "confidence": 0.99,
                },
            ],
        }


class CrossSourceRelationshipExtractor:
    """Deterministic FIR relationship extractor."""

    def extract(
        self,
        text,
        source_record,
    ):
        return [
            Relationship(
                source="Rahul Sharma",
                relationship="ASSOCIATED_WITH",
                target="Priya Singh",
                timestamp="2026-09-05T09:00:00",
                source_record=source_record,
                confidence=0.95,
            )
        ]


class CrossSourceEventExtractor:
    """Deterministic FIR event extractor."""

    def extract(
        self,
        text,
        source_record,
        entities=None,
    ):
        participants = []

        for entity in entities or []:

            entity_type = entity.get(
                "entity_type"
            )

            if hasattr(
                entity_type,
                "value",
            ):
                entity_type = entity_type.value

            if entity_type != "PERSON":
                continue

            name = entity.get(
                "name"
            )

            if name and name in text:
                participants.append(
                    name
                )

        return [
            Event(
                event_type="MEETING",
                timestamp="2026-09-05T09:00:00",
                participants=participants,
                location="Hyderabad",
                source_record=source_record,
                confidence=0.90,
            )
        ]


class CrossSourceCDRProcessor:
    """Wrapper around the real CDR processor."""

    def __init__(self):
        self.processor = CDRProcessor()

    def process(self, data):
        return self.processor.process(
            data
        )


class CrossSourceFinancialProcessor:
    """Wrapper around the real financial processor."""

    def __init__(self):
        self.processor = FinancialProcessor()

    def process(self, data):
        return self.processor.process(
            data
        )


class CrossSourceGraphAdapter:
    """Wrapper around the real GraphAdapter."""

    def __init__(self):
        self.adapter = GraphAdapter()

    def adapt_cdr(self, record):
        return self.adapter.adapt_cdr(
            record
        )

    def adapt_financial(self, record):
        return self.adapter.adapt_financial(
            record
        )

    def adapt_fir(self, extraction):
        return self.adapter.adapt_fir(
            extraction
        )


def create_pipeline():
    """
    Create one shared UnifiedPipeline.

    The same EntityStore is deliberately shared across
    FIR, CDR, and financial processing so that entities
    can be resolved across different source types.
    """

    resolver = EntityResolver(
        similarity=CrossSourceSimilarity(),
        confidence_scorer=(
            CrossSourceConfidenceScorer()
        ),
    )

    return UnifiedPipeline(
        cdr_processor=(
            CrossSourceCDRProcessor()
        ),
        financial_processor=(
            CrossSourceFinancialProcessor()
        ),
        nlp_pipeline=CrossSourceNLP(),
        relationship_extractor=(
            CrossSourceRelationshipExtractor()
        ),
        event_extractor=(
            CrossSourceEventExtractor()
        ),
        entity_resolver=resolver,
        entity_store=EntityStore(),
        graph_adapter=CrossSourceGraphAdapter(),
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


def delete_cross_source_data(
    writer,
    source_records,
):
    """
    Delete only data created by this integration test.

    Canonical entities may have a different original source,
    so the test also removes the known integration entity IDs.
    """

    writer.connect()

    query = """
    MATCH (n)
    WHERE n.source IN $source_records
       OR n.source_record IN $source_records
       OR n.entity_id IN [
            "FIR_CROSS_E001",
            "FIR_CROSS_E002",
            "FIR_CROSS_E003",
            "PHONE_+919988776655"
       ]
    DETACH DELETE n
    """

    with writer.driver.session() as session:
        session.run(
            query,
            source_records=source_records,
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


def query_relationships_for_entity(
    writer,
    entity_id,
):
    """Return all relationships connected to an entity."""

    query = """
    MATCH (
        source:Entity
    )-[r:RELATED]->(
        target:Entity
    )

    WHERE
        source.entity_id = $entity_id
        OR target.entity_id = $entity_id

    RETURN
        source.entity_id AS source_id,
        r.relationship AS relationship,
        target.entity_id AS target_id,
        r.source_record AS source_record,
        r.amount AS amount,
        r.duration AS duration

    ORDER BY r.source_record
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(
            query,
            entity_id=entity_id,
        )

        return [
            {
                "source_id": record[
                    "source_id"
                ],
                "relationship": record[
                    "relationship"
                ],
                "target_id": record[
                    "target_id"
                ],
                "source_record": record[
                    "source_record"
                ],
                "amount": record[
                    "amount"
                ],
                "duration": record[
                    "duration"
                ],
            }
            for record in result
        ]


def query_events_for_entity(
    writer,
    entity_id,
):
    """Return events connected to an entity."""

    query = """
    MATCH (
        p:Entity {
            entity_id: $entity_id
        }
    )-[:INVOLVED_IN]->(
        e:Event
    )

    RETURN
        e.event_id AS event_id,
        e.event_type AS event_type,
        e.source_record AS source_record,
        e.location AS location

    ORDER BY e.event_id
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(
            query,
            entity_id=entity_id,
        )

        return [
            {
                "event_id": record[
                    "event_id"
                ],
                "event_type": record[
                    "event_type"
                ],
                "source_record": record[
                    "source_record"
                ],
                "location": record[
                    "location"
                ],
            }
            for record in result
        ]


def count_source_entities(
    writer,
    source_record,
):
    """Count entities whose original source matches."""

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

        return result.single()["count"]


def count_source_relationships(
    writer,
    source_record,
):
    """Count relationships created from a source."""

    query = """
    MATCH ()-[r:RELATED]->()
    WHERE r.source_record = $source_record

    RETURN count(r) AS count
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(
            query,
            source_record=source_record,
        )

        return result.single()["count"]


def count_source_events(
    writer,
    source_record,
):
    """Count events created from a source."""

    query = """
    MATCH (e:Event)
    WHERE e.source_record = $source_record

    RETURN count(e) AS count
    """

    writer.connect()

    with writer.driver.session() as session:
        result = session.run(
            query,
            source_record=source_record,
        )

        return result.single()["count"]


def test_real_cross_source_fir_cdr_financial_neo4j():
    """
    Test the complete cross-source investigation flow:

    FIR
        ↓
    Entity Resolution
        ↓
    CDR
        ↓
    Entity Resolution
        ↓
    Financial
        ↓
    Entity Resolution
        ↓
    Unified Graph
        ↓
    Neo4j

    The same EntityStore is used for all three sources.
    """

    fir_source = (
        "INTEGRATION_CROSS_FIR_001"
    )

    cdr_source = (
        "INTEGRATION_CROSS_CDR_001"
    )

    financial_source = (
        "INTEGRATION_CROSS_FINANCIAL_001"
    )

    source_records = [
        fir_source,
        cdr_source,
        financial_source,
    ]

    writer = create_writer()

    try:
        # --------------------------------------------------
        # 1. Clean previous integration data
        # --------------------------------------------------

        delete_cross_source_data(
            writer,
            source_records,
        )

        # --------------------------------------------------
        # 2. Create one shared pipeline
        # --------------------------------------------------

        pipeline = create_pipeline()

        # --------------------------------------------------
        # 3. Process FIR
        # --------------------------------------------------

        fir_result = pipeline.process(
            "fir",
            {
                "source_record": fir_source,
                "text": (
                    "Rahul Sharma met "
                    "Priya Singh in Hyderabad. "
                    "Rahul Sharma used "
                    "+919876543210."
                ),
            },
        )

        # --------------------------------------------------
        # 4. Verify FIR
        # --------------------------------------------------

        assert (
            fir_result["record_type"]
            == "fir"
        )

        assert (
            fir_result["source_record"]
            == fir_source
        )

        assert len(
            fir_result["entities"]
        ) == 3

        assert len(
            fir_result["relationships"]
        ) == 1

        assert len(
            fir_result["events"]
        ) == 1

        # --------------------------------------------------
        # 5. Verify FIR canonical entities
        # --------------------------------------------------

        fir_entity_ids = {
            entity["entity_id"]
            for entity in fir_result[
                "entities"
            ]
        }

        assert (
            "FIR_CROSS_E001"
            in fir_entity_ids
        )

        assert (
            "FIR_CROSS_E002"
            in fir_entity_ids
        )

        assert (
            "FIR_CROSS_E003"
            in fir_entity_ids
        )

        # --------------------------------------------------
        # 6. Write FIR graph to Neo4j
        # --------------------------------------------------

        fir_write_result = (
            writer.write_extraction(
                fir_result["graph_data"][
                    "entities"
                ],
                fir_result["graph_data"][
                    "relationships"
                ],
                fir_result["graph_data"][
                    "events"
                ],
            )
        )

        assert (
            fir_write_result[
                "entities_created"
            ] == 3
        )

        assert (
            fir_write_result[
                "relationships_created"
            ] == 1
        )

        assert (
            fir_write_result[
                "events_created"
            ] == 1
        )

        # --------------------------------------------------
        # 7. Process CDR using the SAME pipeline
        # --------------------------------------------------

        cdr_result = pipeline.process(
            "cdr",
            {
                "caller": "9876543210",
                "receiver": "9988776655",
                "timestamp": (
                    "2026-09-05T10:30:00"
                ),
                "duration": 180,
                "source_record": cdr_source,
            },
        )

        # --------------------------------------------------
        # 8. Verify CDR
        # --------------------------------------------------

        assert (
            cdr_result["record_type"]
            == "cdr"
        )

        assert (
            cdr_result["source_record"]
            == cdr_source
        )

        assert len(
            cdr_result["entities"]
        ) == 2

        assert len(
            cdr_result["relationships"]
        ) == 1

        # --------------------------------------------------
        # 9. Verify CDR cross-source resolution
        #
        # The caller already existed in the FIR as:
        #
        # FIR_CROSS_E003
        #
        # Therefore the CDR caller MUST resolve to
        # that canonical ID.
        # --------------------------------------------------

        cdr_entities = (
            cdr_result[
                "entities"
            ]
        )

        cdr_caller = next(
            entity
            for entity in cdr_entities
            if entity["name"]
            == "+919876543210"
        )

        cdr_receiver = next(
            entity
            for entity in cdr_entities
            if entity["name"]
            == "+919988776655"
        )

        assert (
            cdr_caller[
                "entity_id"
            ]
            == "FIR_CROSS_E003"
        )

        assert (
            cdr_receiver[
                "entity_id"
            ]
            == "PHONE_+919988776655"
        )

        # --------------------------------------------------
        # 10. Verify CDR relationship uses canonical IDs
        # --------------------------------------------------

        cdr_relationship = (
            cdr_result[
                "graph_data"
            ][
                "relationships"
            ][0]
        )

        assert (
            cdr_relationship[
                "relationship"
            ]
            == "CALLED"
        )

        assert (
            cdr_relationship[
                "source_entity_id"
            ]
            == "FIR_CROSS_E003"
        )

        assert (
            cdr_relationship[
                "target_entity_id"
            ]
            == "PHONE_+919988776655"
        )

        assert (
            cdr_relationship[
                "duration"
            ]
            == 180
        )

        assert (
            cdr_relationship[
                "source_record"
            ]
            == cdr_source
        )

        # --------------------------------------------------
        # 11. Write CDR graph to Neo4j
        # --------------------------------------------------

        cdr_write_result = (
            writer.write_extraction(
                cdr_result["graph_data"][
                    "entities"
                ],
                cdr_result["graph_data"][
                    "relationships"
                ],
                cdr_result["graph_data"][
                    "events"
                ],
            )
        )

        assert (
            cdr_write_result[
                "relationships_created"
            ] == 1
        )

        # --------------------------------------------------
        # 12. Process Financial transaction using
        #     SAME pipeline and SAME EntityStore
        # --------------------------------------------------

        financial_result = pipeline.process(
            "financial",
            {
                "sender": "Rahul Sharma",
                "receiver": "Priya Singh",
                "amount": 50000,
                "timestamp": (
                    "2026-09-05T12:00:00"
                ),
                "source_record": (
                    financial_source
                ),
            },
        )

        # --------------------------------------------------
        # 13. Verify Financial processing
        # --------------------------------------------------

        assert (
            financial_result[
                "record_type"
            ]
            == "financial"
        )

        assert (
            financial_result[
                "source_record"
            ]
            == financial_source
        )

        assert len(
            financial_result[
                "entities"
            ]
        ) == 2

        assert len(
            financial_result[
                "relationships"
            ]
        ) == 1

        # --------------------------------------------------
        # 14. Verify Financial entities resolve
        #     to the existing FIR canonical entities
        # --------------------------------------------------

        financial_entities = (
            financial_result[
                "entities"
            ]
        )

        rahul_financial = next(
            entity
            for entity in financial_entities
            if entity["name"]
            == "Rahul Sharma"
        )

        priya_financial = next(
            entity
            for entity in financial_entities
            if entity["name"]
            == "Priya Singh"
        )

        assert (
            rahul_financial[
                "entity_id"
            ]
            == "FIR_CROSS_E001"
        )

        assert (
            priya_financial[
                "entity_id"
            ]
            == "FIR_CROSS_E002"
        )

        # --------------------------------------------------
        # 15. Verify Financial relationship uses
        #     canonical IDs
        # --------------------------------------------------

        financial_relationship = (
            financial_result[
                "graph_data"
            ][
                "relationships"
            ][0]
        )

        assert (
            financial_relationship[
                "relationship"
            ]
            == "TRANSFERRED_TO"
        )

        assert (
            financial_relationship[
                "source_entity_id"
            ]
            == "FIR_CROSS_E001"
        )

        assert (
            financial_relationship[
                "target_entity_id"
            ]
            == "FIR_CROSS_E002"
        )

        assert (
            financial_relationship[
                "amount"
            ]
            == 50000.0
        )

        assert (
            financial_relationship[
                "source_record"
            ]
            == financial_source
        )

        # --------------------------------------------------
        # 16. Write Financial graph to Neo4j
        # --------------------------------------------------

        financial_write_result = (
            writer.write_extraction(
                financial_result[
                    "graph_data"
                ][
                    "entities"
                ],
                financial_result[
                    "graph_data"
                ][
                    "relationships"
                ],
                financial_result[
                    "graph_data"
                ][
                    "events"
                ],
            )
        )

        assert (
            financial_write_result[
                "relationships_created"
            ] == 1
        )

        # --------------------------------------------------
        # 17. Verify Rahul canonical entity
        # --------------------------------------------------

        rahul = query_entity(
            writer,
            "FIR_CROSS_E001",
        )

        assert rahul is not None

        assert (
            rahul["entity_id"]
            == "FIR_CROSS_E001"
        )

        assert (
            rahul["name"]
            == "Rahul Sharma"
        )

        assert (
            rahul["entity_type"]
            == "PERSON"
        )

        # --------------------------------------------------
        # 18. Verify Priya canonical entity
        # --------------------------------------------------

        priya = query_entity(
            writer,
            "FIR_CROSS_E002",
        )

        assert priya is not None

        assert (
            priya["entity_id"]
            == "FIR_CROSS_E002"
        )

        assert (
            priya["name"]
            == "Priya Singh"
        )

        # --------------------------------------------------
        # 19. Verify Rahul's phone canonical entity
        # --------------------------------------------------

        rahul_phone = query_entity(
            writer,
            "FIR_CROSS_E003",
        )

        assert (
            rahul_phone
            is not None
        )

        assert (
            rahul_phone[
                "entity_id"
            ]
            == "FIR_CROSS_E003"
        )

        assert (
            rahul_phone[
                "entity_type"
            ]
            == "PHONE"
        )

        assert (
            rahul_phone[
                "name"
            ]
            == "+919876543210"
        )

        # --------------------------------------------------
        # 20. Verify CDR receiver entity
        # --------------------------------------------------

        cdr_receiver_node = query_entity(
            writer,
            "PHONE_+919988776655",
        )

        assert (
            cdr_receiver_node
            is not None
        )

        assert (
            cdr_receiver_node[
                "entity_id"
            ]
            == "PHONE_+919988776655"
        )

        assert (
            cdr_receiver_node[
                "entity_type"
            ]
            == "PHONE"
        )

        assert (
            cdr_receiver_node[
                "name"
            ]
            == "+919988776655"
        )

        # --------------------------------------------------
        # 21. Verify Rahul has relationships from
        #     multiple data sources
        # --------------------------------------------------

        rahul_relationships = (
            query_relationships_for_entity(
                writer,
                "FIR_CROSS_E001",
            )
        )

        assert len(
            rahul_relationships
        ) == 2

        relationship_types = {
            relationship[
                "relationship"
            ]
            for relationship
            in rahul_relationships
        }

        assert (
            "ASSOCIATED_WITH"
            in relationship_types
        )

        assert (
            "TRANSFERRED_TO"
            in relationship_types
        )

        # --------------------------------------------------
        # 22. Verify the financial relationship
        # --------------------------------------------------

        transfer_relationship = next(
            relationship
            for relationship
            in rahul_relationships
            if relationship[
                "relationship"
            ]
            == "TRANSFERRED_TO"
        )

        assert (
            transfer_relationship[
                "amount"
            ]
            == 50000.0
        )

        assert (
            transfer_relationship[
                "source_record"
            ]
            == financial_source
        )

        # --------------------------------------------------
        # 23. Verify the CDR relationship from the
        #     canonical Rahul phone
        # --------------------------------------------------

        phone_relationships = (
            query_relationships_for_entity(
                writer,
                "FIR_CROSS_E003",
            )
        )

        assert len(
            phone_relationships
        ) == 1

        call_relationship = (
            phone_relationships[0]
        )

        assert (
            call_relationship[
                "relationship"
            ]
            == "CALLED"
        )

        assert (
            call_relationship[
                "source_id"
            ]
            == "FIR_CROSS_E003"
        )

        assert (
            call_relationship[
                "target_id"
            ]
            == "PHONE_+919988776655"
        )

        assert (
            call_relationship[
                "duration"
            ]
            == 180
        )

        assert (
            call_relationship[
                "source_record"
            ]
            == cdr_source
        )

        # --------------------------------------------------
        # 24. Verify Rahul's FIR event
        # --------------------------------------------------

        rahul_events = (
            query_events_for_entity(
                writer,
                "FIR_CROSS_E001",
            )
        )

        assert len(
            rahul_events
        ) == 1

        assert (
            rahul_events[0][
                "event_type"
            ]
            == "MEETING"
        )

        assert (
            rahul_events[0][
                "source_record"
            ]
            == fir_source
        )

        assert (
            rahul_events[0][
                "location"
            ]
            == "Hyderabad"
        )

        # --------------------------------------------------
        # 25. Verify source-specific entity counts
        #
        # FIR owns three original entities.
        # CDR creates one NEW entity because the caller
        # was already canonicalized to the FIR phone entity.
        # Financial creates no new entities because both
        # people already exist canonically.
        # --------------------------------------------------

        assert (
            count_source_entities(
                writer,
                fir_source,
            )
            == 3
        )

        assert (
            count_source_entities(
                writer,
                cdr_source,
            )
            == 1
        )

        assert (
            count_source_entities(
                writer,
                financial_source,
            )
            == 0
        )

        # --------------------------------------------------
        # 26. Verify source-specific relationships
        # --------------------------------------------------

        assert (
            count_source_relationships(
                writer,
                fir_source,
            )
            == 1
        )

        assert (
            count_source_relationships(
                writer,
                cdr_source,
            )
            == 1
        )

        assert (
            count_source_relationships(
                writer,
                financial_source,
            )
            == 1
        )

        # --------------------------------------------------
        # 27. Verify source-specific events
        # --------------------------------------------------

        assert (
            count_source_events(
                writer,
                fir_source,
            )
            == 1
        )

        # --------------------------------------------------
        # 28. Verify there is only ONE Rahul Sharma
        # --------------------------------------------------

        query = """
        MATCH (
            e:Entity
        )

        WHERE e.name = "Rahul Sharma"

        RETURN count(e) AS count
        """

        writer.connect()

        with writer.driver.session() as session:
            result = session.run(
                query
            )

            record = result.single()

            assert (
                record["count"]
                == 1
            )

        # --------------------------------------------------
        # 29. Verify there is only ONE canonical
        #     Rahul phone entity
        # --------------------------------------------------

        query = """
        MATCH (
            e:Entity
        )

        WHERE e.name = "+919876543210"

        RETURN count(e) AS count
        """

        with writer.driver.session() as session:
            result = session.run(
                query
            )

            record = result.single()

            assert (
                record["count"]
                == 1
            )

    finally:
        # --------------------------------------------------
        # 30. Clean up integration-test data
        # --------------------------------------------------

        delete_cross_source_data(
            writer,
            source_records,
        )

        writer.close()