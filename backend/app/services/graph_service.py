from app.db.neo4j import get_neo4j_driver
from graph.services.graph_query_service import GraphQueryService


class GraphService:
    """
    Service layer for graph operations.
    """

    def __init__(self):
        self.query_service = GraphQueryService(get_neo4j_driver())

    def get_case_graph(self, case_id: str):
        """
        Return the complete graph for a case.
        """
        return self.query_service.get_case_graph(case_id)

    def get_neighbors(self, entity_id: str):
        """
        Return all neighbors of an entity.
        """
        return self.query_service.get_neighbors(entity_id)

    def get_shortest_path(self, source: str, target: str):
        """
        Return the shortest path between two entities.
        """
        return self.query_service.get_shortest_path(source, target)