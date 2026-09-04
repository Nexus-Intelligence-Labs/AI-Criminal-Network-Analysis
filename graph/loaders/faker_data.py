from faker import Faker
import random
import uuid
from datetime import datetime, timedelta

fake = Faker()

# ---------------------------------------------------
# PERSON
# ---------------------------------------------------

def generate_person(person_id):
    return {
        "person_id": f"P{person_id:05}",
        "name": fake.name(),
        "age": random.randint(18, 70),
        "gender": random.choice(["Male", "Female"]),
        "city": fake.city(),
        "nationality": fake.country(),
        "risk_score": round(random.uniform(0, 100), 2)
    }


# ---------------------------------------------------
# LOCATION
# ---------------------------------------------------

def generate_location(location_id):
    return {
        "location_id": f"L{location_id:05}",
        "city": fake.city(),
        "state": fake.state(),
        "country": fake.country(),
        "address": fake.address().replace("\n", ", ")
    }


# ---------------------------------------------------
# PHONE
# ---------------------------------------------------

def generate_phone(phone_id):
    return {
        "phone_id": f"PH{phone_id:05}",
        "number": fake.phone_number(),
        "carrier": random.choice([
            "Jio",
            "Airtel",
            "Vi",
            "BSNL"
        ])
    }


# ---------------------------------------------------
# VEHICLE
# ---------------------------------------------------

def generate_vehicle(vehicle_id):
    return {
        "vehicle_id": f"V{vehicle_id:05}",
        "registration": fake.license_plate(),
        "manufacturer": random.choice([
            "Toyota",
            "Hyundai",
            "Honda",
            "Mahindra",
            "Tata",
            "Ford"
        ]),
        "color": random.choice([
            "White",
            "Black",
            "Blue",
            "Red",
            "Grey",
            "Silver"
        ])
    }


# ---------------------------------------------------
# BANK ACCOUNT
# ---------------------------------------------------

def generate_bank_account(account_id):
    return {
        "account_id": f"B{account_id:05}",
        "account_number": fake.bban(),
        "bank": random.choice([
            "SBI",
            "HDFC",
            "ICICI",
            "Axis",
            "Canara",
            "Punjab National Bank"
        ]),
        "balance": round(random.uniform(1000, 5000000), 2)
    }


# ---------------------------------------------------
# ORGANIZATION
# ---------------------------------------------------

def generate_organization(org_id):
    return {
        "organization_id": f"O{org_id:05}",
        "name": fake.company(),
        "industry": random.choice([
            "Logistics",
            "Construction",
            "Import",
            "Export",
            "Finance",
            "Retail"
        ])
    }


# ---------------------------------------------------
# CASE
# ---------------------------------------------------

def generate_case(case_id):
    return {
        "case_id": f"C{case_id:05}",
        "title": f"Operation {fake.word().title()}",
        "status": random.choice([
            "Open",
            "Closed",
            "Under Investigation"
        ])
    }


# ---------------------------------------------------
# WEAPON
# ---------------------------------------------------

def generate_weapon(weapon_id):
    return {
        "weapon_id": f"W{weapon_id:05}",
        "type": random.choice([
            "Pistol",
            "Knife",
            "Rifle",
            "SMG",
            "Shotgun"
        ]),
        "serial": str(uuid.uuid4())[:10]
    }


# ---------------------------------------------------
# DRUG
# ---------------------------------------------------

def generate_drug(drug_id):
    return {
        "drug_id": f"D{drug_id:05}",
        "name": random.choice([
            "Cocaine",
            "Heroin",
            "Methamphetamine",
            "Cannabis",
            "MDMA"
        ]),
        "quantity": random.randint(1, 500)
    }


# ---------------------------------------------------
# EVIDENCE
# ---------------------------------------------------

def generate_evidence(evidence_id):
    return {
        "evidence_id": f"E{evidence_id:05}",
        "type": random.choice([
            "Phone",
            "Laptop",
            "Weapon",
            "Cash",
            "Document",
            "Fingerprint"
        ]),
        "collected_on": (
            datetime.now() -
            timedelta(days=random.randint(1, 365))
        ).strftime("%Y-%m-%d")
    }