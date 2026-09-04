from nlp.entity_extractor import EntityExtractor


def get_entities(text):
    extractor = EntityExtractor()
    return extractor.extract_entities(text, "TEST_001")


def find_entity(entities, entity_type, name):
    return any(
        entity["entity_type"] == entity_type
        and entity["name"].lower() == name.lower()
        for entity in entities
    )


def test_person_extraction():

    text = "Rahul Sharma met Priya yesterday."

    entities = get_entities(text)

    assert find_entity(
        entities,
        "PERSON",
        "Rahul Sharma"
    )

    assert find_entity(
        entities,
        "PERSON",
        "Priya"
    )


def test_location_extraction():

    text = "The meeting took place in Hyderabad."

    entities = get_entities(text)

    assert find_entity(
        entities,
        "LOCATION",
        "Hyderabad"
    )


def test_organization_extraction():

    text = "The investigation involved State Bank of India."

    entities = get_entities(text)

    assert find_entity(
        entities,
        "ORGANIZATION",
        "State Bank of India"
    )


def test_vehicle_extraction():

    text = "The suspect used vehicle TS09AB1234."

    entities = get_entities(text)

    assert find_entity(
        entities,
        "VEHICLE",
        "TS09AB1234"
    )


def test_phone_extraction():

    text = "Contact number is 9876543210."

    entities = get_entities(text)

    assert find_entity(
        entities,
        "PHONE",
        "9876543210"
    )


def test_complete_investigation_text():

    text = (
        "Rahul Sharma met Priya in Hyderabad. "
        "They used vehicle TS09AB1234. "
        "Contact 9876543210."
    )

    entities = get_entities(text)

    assert find_entity(
        entities,
        "PERSON",
        "Rahul Sharma"
    )

    assert find_entity(
        entities,
        "PERSON",
        "Priya"
    )

    assert find_entity(
        entities,
        "LOCATION",
        "Hyderabad"
    )

    assert find_entity(
        entities,
        "VEHICLE",
        "TS09AB1234"
    )

    assert find_entity(
        entities,
        "PHONE",
        "9876543210"
    )
def test_indian_phone_with_country_code():

    text = "The suspect's contact number is +919876543210."

    entities = get_entities(text)

    assert find_entity(
        entities,
        "PHONE",
        "+919876543210"
    )


def test_vehicle_registration_variation():

    text = "Vehicle registration number TS09AB1234 was reported."

    entities = get_entities(text)

    assert find_entity(
        entities,
        "VEHICLE",
        "TS09AB1234"
    )


def test_multiple_people_and_locations():

    text = (
        "Rahul Sharma and Priya travelled from Hyderabad "
        "to Mumbai."
    )

    entities = get_entities(text)

    assert find_entity(entities, "PERSON", "Rahul Sharma")
    assert find_entity(entities, "PERSON", "Priya")
    assert find_entity(entities, "LOCATION", "Hyderabad")
    assert find_entity(entities, "LOCATION", "Mumbai")


def test_multiple_entities_same_text():

    text = (
        "Amit Kumar contacted Ravi Kumar. "
        "They were located in Delhi."
    )

    entities = get_entities(text)

    assert find_entity(entities, "PERSON", "Amit Kumar")
    assert find_entity(entities, "PERSON", "Ravi Kumar")
    assert find_entity(entities, "LOCATION", "Delhi")