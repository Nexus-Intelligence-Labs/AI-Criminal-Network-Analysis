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

        query = self.load_query("get_case_graph.cypher")

        with self.driver.session() as session:
            result = session.run(query, case_id=case_id)
            return [record.data() for record in result]

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