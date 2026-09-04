// Find shortest path between two entities

MATCH (start:Entity {entity_id: $source})
MATCH (end:Entity {entity_id: $target})

MATCH path = shortestPath((start)-[*]-(end))

RETURN path;