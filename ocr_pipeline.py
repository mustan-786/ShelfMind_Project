import cv2
import pytesseract
import re
import os
from rapidfuzz import process

# Set Tesseract path if on Windows (default location)
if os.name == 'nt' and os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

MASTER_CATALOG = [
    "Fortune Sunlite Sunflower Oil 1L",
    "Everest Garam Masala 100g",
    "Tata Salt Vacuum Evaporated 1kg",
    "Parle-G Gold Biscuits 1kg",
    "Aashirvaad Superior MP Atta 10kg",
    "Surf Excel Quick Wash Detergent 1kg",
    "Maggi 2-Minute Instant Noodles 280g"
]


def preprocess_and_ocr(image_bytes):
    """Processes uploaded image bytes and extracts text"""
    import numpy as np
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Run OCR
    raw_text = pytesseract.image_to_string(processed)
    return raw_text


def parse_items(raw_text):
    """Parses text into item lines with fuzzy matching"""
    extracted = []
    lines = raw_text.split('\n')
    for line in lines:
        match = re.search(r'([A-Za-z0-9\s\.\-]+)\s+(\d+)\s*(pcs|pkts|kg|box)?\s+([0-9]+\.?[0-9]*)', line)
        if match:
            raw_name = match.group(1).strip()
            qty = int(match.group(2))
            price = float(match.group(4))

            best_match, score, _ = process.extractOne(raw_name, MASTER_CATALOG)
            final_name = best_match if score > 50 else raw_name

            extracted.append({
                "Item Name": final_name,
                "Quantity": qty,
                "Rate (₹)": price,
                "Match Confidence": f"{round(score)}%"
            })
    return extracted