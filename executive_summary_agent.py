import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import tempfile
import os
import docx
import openai

# Set your OpenAI API key from Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="نموذج عرض لسعادة الرئيس التنفيذي", layout="centered")

st.title("📝 نموذج عرض لسعادة الرئيس التنفيذي")
st.markdown("ارفع ملفات PDF، Word، أو صور، وسيقوم الوكيل بإنشاء عرض مختصر رسمي.")

uploaded_files = st.file_uploader("ارفع ملفاتك هنا", type=["pdf", "docx", "png", "jpg", "jpeg"], accept_multiple_files=True)

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image, lang='ara')

def generate_arabic_summary(text_input):
    prompt = f"""
    النص التالي يحتوي على معلومات من وثائق متعددة. 
    استخرج أهم النقاط وقم بصياغة نموذج عرض رسمي موجه إلى سعادة الرئيس التنفيذي، مع مراعاة اللغة الرسمية والنقاط التنفيذية الواضحة:

    النص:
    {text_input}

    نموذج العرض:
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "أنت مساعد محترف تكتب باللغة العربية نموذج عرض رسمي."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

if uploaded_files:
    combined_text = ""
    for file in uploaded_files:
        filetype = file.name.split('.')[-1].lower()
        try:
            if filetype == "pdf":
                combined_text += extract_text_from_pdf(file) + "\n"
            elif filetype == "docx":
                combined_text += extract_text_from_docx(file) + "\n"
            elif filetype in ["jpg", "jpeg", "png"]:
                combined_text += extract_text_from_image(file) + "\n"
            else:
                st.warning(f"صيغة غير مدعومة: {file.name}")
        except Exception as e:
            st.error(f"فشل في معالجة {file.name}: {e}")

    if combined_text.strip():
        with st.spinner("يتم توليد نموذج العرض..."):
            summary = generate_arabic_summary(combined_text)
            st.subheader("📄 نموذج العرض الناتج")
            st.text_area("النص النهائي", summary, height=400)
    else:
        st.warning("لم يتم العثور على نص يمكن معالجته.")
