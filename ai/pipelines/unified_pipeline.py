from pipelines.cdr_processor import CDRProcessor
from pipelines.financial_processor import FinancialProcessor

from nlp.pipeline import NLPPipeline

from relationship_extraction.extractor import RelationshipExtractor
from event_extraction.extractor import EventExtractor

from validation.validators import RelationshipValidator
from validation.confidence import ConfidenceScorer

from entity_resolution.resolver import EntityResolver
from entity_resolution.store import (
    EntityStore,
    PersistentEntityStore,
)

from graph.graph_adapter import GraphAdapter
from graph.neo4j_writer import Neo4jGraphWriter

from models.schemas import ExtractionResult


class UnifiedPipeline:
    """Unified processing pipeline for CDR, financial, and FIR data."""

    def __init__(
        self,
        cdr_processor=None,
        financial_processor=None,
        nlp_pipeline=None,
        relationship_extractor=None,
        event_extractor=None,
        relationship_validator=None,
        confidence_scorer=None,
        entity_resolver=None,
        entity_store=None,
        graph_adapter=None,
        neo4j_writer=None,
    ):
        self.cdr_processor = (
            cdr_processor
            or CDRProcessor()
        )

        self.financial_processor = (
            financial_processor
            or FinancialProcessor()
        )

        self.nlp_pipeline = (
            nlp_pipeline
            or NLPPipeline()
        )

        self.relationship_extractor = (
            relationship_extractor
            or RelationshipExtractor()
        )

        self.event_extractor = (
            event_extractor
            or EventExtractor()
        )

        self.relationship_validator = (
            relationship_validator
            or RelationshipValidator()
        )

        self.confidence_scorer = (
            confidence_scorer
            or ConfidenceScorer()
        )

        self.entity_resolver = (
            entity_resolver
            or EntityResolver()
        )

        self.graph_adapter = (
            graph_adapter
            or GraphAdapter()
        )

        self.neo4j_writer = (
            neo4j_writer
        )

        # --------------------------------------------------
        # Choose the appropriate entity store.
        #
        # When Neo4j is configured, use the persistent
        # global-ID store.
        #
        # Unit tests that do not provide Neo4j continue
        # using the normal in-memory EntityStore.
        # --------------------------------------------------

        if entity_store is not None:

            self.entity_store = (
                entity_store
            )

        elif self.neo4j_writer is not None:

            self.entity_store = (
                PersistentEntityStore(
                    self.neo4j_writer
                )
            )

        else:

            self.entity_store = (
                EntityStore()
            )

    def _resolve_entities(
        self,
        entities
    ):
        """Resolve incoming entities against canonical entities."""

        resolved_entities = []
        resolution_results = []

        for entity in entities:

            result = (
                self.entity_resolver.resolve_entity(
                    entity,
                    self.entity_store,
                )
            )

            resolution_results.append(
                result
            )

            if (
                result["action"] == "MATCH"
                and result.get(
                    "canonical_entity"
                ) is not None
            ):

                resolved_entities.append(
                    result[
                        "canonical_entity"
                    ]
                )

            elif (
                result["action"] == "CREATE"
                and result.get(
                    "canonical_entity"
                ) is not None
            ):

                resolved_entities.append(
                    result[
                        "canonical_entity"
                    ]
                )

            else:

                resolved_entities.append(
                    entity
                )

        return (
            resolved_entities,
            resolution_results,
        )

    @staticmethod
    def _entity_id(entity):
        """Return an entity ID."""

        if not isinstance(
            entity,
            dict,
        ):
            return None

        return entity.get(
            "entity_id"
        )

    @staticmethod
    def _entity_name(entity):
        """Return an entity name."""

        if not isinstance(
            entity,
            dict,
        ):
            return None

        return entity.get(
            "name"
        )

    def _build_canonical_mapping(
        self,
        resolution_results,
    ):
        """Map incoming IDs/names to canonical IDs."""

        incoming_to_canonical = {}

        for result in resolution_results:

            incoming_entity = result.get(
                "entity"
            )

            if not isinstance(
                incoming_entity,
                dict,
            ):
                continue

            action = result.get(
                "action"
            )

            incoming_id = (
                self._entity_id(
                    incoming_entity
                )
            )

            incoming_name = (
                self._entity_name(
                    incoming_entity
                )
            )

            if action == "MATCH":

                canonical_id = result.get(
                    "canonical_entity_id"
                )

                canonical_entity = result.get(
                    "canonical_entity"
                )

                if not canonical_id:
                    continue

                if incoming_id:
                    incoming_to_canonical[
                        incoming_id
                    ] = canonical_id

                if incoming_name:
                    incoming_to_canonical[
                        incoming_name
                    ] = canonical_id

                if canonical_entity:

                    canonical_entity_id = (
                        self._entity_id(
                            canonical_entity
                        )
                    )

                    canonical_name = (
                        self._entity_name(
                            canonical_entity
                        )
                    )

                    if canonical_entity_id:

                        incoming_to_canonical[
                            canonical_entity_id
                        ] = canonical_id

                    if canonical_name:

                        incoming_to_canonical[
                            canonical_name
                        ] = canonical_id

            elif action == "CREATE":

                canonical_id = result.get(
                    "canonical_entity_id"
                )

                canonical_entity = result.get(
                    "canonical_entity"
                )

                if not canonical_id:
                    canonical_id = (
                        self._entity_id(
                            canonical_entity
                        )
                    )

                if not canonical_id:
                    canonical_id = incoming_id

                if canonical_id is None:
                    continue

                if incoming_id:
                    incoming_to_canonical[
                        incoming_id
                    ] = canonical_id

                if incoming_name:
                    incoming_to_canonical[
                        incoming_name
                    ] = canonical_id

            else:

                if incoming_id:
                    incoming_to_canonical[
                        incoming_id
                    ] = incoming_id

                if incoming_name and incoming_id:
                    incoming_to_canonical[
                        incoming_name
                    ] = incoming_id

        return incoming_to_canonical

    def _canonicalize_graph_data(
        self,
        graph_data,
        resolution_results,
    ):
        """Replace graph references with canonical IDs."""

        incoming_to_canonical = (
            self._build_canonical_mapping(
                resolution_results
            )
        )

        unique_entities = {}

        for result in resolution_results:

            action = result.get(
                "action"
            )

            incoming_entity = result.get(
                "entity"
            )

            if not isinstance(
                incoming_entity,
                dict,
            ):
                continue

            if action == "MATCH":

                canonical_entity = result.get(
                    "canonical_entity"
                )

            elif action == "CREATE":

                canonical_entity = (
                    result.get(
                        "canonical_entity"
                    )
                    or incoming_entity
                )

            else:

                canonical_entity = (
                    incoming_entity
                )

            if not isinstance(
                canonical_entity,
                dict,
            ):
                continue

            entity_id = self._entity_id(
                canonical_entity
            )

            if entity_id:
                unique_entities[
                    entity_id
                ] = canonical_entity

        canonical_relationships = []

        for original_relationship in graph_data.get(
            "relationships",
            [],
        ):

            relationship = dict(
                original_relationship
            )

            source_id = relationship.get(
                "source_entity_id"
            )

            target_id = relationship.get(
                "target_entity_id"
            )

            source_name = relationship.get(
                "source"
            )

            target_name = relationship.get(
                "target"
            )

            canonical_source_id = (
                incoming_to_canonical.get(
                    source_id
                )
            )

            if canonical_source_id is None:

                canonical_source_id = (
                    incoming_to_canonical.get(
                        source_name
                    )
                )

            if canonical_source_id is None:

                canonical_source_id = source_id

            canonical_target_id = (
                incoming_to_canonical.get(
                    target_id
                )
            )

            if canonical_target_id is None:

                canonical_target_id = (
                    incoming_to_canonical.get(
                        target_name
                    )
                )

            if canonical_target_id is None:

                canonical_target_id = target_id

            relationship[
                "source_entity_id"
            ] = canonical_source_id

            relationship[
                "target_entity_id"
            ] = canonical_target_id

            canonical_relationships.append(
                relationship
            )

        canonical_events = []

        for original_event in graph_data.get(
            "events",
            [],
        ):

            event = dict(
                original_event
            )

            canonical_participant_ids = []

            for participant_id in event.get(
                "participant_entity_ids",
                [],
            ):

                canonical_id = (
                    incoming_to_canonical.get(
                        participant_id
                    )
                    or participant_id
                )

                if (
                    canonical_id
                    and canonical_id
                    not in canonical_participant_ids
                ):

                    canonical_participant_ids.append(
                        canonical_id
                    )

            for participant in event.get(
                "participants",
                [],
            ):

                canonical_id = (
                    incoming_to_canonical.get(
                        participant
                    )
                )

                if (
                    canonical_id
                    and canonical_id
                    not in canonical_participant_ids
                ):

                    canonical_participant_ids.append(
                        canonical_id
                    )

            event[
                "participant_entity_ids"
            ] = canonical_participant_ids

            canonical_events.append(
                event
            )

        return {
            "entities": list(
                unique_entities.values()
            ),
            "relationships": (
                canonical_relationships
            ),
            "events": canonical_events,
        }

    def write_to_neo4j(
        self,
        graph_data
    ):
        """Write graph data to Neo4j."""

        if self.neo4j_writer is None:
            raise RuntimeError(
                "Neo4j writer is not configured."
            )

        return self.neo4j_writer.write_extraction(
            graph_data.get(
                "entities",
                []
            ),
            graph_data.get(
                "relationships",
                []
            ),
            graph_data.get(
                "events",
                []
            ),
        )

    def process(
        self,
        record_type: str,
        data
    ):
        """Process one supported record type."""

        if record_type == "cdr":

            record = (
                self.cdr_processor.process(
                    data
                )
            )

            original_graph_data = (
                self.graph_adapter.adapt_cdr(
                    record
                )
            )

            (
                resolved_entities,
                resolution_results,
            ) = self._resolve_entities(
                original_graph_data[
                    "entities"
                ]
            )

            graph_data = (
                self._canonicalize_graph_data(
                    original_graph_data,
                    resolution_results,
                )
            )

            return {
                "record_type": "cdr",
                "source_record": (
                    record.source_record
                ),
                "data": record,
                "entities": resolved_entities,
                "relationships": graph_data[
                    "relationships"
                ],
                "resolution": resolution_results,
                "events": [],
                "graph_data": graph_data,
            }

        if record_type == "financial":

            record = (
                self.financial_processor.process(
                    data
                )
            )

            original_graph_data = (
                self.graph_adapter.adapt_financial(
                    record
                )
            )

            (
                resolved_entities,
                resolution_results,
            ) = self._resolve_entities(
                original_graph_data[
                    "entities"
                ]
            )

            graph_data = (
                self._canonicalize_graph_data(
                    original_graph_data,
                    resolution_results,
                )
            )

            return {
                "record_type": "financial",
                "source_record": (
                    record.source_record
                ),
                "data": record,
                "entities": resolved_entities,
                "relationships": graph_data[
                    "relationships"
                ],
                "resolution": resolution_results,
                "events": [],
                "graph_data": graph_data,
            }

        if record_type == "fir":

            source_record = data[
                "source_record"
            ]

            source_text = data[
                "text"
            ]

            nlp_result = (
                self.nlp_pipeline.process(
                    source_text,
                    source_record,
                )
            )

            (
                resolved_entities,
                resolution_results,
            ) = self._resolve_entities(
                nlp_result[
                    "entities"
                ]
            )

            relationships = (
                self.relationship_extractor.extract(
                    nlp_result["text"],
                    source_record,
                )
            )

            validated_relationships = []

            for relationship in relationships:

                validated = (
                    self.relationship_validator.validate(
                        relationship.model_dump()
                    )
                )

                confidence_level = (
                    self.confidence_scorer.classify(
                        validated.confidence
                    )
                )

                validated_relationships.append(
                    {
                        "relationship": validated,
                        "confidence_level": (
                            confidence_level
                        ),
                    }
                )

            events = (
                self.event_extractor.extract(
                    nlp_result["text"],
                    source_record,
                    resolved_entities,
                )
            )

            graph_relationships = [
                item["relationship"]
                for item in validated_relationships
            ]

            extraction = ExtractionResult(
                source_record=source_record,
                source_text=nlp_result["text"],
                entities=resolved_entities,
                relationships=graph_relationships,
                events=events,
            )

            original_graph_data = (
                self.graph_adapter.adapt_fir(
                    extraction
                )
            )

            graph_data = (
                self._canonicalize_graph_data(
                    original_graph_data,
                    resolution_results,
                )
            )

            return {
                "record_type": "fir",
                "source_record": source_record,
                "data": {
                    "source": source_record,
                    "text": nlp_result["text"],
                    "entities": resolved_entities,
                },
                "entities": resolved_entities,
                "relationships": validated_relationships,
                "resolution": resolution_results,
                "events": events,
                "graph_data": graph_data,
            }

        raise ValueError(
            f"Unsupported record type: {record_type}"
        )