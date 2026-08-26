import json
import os
import streamlit as st
from google import genai
from google.genai import types

# 👇 PASTE YOUR KEY INSIDE THE QUOTES BELOW 👇
GEMINI_API_KEY = "PASTE_YOUR_COPIED_KEY_HERE"

# For Streamlit Cloud deployment (auto-reads from secrets if available):
if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)


def extract_invoice_data_with_ai(image_bytes):
    """
    Uses Multimodal Vision AI to parse complex, tilted,
    handwritten, or dot-matrix Indian Kirana invoices into clean JSON.
    """
    prompt = """
    You are an expert document parser for Indian Kirana grocery store wholesale bills.
    Analyze this invoice image and extract all purchased line items accurately.

    Even if the text is faint, dot-matrix, handwritten, or on colored/pink paper:
    1. Extract the Item Name (clean standard product name with brand and size/weight if visible).
    2. Extract the Quantity (integer).
    3. Extract the Unit Wholesale Rate in INR (float).
    4. Extract the Total Amount in INR (float).

    Return ONLY a valid JSON array of objects with these exact keys:
    [
      {
        "Item Name": "Product Name",
        "Quantity": 10,
        "Rate (₹)": 45.0,
        "Total (₹)": 450.0
      }
    ]
    Do not wrap the response in markdown quotes or extra conversational text. Return only the raw JSON.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                prompt
            ]
        )

        raw_output = response.text.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]

        data = json.loads(raw_output.strip())
        return data

    except Exception as e:
        print(f"Vision AI Parsing Error: {e}")
        return []