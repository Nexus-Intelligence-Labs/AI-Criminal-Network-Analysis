from event_extraction.extractor import EventExtractor
from models.schemas import CDRRecord, FinancialTransaction


class MockCDRProcessor:
    def process(self, data):
        return CDRRecord(
            caller="+919876543210",
            receiver="+919812345678",
            timestamp="2026-09-04T10:30:00",
            duration=245,
            source_record="CDR_001",
        )


class MockFinancialProcessor:
    def process(self, data):
        return FinancialTransaction(
            sender="Rahul Sharma",
            receiver="Amit Kumar",
            amount=50000,
            timestamp="2026-09-04T11:00:00",
            source_record="TXN_001",
        )


class MockNLPPipeline:
    def process(self, text, source_id):
        return {
            "source": source_id,
            "text": text,
            "entities": [
                {
                    "entity_id": "E001",
                    "entity_type": "PERSON",
                    "name": "Rahul Sharma",
                    "source": source_id,
                    "confidence": 0.95,
                },
                {
                    "entity_id": "E002",
                    "entity_type": "PERSON",
                    "name": "Priya Singh",
                    "source": source_id,
                    "confidence": 0.94,
                },
            ],
        }


class MockRelationshipExtractor:
    def extract(self, text, source_record):
        from models.schemas import Relationship

        return [
            Relationship(
                source="Rahul Sharma",
                relationship="CALLED",
                target="Priya Singh",
                source_record=source_record,
                confidence=0.94,
            )
        ]


class MockRelationshipValidator:
    def validate(self, data):
        from models.schemas import Relationship

        return Relationship.model_validate(data)


class MockConfidenceScorer:
    def classify(self, confidence):
        if confidence >= 0.90:
            return "HIGH"

        if confidence >= 0.70:
            return "REVIEW"

        return "LOW"


def create_pipeline():
    from pipelines.unified_pipeline import UnifiedPipeline

    return UnifiedPipeline(
        cdr_processor=MockCDRProcessor(),
        financial_processor=MockFinancialProcessor(),
        nlp_pipeline=MockNLPPipeline(),
        relationship_extractor=MockRelationshipExtractor(),
        relationship_validator=MockRelationshipValidator(),
        confidence_scorer=MockConfidenceScorer(),
    )


def test_cdr_path():
    pipeline = create_pipeline()

    result = pipeline.process(
        "cdr",
        {
            "caller": "9876543210",
            "receiver": "9812345678",
            "timestamp": "2026-09-04T10:30:00",
            "duration": 245,
            "source_record": "CDR_001",
        },
    )

    assert result["record_type"] == "cdr"
    assert result["source_record"] == "CDR_001"
    assert result["data"].caller == "+919876543210"


def test_financial_path():
    pipeline = create_pipeline()

    result = pipeline.process(
        "financial",
        {
            "sender": "Rahul Sharma",
            "receiver": "Amit Kumar",
            "amount": 50000,
            "timestamp": "2026-09-04T11:00:00",
            "source_record": "TXN_001",
        },
    )

    assert result["record_type"] == "financial"
    assert result["source_record"] == "TXN_001"
    assert result["data"].amount == 50000.0


def test_fir_path():
    pipeline = create_pipeline()

    result = pipeline.process(
        "fir",
        {
            "text": "Rahul Sharma called Priya Singh.",
            "source_record": "FIR_001",
        },
    )

    assert result["record_type"] == "fir"
    assert result["source_record"] == "FIR_001"

    assert len(result["data"]["entities"]) == 2
    assert len(result["relationships"]) == 1

    relationship = result["relationships"][0]

    assert relationship["relationship"].source == "Rahul Sharma"
    assert relationship["relationship"].target == "Priya Singh"
    assert relationship["confidence_level"] == "HIGH"


def test_unsupported_record_type():
    pipeline = create_pipeline()

    try:
        pipeline.process("unknown", {})
        assert False
    except ValueError as exc:
        assert "Unsupported record type" in str(exc)


def test_fir_event_extraction():
    pipeline = create_pipeline()

    pipeline.event_extractor = EventExtractor()

    result = pipeline.process(
        "fir",
        {
            "source_record": "FIR_EVENT_INTEGRATION",
            "text": "Rahul Sharma called Priya Singh.",
        },
    )

    assert "events" in result
    assert len(result["events"]) == 1

    event = result["events"][0]

    assert event.event_type == "CALL"
    assert event.source_record == "FIR_EVENT_INTEGRATION"

    assert event.participants == [
        "Rahul Sharma",
        "Priya Singh",
    ]

    assert event.confidence == 0.90