from entity_resolution.resolver import EntityResolver
from entity_resolution.store import EntityStore


class CrossSourceSimilarity:
    """
    Deterministic multi-field similarity engine for
    cross-source entity-resolution tests.
    """

    def multi_field_similarity(
        self,
        entity1,
        entity2,
    ):
        name1 = entity1.get("name", "").lower()
        name2 = entity2.get("name", "").lower()

        phone1 = entity1.get("phone")
        phone2 = entity2.get("phone")

        # Exact phone match is strong evidence.
        if (
            phone1 is not None
            and phone2 is not None
            and self._normalize_phone(phone1)
            == self._normalize_phone(phone2)
        ):
            if name1 == name2:
                score = 1.0
                name_score = 1.0
            else:
                score = 0.96
                name_score = 0.80

            return {
                "field_scores": {
                    "name": name_score,
                    "phone": 1.0,
                },
                "combined_score": score,
            }

        # Similar name without matching phone.
        if (
            name1 == "rahul sharma"
            and name2 == "rahul s."
        ) or (
            name1 == "rahul s."
            and name2 == "rahul sharma"
        ):
            return {
                "field_scores": {
                    "name": 0.80,
                    "phone": 0.0,
                },
                "combined_score": 0.80,
            }

        # Clearly different entities.
        return {
            "field_scores": {
                "name": 0.20,
                "phone": 0.0,
            },
            "combined_score": 0.20,
        }

    @staticmethod
    def _normalize_phone(phone):
        value = "".join(
            character
            for character in str(phone)
            if character.isdigit()
        )

        if value.startswith("91") and len(value) == 12:
            value = value[2:]

        if value.startswith("0") and len(value) == 11:
            value = value[1:]

        return value


class ConfidenceScorer:
    """Confidence classification for integration tests."""

    def classify(self, score):
        if score >= 0.90:
            return "HIGH"

        if score >= 0.70:
            return "REVIEW"

        return "LOW"


def create_resolver():
    return EntityResolver(
        similarity=CrossSourceSimilarity(),
        confidence_scorer=ConfidenceScorer(),
    )


def test_fir_entity_becomes_canonical_entity():
    resolver = create_resolver()
    store = EntityStore()

    fir_entity = {
        "entity_id": "FIR_E001",
        "entity_type": "PERSON",
        "name": "Rahul Sharma",
        "phone": "+91 9876543210",
        "source": "FIR_001",
        "confidence": 0.95,
    }

    result = resolver.resolve_entity(
        fir_entity,
        store,
    )

    assert result["action"] == "CREATE"
    assert result["canonical_entity_id"] == "FIR_E001"

    assert len(store) == 1


def test_same_person_from_second_source_matches_canonical_entity():
    resolver = create_resolver()
    store = EntityStore()

    fir_entity = {
        "entity_id": "FIR_E001",
        "entity_type": "PERSON",
        "name": "Rahul Sharma",
        "phone": "+91 9876543210",
        "source": "FIR_001",
        "confidence": 0.95,
    }

    store.add_entity(fir_entity)

    second_source_entity = {
        "entity_id": "CDR_E001",
        "entity_type": "PERSON",
        "name": "Rahul S.",
        "phone": "9876543210",
        "source": "CDR_001",
        "confidence": 0.90,
    }

    result = resolver.resolve_entity(
        second_source_entity,
        store,
    )

    assert result["action"] == "MATCH"
    assert result["confidence_level"] == "HIGH"

    assert result["canonical_entity_id"] == "FIR_E001"

    assert result["field_scores"]["phone"] == 1.0

    assert len(store) == 1


def test_same_person_information_is_merged():
    resolver = create_resolver()
    store = EntityStore()

    fir_entity = {
        "entity_id": "FIR_E001",
        "entity_type": "PERSON",
        "name": "Rahul Sharma",
        "phone": "+91 9876543210",
        "source": "FIR_001",
        "confidence": 0.95,
    }

    store.add_entity(fir_entity)

    second_source_entity = {
        "entity_id": "CDR_E001",
        "entity_type": "PERSON",
        "name": "Rahul S.",
        "phone": "9876543210",
        "address": "Banjara Hills",
        "organization": "ABC Ltd",
        "source": "CDR_001",
        "confidence": 0.90,
    }

    result = resolver.resolve_entity(
        second_source_entity,
        store,
    )

    assert result["action"] == "MATCH"

    canonical = store.get_entity(
        "FIR_E001"
    )

    assert canonical["entity_id"] == "FIR_E001"

    assert canonical["name"] == "Rahul Sharma"

    assert canonical["phone"] == (
        "+91 9876543210"
    )

    assert canonical["address"] == (
        "Banjara Hills"
    )

    assert canonical["organization"] == (
        "ABC Ltd"
    )

    assert len(store) == 1


def test_different_person_is_not_merged():
    resolver = create_resolver()
    store = EntityStore()

    existing_entity = {
        "entity_id": "E001",
        "entity_type": "PERSON",
        "name": "Rahul Sharma",
        "phone": "+91 9876543210",
        "source": "FIR_001",
        "confidence": 0.95,
    }

    store.add_entity(existing_entity)

    different_entity = {
        "entity_id": "E002",
        "entity_type": "PERSON",
        "name": "Amit Kumar",
        "phone": "9988776655",
        "source": "FIN_001",
        "confidence": 0.95,
    }

    result = resolver.resolve_entity(
        different_entity,
        store,
    )

    assert result["action"] == "CREATE"

    assert result["canonical_entity_id"] == (
        "E002"
    )

    assert len(store) == 2


def test_similar_name_without_strong_identifier_requires_review():
    resolver = create_resolver()
    store = EntityStore()

    existing_entity = {
        "entity_id": "E001",
        "entity_type": "PERSON",
        "name": "Rahul Sharma",
        "phone": "+91 9876543210",
        "source": "FIR_001",
        "confidence": 0.95,
    }

    store.add_entity(existing_entity)

    uncertain_entity = {
        "entity_id": "E002",
        "entity_type": "PERSON",
        "name": "Rahul S.",
        "source": "FIR_002",
        "confidence": 0.90,
    }

    result = resolver.resolve_entity(
        uncertain_entity,
        store,
    )

    assert result["action"] == "REVIEW"

    assert result["confidence_level"] == (
        "REVIEW"
    )

    assert result["canonical_entity_id"] is None

    assert len(store) == 1


def test_cross_source_entity_keeps_canonical_id():
    resolver = create_resolver()
    store = EntityStore()

    first_entity = {
        "entity_id": "E001",
        "entity_type": "PERSON",
        "name": "Rahul Sharma",
        "phone": "+91 9876543210",
        "source": "FIR_001",
        "confidence": 0.95,
    }

    store.add_entity(first_entity)

    second_entity = {
        "entity_id": "E002",
        "entity_type": "PERSON",
        "name": "Rahul S.",
        "phone": "9876543210",
        "source": "FIN_001",
        "confidence": 0.90,
    }

    result = resolver.resolve_entity(
        second_entity,
        store,
    )

    assert result["action"] == "MATCH"

    assert result["canonical_entity_id"] == (
        "E001"
    )

    canonical = store.get_entity("E001")

    assert canonical["entity_id"] == "E001"

    assert store.get_entity("E002") is None

    assert len(store) == 1