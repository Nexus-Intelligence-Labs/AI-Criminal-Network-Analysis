from graph.neo4j_writer import Neo4jGraphWriter


class MockRecord:
    def __init__(self, count):
        self.count = count

    def __getitem__(self, key):
        if key == "count":
            return self.count
        raise KeyError(key)


class MockResult:
    def __init__(self, count):
        self.count = count

    def single(self):
        return MockRecord(self.count)


class MockSession:
    def __init__(self):
        self.queries = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def run(self, query, **parameters):
        self.queries.append({
            "query": query,
            "parameters": parameters,
        })

        if "entities" in parameters:
            return MockResult(len(parameters["entities"]))

        if "relationships" in parameters:
            return MockResult(len(parameters["relationships"]))

        if "events" in parameters:
            return MockResult(len(parameters["events"]))

        return MockResult(0)


class MockDriver:
    def __init__(self):
        self.session_instance = MockSession()
        self.closed = False

    def session(self):
        return self.session_instance

    def close(self):
        self.closed = True


def test_create_entities():
    writer = Neo4jGraphWriter()
    writer.driver = MockDriver()

    entities = [
        {
            "entity_id": "E001",
            "entity_type": "PERSON",
            "name": "Rahul Sharma",
            "source": "FIR_001",
            "confidence": 0.95,
        },
        {
            "entity_id": "E002",
            "entity_type": "PERSON",
            "name": "Priya Singh",
            "source": "FIR_001",
            "confidence": 0.94,
        },
    ]

    count = writer.create_entities(entities)

    assert count == 2
    assert len(writer.driver.session_instance.queries) == 1


def test_create_relationships():
    writer = Neo4jGraphWriter()
    writer.driver = MockDriver()

    relationships = [
        {
            "source": "Rahul Sharma",
            "relationship": "CALLED",
            "target": "Priya Singh",
            "timestamp": None,
            "source_record": "FIR_001",
            "confidence": 0.94,
        }
    ]

    count = writer.create_relationships(relationships)

    assert count == 1
    assert len(writer.driver.session_instance.queries) == 1


def test_create_events():
    writer = Neo4jGraphWriter()
    writer.driver = MockDriver()

    events = [
        {
            "event_id": "EVENT_FIR_001_1",
            "event_type": "CALL",
            "timestamp": None,
            "location": None,
            "amount": None,
            "participants": [
                "Rahul Sharma",
                "Priya Singh",
            ],
            "source_record": "FIR_001",
            "confidence": 0.92,
        }
    ]

    count = writer.create_events(events)

    assert count == 1
    assert len(writer.driver.session_instance.queries) == 1

    query_data = writer.driver.session_instance.queries[0]

    assert "CREATE" not in query_data["query"]
    assert "Event" in query_data["query"]
    assert "INVOLVED_IN" in query_data["query"]


def test_empty_entities():
    writer = Neo4jGraphWriter()

    assert writer.create_entities([]) == 0


def test_empty_relationships():
    writer = Neo4jGraphWriter()

    assert writer.create_relationships([]) == 0


def test_empty_events():
    writer = Neo4jGraphWriter()

    assert writer.create_events([]) == 0


def test_write_extraction():
    writer = Neo4jGraphWriter()
    writer.driver = MockDriver()

    entities = [
        {
            "entity_id": "E001",
            "entity_type": "PERSON",
            "name": "Rahul Sharma",
            "source": "FIR_001",
            "confidence": 0.95,
        }
    ]

    relationships = [
        {
            "source": "Rahul Sharma",
            "relationship": "CALLED",
            "target": "Priya Singh",
            "timestamp": None,
            "source_record": "FIR_001",
            "confidence": 0.94,
        }	
    ]

    events = [
        {
            "event_id": "EVENT_FIR_001_1",
            "event_type": "CALL",
            "timestamp": None,
            "location": None,
            "amount": None,
            "participants": [
                "Rahul Sharma",
                "Priya Singh",
            ],
            "source_record": "FIR_001",
            "confidence": 0.92,
        }
    ]

    result = writer.write_extraction(
        entities,
        relationships,
        events,
    )

    assert result["entities_created"] == 1
    assert result["relationships_created"] == 1
    assert result["events_created"] == 1