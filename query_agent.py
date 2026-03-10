from neo4j import GraphDatabase
import requests


# Neo4j connection
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "yourpass"))


def clean_cypher(query):
    """
    Clean LLM generated Cypher
    """

    if not query:
        return ""

    # remove markdown
    query = query.replace("```cypher", "")
    query = query.replace("```", "")

    # remove quotes
    query = query.replace('"', "")
    query = query.replace("'", "'")

    # remove escaped newlines
    query = query.replace("\\n", " ")

    # remove real newlines
    query = query.replace("\n", " ")

    # collapse multiple spaces
    query = " ".join(query.split())

    return query.strip()

def run_cypher(query):

    query = clean_cypher(query)

    print("\nClean Cypher:")
    print(query)

    with driver.session() as session:
        result = session.run(query)

        records = []
        for r in result:
            records.append(r.data())

        return records

def generate_cypher(question):

    url = "your_api"

    prompt = f"""
You are an expert in Neo4j Cypher.

Database schema:

Nodes:
Patient(name)
Doctor(name)
Hospital(name)

Relationships:
(:Patient)-[:TREATED_BY]->(:Doctor)
(:Doctor)-[:WORKS_AT]->(:Hospital)

Convert the following question into a Cypher query.

Question:
{question}

Return ONLY the Cypher query.
"""

    data = {
        "prompt": prompt,
        "ocr_text": question
    }

    res = requests.post(url, json=data)

    return res.text


while True:

    question = input("\nAsk a question: ")

    cypher_query = generate_cypher(question)

    print("\nGenerated Cypher:")
    print(cypher_query)

    result = run_cypher(cypher_query)

    print("\nResult:")
    print(result)