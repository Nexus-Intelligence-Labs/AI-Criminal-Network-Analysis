from pathlib import Path


class GraphQueryService:
    """
    Executes reusable Cypher queries.
    """

    def __init__(self, driver):
        self.driver = driver

    def load_query(self, filename: str) -> str:
        query_path = (
            Path(__file__).parent.parent
            / "queries"
            / filename
        )

        with open(query_path, "r", encoding="utf-8") as file:
            return file.read()

    def get_case_graph(self, case_id: str):
        """
        Return the complete graph for a case.
        """

        query = """
        MATCH (source:Entity {case_id: $case_id})
        OPTIONAL MATCH (source)-[relationship:RELATED]->(target:Entity {case_id: $case_id})
        RETURN collect(DISTINCT {
            id: source.entity_id,
            type: toLower(source.entity_type),
            label: source.name,
            case_id: source.case_id,
            source_record: source.source_record
        }) AS nodes,
        collect(DISTINCT CASE WHEN relationship IS NULL THEN NULL ELSE {
            id: relationship.relationship_id,
            source: source.entity_id,
            target: target.entity_id,
            type: relationship.relationship,
            source_record: relationship.source_record
        } END) AS edges
        """

        with self.driver.session() as session:
            result = session.run(query, case_id=case_id).single()
            data = result.data()
            return {
                "nodes": data["nodes"],
                "edges": [edge for edge in data["edges"] if edge is not None],
            }

    def get_neighbors(self, entity_id: str):
        """
        Return all directly connected entities.
        """

        query = self.load_query("get_neighbors.cypher")

        with self.driver.session() as session:
            result = session.run(
                query,
                entity_id=entity_id
            )
            return [record.data() for record in result]

    def get_shortest_path(self, source: str, target: str):
        """
        Return the shortest path between two entities.
        """

        query = self.load_query("shortest_path.cypher")

        with self.driver.session() as session:
            result = session.run(
                query,
                source=source,
                target=target
            )
            return [record.data() for record in result]