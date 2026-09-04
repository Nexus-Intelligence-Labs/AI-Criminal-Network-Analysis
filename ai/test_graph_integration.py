from pipelines.cdr_processor import CDRProcessor
from graph.graph_adapter import GraphAdapter
from graph.neo4j_writer import Neo4jGraphWriter


cdr_processor = CDRProcessor()
adapter = GraphAdapter()
writer = Neo4jGraphWriter()

cdr_data = {
    "caller": "9876543210",
    "receiver": "9123456789",
    "timestamp": "2026-09-04T10:30:00",
    "duration": 120,
    "source_record": "CDR_INTEGRATION_TEST",
}

record = cdr_processor.process(cdr_data)

graph_data = adapter.adapt_cdr(record)

result = writer.write_extraction(
    graph_data["entities"],
    graph_data["relationships"],
)

print("CDR RECORD:")
print(record)

print("\nGRAPH DATA:")
print(graph_data)

print("\nNEO4J RESULT:")
print(result)

writer.close()