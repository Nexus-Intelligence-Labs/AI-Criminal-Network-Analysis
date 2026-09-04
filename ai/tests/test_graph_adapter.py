from models.schemas import CDRRecord, FinancialTransaction
from graph.graph_adapter import GraphAdapter


def test_adapt_cdr():
    adapter = GraphAdapter()

    record = CDRRecord(
        caller="9876543210",
        receiver="9123456789",
        timestamp="2026-09-04T10:30:00",
        duration=120,
        source_record="CDR_001",
    )

    result = adapter.adapt_cdr(record)

    assert len(result["entities"]) == 2
    assert len(result["relationships"]) == 1

    assert result["entities"][0]["entity_type"] == "PHONE"
    assert result["entities"][0]["name"] == "9876543210"

    relationship = result["relationships"][0]

    assert relationship["source"] == "9876543210"
    assert relationship["relationship"] == "CALLED"
    assert relationship["target"] == "9123456789"
    assert relationship["duration"] == 120


def test_adapt_financial():
    adapter = GraphAdapter()

    transaction = FinancialTransaction(
        sender="Rahul",
        receiver="Priya",
        amount=50000.0,
        timestamp="2026-09-04T11:00:00",
        source_record="TXN_001",
    )

    result = adapter.adapt_financial(transaction)

    assert len(result["entities"]) == 2
    assert len(result["relationships"]) == 1

    assert result["entities"][0]["name"] == "Rahul"
    assert result["entities"][1]["name"] == "Priya"

    relationship = result["relationships"][0]

    assert relationship["source"] == "Rahul"
    assert relationship["relationship"] == "TRANSFERRED_TO"
    assert relationship["target"] == "Priya"
    assert relationship["amount"] == 50000.0
def test_adapt_fir():
    from models.schemas import (
        Entity,
        EntityType,
        Relationship,
        ExtractionResult,
    )

    extraction = ExtractionResult(
        source_record="FIR_GRAPH_TEST",
        source_text="Rahul Sharma called Priya Singh.",
        entities=[
            Entity(
                entity_id="E001",
                entity_type=EntityType.PERSON,
                name="Rahul Sharma",
                source="FIR_GRAPH_TEST",
                confidence=0.95,
            ),
            Entity(
                entity_id="E002",
                entity_type=EntityType.PERSON,
                name="Priya Singh",
                source="FIR_GRAPH_TEST",
                confidence=0.94,
            ),
        ],
        relationships=[
            Relationship(
                source="Rahul Sharma",
                relationship="CALLED",
                target="Priya Singh",
                source_record="FIR_GRAPH_TEST",
                confidence=0.92,
            )
        ],
    )
    adapter = GraphAdapter()

    result = adapter.adapt_fir(extraction)

    assert len(result["entities"]) == 2
    assert len(result["relationships"]) == 1

    assert result["entities"][0]["name"] == "Rahul Sharma"
    assert result["entities"][0]["entity_type"] == "PERSON"

    assert result["relationships"][0]["source"] == "Rahul Sharma"
    assert result["relationships"][0]["target"] == "Priya Singh"
    assert result["relationships"][0]["relationship"] == "CALLED"