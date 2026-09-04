"""
Graph Centrality Analytics

Computes importance scores for entities
using Neo4j Graph Data Science (GDS).
"""


class CentralityAnalytics:

    def __init__(self, driver):
        self.driver = driver

    def degree_centrality(self):
    """
    Returns the number of connections for every entity.
    """

    query = """
    MATCH (n:Entity)
    OPTIONAL MATCH (n)-[r]-()
    RETURN
        n.entity_id AS entity_id,
        n.name AS name,
        COUNT(r) AS degree
    ORDER BY degree DESC
    """

    with self.driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]

    def pagerank(self):
    """
    Returns the most influential entities
    using Neo4j PageRank.
    """

    query = """
    CALL gds.pageRank.stream('criminalGraph')
    YIELD nodeId, score

    RETURN
        gds.util.asNode(nodeId).entity_id AS entity_id,
        gds.util.asNode(nodeId).name AS name,
        score

    ORDER BY score DESC
    """

    with self.driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]