import pytest

from pipelines.financial_processor import FinancialProcessor


def test_financial_transaction_processing():
    processor = FinancialProcessor()

    result = processor.process({
        "sender": "Rahul Sharma",
        "receiver": "Amit Kumar",
        "amount": 50000,
        "timestamp": "2026-09-04T11:00:00",
        "source_record": "TXN_001",
    })

    assert result.sender == "Rahul Sharma"
    assert result.receiver == "Amit Kumar"
    assert result.amount == 50000.0


def test_amount_string_conversion():
    processor = FinancialProcessor()

    result = processor.process({
        "sender": "Rahul Sharma",
        "receiver": "Amit Kumar",
        "amount": "75000",
        "timestamp": "2026-09-04T11:00:00",
        "source_record": "TXN_002",
    })

    assert result.amount == 75000.0


def test_sender_receiver_whitespace():
    processor = FinancialProcessor()

    result = processor.process({
        "sender": "  Rahul Sharma  ",
        "receiver": "  Amit Kumar  ",
        "amount": 10000,
        "timestamp": "2026-09-04T11:00:00",
        "source_record": "TXN_003",
    })

    assert result.sender == "Rahul Sharma"
    assert result.receiver == "Amit Kumar"


def test_negative_amount_rejected():
    processor = FinancialProcessor()

    with pytest.raises(ValueError):
        processor.process({
            "sender": "Rahul Sharma",
            "receiver": "Amit Kumar",
            "amount": -5000,
            "timestamp": "2026-09-04T11:00:00",
            "source_record": "TXN_004",
        })


def test_invalid_input_type_rejected():
    processor = FinancialProcessor()

    with pytest.raises(TypeError):
        processor.process("invalid transaction")