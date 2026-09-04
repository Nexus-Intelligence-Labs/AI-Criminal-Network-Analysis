import pytest

from pipelines.cdr_processor import CDRProcessor


def test_cdr_phone_normalization():
    processor = CDRProcessor()

    result = processor.process({
        "caller": "9876543210",
        "receiver": "9812345678",
        "timestamp": "2026-09-04T10:30:00",
        "duration": 245,
        "source_record": "CDR_001",
    })

    assert result.caller == "+919876543210"
    assert result.receiver == "+919812345678"


def test_cdr_hyphen_and_space_normalization():
    processor = CDRProcessor()

    result = processor.process({
        "caller": "+91 9876543210",
        "receiver": "+91-9812345678",
        "timestamp": "2026-09-04T10:30:00",
        "duration": 120,
        "source_record": "CDR_002",
    })

    assert result.caller == "+919876543210"
    assert result.receiver == "+919812345678"


def test_cdr_duration_conversion():
    processor = CDRProcessor()

    result = processor.process({
        "caller": "9876543210",
        "receiver": "9812345678",
        "timestamp": "2026-09-04T10:30:00",
        "duration": "300",
        "source_record": "CDR_003",
    })

    assert result.duration == 300.0


def test_invalid_phone_rejected():
    processor = CDRProcessor()

    with pytest.raises(ValueError):
        processor.process({
            "caller": "1234567890",
            "receiver": "9812345678",
            "timestamp": "2026-09-04T10:30:00",
            "duration": 100,
            "source_record": "CDR_004",
        })


def test_invalid_input_type_rejected():
    processor = CDRProcessor()

    with pytest.raises(TypeError):
        processor.process("invalid CDR")