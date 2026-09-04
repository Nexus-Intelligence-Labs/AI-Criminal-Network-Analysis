import random
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "change_me"

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)


def run(query, parameters=None):
    with driver.session() as session:
        session.run(query, parameters or {})


def get_ids(label, property_name):

    query = f"""
    MATCH (n:{label})
    RETURN n.{property_name} AS id
    """

    with driver.session() as session:
        return [r["id"] for r in session.run(query)]

def create_knows_relationships():

    persons = get_ids("Person", "person_id")

    created = 0

    with driver.session() as session:

        for person in persons:

            # Each person knows 3–8 other people
            others = random.sample(
                persons,
                random.randint(3, 8)
            )

            for other in others:

                if person == other:
                    continue

                session.run("""
                    MATCH (a:Person {person_id:$a})
                    MATCH (b:Person {person_id:$b})
                    MERGE (a)-[:KNOWS]->(b)
                """, {
                    "a": person,
                    "b": other
                })

                created += 1

    print(f"KNOWS relationships created: {created}")

def create_uses_phone_relationships():

    persons = get_ids("Person", "person_id")
    phones = get_ids("Phone", "phone_id")

    relationships = []

    for person in persons:

        owned = random.sample(
            phones,
            random.randint(1, 3)
        )

        for phone in owned:

            relationships.append({
                "person": person,
                "phone": phone
            })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (p:Person {person_id: row.person})
        MATCH (ph:Phone {phone_id: row.phone})

        MERGE (p)-[:USES_PHONE]->(ph)
        """, {
            "rows": relationships
        })

    print(f"USES_PHONE relationships created: {len(relationships)}")

def create_involved_in_relationships():

    persons = get_ids("Person", "person_id")
    cases = get_ids("Case", "case_id")

    created = 0

    with driver.session() as session:

        for person in persons:

            case = random.choice(cases)

            session.run("""
                MATCH (p:Person {person_id:$person})
                MATCH (c:Case {case_id:$case})

                MERGE (p)-[:INVOLVED_IN]->(c)
            """, {
                "person": person,
                "case": case
            })

            created += 1

    print("INVOLVED_IN:", created)

def create_owns_vehicle_relationships():

    persons = get_ids("Person", "person_id")
    vehicles = get_ids("Vehicle", "vehicle_id")

    relationships = []

    available_vehicles = vehicles.copy()
    random.shuffle(available_vehicles)

    for person in persons:

        if not available_vehicles:
            break

        count = random.randint(0, 2)

        for _ in range(count):

            if not available_vehicles:
                break

            vehicle = available_vehicles.pop()

            relationships.append({
                "person": person,
                "vehicle": vehicle
            })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (p:Person {person_id: row.person})
        MATCH (v:Vehicle {vehicle_id: row.vehicle})

        MERGE (p)-[:OWNS_VEHICLE]->(v)
        """, {
            "rows": relationships
        })

    print(f"OWNS_VEHICLE relationships created: {len(relationships)}")

def create_owns_account_relationships():

    persons = get_ids("Person", "person_id")
    accounts = get_ids("BankAccount", "account_id")

    relationships = []

    available_accounts = accounts.copy()
    random.shuffle(available_accounts)

    for person in persons:

        if not available_accounts:
            break

        count = random.randint(0, 3)

        for _ in range(count):

            if not available_accounts:
                break

            account = available_accounts.pop()

            relationships.append({
                "person": person,
                "account": account
            })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (p:Person {person_id: row.person})
        MATCH (a:BankAccount {account_id: row.account})

        MERGE (p)-[:OWNS_ACCOUNT]->(a)
        """, {
            "rows": relationships
        })

    print(f"OWNS_ACCOUNT relationships created: {len(relationships)}")

def create_visited_relationships():

    persons = get_ids("Person", "person_id")
    locations = get_ids("Location", "location_id")

    rows = []

    for person in persons:

        visits = random.sample(
            locations,
            random.randint(2, 6)
        )

        for location in visits:

            rows.append({
                "person": person,
                "location": location
            })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (p:Person {person_id:row.person})
        MATCH (l:Location {location_id:row.location})

        MERGE (p)-[:VISITED]->(l)
        """, {
            "rows": rows
        })

    print(f"VISITED relationships created: {len(rows)}")

def create_case_relationships():

    persons = get_ids("Person", "person_id")
    cases = get_ids("Case", "case_id")

    rows = []

    for person in persons:

        if random.random() < 0.30:

            case = random.choice(cases)

            rows.append({
                "person": person,
                "case": case
            })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (p:Person {person_id:row.person})
        MATCH (c:Case {case_id:row.case})

        MERGE (p)-[:INVOLVED_IN]->(c)
        """, {
            "rows": rows
        })

    print(f"INVOLVED_IN relationships created: {len(rows)}")

def create_transferred_to_relationships():

    accounts = get_ids("BankAccount", "account_id")

    created = 0

    with driver.session() as session:

        for account in accounts:

            receivers = random.sample(
                accounts,
                random.randint(1, 4)
            )

            for receiver in receivers:

                if account == receiver:
                    continue

                session.run("""
                    MATCH (a:BankAccount {account_id:$a})
                    MATCH (b:BankAccount {account_id:$b})

                    MERGE (a)-[:TRANSFERRED_TO {
                        amount: toInteger(rand()*90000)+1000,
                        currency:"INR"
                    }]->(b)
                """, {
                    "a": account,
                    "b": receiver
                })

                created += 1

    print("TRANSFERRED_TO relationships created:", created)

def create_called_relationships():

    phones = get_ids("Phone", "phone_id")

    rows = []

    for phone in phones:

        others = random.sample(
            phones,
            random.randint(2, 5)
        )

        for other in others:

            if phone == other:
                continue

            rows.append({
                "a": phone,
                "b": other
            })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (a:Phone {phone_id:row.a})
        MATCH (b:Phone {phone_id:row.b})

        MERGE (a)-[:CALLED]->(b)
        """, {"rows": rows})

    print("CALLED:", len(rows))

def create_associated_with():

    persons = get_ids("Person", "person_id")

    rows = []

    for person in persons:

        partners = random.sample(
            persons,
            random.randint(1,4)
        )

        for p in partners:

            if p != person:

                rows.append({
                    "a": person,
                    "b": p
                })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (a:Person {person_id:row.a})
        MATCH (b:Person {person_id:row.b})

        MERGE (a)-[:ASSOCIATED_WITH]->(b)
        """, {"rows": rows})

    print("ASSOCIATED_WITH:", len(rows))

def create_lives_at():

    persons = get_ids("Person","person_id")
    locations = get_ids("Location","location_id")

    rows=[]

    for p in persons:

        rows.append({
            "person":p,
            "location":random.choice(locations)
        })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (p:Person {person_id:row.person})
        MATCH (l:Location {location_id:row.location})

        MERGE (p)-[:LIVES_AT]->(l)
        """,{"rows":rows})

    print("LIVES_AT:",len(rows))

def create_works_at():

    persons=get_ids("Person","person_id")
    entities=get_ids("Entity","entity_id")

    rows=[]

    for p in persons:

        if random.random()<0.7:

            rows.append({
                "person":p,
                "entity":random.choice(entities)
            })

    with driver.session() as session:

        session.run("""

        UNWIND $rows AS row

        MATCH (p:Person {person_id:row.person})
        MATCH (e:Entity {entity_id:row.entity})

        MERGE (p)-[:WORKS_AT]->(e)

        """,{"rows":rows})

    print("WORKS_AT:",len(rows))

def create_registered_at():

    vehicles=get_ids("Vehicle","vehicle_id")
    locations=get_ids("Location","location_id")

    rows=[]

    for v in vehicles:

        rows.append({
            "vehicle":v,
            "location":random.choice(locations)
        })

    with driver.session() as session:

        session.run("""

        UNWIND $rows AS row

        MATCH (v:Vehicle {vehicle_id:row.vehicle})
        MATCH (l:Location {location_id:row.location})

        MERGE (v)-[:REGISTERED_AT]->(l)

        """,{"rows":rows})

    print("REGISTERED_AT:",len(rows))

def create_owns_entity():

    persons=get_ids("Person","person_id")
    entities=get_ids("Entity","entity_id")

    rows=[]

    for e in entities:

        rows.append({
            "person":random.choice(persons),
            "entity":e
        })

    with driver.session() as session:

        session.run("""

        UNWIND $rows AS row

        MATCH (p:Person {person_id:row.person})
        MATCH (e:Entity {entity_id:row.entity})

        MERGE (p)-[:OWNS_ENTITY]->(e)

        """,{"rows":rows})

    print("OWNS_ENTITY:",len(rows))

def create_located_at():

    entities=get_ids("Entity","entity_id")
    locations=get_ids("Location","location_id")

    rows=[]

    for e in entities:

        rows.append({
            "entity":e,
            "location":random.choice(locations)
        })

    with driver.session() as session:

        session.run("""

        UNWIND $rows AS row

        MATCH (e:Entity {entity_id:row.entity})
        MATCH (l:Location {location_id:row.location})

        MERGE (e)-[:LOCATED_AT]->(l)

        """,{"rows":rows})

    print("LOCATED_AT:",len(rows))

def create_linked_accounts():

    accounts=get_ids("BankAccount","account_id")

    rows=[]

    for acc in accounts:

        others=random.sample(accounts,2)

        for o in others:

            if acc!=o:

                rows.append({
                    "a":acc,
                    "b":o
                })

    with driver.session() as session:

        session.run("""

        UNWIND $rows AS row

        MATCH (a:BankAccount {account_id:row.a})
        MATCH (b:BankAccount {account_id:row.b})

        MERGE (a)-[:LINKED_TO]->(b)

        """,{"rows":rows})

    print("LINKED_TO:",len(rows))

def create_associated_with_relationships():

    persons = get_ids("Person", "person_id")
    rows = []

    for person in persons:

        associates = random.sample(
            persons,
            random.randint(2, 5)
        )

        for associate in associates:

            if person != associate:
                rows.append({
                    "a": person,
                    "b": associate
                })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (a:Person {person_id:row.a})
        MATCH (b:Person {person_id:row.b})

        MERGE (a)-[:ASSOCIATED_WITH]->(b)
        """, {"rows": rows})

    print("ASSOCIATED_WITH:", len(rows))

def create_called_relationships():

    phones = get_ids("Phone", "phone_id")
    rows = []

    for phone in phones:

        others = random.sample(
            phones,
            random.randint(2, 6)
        )

        for other in others:

            if phone != other:
                rows.append({
                    "a": phone,
                    "b": other
                })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (a:Phone {phone_id:row.a})
        MATCH (b:Phone {phone_id:row.b})

        MERGE (a)-[:CALLED]->(b)
        """, {"rows": rows})

    print("CALLED:", len(rows))

def create_lives_at_relationships():

    persons = get_ids("Person", "person_id")
    locations = get_ids("Location", "location_id")

    rows = []

    for person in persons:

        rows.append({
            "person": person,
            "location": random.choice(locations)
        })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (p:Person {person_id:row.person})
        MATCH (l:Location {location_id:row.location})

        MERGE (p)-[:LIVES_AT]->(l)
        """, {"rows": rows})

    print("LIVES_AT:", len(rows))

def create_registered_at_relationships():

    phones = get_ids("Phone", "phone_id")
    locations = get_ids("Location", "location_id")

    rows = []

    for phone in phones:

        rows.append({
            "phone": phone,
            "location": random.choice(locations)
        })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (p:Phone {phone_id:row.phone})
        MATCH (l:Location {location_id:row.location})

        MERGE (p)-[:REGISTERED_AT]->(l)
        """, {"rows": rows})

    print("REGISTERED_AT:", len(rows))

def create_works_with_relationships():

    persons = get_ids("Person", "person_id")

    rows = []

    for person in persons:

        partners = random.sample(
            persons,
            random.randint(1, 4)
        )

        for partner in partners:

            if partner != person:
                rows.append({
                    "a": person,
                    "b": partner
                })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (a:Person {person_id:row.a})
        MATCH (b:Person {person_id:row.b})

        MERGE (a)-[:WORKS_WITH]->(b)
        """, {"rows": rows})

    print("WORKS_WITH:", len(rows))

def create_money_transfer_relationships():

    accounts = get_ids("BankAccount", "account_id")

    rows = []

    for account in accounts:

        receivers = random.sample(
            accounts,
            random.randint(1, 4)
        )

        for receiver in receivers:

            if account != receiver:

                rows.append({
                    "from": account,
                    "to": receiver,
                    "amount": random.randint(500,50000)
                })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (a:BankAccount {account_id:row.from})
        MATCH (b:BankAccount {account_id:row.to})

        MERGE (a)-[:MONEY_TRANSFER {amount:row.amount}]->(b)
        """, {"rows": rows})

    print("MONEY_TRANSFER:", len(rows))

def create_located_in_relationships():

    vehicles = get_ids("Vehicle", "vehicle_id")
    locations = get_ids("Location", "location_id")

    rows = []

    for vehicle in vehicles:

        rows.append({
            "vehicle": vehicle,
            "location": random.choice(locations)
        })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (v:Vehicle {vehicle_id:row.vehicle})
        MATCH (l:Location {location_id:row.location})

        MERGE (v)-[:LOCATED_IN]->(l)
        """, {"rows": rows})

    print("LOCATED_IN:", len(rows))

def create_linked_case_relationships():

    cases = get_ids("Case", "case_id")

    rows = []

    for case in cases:

        if random.random() < 0.6:

            other = random.choice(cases)

            if case != other:

                rows.append({
                    "a": case,
                    "b": other
                })

    with driver.session() as session:

        session.run("""
        UNWIND $rows AS row

        MATCH (a:Case {case_id:row.a})
        MATCH (b:Case {case_id:row.b})

        MERGE (a)-[:LINKED_TO]->(b)
        """, {"rows": rows})

    print("LINKED_TO:", len(rows))

def main():
    # create_knows_relationships()   # Already created

    create_uses_phone_relationships()
    create_visited_relationships()
    create_owns_account_relationships()
    create_owns_vehicle_relationships()
    create_case_relationships()
    create_knows_relationships()
    create_involved_in_relationships()
    create_transferred_to_relationships()
    create_called_relationships()
    create_associated_with_relationships()
    create_lives_at()
    create_works_at()
    create_registered_at()
    create_owns_entity()
    create_located_at()
    create_linked_accounts()
    create_called_relationships()
    create_lives_at_relationships()
    create_registered_at_relationships()
    create_works_with_relationships()
    create_money_transfer_relationships()
    create_located_in_relationships()
    create_linked_case_relationships()


    driver.close()


if __name__ == "__main__":
    main()