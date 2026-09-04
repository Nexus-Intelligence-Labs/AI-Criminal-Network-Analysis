from entity_resolution.store import EntityStore


def create_entity():
    return {
        "entity_id": "E001",
        "entity_type": "PERSON",
        "name": "Rahul Sharma",
        "source": "FIR_001",
        "confidence": 0.95,
    }


def test_add_entity():
    store = EntityStore()

    entity = create_entity()

    entity_id = store.add_entity(entity)

    assert entity_id == "E001"
    assert len(store) == 1


def test_get_entity():
    store = EntityStore()

    entity = create_entity()

    store.add_entity(entity)

    result = store.get_entity("E001")

    assert result["name"] == "Rahul Sharma"


def test_get_all_entities():
    store = EntityStore()

    store.add_entity(create_entity())

    store.add_entity({
        "entity_id": "E002",
        "entity_type": "PERSON",
        "name": "Priya Singh",
        "source": "FIR_002",
        "confidence": 0.94,
    })

    entities = store.get_all_entities()

    assert len(entities) == 2


def test_remove_entity():
    store = EntityStore()

    store.add_entity(create_entity())

    assert store.remove_entity("E001") is True
    assert store.get_entity("E001") is None
    assert len(store) == 0


def test_remove_missing_entity():
    store = EntityStore()

    assert store.remove_entity("E999") is False


def test_clear():
    store = EntityStore()

    store.add_entity(create_entity())

    store.clear()

    assert len(store) == 0


def test_update_entity():
    store = EntityStore()

    store.add_entity(create_entity())

    result = store.update_entity(
        "E001",
        {
            "phone": "+919876543210",
        },
    )

    assert result["phone"] == "+919876543210"


def test_merge_entity():
    store = EntityStore()

    store.add_entity(create_entity())

    incoming_entity = {
        "entity_id": "E999",
        "entity_type": "PERSON",
        "name": "Rahul S.",
        "phone": "+919876543210",
        "source": "CDR_001",
    }

    result = store.merge_entity(
        "E001",
        incoming_entity,
    )

    assert result["entity_id"] == "E001"
    assert result["name"] == "Rahul Sharma"
    assert result["phone"] == "+919876543210"


def test_merge_does_not_replace_existing_information():
    store = EntityStore()

    store.add_entity({
        "entity_id": "E001",
        "entity_type": "PERSON",
        "name": "Rahul Sharma",
        "phone": "+919876543210",
    })

    incoming_entity = {
        "entity_id": "E999",
        "entity_type": "PERSON",
        "name": "Rahul S.",
        "phone": "+919999999999",
    }

    result = store.merge_entity(
        "E001",
        incoming_entity,
    )

    assert result["name"] == "Rahul Sharma"
    assert result["phone"] == "+919876543210"


def test_merge_adds_missing_fields():
    store = EntityStore()

    store.add_entity({
        "entity_id": "E001",
        "entity_type": "PERSON",
        "name": "Rahul Sharma",
    })

    incoming_entity = {
        "entity_id": "E999",
        "entity_type": "PERSON",
        "phone": "+919876543210",
        "address": "Banjara Hills",
    }

    result = store.merge_entity(
        "E001",
        incoming_entity,
    )

    assert result["phone"] == "+919876543210"
    assert result["address"] == "Banjara Hills"


def test_update_missing_entity_fails():
    store = EntityStore()

    try:
        store.update_entity(
            "E999",
            {"phone": "+919876543210"},
        )
        assert False
    except KeyError:
        assert True