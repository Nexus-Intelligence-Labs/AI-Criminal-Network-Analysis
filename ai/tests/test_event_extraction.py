from event_extraction.extractor import EventExtractor


def test_call_event_extraction():
    extractor = EventExtractor()

    entities = [
        {
            "entity_type": "PERSON",
            "name": "Rahul Sharma",
        },
        {
            "entity_type": "PERSON",
            "name": "Priya Singh",
        },
    ]

    events = extractor.extract(
        "Rahul Sharma called Priya Singh.",
        "FIR_EVENT_001",
        entities,
    )

    assert len(events) == 1
    assert events[0].event_type == "CALL"
    assert events[0].participants == [
        "Rahul Sharma",
        "Priya Singh",
    ]
    assert events[0].source_record == "FIR_EVENT_001"
    assert events[0].confidence == 0.90


def test_transfer_event_extraction():
    extractor = EventExtractor()

    entities = [
        {
            "entity_type": "PERSON",
            "name": "Rahul Sharma",
        },
        {
            "entity_type": "PERSON",
            "name": "Priya Singh",
        },
    ]

    events = extractor.extract(
        "Rahul Sharma transferred money to Priya Singh.",
        "FIR_EVENT_002",
        entities,
    )

    assert len(events) == 1
    assert events[0].event_type == "TRANSFER"
    assert "Rahul Sharma" in events[0].participants
    assert "Priya Singh" in events[0].participants


def test_empty_text_returns_no_events():
    extractor = EventExtractor()

    events = extractor.extract(
        "",
        "FIR_EVENT_003",
    )

    assert events == []


def test_invalid_text_rejected():
    extractor = EventExtractor()

    try:
        extractor.extract(
            None,
            "FIR_EVENT_004",
        )
        assert False
    except TypeError:
        assert True


def test_unsupported_text_returns_no_events():
    extractor = EventExtractor()

    events = extractor.extract(
        "The investigation continued normally.",
        "FIR_EVENT_005",
    )

    assert events == []