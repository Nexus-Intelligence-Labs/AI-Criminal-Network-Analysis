from pipelines.financial_processor import FinancialProcessor
from graph.graph_adapter import GraphAdapter
from graph.neo4j_writer import Neo4jGraphWriter


processor = FinancialProcessor()
adapter = GraphAdapter()
writer = Neo4jGraphWriter()

transaction_data = {
    "sender": "Rahul Sharma",
    "receiver": "Priya Singh",
    "amount": 50000,
    "timestamp": "2026-09-04T11:00:00",
    "source_record": "FINANCIAL_INTEGRATION_TEST",
}

transaction = processor.process(transaction_data)

graph_data = adapter.adapt_financial(transaction)

result = writer.write_extraction(
    graph_data["entities"],
    graph_data["relationships"],
)

print("FINANCIAL TRANSACTION:")
print(transaction)

print("\nGRAPH DATA:")
print(graph_data)

print("\nNEO4J RESULT:")
print(result)

writer.close()