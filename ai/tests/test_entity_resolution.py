from entity_resolution.resolver import EntityResolver
from entity_resolution.store import EntityStore


class MockSimilarity:
    """Mock similarity engine for resolver unit tests."""

    def __init__(self, score=0.95):
        self.score = score

    def fuzzy_similarity(self, value1, value2):
        return self.score

    def semantic_similarity(self, value1, value2):
        return self.score

    def combined_similarity(
        self,
        fuzzy_score,
        semantic_score,
    ):
        return self.score


class MockConfidenceScorer:
    """Mock confidence scorer."""

    def classify(self, score):
        if score >= 0.90:
            return "HIGH"

        if score >= 0.70:
            return "REVIEW"

        return "LOW"


class MockMultiFieldSimilarity(MockSimilarity):
    """Mock similarity engine supporting multiple fields."""

    def __init__(
        self,
        score=0.95,
        field_scores=None,
    ):
        super().__init__(score)
        self.field_scores = field_scores or {
            "name": score,
        }

    def multi_field_similarity(
        self,
        entity1,
        entity2,
    ):
        return {
            "field_scores": self.field_scores,
            "combined_score": self.score,
        }


def create_entity(
    entity_id="E001",
    name="Rahul Sharma",
    phone=None,
    address=None,
    organization=None,
):
    entity = {
        "entity_id": entity_id,
        "entity_type": "PERSON",
        "name": name,
        "source": "FIR_001",
        "confidence": 0.95,
    }

    if phone is not None:
        entity["phone"] = phone

    if address is not None:
        entity["address"] = address

    if organization is not None:
        entity["organization"] = organization

    return entity


def create_resolver(
    similarity=None,
):
    return EntityResolver(
        similarity=similarity or MockSimilarity(),
        confidence_scorer=MockConfidenceScorer(),
    )


def test_compare():
    resolver = create_resolver()

    result = resolver.compare(
        "Rahul Sharma",
        "Rahul Sharma",
    )

    assert result["entity1"] == "Rahul Sharma"
    assert result["entity2"] == "Rahul Sharma"
    assert result["fuzzy_score"] == 0.95
    assert result["semantic_score"] == 0.95
    assert result["combined_score"] == 0.95
    assert result["confidence_level"] == "HIGH"


def test_compare_entities_with_multi_field_similarity():
    similarity = MockMultiFieldSimilarity(
        score=0.94,
        field_scores={
            "name": 0.90,
            "phone": 1.0,
            "address": 0.95,
        },
    )

    resolver = create_resolver(similarity)

    entity1 = create_entity(
        name="Rahul Sharma",
        phone="+919876543210",
        address="Banjara Hills",
    )

    entity2 = create_entity(
        entity_id="E002",
        name="Rahul S.",
        phone="9876543210",
        address="Banjara Hills",
    )

    result = resolver.compare_entities(
        entity1,
        entity2,
    )

    assert result["combined_score"] == 0.94
    assert result["confidence_level"] == "HIGH"

    assert result["field_scores"]["name"] == 0.90
    assert result["field_scores"]["phone"] == 1.0
    assert result["field_scores"]["address"] == 0.95


def test_resolve_first_entity_creates():
    resolver = create_resolver()
    store = EntityStore()

    entity = create_entity()

    result = resolver.resolve_entity(
        entity,
        store,
    )

    assert result["action"] == "CREATE"
    assert result["canonical_entity_id"] == "E001"
    assert len(store) == 1


def test_high_confidence_match_merges_entity():
    similarity = MockMultiFieldSimilarity(
        score=0.95,
        field_scores={
            "name": 0.90,
            "phone": 1.0,
        },
    )

    resolver = create_resolver(similarity)
    store = EntityStore()

    original = create_entity(
        entity_id="E001",
        name="Rahul Sharma",
    )

    store.add_entity(original)

    incoming = create_entity(
        entity_id="E002",
        name="Rahul S.",
        phone="+919876543210",
    )

    result = resolver.resolve_entity(
        incoming,
        store,
    )

    assert result["action"] == "MATCH"
    assert result["confidence_level"] == "HIGH"
    assert result["canonical_entity_id"] == "E001"

    canonical = store.get_entity("E001")

    assert canonical["name"] == "Rahul Sharma"
    assert canonical["phone"] == "+919876543210"

    assert len(store) == 1


def test_review_does_not_merge():
    similarity = MockMultiFieldSimilarity(
        score=0.80,
        field_scores={
            "name": 0.80,
        },
    )

    resolver = create_resolver(similarity)
    store = EntityStore()

    original = create_entity(
        entity_id="E001",
        name="Rahul Sharma",
    )

    store.add_entity(original)

    incoming = create_entity(
        entity_id="E002",
        name="Rahul S.",
        phone="+919876543210",
    )

    result = resolver.resolve_entity(
        incoming,
        store,
    )

    assert result["action"] == "REVIEW"
    assert result["confidence_level"] == "REVIEW"

    assert result["canonical_entity_id"] is None

    canonical = store.get_entity("E001")

    assert "phone" not in canonical

    assert len(store) == 1


def test_low_confidence_creates_new_entity():
    similarity = MockMultiFieldSimilarity(
        score=0.50,
        field_scores={
            "name": 0.50,
        },
    )

    resolver = create_resolver(similarity)
    store = EntityStore()

    original = create_entity(
        entity_id="E001",
        name="Rahul Sharma",
    )

    store.add_entity(original)

    incoming = create_entity(
        entity_id="E002",
        name="Amit Kumar",
    )

    result = resolver.resolve_entity(
        incoming,
        store,
    )

    assert result["action"] == "CREATE"
    assert result["confidence_level"] == "LOW"
    assert result["canonical_entity_id"] == "E002"

    assert len(store) == 2


def test_different_entity_types_are_not_compared():
    similarity = MockMultiFieldSimilarity(
        score=0.99,
    )

    resolver = create_resolver(similarity)
    store = EntityStore()

    person = create_entity(
        entity_id="E001",
        name="Rahul Sharma",
    )

    store.add_entity(person)

    vehicle = {
        "entity_id": "V001",
        "entity_type": "VEHICLE",
        "name": "KA01AB1234",
        "source": "CDR_001",
        "confidence": 1.0,
    }

    result = resolver.resolve_entity(
        vehicle,
        store,
    )

    assert result["action"] == "CREATE"
    assert result["canonical_entity_id"] == "V001"

    assert len(store) == 2


def test_same_phone_can_produce_high_confidence_match():
    similarity = MockMultiFieldSimilarity(
        score=0.96,
        field_scores={
            "name": 0.75,
            "phone": 1.0,
        },
    )

    resolver = create_resolver(similarity)
    store = EntityStore()

    original = create_entity(
        entity_id="E001",
        name="Rahul Sharma",
        phone="+919876543210",
    )

    store.add_entity(original)

    incoming = create_entity(
        entity_id="E002",
        name="Rahul S.",
        phone="9876543210",
    )

    result = resolver.resolve_entity(
        incoming,
        store,
    )

    assert result["action"] == "MATCH"
    assert result["canonical_entity_id"] == "E001"
    assert result["field_scores"]["phone"] == 1.0


def test_matched_entity_is_canonical_entity():
    similarity = MockMultiFieldSimilarity(
        score=0.95,
        field_scores={
            "name": 0.92,
            "phone": 1.0,
        },
    )

    resolver = create_resolver(similarity)
    store = EntityStore()

    original = create_entity(
        entity_id="E001",
        name="Rahul Sharma",
    )

    store.add_entity(original)

    incoming = create_entity(
        entity_id="E002",
        name="Rahul S.",
        phone="+919876543210",
    )

    result = resolver.resolve_entity(
        incoming,
        store,
    )

    assert result["action"] == "MATCH"
    assert result["matched_entity"]["entity_id"] == "E001"
    assert result["canonical_entity"]["entity_id"] == "E001"


def test_multiple_entities_choose_best_match():
    class CandidateSimilarity(MockSimilarity):
        def multi_field_similarity(
            self,
            entity1,
            entity2,
        ):
            if entity2["entity_id"] == "E001":
                score = 0.75
            else:
                score = 0.96

            return {
                "field_scores": {
                    "name": score,
                },
                "combined_score": score,
            }

    resolver = create_resolver(
        CandidateSimilarity()
    )

    store = EntityStore()

    store.add_entity(
        create_entity(
            entity_id="E001",
            name="Rahul Sharma",
        )
    )

    store.add_entity(
        create_entity(
            entity_id="E002",
            name="Rahul S.",
        )
    )

    incoming = create_entity(
        entity_id="E003",
        name="Rahul Sharma",
    )

    result = resolver.resolve_entity(
        incoming,
        store,
    )

    assert result["action"] == "MATCH"
    assert result["canonical_entity_id"] == "E002"
    assert result["similarity"] == 0.96