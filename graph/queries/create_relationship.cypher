// Create or Update a Relationship

MATCH (source:Entity {entity_id: $source})
MATCH (target:Entity {entity_id: $target})

MERGE (source)-[r:RELATED_TO]->(target)

SET
    r.relationship_id = $relationship_id,
    r.case_id = $case_id,
    r.relationship = $relationship,
    r.source_record = $source_record,
    r.confidence = $confidence,
    r.weight = $weight,
    r.timestamp = $timestamp,
    r.created_at = $created_at

RETURN r;