import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np
import cv2
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
from pdf2image import convert_from_path


# Initialize OCR
ocr = PaddleOCR(
    lang="en",
    use_angle_cls=False,
    show_log=False,
    det_limit_side_len=640
)


def preprocess_image(img):
    """
    Basic preprocessing to improve OCR stability
    """

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h, w = img.shape
    max_size = 1500

    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    return img


# -------------------------
# FAST PDF TEXT EXTRACTION
# -------------------------

def extract_pdf_fast(pdf_path):
    """
    Try extracting text directly from PDF (very fast)
    """

    try:
        doc = fitz.open(pdf_path)
        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        return text.strip()

    except Exception as e:
        print("Fast PDF extraction failed:", pdf_path, "|", e)
        return ""


# -------------------------
# OCR IMAGE
# -------------------------

def extract_text_from_image(image_path):

    try:
        img = cv2.imread(image_path)

        if img is None:
            return ""

        img = preprocess_image(img)

        result = ocr.ocr(img)

        text = []

        if result and result[0]:
            for line in result[0]:
                text.append(line[1][0])

        return "\n".join(text)

    except Exception as e:
        print("OCR failed for image:", image_path, "| Error:", e)
        return ""


# -------------------------
# OCR PDF
# -------------------------

def extract_text_from_pdf(pdf_path):

    # Step 1: try fast text extraction
    fast_text = extract_pdf_fast(pdf_path)

    if fast_text and len(fast_text) > 50:
        print("Fast PDF text extraction used")
        return fast_text

    print("No embedded text → running OCR")

    full_text = []

    try:
        images = convert_from_path(pdf_path, dpi=120)

        for img in images:

            img_np = np.array(img)
            img_np = preprocess_image(img_np)

            result = ocr.ocr(img_np)

            if not result or not result[0]:
                continue

            for line in result[0]:
                full_text.append(line[1][0])

    except Exception as e:
        print("OCR failed for PDF:", pdf_path, "| Error:", e)

    return "\n".join(full_text)


# -------------------------
# STREAM FILE PROCESSING
# -------------------------

def process_folder(folder):

    for root, dirs, files in os.walk(folder):

        for file in files:

            path = os.path.join(root, file)

            print("Running OCR on:", path)

            if file.lower().endswith(".pdf"):
                text = extract_text_from_pdf(path)

            elif file.lower().endswith((".png", ".jpg", ".jpeg")):
                text = extract_text_from_image(path)

            else:
                print("Skipping unsupported file:", path)
                continue

            if not text or len(text.strip()) == 0:
                print("⚠️ OCR returned empty text for:", path)
                continue

            yield path, text