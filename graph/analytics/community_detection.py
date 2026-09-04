"""
Community Detection

Finds groups of closely connected entities
using Neo4j Graph Data Science.
"""


class CommunityDetection:

    def __init__(self, driver):
        self.driver = driver

    def louvain(self):
        """
        Detect criminal communities using Louvain algorithm.
        """

        query = """
        CALL gds.louvain.stream('criminalGraph')
        YIELD nodeId, communityId

        RETURN
            gds.util.asNode(nodeId).entity_id AS entity_id,
            gds.util.asNode(nodeId).name AS name,
            communityId

        ORDER BY communityId
        """

        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]