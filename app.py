import streamlit as st
import pandas as pd
from translations import TRANSLATIONS
from ocr_pipeline import extract_invoice_data_with_ai

st.set_page_config(
    page_title="SHELF MIND Mobile",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Language Selector
lang_choice = st.selectbox(
    "🌐 Select Language / भाषा निवडा / भाषा चुनें",
    ["English", "मराठी (Marathi)", "हिंदी (Hindi)"],
    index=0
)

lang_key = "en"
if "Marathi" in lang_choice:
    lang_key = "mr"
elif "Hindi" in lang_choice:
    lang_key = "hi"

t = TRANSLATIONS[lang_key]

st.title(f"📱 {t['app_title']}")
st.caption(f"{t['app_subtitle']}")

kpi1, kpi2 = st.columns(2)
kpi1.metric(t["total_skus"], "142")
kpi2.metric(t["working_capital"], "₹1,42,800")
st.metric(t["dead_stock"], "₹14,200", delta="-₹2,500 Clearance", delta_color="inverse")

st.divider()

tab1, tab2, tab3 = st.tabs([t["tab_upload"], t["tab_stock"], t["tab_alerts"]])

with tab1:
    st.subheader(t["upload_heading"])

    input_mode = st.radio("Capture Method:", ["📸 Open Phone Camera", "📁 Upload from Gallery"], horizontal=True)

    image_file = None
    if input_mode == "📸 Open Phone Camera":
        image_file = st.camera_input("Take a clear photo of the wholesale bill")
    else:
        image_file = st.file_uploader(t["upload_btn"], type=["jpg", "png", "jpeg"])

    if image_file is not None:
        st.info("⚡ Vision AI is analyzing invoice layout, columns, and items...")

        items = extract_invoice_data_with_ai(image_file.getvalue())

        if items and len(items) > 0:
            st.success("✅ Items successfully parsed from invoice!")
            st.write("### 📋 Extracted Bill Items:")
            st.dataframe(pd.DataFrame(items), use_container_width=True)

            if st.button(f"✅ {t['save_stock_btn']}", use_container_width=True):
                st.toast(t["stock_updated_toast"])
        else:
            st.error("Could not extract line items. Please ensure the bill table is clearly visible.")

with tab2:
    st.subheader(t["tab_stock"])
    stock_data = {
        "Product SKU": ["Fortune Sunlite Oil 1L", "Tata Salt 1kg", "Parle-G Gold 1kg", "Brand-X Detergent 1kg"],
        "Qty": [15, 40, 25, 18],
        "Velocity": ["Fast", "Normal", "Fast", "Stagnant"]
    }
    st.dataframe(pd.DataFrame(stock_data), use_container_width=True)

with tab3:
    st.subheader(t["tab_alerts"])
    st.warning(t["dead_stock_alert"])
    st.info(t["weather_alert"])