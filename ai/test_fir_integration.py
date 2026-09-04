from models.schemas import (
    Entity,
    EntityType,
    Relationship,
    ExtractionResult,
)
from graph.graph_adapter import GraphAdapter
from graph.neo4j_writer import Neo4jGraphWriter


extraction = ExtractionResult(
    source_record="FIR_INTEGRATION_TEST",
    source_text="Rahul Sharma called Priya Singh.",
    entities=[
        Entity(
            entity_id="FIR_E001",
            entity_type=EntityType.PERSON,
            name="Rahul Sharma",
            source="FIR_INTEGRATION_TEST",
            confidence=0.95,
        ),
        Entity(
            entity_id="FIR_E002",
            entity_type=EntityType.PERSON,
            name="Priya Singh",
            source="FIR_INTEGRATION_TEST",
            confidence=0.94,
        ),
    ],
    relationships=[
        Relationship(
            source="Rahul Sharma",
            relationship="CALLED",
            target="Priya Singh",
            source_record="FIR_INTEGRATION_TEST",
            confidence=0.92,
        )
    ],
)


adapter = GraphAdapter()
graph_data = adapter.adapt_fir(extraction)

print("GRAPH DATA:")
print(graph_data)

writer = Neo4jGraphWriter()

result = writer.write_extraction(
    graph_data["entities"],
    graph_data["relationships"],
)

print("\nNEO4J RESULT:")
print(result)

writer.close()