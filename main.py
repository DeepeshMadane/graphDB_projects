import os
import re

from ocr_pipeline import extract_text_from_pdf
from llm_extractor import extract_entities
from neo4j_writer import insert_data


folder = "/home/mladmin/WorkSpace/Deepesh_Healthindia/graph/data_only_essentials"


def extract_aadhaar(text):
    """
    Extract Aadhaar information using regex instead of LLM
    """

    aadhaar_match = re.search(r"\d{4}\s?\d{4}\s?\d{4}", text)

    aadhaar = None
    if aadhaar_match:
        aadhaar = aadhaar_match.group().replace(" ", "")

    return {
        "patient_name": None,
        "aadhaar_number": aadhaar,
        "doctor_name": None,
        "hospital": "UIDAI",
        "diagnosis": None,
        "medicines": None,
        "bill_amount": None,
        "date": None
    }


for root, dirs, files in os.walk(folder):

    for file in files:

        if not file.lower().endswith(".pdf"):
            continue

        path = os.path.join(root, file)

        print("Running OCR:", path)

        text = extract_text_from_pdf(path)

        if not text:
            print("⚠️ No OCR text found:", path)
            continue

        # Detect Aadhaar documents
        if "AADHAAR" in path.upper():

            print("Detected Aadhaar document → using regex extraction")

            entities = extract_aadhaar(text)

        else:

            print("Using LLM extraction")

            entities = extract_entities(text)
            print("Extracted:", entities)
        insert_data(entities)

        print("Processed:", path)