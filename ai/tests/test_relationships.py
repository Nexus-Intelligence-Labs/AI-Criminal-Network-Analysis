from relationship_extraction.extractor import (
    RelationshipExtractor,
)


class FakeGeminiClient:
    """
    Fake Gemini client for offline unit tests.

    No real API request is made.
    """

    def __init__(
        self,
        response,
    ):
        self.response = response
        self.last_prompt = None

    def generate_relationships(
        self,
        prompt,
    ):
        self.last_prompt = prompt
        return self.response


def create_extractor(
    response,
):
    """Create an extractor using a fake Gemini client."""

    return RelationshipExtractor(
        client=FakeGeminiClient(
            response
        )
    )


def test_build_prompt():
    """Verify the extraction prompt."""

    extractor = create_extractor(
        {
            "relationships": []
        }
    )

    prompt = extractor.build_prompt(
        "Rahul Sharma called Priya Singh.",
        "FIR_001",
    )

    assert (
        "Rahul Sharma called Priya Singh."
        in prompt
    )

    assert (
        "FIR_001"
        in prompt
    )

    assert (
        "Never invent evidence."
        in prompt
    )


def test_parse_relationships():
    """Verify structured relationship parsing."""

    extractor = create_extractor(
        {
            "relationships": [
                {
                    "source": "Rahul Sharma",
                    "relationship": "CALLED",
                    "target": "Priya Singh",
                    "timestamp": (
                        "2026-09-05T10:30:00"
                    ),
                    "source_record": "FIR_001",
                    "confidence": 0.95,
                }
            ]
        }
    )

    relationships = (
        extractor.extract(
            "Rahul Sharma called Priya Singh.",
            "FIR_001",
        )
    )

    assert len(
        relationships
    ) == 1

    relationship = relationships[0]

    assert (
        relationship.source
        == "Rahul Sharma"
    )

    assert (
        relationship.relationship
        == "CALLED"
    )

    assert (
        relationship.target
        == "Priya Singh"
    )

    assert (
        relationship.source_record
        == "FIR_001"
    )

    assert (
        relationship.confidence
        == 0.95
    )


def test_empty_relationship_list():
    """Verify text with no relationships is accepted."""

    extractor = create_extractor(
        {
            "relationships": []
        }
    )

    relationships = (
        extractor.extract(
            "The document contains no supported relationship.",
            "FIR_002",
        )
    )

    assert relationships == []


def test_missing_source_record_is_replaced():
    """
    Verify the extractor always preserves the real
    source record ID.
    """

    extractor = create_extractor(
        {
            "relationships": [
                {
                    "source": "Rahul Sharma",
                    "relationship": "KNOWS",
                    "target": "Amit Kumar",
                    "timestamp": None,
                    "source_record": None,
                    "confidence": 0.88,
                }
            ]
        }
    )

    relationships = (
        extractor.extract(
            "Rahul Sharma knows Amit Kumar.",
            "FIR_003",
        )
    )

    assert len(
        relationships
    ) == 1

    assert (
        relationships[0].source_record
        == "FIR_003"
    )


def test_unsupported_relationship_is_rejected():
    """Unsupported relationship types must fail validation."""

    extractor = create_extractor(
        {
            "relationships": [
                {
                    "source": "Rahul Sharma",
                    "relationship": "FRIEND_OF",
                    "target": "Priya Singh",
                    "timestamp": None,
                    "source_record": "FIR_004",
                    "confidence": 0.90,
                }
            ]
        }
    )

    try:
        extractor.extract(
            "Rahul Sharma is a friend of Priya Singh.",
            "FIR_004",
        )

        assert False

    except ValueError as exc:

        assert (
            "Unsupported relationship type"
            in str(exc)
        )


def test_extract_without_real_api():
    """
    Verify extraction can be tested without a real
    Gemini API call.
    """

    fake_client = FakeGeminiClient(
        {
            "relationships": [
                {
                    "source": "Rahul Sharma",
                    "relationship": "CALLED",
                    "target": "Priya Singh",
                    "timestamp": None,
                    "source_record": "FIR_005",
                    "confidence": 0.91,
                }
            ]
        }
    )

    extractor = RelationshipExtractor(
        client=fake_client
    )

    result = extractor.extract(
        "Rahul Sharma called Priya Singh.",
        "FIR_005",
    )

    assert len(result) == 1

    assert (
        fake_client.last_prompt
        is not None
    )

    assert (
        result[0].relationship
        == "CALLED"
    )