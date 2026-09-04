// Create or Update an Entity

MERGE (e:Entity {entity_id: $entity_id})

SET
    e.case_id = $case_id,
    e.entity_type = $entity_type,
    e.name = $name,
    e.source = $source,
    e.source_record = $source_record,
    e.confidence = $confidence,
    e.created_at = $created_at,
    e.updated_at = $updated_at

RETURN e;