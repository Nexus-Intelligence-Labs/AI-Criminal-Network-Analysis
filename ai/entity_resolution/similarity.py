from thefuzz import fuzz
from sentence_transformers import SentenceTransformer


class EntitySimilarity:
    """Calculate similarity between entities using multiple signals."""

    def __init__(self, model=None):
        self.model = model or SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def fuzzy_similarity(self, value1: str, value2: str) -> float:
        """Calculate fuzzy string similarity."""

        if not isinstance(value1, str):
            raise TypeError("value1 must be a string")

        if not isinstance(value2, str):
            raise TypeError("value2 must be a string")

        if not value1.strip() or not value2.strip():
            return 0.0

        score = fuzz.ratio(
            value1.strip().lower(),
            value2.strip().lower(),
        )

        return score / 100.0

    def semantic_similarity(self, value1: str, value2: str) -> float:
        """Calculate semantic similarity using embeddings."""

        if not isinstance(value1, str):
            raise TypeError("value1 must be a string")

        if not isinstance(value2, str):
            raise TypeError("value2 must be a string")

        if not value1.strip() or not value2.strip():
            return 0.0

        embeddings = self.model.encode(
            [value1, value2],
            normalize_embeddings=True,
        )

        score = float(embeddings[0] @ embeddings[1])

        return max(0.0, min(1.0, score))

    def combined_similarity(
        self,
        fuzzy_score: float,
        semantic_score: float,
    ) -> float:
        """Combine fuzzy and semantic similarity."""

        return (
            0.4 * fuzzy_score
            + 0.6 * semantic_score
        )

    def field_similarity(
        self,
        value1,
        value2,
        field_type: str,
    ) -> float:
        """Calculate similarity appropriate for a specific entity field."""

        if value1 is None or value2 is None:
            return 0.0

        value1 = str(value1).strip()
        value2 = str(value2).strip()

        if not value1 or not value2:
            return 0.0

        if field_type in {
            "phone",
            "vehicle",
        }:
            normalized1 = self._normalize_identifier(value1)
            normalized2 = self._normalize_identifier(value2)

            if normalized1 == normalized2:
                return 1.0

            return self.fuzzy_similarity(
                normalized1,
                normalized2,
            )

        if field_type in {
            "name",
            "address",
            "organization",
        }:
            fuzzy_score = self.fuzzy_similarity(
                value1,
                value2,
            )

            semantic_score = self.semantic_similarity(
                value1,
                value2,
            )

            return self.combined_similarity(
                fuzzy_score,
                semantic_score,
            )

        return self.fuzzy_similarity(
            value1,
            value2,
        )

    def multi_field_similarity(
        self,
        entity1: dict,
        entity2: dict,
    ) -> dict:
        """Compare entities using multiple available fields."""

        fields = {
            "name": 0.35,
            "phone": 0.30,
            "address": 0.20,
            "organization": 0.15,
        }

        scores = {}
        available_weights = 0.0

        for field, weight in fields.items():

            value1 = entity1.get(field)
            value2 = entity2.get(field)

            if (
                value1 is None
                or value2 is None
                or not str(value1).strip()
                or not str(value2).strip()
            ):
                continue

            scores[field] = self.field_similarity(
                value1,
                value2,
                field,
            )

            available_weights += weight

        if available_weights == 0:
            return {
                "field_scores": {},
                "combined_score": 0.0,
            }

        weighted_score = sum(
            scores[field] * fields[field]
            for field in scores
        )

        combined_score = (
            weighted_score / available_weights
        )

        return {
            "field_scores": scores,
            "combined_score": round(
                combined_score,
                4,
            ),
        }

    

    @staticmethod
    def _normalize_identifier(value: str) -> str:
        """Normalize phone numbers and vehicle identifiers."""

        normalized = "".join(
            character
            for character in value.upper()
            if character.isalnum()
        )

        # Normalize Indian phone numbers to the 10-digit form.
        if normalized.startswith("91") and len(normalized) == 12:
            normalized = normalized[2:]

        if normalized.startswith("0") and len(normalized) == 11:
            normalized = normalized[1:]

        return normalized