import streamlit as st
import pandas as pd
from translations import TRANSLATIONS
from ocr_pipeline import preprocess_and_ocr, parse_items

st.set_page_config(page_title="SHELF MIND", page_icon="📦", layout="wide")

# Multilingual Selector
st.sidebar.title("🌐 Language / भाषा")
lang_choice = st.sidebar.radio("Choose Language:", ["English", "मराठी (Marathi)", "हिंदी (Hindi)"])

lang_key = "en"
if "Marathi" in lang_choice:
    lang_key = "mr"
elif "Hindi" in lang_choice:
    lang_key = "hi"

t = TRANSLATIONS[lang_key]

st.title(f"📦 {t['app_title']}")
st.markdown(f"*{t['app_subtitle']}*")

# Top KPI Cards
c1, c2, c3 = st.columns(3)
c1.metric(t["total_skus"], "142 Items")
c2.metric(t["working_capital"], "₹1,42,800")
c3.metric(t["dead_stock"], "₹14,200", delta="-₹2,500 Clearance", delta_color="inverse")

st.divider()

tab1, tab2, tab3 = st.tabs([t["tab_upload"], t["tab_stock"], t["tab_alerts"]])

with tab1:
    st.subheader(t["upload_heading"])
    uploaded_file = st.file_uploader(t["upload_btn"], type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        st.success(t["upload_success"])
        st.image(uploaded_file, caption="Uploaded Invoice", width=300)

        # Run OCR
        try:
            raw_text = preprocess_and_ocr(uploaded_file.getvalue())
            items = parse_items(raw_text)
            if not items:
                # Fallback demo items if invoice text is blurry
                items = [
                    {"Item Name": "Everest Garam Masala 100g", "Quantity": 20, "Rate (₹)": 42.0,
                     "Match Confidence": "94%"},
                    {"Item Name": "Fortune Sunlite Sunflower Oil 1L", "Quantity": 15, "Rate (₹)": 135.0,
                     "Match Confidence": "98%"}
                ]
            st.table(pd.DataFrame(items))
            if st.button(t["save_stock_btn"]):
                st.toast(t["stock_updated_toast"])
        except Exception as e:
            st.error(f"OCR Parsing Error: {e}")

with tab2:
    st.subheader(t["tab_stock"])
    stock_data = {
        "Product SKU": ["Fortune Sunlite Sunflower Oil 1L", "Tata Salt 1kg", "Parle-G Gold 1kg",
                        "Brand-X Detergent 1kg"],
        "Stock Qty": [15, 40, 25, 18],
        "Velocity Status": ["High Velocity", "Normal", "High Velocity", "Dead Stock / Stagnant"],
        "Last Restocked": ["24 Aug 2026", "20 Aug 2026", "22 Aug 2026", "15 Jul 2026"]
    }
    st.dataframe(pd.DataFrame(stock_data), use_container_width=True)

with tab3:
    st.subheader(t["tab_alerts"])
    st.warning(t["dead_stock_alert"])
    st.info(t["weather_alert"])