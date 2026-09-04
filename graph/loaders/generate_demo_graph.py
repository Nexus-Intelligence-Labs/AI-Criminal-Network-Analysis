from neo4j import GraphDatabase
from graph.loaders.faker_data import generate_person

# =====================================
# Neo4j Connection
# =====================================

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "change_me"   # <-- Replace with your Neo4j password

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)


# =====================================
# Utility Functions
# =====================================

def test_connection():
    """Test Neo4j connection."""
    with driver.session() as session:
        result = session.run(
            "RETURN 'Connected Successfully' AS message"
        )
        print(result.single()["message"])


def clear_database():
    """Delete all nodes and relationships."""
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("Database cleared.")


# =====================================
# Create Nodes
# =====================================

def create_case():
    """Create one investigation case."""
    with driver.session() as session:
        session.run("""
        CREATE (:Case {
            case_id:'CASE001',
            title:'Operation Falcon',
            status:'Open'
        })
        """)
        print("Case created.")


def create_people(count=100):
    """Create Person nodes."""

    with driver.session() as session:

        for i in range(1, count + 1):

            person = generate_person(i)

            session.run("""
            CREATE (:Person {
                person_id:$person_id,
                name:$name,
                age:$age,
                city:$city
            })
            """, **person)

    print(f"{count} persons created.")


# =====================================
# Main
# =====================================

if __name__ == "__main__":

    test_connection()

    clear_database()

    create_case()

    create_people(100)

    driver.close()

    print("\nDemo graph created successfully!")