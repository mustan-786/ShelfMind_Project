import cv2
import pytesseract
import re
import os
import numpy as np
from rapidfuzz import process

# Windows local Tesseract path setup
if os.name == 'nt' and os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Master SKU list for fuzzy matching
MASTER_CATALOG = [
    "Fortune Sunlite Sunflower Oil 1L",
    "Everest Garam Masala 100g",
    "Tata Salt Vacuum Evaporated 1kg",
    "Parle-G Gold Biscuits 1kg",
    "Aashirvaad Superior MP Atta 10kg",
    "Surf Excel Quick Wash Detergent 1kg",
    "Maggi 2-Minute Instant Noodles 280g",
    "Dettol Original Soap 75g",
    "Colgate Strong Teeth Toothpaste 100g",
    "Red Label Tea 250g",
    "Gemini Sunflower Oil 1L"
]


def preprocess_and_ocr(image_bytes):
    """
    Optimized pre-processing for pink/yellow Indian wholesale invoices.
    Uses OTSU Binarization + Morphological Cleaning.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 1. Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Increase contrast to suppress pink/yellow background color
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(gray)

    # 3. OTSU Thresholding (automatically finds optimum threshold between ink and paper)
    _, binary = cv2.threshold(contrast_enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 4. Tesseract OCR with Page Segmentation Mode 6 (Assumes a single uniform block of text/table)
    custom_config = r'--oem 3 --psm 6'
    raw_text = pytesseract.image_to_string(binary, config=custom_config)

    return raw_text


def parse_items(raw_text):
    """
    Flexible line-by-line parser for wholesale invoices.
    Extracts text tokens and isolates quantity & price.
    """
    extracted = []
    lines = raw_text.split('\n')

    # Stop words / Header words to ignore
    ignore_headers = ["invoice", "bill", "tax", "description", "particulars", "amount", "rate", "qty", "hsn", "gst",
                      "total", "subtotal", "date", "s.no", "sr"]

    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line or len(cleaned_line) < 4:
            continue

        lower_line = cleaned_line.lower()
        if any(lower_line.startswith(h) for h in ignore_headers):
            continue

        # Find all numbers (integers or decimals) in the row
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', cleaned_line)

        # Extract text description by stripping out pure digits
        text_part = re.sub(r'[\d\.,\/\-\|]+', ' ', cleaned_line).strip()

        if len(text_part) > 2 and len(numbers) >= 1:
            raw_name = text_part

            # Typical column ordering in bills: [Qty, Rate, Amount] or [HSN, Qty, Rate, Amount]
            if len(numbers) == 1:
                qty = int(float(numbers[0]))
                price = 0.0
            elif len(numbers) >= 2:
                qty = int(float(numbers[-2])) if float(numbers[-2]) < 1000 else 1
                price = float(numbers[-1])

            # Fuzzy match raw extracted product string against store master catalog
            best_match, score, _ = process.extractOne(raw_name, MASTER_CATALOG)
            final_name = best_match if score >= 45 else raw_name

            extracted.append({
                "Item Name": final_name,
                "Quantity": qty,
                "Rate (₹)": price,
                "Match Confidence": f"{round(score)}%"
            })

    return extracted