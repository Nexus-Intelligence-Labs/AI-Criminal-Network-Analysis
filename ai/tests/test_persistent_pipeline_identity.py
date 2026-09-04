import os

import pytest

from entity_resolution.store import PersistentEntityStore
from graph.graph_adapter import GraphAdapter
from graph.neo4j_writer import Neo4jGraphWriter
from models.schemas import Event, Relationship
from pipelines.unified_pipeline import UnifiedPipeline


class PersistentTestNLP:
    """
    Deterministic FIR NLP component.

    This test deliberately uses fixed source-local IDs so we
    can prove that PersistentEntityStore replaces them with
    globally generated canonical IDs.
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
                    "entity_id": "FIR_LOCAL_E001",
                    "entity_type": "PERSON",
                    "name": "Rahul Sharma",
                    "source": source_id,
                    "confidence": 0.98,
                },
                {
                    "entity_id": "FIR_LOCAL_E002",
                    "entity_type": "PERSON",
                    "name": "Priya Singh",
                    "source": source_id,
                    "confidence": 0.97,
                },
                {
                    "entity_id": "FIR_LOCAL_E003",
                    "entity_type": "PHONE",
                    "name": "+919876543210",
                    "source": source_id,
                    "confidence": 0.99,
                },
            ],
        }


class PersistentTestRelationshipExtractor:
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


class PersistentTestEventExtractor:
    """Deterministic event extractor."""

    def extract(
        self,
        text,
        source_record,
        entities=None,
    ):
        participants = []

        for entity in entities or []:
            if entity.get(
                "entity_type"
            ) != "PERSON":
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


class PersistentTestSimilarity:
    """
    Deterministic identity similarity.

    Exact normalized values are treated as identical.
    Different values are treated as different.
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
                    "identity": 0.0,
                },
                "combined_score": 0.0,
            }

        value1 = (
            entity1.get("name", "")
            .strip()
            .lower()
        )

        value2 = (
            entity2.get("name", "")
            .strip()
            .lower()
        )

        if value1 == value2:
            score = 1.0
        else:
            score = 0.10

        return {
            "field_scores": {
                "identity": score,
            },
            "combined_score": score,
        }


class PersistentTestConfidenceScorer:
    """Deterministic confidence classifier."""

    def classify(
        self,
        score,
    ):
        if score >= 0.90:
            return "HIGH"

        if score >= 0.70:
            return "REVIEW"

        return "LOW"


class PersistentTestCDRProcessor:
    """
    Deterministic CDR processor for this test.

    It uses the actual input shape expected by the real
    UnifiedPipeline.
    """

    def process(
        self,
        data,
    ):
        from pipelines.cdr_processor import (
            CDRProcessor,
        )

        return CDRProcessor().process(
            data
        )


class PersistentTestFinancialProcessor:
    """Use the real financial processor."""

    def process(
        self,
        data,
    ):
        from pipelines.financial_processor import (
            FinancialProcessor,
        )

        return FinancialProcessor().process(
            data
        )


def create_writer():
    """Create the real Neo4j writer."""

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


def create_pipeline(
    writer,
    nlp_pipeline=None,
):
    """
    Create a real UnifiedPipeline WITHOUT explicitly
    supplying an EntityStore.

    This is important because UnifiedPipeline must
    automatically create PersistentEntityStore when a
    Neo4j writer is supplied.
    """

    from entity_resolution.resolver import (
        EntityResolver,
    )
    from validation.confidence import (
        ConfidenceScorer,
    )
    from validation.validators import (
        RelationshipValidator,
    )

    resolver = EntityResolver(
        similarity=PersistentTestSimilarity(),
        confidence_scorer=(
            PersistentTestConfidenceScorer()
        ),
    )

    return UnifiedPipeline(
        nlp_pipeline=(
            nlp_pipeline
            or PersistentTestNLP()
        ),
        cdr_processor=(
            PersistentTestCDRProcessor()
        ),
        financial_processor=(
            PersistentTestFinancialProcessor()
        ),
        relationship_extractor=(
            PersistentTestRelationshipExtractor()
        ),
        event_extractor=(
            PersistentTestEventExtractor()
        ),
        relationship_validator=(
            RelationshipValidator()
        ),
        confidence_scorer=(
            ConfidenceScorer()
        ),
        entity_resolver=resolver,
        graph_adapter=GraphAdapter(),
        neo4j_writer=writer,
    )


def delete_test_data(
    writer,
):
    """Delete only data created by this test."""

    writer.connect()

    query = """
    MATCH (n)
    WHERE n.source IN [
        "PERSISTENT_PIPELINE_FIR",
        "PERSISTENT_PIPELINE_FINANCIAL"
    ]
       OR n.source_record IN [
        "PERSISTENT_PIPELINE_FIR",
        "PERSISTENT_PIPELINE_CDR",
        "PERSISTENT_PIPELINE_FINANCIAL"
    ]
    DETACH DELETE n
    """

    with writer.driver.session() as session:
        session.run(query)


def test_unified_pipeline_uses_persistent_global_identity():
    """
    Verify that the actual UnifiedPipeline:

    1. Automatically selects PersistentEntityStore.
    2. Converts source-local IDs into global IDs.
    3. Persists them to Neo4j.
    4. A new pipeline instance loads the same entities.
    5. A later CDR resolves the same phone to the same
       canonical global ID.
    6. A later financial record resolves the same people
       to the same canonical global IDs.
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
        # 2. Create FIRST pipeline instance
        #
        # No explicit EntityStore is supplied.
        # UnifiedPipeline must create PersistentEntityStore.
        # --------------------------------------------------

        pipeline_one = create_pipeline(
            writer
        )

        assert isinstance(
            pipeline_one.entity_store,
            PersistentEntityStore,
        )

        # --------------------------------------------------
        # 3. Process FIR
        # --------------------------------------------------

        fir_result = pipeline_one.process(
            "fir",
            {
                "source_record": (
                    "PERSISTENT_PIPELINE_FIR"
                ),
                "text": (
                    "Rahul Sharma met "
                    "Priya Singh in Hyderabad. "
                    "Rahul Sharma used "
                    "+919876543210."
                ),
            },
        )

        # --------------------------------------------------
        # 4. Find canonical entities created by FIR
        # --------------------------------------------------

        fir_entities = (
            fir_result["entities"]
        )

        rahul = next(
            entity
            for entity in fir_entities
            if entity["name"]
            == "Rahul Sharma"
        )

        priya = next(
            entity
            for entity in fir_entities
            if entity["name"]
            == "Priya Singh"
        )

        rahul_phone = next(
            entity
            for entity in fir_entities
            if entity["name"]
            == "+919876543210"
        )

        rahul_id = rahul[
            "entity_id"
        ]

        priya_id = priya[
            "entity_id"
        ]

        phone_id = rahul_phone[
            "entity_id"
        ]

        # --------------------------------------------------
        # 5. Verify global canonical IDs
        # --------------------------------------------------

        assert rahul_id.startswith(
            "ENTITY_"
        )

        assert priya_id.startswith(
            "ENTITY_"
        )

        assert phone_id.startswith(
            "ENTITY_"
        )

        assert rahul_id != (
            "FIR_LOCAL_E001"
        )

        assert priya_id != (
            "FIR_LOCAL_E002"
        )

        assert phone_id != (
            "FIR_LOCAL_E003"
        )

        assert (
            rahul_id
            != priya_id
        )

        assert (
            rahul_id
            != phone_id
        )

        assert (
            priya_id
            != phone_id
        )

        # --------------------------------------------------
        # 6. Verify source-local IDs are preserved
        # --------------------------------------------------

        assert (
            rahul[
                "source_entity_id"
            ]
            == "FIR_LOCAL_E001"
        )

        assert (
            priya[
                "source_entity_id"
            ]
            == "FIR_LOCAL_E002"
        )

        assert (
            rahul_phone[
                "source_entity_id"
            ]
            == "FIR_LOCAL_E003"
        )

        # --------------------------------------------------
        # 7. Create SECOND pipeline instance
        #
        # It must load the existing canonical entities
        # from Neo4j.
        # --------------------------------------------------

        pipeline_two = create_pipeline(
            writer
        )

        assert isinstance(
            pipeline_two.entity_store,
            PersistentEntityStore,
        )

        # --------------------------------------------------
        # 8. Verify the new store loaded existing entities
        # --------------------------------------------------

        restored_rahul = (
            pipeline_two.entity_store.get_entity(
                rahul_id
            )
        )

        restored_priya = (
            pipeline_two.entity_store.get_entity(
                priya_id
            )
        )

        restored_phone = (
            pipeline_two.entity_store.get_entity(
                phone_id
            )
        )

        assert restored_rahul is not None
        assert restored_priya is not None
        assert restored_phone is not None

        assert (
            restored_rahul[
                "name"
            ]
            == "Rahul Sharma"
        )

        assert (
            restored_priya[
                "name"
            ]
            == "Priya Singh"
        )

        assert (
            restored_phone[
                "name"
            ]
            == "+919876543210"
        )

        # --------------------------------------------------
        # 9. Process CDR through SECOND pipeline
        #
        # The CDR caller is Rahul's existing phone.
        # --------------------------------------------------

        cdr_result = pipeline_two.process(
            "cdr",
            {
                "caller": "9876543210",
                "receiver": "9988776655",
                "timestamp": (
                    "2026-09-05T10:30:00"
                ),
                "duration": 180,
                "source_record": (
                    "PERSISTENT_PIPELINE_CDR"
                ),
            },
        )

        # --------------------------------------------------
        # 10. Verify CDR caller uses the existing
        #     canonical global ID
        # --------------------------------------------------

        cdr_entities = (
            cdr_result["entities"]
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
            == phone_id
        )

        assert (
            cdr_caller[
                "entity_id"
            ].startswith("ENTITY_")
        )

        assert (
            cdr_receiver[
                "entity_id"
            ].startswith("ENTITY_")
        )

        # --------------------------------------------------
        # 11. Verify CDR relationship uses the
        #     persistent canonical phone ID
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
                "source_entity_id"
            ]
            == phone_id
        )

        assert (
            cdr_relationship[
                "target_entity_id"
            ]
            == cdr_receiver[
                "entity_id"
            ]
        )

        # --------------------------------------------------
        # 12. Process Financial record through the
        #     SAME second pipeline
        # --------------------------------------------------

        financial_result = (
            pipeline_two.process(
                "financial",
                {
                    "sender": "Rahul Sharma",
                    "receiver": "Priya Singh",
                    "amount": 50000,
                    "timestamp": (
                        "2026-09-05T12:00:00"
                    ),
                    "source_record": (
                        "PERSISTENT_PIPELINE_FINANCIAL"
                    ),
                },
            )
        )

        # --------------------------------------------------
        # 13. Verify financial entities resolve to
        #     previously persisted canonical IDs
        # --------------------------------------------------

        financial_entities = (
            financial_result[
                "entities"
            ]
        )

        financial_rahul = next(
            entity
            for entity in financial_entities
            if entity["name"]
            == "Rahul Sharma"
        )

        financial_priya = next(
            entity
            for entity in financial_entities
            if entity["name"]
            == "Priya Singh"
        )

        assert (
            financial_rahul[
                "entity_id"
            ]
            == rahul_id
        )

        assert (
            financial_priya[
                "entity_id"
            ]
            == priya_id
        )

        # --------------------------------------------------
        # 14. Verify financial relationship also uses
        #     persistent canonical IDs
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
                "source_entity_id"
            ]
            == rahul_id
        )

        assert (
            financial_relationship[
                "target_entity_id"
            ]
            == priya_id
        )

        assert (
            financial_relationship[
                "amount"
            ]
            == 50000.0
        )

        # --------------------------------------------------
        # 15. Query Neo4j directly and confirm the
        #     canonical entities exist
        # --------------------------------------------------

        writer.connect()

        query = """
        MATCH (e:Entity)

        WHERE e.entity_id IN $entity_ids

        RETURN
            e.entity_id AS entity_id,
            e.name AS name,
            e.source_entity_id AS source_entity_id
        ORDER BY e.entity_id
        """

        with writer.driver.session() as session:

            result = session.run(
                query,
                entity_ids=[
                    rahul_id,
                    priya_id,
                    phone_id,
                ],
            )

            records = [
                dict(record)
                for record in result
            ]

        assert len(
            records
        ) == 3

        returned_ids = {
            record[
                "entity_id"
            ]
            for record in records
        }

        assert returned_ids == {
            rahul_id,
            priya_id,
            phone_id,
        }

        # --------------------------------------------------
        # 16. Verify no source-local ID was persisted
        #     as the canonical entity ID
        # --------------------------------------------------

        assert (
            "FIR_LOCAL_E001"
            not in returned_ids
        )

        assert (
            "FIR_LOCAL_E002"
            not in returned_ids
        )

        assert (
            "FIR_LOCAL_E003"
            not in returned_ids
        )

    finally:
        # --------------------------------------------------
        # 17. Clean up test data
        # --------------------------------------------------

        delete_test_data(
            writer
        )

        writer.close()