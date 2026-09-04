import os

from neo4j import GraphDatabase


class Neo4jGraphWriter:
    """Write entities, relationships, and events to Neo4j."""

    def __init__(
        self,
        uri=None,
        username=None,
        password=None,
    ):
        self.uri = (
            uri
            or os.getenv(
                "NEO4J_URI",
                "bolt://localhost:7687",
            )
        )

        self.username = (
            username
            or os.getenv(
                "NEO4J_USERNAME",
                "neo4j",
            )
        )

        self.password = (
            password
            or os.getenv(
                "NEO4J_PASSWORD",
                "",
            )
        )

        self.driver = None

    def connect(self):
        """Create the Neo4j driver."""

        if self.driver is None:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(
                    self.username,
                    self.password,
                ),
            )

    def close(self):
        """Close the Neo4j driver."""

        if self.driver is not None:
            self.driver.close()
            self.driver = None

    def create_entities(
        self,
        entities
    ):
        """Create or update entities using canonical IDs."""

        if not entities:
            return 0

        query = """
        UNWIND $entities AS entity

        MERGE (
            e:Entity {
                entity_id: entity.entity_id
            }
        )

        SET
            e.entity_type = entity.entity_type,
            e.name = entity.name,
            e.source = entity.source,
            e.source_entity_id = entity.source_entity_id,
            e.confidence = entity.confidence

        RETURN count(e) AS count
        """

        self.connect()

        with self.driver.session() as session:

            result = session.run(
                query,
                entities=entities,
            )

            record = result.single()

            return record["count"]

    def create_relationships(
        self,
        relationships
    ):
        """
        Create historical relationships using relationship_id.
        """

        if not relationships:
            return 0

        query = """
        UNWIND $relationships AS rel

        MATCH (
            source:Entity {
                entity_id: rel.source_entity_id
            }
        )

        MATCH (
            target:Entity {
                entity_id: rel.target_entity_id
            }
        )

        MERGE (
            source
        )-[r:RELATED {
            relationship_id: rel.relationship_id
        }]->(
            target
        )

        SET
            r.relationship = rel.relationship,
            r.timestamp = rel.timestamp,
            r.source_record = rel.source_record,
            r.confidence = rel.confidence,
            r.duration = rel.duration,
            r.amount = rel.amount

        RETURN count(r) AS count
        """

        self.connect()

        with self.driver.session() as session:

            result = session.run(
                query,
                relationships=relationships,
            )

            record = result.single()

            return record["count"]

    def create_events(
        self,
        events
    ):
        """Create event nodes and connect them to entities."""

        if not events:
            return 0

        query = """
        UNWIND $events AS event

        MERGE (
            e:Event {
                event_id: event.event_id
            }
        )

        SET
            e.event_type = event.event_type,
            e.timestamp = event.timestamp,
            e.location = event.location,
            e.amount = event.amount,
            e.source_record = event.source_record,
            e.confidence = event.confidence

        WITH e, event

        UNWIND event.participant_entity_ids
            AS participant_id

        MATCH (
            p:Entity {
                entity_id: participant_id
            }
        )

        MERGE (
            p
        )-[r:INVOLVED_IN]->(
            e
        )

        SET
            r.source_record = event.source_record,
            r.confidence = event.confidence

        RETURN count(DISTINCT e) AS count
        """

        self.connect()

        with self.driver.session() as session:

            result = session.run(
                query,
                events=events,
            )

            record = result.single()

            return record["count"]

    def write_extraction(
        self,
        entities,
        relationships,
        events=None,
    ):
        """Write entities, relationships, and events."""

        events = events or []

        entity_count = self.create_entities(
            entities
        )

        relationship_count = (
            self.create_relationships(
                relationships
            )
        )

        event_count = self.create_events(
            events
        )

        return {
            "entities_created": entity_count,
            "relationships_created": (
                relationship_count
            ),
            "events_created": event_count,
        }