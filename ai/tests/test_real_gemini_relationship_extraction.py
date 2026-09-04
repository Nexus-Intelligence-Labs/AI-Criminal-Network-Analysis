import os

import pytest

from relationship_extraction.extractor import (
    RelationshipExtractor,
)


@pytest.mark.real_llm
def test_real_gemini_relationship_extraction():
    """
    Real Gemini API integration test.

    Requires GEMINI_API_KEY.
    """

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        pytest.skip(
            "GEMINI_API_KEY is not set."
        )

    extractor = RelationshipExtractor()

    relationships = extractor.extract(
        (
            "On 5 September 2026 at 10:30, "
            "Rahul Sharma called Priya Singh."
        ),
        "REAL_GEMINI_FIR_001",
    )

    assert isinstance(
        relationships,
        list,
    )

    assert len(
        relationships
    ) >= 1

    matching_relationship = None

    for relationship in relationships:

        if (
            relationship.source
            == "Rahul Sharma"
            and relationship.target
            == "Priya Singh"
            and relationship.relationship
            == "CALLED"
        ):
            matching_relationship = (
                relationship
            )
            break

    assert (
        matching_relationship
        is not None
    )

    assert (
        matching_relationship.source_record
        == "REAL_GEMINI_FIR_001"
    )

    assert (
        0.0
        <= matching_relationship.confidence
        <= 1.0
    )