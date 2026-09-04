from entity_resolution.similarity import EntitySimilarity


def test_phone_exact_match():
    similarity = EntitySimilarity()

    score = similarity.field_similarity(
        "+91 9876543210",
        "9876543210",
        "phone",
    )

    assert score == 1.0


def test_vehicle_exact_match():
    similarity = EntitySimilarity()

    score = similarity.field_similarity(
        "KA01AB1234",
        "KA 01 AB 1234",
        "vehicle",
    )

    assert score == 1.0


def test_multi_field_match():
    similarity = EntitySimilarity()

    entity1 = {
        "name": "Rahul Sharma",
        "phone": "+91 9876543210",
        "address": "Banjara Hills",
        "organization": "ABC Ltd",
    }

    entity2 = {
        "name": "Rahul S.",
        "phone": "9876543210",
        "address": "Banjara Hills",
        "organization": "ABC Ltd",
    }

    result = similarity.multi_field_similarity(
        entity1,
        entity2,
    )

    assert "field_scores" in result
    assert "combined_score" in result

    assert result["field_scores"]["phone"] == 1.0
    assert result["field_scores"]["address"] > 0.9
    assert result["combined_score"] > 0.8


def test_multi_field_missing_values():
    similarity = EntitySimilarity()

    entity1 = {
        "name": "Rahul Sharma",
        "phone": "+91 9876543210",
    }

    entity2 = {
        "name": "Rahul S.",
        "phone": "9876543210",
    }

    result = similarity.multi_field_similarity(
        entity1,
        entity2,
    )

    assert result["field_scores"]["phone"] == 1.0
    assert result["combined_score"] > 0.5