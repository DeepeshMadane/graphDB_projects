from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "deepesh123"))


def write_patient(tx, data):

    patient = data.get("patient_name")
    doctor = data.get("doctor_name")
    hospital = data.get("hospital")

    # Skip if patient missing
    if not patient:
        print("Skipping record — patient name missing:", data)
        return

    # fallback values
    doctor = doctor if doctor else "Unknown Doctor"
    hospital = hospital if hospital else "Unknown Hospital"

    tx.run(
        """
        MERGE (p:Patient {name:$patient})
        MERGE (d:Doctor {name:$doctor})
        MERGE (h:Hospital {name:$hospital})
        MERGE (d)-[:WORKS_AT]->(h)
        MERGE (p)-[:TREATED_BY]->(d)
        """,
        patient=patient,
        doctor=doctor,
        hospital=hospital
    )


def insert_data(data):

    with driver.session() as session:
        session.execute_write(write_patient, data)