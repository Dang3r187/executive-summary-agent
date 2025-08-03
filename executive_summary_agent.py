import streamlit as st
from openai import OpenAI
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image

# Initialize OpenAI client using Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="نموذج عرض لسعادة الرئيس التنفيذي", layout="centered")
st.title("📄 نموذج عرض لسعادة الرئيس التنفيذي")

uploaded_file = st.file_uploader("ارفع ملف PDF أو صورة", type=["pdf", "jpg", "jpeg", "png"])

def extract_text_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except:
        return ""

def extract_text_with_ocr(file):
    try:
        images = convert_from_bytes(file.read())
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img, lang="ara+eng") + "\n"
        return text.strip()
    except Exception as e:
        return f"OCR failed: {e}"

def generate_summary(text, language="arabic"):
    if language == "arabic":
        prompt = f"يرجى تقديم ملخص تنفيذي احترافي للنص التالي:\n\n{text}\n\nالملخص:"
    else:
        prompt = f"Please provide a professional executive summary for the following text:\n\n{text}\n\nSummary:"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

if uploaded_file:
    with st.spinner("جارٍ قراءة الملف..."):
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        text = extract_text_from_pdf(uploaded_file)

        if not text:
            st.warning("لم يتم العثور على نص قابل للقراءة. سيتم استخدام OCR...")
            uploaded_file.seek(0)
            text = extract_text_with_ocr(uploaded_file)

        if not text or text.startswith("OCR failed"):
            st.error("تعذر استخراج النص من الملف. يرجى رفع نسخة أوضح.")
        else:
            with st.spinner("جارٍ توليد الملخص التنفيذي..."):
                summary = generate_summary(text)
                st.subheader("✍️ الملخص التنفيذي:")
                st.write(summary)
