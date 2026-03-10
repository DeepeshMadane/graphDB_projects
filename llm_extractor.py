import requests
import json


def generate_gemini_api(prompt, text):

    url = "your_api"

    data = {
        "prompt": prompt,
        "ocr_text": text
    }

    try:
        res = requests.post(url, json=data, timeout=60)
        return res.json()

    except Exception as e:
        print("Gemini API error:", e)
        return {}


def clean_text(text):

    lines = text.split("\n")
    cleaned = []

    for line in lines:

        line = line.strip()

        if len(line) < 2:
            continue

        cleaned.append(line)

    # remove duplicates
    cleaned = list(dict.fromkeys(cleaned))

    return "\n".join(cleaned)


def safe_json_parse(text):

    try:
        return json.loads(text)

    except:
        pass

    start = text.find("{")
    end = text.rfind("}") + 1

    if start != -1 and end != -1:

        try:
            return json.loads(text[start:end])
        except:
            pass

    return {"raw_output": text}

def extract_entities(text):

    text = clean_text(text)
    text = text[:4000]

    prompt = """
    
You are a medical document information extractor.

Extract structured information from the document.

Return ONLY valid JSON.

Fields:
patient_name
aadhaar_number
doctor_name
hospital
diagnosis
medicines
bill_amount
date

If value missing return null.
"""

    response = generate_gemini_api(prompt, text)

    if not response:
        return {}

    # handle different response types
    if isinstance(response, dict):

        content = (
            response.get("text")
            or response.get("response")
            or response.get("generated_text")
            or ""
        )

    else:
        # response is already string
        content = response

    return safe_json_parse(content)
