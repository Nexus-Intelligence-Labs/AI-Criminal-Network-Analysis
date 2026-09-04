"""
Graph Loader

Responsible for synchronizing data from PostgreSQL
into Neo4j.

PostgreSQL = Source of Truth
Neo4j = Graph Layer
"""

from neo4j import Driver
from pathlib import Path


class GraphLoader:
    def __init__(self, driver: Driver):
        self.driver = driver

    def load_query(self, filename: str) -> str:
        """Load a Cypher query from the queries directory."""
        query_path = Path(__file__).parent.parent / "queries" / filename

        with open(query_path, encoding="utf-8") as file:
            return file.read()

    def load_entity(self, entity: dict):
        """Create or update an Entity node."""
        label = entity["entity_type"].title().replace("_", "")
        query = f"""
        MERGE (e:Entity:{label} {{entity_id: $entity_id}})

        SET
            e.case_id = $case_id,
            e.entity_type = $entity_type,
            e.name = $name,
            e.source = $source,
            e.source_record = $source_record,
            e.confidence = $confidence,
            e.created_at = $created_at,
            e.updated_at = $updated_at

        RETURN e
        """

        with self.driver.session() as session:
            session.run(query, **entity)

    def load_relationship(self, relationship: dict):
        """Create or update a relationship between two entities."""
        relationship_type = relationship["relationship"]
        if not relationship_type.isidentifier():
            raise ValueError(
                "Relationship types must contain only letters, digits, and underscores."
            )

        query = f"""
        MATCH (source:Entity {{entity_id: $source}})
        MATCH (target:Entity {{entity_id: $target}})

        MERGE (source)-[r:{relationship_type}]->(target)

        SET
            r.relationship_id = $relationship_id,
            r.case_id = $case_id,
            r.source_record = $source_record,
            r.confidence = $confidence,
            r.weight = $weight,
            r.timestamp = $timestamp,
            r.created_at = $created_at

        RETURN r
        """

        with self.driver.session() as session:
            session.run(query, **relationship)

    def sync_case(self, entities: list[dict], relationships: list[dict]):
        """Load an entire investigation into Neo4j."""
        for entity in entities:
            self.load_entity(entity)

        for relationship in relationships:
            self.load_relationship(relationship)
