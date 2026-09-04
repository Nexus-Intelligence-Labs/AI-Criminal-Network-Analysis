// Fetch complete graph for a case

MATCH (e:Entity)
WHERE e.case_id = $case_id

OPTIONAL MATCH (e)-[r]->(connected)

WHERE connected.case_id = $case_id

RETURN
    e,
    r,
    connected;