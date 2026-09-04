import random
from neo4j import GraphDatabase

from graph.loaders.faker_data import (
    generate_person,
    generate_location,
    generate_phone,
    generate_vehicle,
    generate_bank_account,
    generate_organization,
    generate_case,
    generate_weapon,
    generate_drug,
    generate_evidence,
)

# ==========================================
# Neo4j Connection
# ==========================================

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "change_me"

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)


# ==========================================
# Configuration
# ==========================================

CONFIG = {
    "persons": 500,
    "locations": 100,
    "phones": 400,
    "vehicles": 200,
    "accounts": 300,
    "organizations": 50,
    "cases": 50,
    "weapons": 100,
    "drugs": 150,
    "evidence": 150,
}


# ==========================================
# Utility
# ==========================================

def run_query(query, parameters=None):
    with driver.session() as session:
        session.run(query, parameters or {})


def clear_database():
    print("Clearing database...")
    run_query("MATCH (n) DETACH DELETE n")
    print("Database cleared.")


def create_constraints():

    constraints = [

        "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.person_id IS UNIQUE",

        "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE",

        "CREATE CONSTRAINT phone_id IF NOT EXISTS FOR (p:Phone) REQUIRE p.phone_id IS UNIQUE",

        "CREATE CONSTRAINT vehicle_id IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.vehicle_id IS UNIQUE",

        "CREATE CONSTRAINT account_id IF NOT EXISTS FOR (b:BankAccount) REQUIRE b.account_id IS UNIQUE",

        "CREATE CONSTRAINT org_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.organization_id IS UNIQUE",

        "CREATE CONSTRAINT case_id IF NOT EXISTS FOR (c:Case) REQUIRE c.case_id IS UNIQUE",

        "CREATE CONSTRAINT weapon_id IF NOT EXISTS FOR (w:Weapon) REQUIRE w.weapon_id IS UNIQUE",

        "CREATE CONSTRAINT drug_id IF NOT EXISTS FOR (d:Drug) REQUIRE d.drug_id IS UNIQUE",

        "CREATE CONSTRAINT evidence_id IF NOT EXISTS FOR (e:Evidence) REQUIRE e.evidence_id IS UNIQUE",

    ]

    with driver.session() as session:
        for query in constraints:
            session.run(query)

    print("Constraints created.")

def insert_node(label, data):

    properties = ", ".join(
        [f"{key}: ${key}" for key in data.keys()]
    )

    query = f"""
    CREATE (n:{label} {{
        {properties}
    }})
    """

    run_query(query, data)

def generate_all_nodes():

    print("Generating Persons...")

    for i in range(CONFIG["persons"]):
        insert_node("Person", generate_person(i + 1))

    print("Generating Locations...")

    for i in range(CONFIG["locations"]):
        insert_node("Location", generate_location(i + 1))

    print("Generating Phones...")

    for i in range(CONFIG["phones"]):
        insert_node("Phone", generate_phone(i + 1))

    print("Generating Vehicles...")

    for i in range(CONFIG["vehicles"]):
        insert_node("Vehicle", generate_vehicle(i + 1))

    print("Generating Bank Accounts...")

    for i in range(CONFIG["accounts"]):
        insert_node("BankAccount", generate_bank_account(i + 1))

    print("Generating Organizations...")

    for i in range(CONFIG["organizations"]):
        insert_node("Organization", generate_organization(i + 1))

    print("Generating Cases...")

    for i in range(CONFIG["cases"]):
        insert_node("Case", generate_case(i + 1))

    print("Generating Weapons...")

    for i in range(CONFIG["weapons"]):
        insert_node("Weapon", generate_weapon(i + 1))

    print("Generating Drugs...")

    for i in range(CONFIG["drugs"]):
        insert_node("Drug", generate_drug(i + 1))

    print("Generating Evidence...")

    for i in range(CONFIG["evidence"]):
        insert_node("Evidence", generate_evidence(i + 1))

    print("All nodes created.")


# ==========================================
# MAIN
# ==========================================

def main():

    clear_database()

    create_constraints()

    generate_all_nodes()

    print("Finished.")


if __name__ == "__main__":

    main()

    driver.close()