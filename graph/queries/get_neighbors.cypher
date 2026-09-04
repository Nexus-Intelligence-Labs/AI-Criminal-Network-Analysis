// Get all neighbors of an entity

MATCH (e:Entity {entity_id: $entity_id})

OPTIONAL MATCH (e)-[r]-(neighbor)

RETURN
    e,
    r,
    neighbor;