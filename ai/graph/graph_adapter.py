from models.schemas import (
    CDRRecord,
    FinancialTransaction,
    ExtractionResult,
)


class GraphAdapter:
    """Convert processed records into Neo4j-ready graph data."""

    @staticmethod
    def _relationship_id(
        source_record,
        index,
    ):
        """
        Create a stable ID for one relationship occurrence.

        The source record identifies the underlying evidence
        record, while the index allows one source record to
        contain multiple extracted relationships.
        """

        return (
            f"REL_{source_record}_{index}"
        )

    def adapt_cdr(
        self,
        record: CDRRecord
    ):
        """Convert a CDR record into graph data."""

        caller_id = f"PHONE_{record.caller}"
        receiver_id = f"PHONE_{record.receiver}"

        entities = [
            {
                "entity_id": caller_id,
                "entity_type": "PHONE",
                "name": record.caller,
                "source": record.source_record,
                "confidence": 1.0,
            },
            {
                "entity_id": receiver_id,
                "entity_type": "PHONE",
                "name": record.receiver,
                "source": record.source_record,
                "confidence": 1.0,
            },
        ]

        relationship_id = (
            self._relationship_id(
                record.source_record,
                1,
            )
        )

        relationships = [
            {
                "relationship_id": relationship_id,
                "source": record.caller,
                "source_entity_id": caller_id,
                "relationship": "CALLED",
                "target": record.receiver,
                "target_entity_id": receiver_id,
                "timestamp": record.timestamp,
                "source_record": record.source_record,
                "duration": record.duration,
                "confidence": 1.0,
            }
        ]

        return {
            "entities": entities,
            "relationships": relationships,
            "events": [],
        }

    def adapt_financial(
        self,
        transaction: FinancialTransaction
    ):
        """Convert a financial transaction into graph data."""

        sender_id = (
            f"PARTY_{transaction.sender}"
        )

        receiver_id = (
            f"PARTY_{transaction.receiver}"
        )

        entities = [
            {
                "entity_id": sender_id,
                "entity_type": "PERSON",
                "name": transaction.sender,
                "source": transaction.source_record,
                "confidence": 1.0,
            },
            {
                "entity_id": receiver_id,
                "entity_type": "PERSON",
                "name": transaction.receiver,
                "source": transaction.source_record,
                "confidence": 1.0,
            },
        ]

        relationship_id = (
            self._relationship_id(
                transaction.source_record,
                1,
            )
        )

        relationships = [
            {
                "relationship_id": relationship_id,
                "source": transaction.sender,
                "source_entity_id": sender_id,
                "relationship": (
                    "TRANSFERRED_TO"
                ),
                "target": transaction.receiver,
                "target_entity_id": receiver_id,
                "timestamp": transaction.timestamp,
                "source_record": (
                    transaction.source_record
                ),
                "amount": transaction.amount,
                "confidence": 1.0,
            }
        ]

        return {
            "entities": entities,
            "relationships": relationships,
            "events": [],
        }

    def adapt_fir(
        self,
        extraction: ExtractionResult
    ):
        """Convert FIR extraction results into graph data."""

        entities = []

        for entity in extraction.entities:

            entity_type = entity.entity_type

            if hasattr(
                entity_type,
                "value",
            ):
                entity_type = entity_type.value

            entities.append(
                {
                    "entity_id": entity.entity_id,
                    "entity_type": entity_type,
                    "name": entity.name,
                    "source": entity.source,
                    "confidence": entity.confidence,
                }
            )

        # Build a name -> canonical ID lookup.
        entity_id_by_name = {}

        for entity in entities:

            entity_id = entity.get(
                "entity_id"
            )

            name = entity.get(
                "name"
            )

            if entity_id and name:
                entity_id_by_name[
                    name
                ] = entity_id

        relationships = []

        for index, relationship in enumerate(
            extraction.relationships,
            start=1,
        ):

            source_entity_id = (
                entity_id_by_name.get(
                    relationship.source
                )
            )

            target_entity_id = (
                entity_id_by_name.get(
                    relationship.target
                )
            )

            relationship_id = (
                self._relationship_id(
                    extraction.source_record,
                    index,
                )
            )

            relationships.append(
                {
                    "relationship_id": (
                        relationship_id
                    ),
                    "source": relationship.source,
                    "source_entity_id": (
                        source_entity_id
                    ),
                    "relationship": (
                        relationship.relationship
                    ),
                    "target": relationship.target,
                    "target_entity_id": (
                        target_entity_id
                    ),
                    "timestamp": (
                        relationship.timestamp
                    ),
                    "source_record": (
                        relationship.source_record
                        or extraction.source_record
                    ),
                    "confidence": (
                        relationship.confidence
                    ),
                }
            )

        events = self.adapt_events(
            extraction.events,
            extraction.source_record,
            entities,
        )

        return {
            "entities": entities,
            "relationships": relationships,
            "events": events,
        }

    def adapt_events(
        self,
        events,
        source_record,
        entities=None,
    ):
        """Convert extracted events into graph event data."""

        entities = entities or []

        entity_id_by_name = {}

        for entity in entities:

            entity_id = entity.get(
                "entity_id"
            )

            name = entity.get(
                "name"
            )

            if entity_id and name:
                entity_id_by_name[
                    name
                ] = entity_id

        graph_events = []

        for index, event in enumerate(
            events,
            start=1,
        ):

            event_id = (
                f"EVENT_{source_record}_{index}"
            )

            participant_entity_ids = []

            for participant in event.participants:

                entity_id = (
                    entity_id_by_name.get(
                        participant
                    )
                )

                if (
                    entity_id
                    and entity_id
                    not in participant_entity_ids
                ):
                    participant_entity_ids.append(
                        entity_id
                    )

            graph_events.append(
                {
                    "event_id": event_id,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp,
                    "location": event.location,
                    "amount": event.amount,
                    "participants": event.participants,
                    "participant_entity_ids": (
                        participant_entity_ids
                    ),
                    "source_record": (
                        event.source_record
                        or source_record
                    ),
                    "confidence": event.confidence,
                }
            )

        return graph_events