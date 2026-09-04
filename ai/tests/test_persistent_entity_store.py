import os

import pytest

from entity_resolution.store import (
    PersistentEntityStore,
)

from graph.neo4j_writer import (
    Neo4jGraphWriter,
)


def create_writer():
    """Create a Neo4j writer."""

    uri = os.getenv(
        "NEO4J_URI",
        "bolt://localhost:7687",
    )

    username = os.getenv(
        "NEO4J_USERNAME",
        "neo4j",
    )

    password = os.getenv(
        "NEO4J_PASSWORD",
        "",
    )

    if not password:
        pytest.fail(
            "NEO4J_PASSWORD is not set."
        )

    return Neo4jGraphWriter(
        uri=uri,
        username=username,
        password=password,
    )


def cleanup_test_data(
    writer,
):
    """Remove only persistent-identity test entities."""

    writer.connect()

    query = """
    MATCH (e:Entity)

    WHERE e.source IN [
        "PERSISTENCE_TEST_001",
        "PERSISTENCE_TEST_002"
    ]

    DETACH DELETE e
    """

    with writer.driver.session() as session:
        session.run(query)


def test_persistent_entity_gets_global_id():
    """A source-local ID must be replaced by a global ID."""

    writer = create_writer()

    try:
        cleanup_test_data(
            writer
        )

        store = PersistentEntityStore(
            writer,
            load_existing=True,
        )

        entity = {
            "entity_id": "E001",
            "entity_type": "PERSON",
            "name": "Persistent Test Person",
            "source": (
                "PERSISTENCE_TEST_001"
            ),
            "confidence": 0.95,
        }

        canonical_id = store.add_entity(
            entity
        )

        assert canonical_id.startswith(
            "ENTITY_"
        )

        assert canonical_id != (
            "E001"
        )

        stored = store.get_entity(
            canonical_id
        )

        assert stored is not None

        assert stored[
            "entity_id"
        ] == canonical_id

        assert stored[
            "source_entity_id"
        ] == "E001"

    finally:
        cleanup_test_data(
            writer
        )

        writer.close()


def test_entity_survives_store_restart():
    """
    An entity written by one PersistentEntityStore must
    remain available to a new store instance.
    """

    writer = create_writer()

    try:
        cleanup_test_data(
            writer
        )

        first_store = PersistentEntityStore(
            writer,
            load_existing=True,
        )

        entity = {
            "entity_id": "E002",
            "entity_type": "PERSON",
            "name": "Restart Test Person",
            "source": (
                "PERSISTENCE_TEST_002"
            ),
            "confidence": 0.96,
        }

        canonical_id = (
            first_store.add_entity(
                entity
            )
        )

        assert canonical_id.startswith(
            "ENTITY_"
        )

        second_store = PersistentEntityStore(
            writer,
            load_existing=True,
        )

        restored = second_store.get_entity(
            canonical_id
        )

        assert restored is not None

        assert restored[
            "entity_id"
        ] == canonical_id

        assert restored[
            "name"
        ] == "Restart Test Person"

        assert restored[
            "source_entity_id"
        ] == "E002"

    finally:
        cleanup_test_data(
            writer
        )

        writer.close()


def test_global_ids_are_unique():
    """Every newly created entity must receive a different ID."""

    writer = create_writer()

    try:
        cleanup_test_data(
            writer
        )

        store = PersistentEntityStore(
            writer,
            load_existing=True,
        )

        entity1 = {
            "entity_id": "E003",
            "entity_type": "PERSON",
            "name": "Global ID Person One",
            "source": (
                "PERSISTENCE_TEST_001"
            ),
            "confidence": 0.95,
        }

        entity2 = {
            "entity_id": "E004",
            "entity_type": "PERSON",
            "name": "Global ID Person Two",
            "source": (
                "PERSISTENCE_TEST_001"
            ),
            "confidence": 0.95,
        }

        id1 = store.add_entity(
            entity1
        )

        id2 = store.add_entity(
            entity2
        )

        assert id1 != id2

        assert id1.startswith(
            "ENTITY_"
        )

        assert id2.startswith(
            "ENTITY_"
        )

    finally:
        cleanup_test_data(
            writer
        )

        writer.close()