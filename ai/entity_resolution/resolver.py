from entity_resolution.similarity import EntitySimilarity
from validation.confidence import ConfidenceScorer


class EntityResolver:
    def __init__(
        self,
        similarity=None,
        confidence_scorer=None
    ):
        self.similarity = (
            similarity
            or EntitySimilarity()
        )

        self.confidence_scorer = (
            confidence_scorer
            or ConfidenceScorer()
        )

    def compare(
        self,
        name1: str,
        name2: str
    ) -> dict:
        """Compare two entity names."""

        fuzzy_score = (
            self.similarity.fuzzy_similarity(
                name1,
                name2
            )
        )

        semantic_score = (
            self.similarity.semantic_similarity(
                name1,
                name2
            )
        )

        combined_score = (
            self.similarity.combined_similarity(
                fuzzy_score,
                semantic_score
            )
        )

        confidence_level = (
            self.confidence_scorer.classify(
                combined_score
            )
        )

        return {
            "entity1": name1,
            "entity2": name2,
            "fuzzy_score": round(
                fuzzy_score,
                4
            ),
            "semantic_score": round(
                semantic_score,
                4
            ),
            "combined_score": round(
                combined_score,
                4
            ),
            "confidence_level": (
                confidence_level
            ),
        }

    def compare_entities(
        self,
        entity1: dict,
        entity2: dict,
    ) -> dict:
        """Compare two entities using all available fields."""

        if hasattr(
            self.similarity,
            "multi_field_similarity"
        ):
            result = (
                self.similarity.multi_field_similarity(
                    entity1,
                    entity2,
                )
            )

            combined_score = (
                result["combined_score"]
            )

            confidence_level = (
                self.confidence_scorer.classify(
                    combined_score
                )
            )

            return {
                "entity1": entity1,
                "entity2": entity2,
                "field_scores": (
                    result["field_scores"]
                ),
                "combined_score": (
                    combined_score
                ),
                "confidence_level": (
                    confidence_level
                ),
            }

        name_result = self.compare(
            entity1["name"],
            entity2["name"],
        )

        return {
            "entity1": entity1,
            "entity2": entity2,
            "field_scores": {
                "name": (
                    name_result[
                        "combined_score"
                    ]
                ),
            },
            "combined_score": (
                name_result[
                    "combined_score"
                ]
            ),
            "confidence_level": (
                name_result[
                    "confidence_level"
                ]
            ),
        }

    @staticmethod
    def _get_canonical_entity(
        entity_store,
        canonical_id,
        fallback_entity,
    ):
        """
        Return the canonical entity actually stored by the
        entity store.

        PersistentEntityStore may replace the incoming
        source-local ID with a globally generated ID.
        """

        if canonical_id is not None:

            canonical_entity = (
                entity_store.get_entity(
                    canonical_id
                )
            )

            if canonical_entity is not None:
                return canonical_entity

        return fallback_entity

    def resolve_entity(
        self,
        entity,
        entity_store
    ):
        """
        Resolve an incoming entity against existing
        canonical entities.
        """

        candidates = (
            entity_store.get_all_entities()
        )

        # --------------------------------------------------
        # No existing entities.
        # --------------------------------------------------
        #
        # Create the first canonical entity.
        # IMPORTANT: return the entity stored by the store,
        # not the original source-local entity.
        # --------------------------------------------------

        if not candidates:

            canonical_id = (
                entity_store.add_entity(
                    entity
                )
            )

            canonical_entity = (
                self._get_canonical_entity(
                    entity_store,
                    canonical_id,
                    entity,
                )
            )

            return {
                "action": "CREATE",
                "entity": entity,
                "matched_entity": None,
                "canonical_entity": (
                    canonical_entity
                ),
                "canonical_entity_id": (
                    canonical_id
                ),
                "confidence_level": "LOW",
            }

        best_match = None
        best_result = None

        # --------------------------------------------------
        # Compare against existing canonical entities.
        # --------------------------------------------------

        for candidate in candidates:

            # Only compare the same entity type.
            if (
                candidate.get(
                    "entity_type"
                )
                != entity.get(
                    "entity_type"
                )
            ):
                continue

            result = (
                self.compare_entities(
                    entity,
                    candidate,
                )
            )

            if (
                best_result is None
                or result[
                    "combined_score"
                ]
                > best_result[
                    "combined_score"
                ]
            ):
                best_result = result
                best_match = candidate

        # --------------------------------------------------
        # No entity of the same type exists.
        # --------------------------------------------------

        if best_result is None:

            canonical_id = (
                entity_store.add_entity(
                    entity
                )
            )

            canonical_entity = (
                self._get_canonical_entity(
                    entity_store,
                    canonical_id,
                    entity,
                )
            )

            return {
                "action": "CREATE",
                "entity": entity,
                "matched_entity": None,
                "canonical_entity": (
                    canonical_entity
                ),
                "canonical_entity_id": (
                    canonical_id
                ),
                "confidence_level": "LOW",
            }

        # --------------------------------------------------
        # HIGH-confidence match.
        # --------------------------------------------------

        if (
            best_result[
                "confidence_level"
            ]
            == "HIGH"
        ):

            canonical_id = (
                best_match[
                    "entity_id"
                ]
            )

            canonical_entity = (
                entity_store.merge_entity(
                    canonical_id,
                    entity,
                )
            )

            return {
                "action": "MATCH",
                "entity": entity,
                "matched_entity": (
                    canonical_entity
                ),
                "canonical_entity": (
                    canonical_entity
                ),
                "canonical_entity_id": (
                    canonical_id
                ),
                "confidence_level": "HIGH",
                "similarity": (
                    best_result[
                        "combined_score"
                    ]
                ),
                "field_scores": (
                    best_result[
                        "field_scores"
                    ]
                ),
            }

        # --------------------------------------------------
        # REVIEW confidence.
        # --------------------------------------------------
        #
        # Do not merge automatically.
        # --------------------------------------------------

        if (
            best_result[
                "confidence_level"
            ]
            == "REVIEW"
        ):

            return {
                "action": "REVIEW",
                "entity": entity,
                "matched_entity": (
                    best_match
                ),
                "canonical_entity": None,
                "canonical_entity_id": None,
                "confidence_level": "REVIEW",
                "similarity": (
                    best_result[
                        "combined_score"
                    ]
                ),
                "field_scores": (
                    best_result[
                        "field_scores"
                    ]
                ),
            }

        # --------------------------------------------------
        # LOW confidence.
        # --------------------------------------------------
        #
        # Create a new canonical entity and return the
        # entity actually stored by the EntityStore.
        # --------------------------------------------------

        canonical_id = (
            entity_store.add_entity(
                entity
            )
        )

        canonical_entity = (
            self._get_canonical_entity(
                entity_store,
                canonical_id,
                entity,
            )
        )

        return {
            "action": "CREATE",
            "entity": entity,
            "matched_entity": None,
            "canonical_entity": (
                canonical_entity
            ),
            "canonical_entity_id": (
                canonical_id
            ),
            "confidence_level": "LOW",
            "similarity": (
                best_result[
                    "combined_score"
                ]
            ),
            "field_scores": (
                best_result[
                    "field_scores"
                ]
            ),
        }