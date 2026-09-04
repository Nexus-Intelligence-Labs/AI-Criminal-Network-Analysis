import pytest

from validation.confidence import ConfidenceScorer
from validation.validators import RelationshipValidator


def test_high_confidence():
    scorer = ConfidenceScorer()

    assert scorer.classify(0.95) == "HIGH"


def test_review_confidence():
    scorer = ConfidenceScorer()

    assert scorer.classify(0.80) == "REVIEW"


def test_low_confidence():
    scorer = ConfidenceScorer()

    assert scorer.classify(0.50) == "LOW"


def test_valid_relationship():
    validator = RelationshipValidator()

    relationship = validator.validate({
        "source": "Rahul Sharma",
        "relationship": "CALLED",
        "target": "Priya Singh",
        "source_record": "FIR_001",
        "confidence": 0.94
    })

    assert relationship.source == "Rahul Sharma"
    assert relationship.target == "Priya Singh"
    assert relationship.confidence == 0.94


def test_invalid_confidence_rejected():
    validator = RelationshipValidator()

    with pytest.raises(ValueError):
        validator.validate({
            "source": "Rahul Sharma",
            "relationship": "CALLED",
            "target": "Priya Singh",
            "source_record": "FIR_001",
            "confidence": 1.5
        })


def test_invalid_data_type_rejected():
    validator = RelationshipValidator()

    with pytest.raises(TypeError):
        validator.validate("invalid relationship")


def test_multiple_relationships():
    validator = RelationshipValidator()

    relationships = validator.validate_many([
        {
            "source": "Rahul Sharma",
            "relationship": "CALLED",
            "target": "Priya Singh",
            "source_record": "FIR_001",
            "confidence": 0.94
        },
        {
            "source": "Rahul Sharma",
            "relationship": "LOCATED_AT",
            "target": "Hyderabad",
            "source_record": "FIR_001",
            "confidence": 0.91
        }
    ])

    assert len(relationships) == 2
    assert relationships[0].relationship == "CALLED"
    assert relationships[1].relationship == "LOCATED_AT"