import streamlit as st
from openai import OpenAI
from docx import Document
from docx.shared import Pt
import docx2txt
import PyPDF2
from io import BytesIO

# ---------------------- UI ----------------------
st.title("BRFv1.0 Resume Formatter")

# ---------------------- CHECK SECRET ----------------------
if "OPENAI_API_KEY" not in st.secrets:
    st.error("OPENAI_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------- BRF PROMPT ----------------------
BRF_PROMPT = """
PASTE YOUR COMPLETE BRFv1.0 MASTER PROMPT HERE EXACTLY
"""

# ---------------------- FUNCTIONS ----------------------

def extract_text(uploaded_file):
    try:
        if uploaded_file.name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text

        elif uploaded_file.name.endswith(".docx"):
            return docx2txt.process(uploaded_file)

        else:
            return uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error extracting file: {e}")
        return ""

def get_candidate_name(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if len(lines) > 0:
        words = lines[0].split()
        if len(words) >= 2:
            return words[0] + " " + words[1]
    return "Formatted Resume"

def generate_docx(content):
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(10)

    for line in content.split("\n"):
        doc.add_paragraph(line)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ---------------------- FILE UPLOAD ----------------------

uploaded_file = st.file_uploader(
    "Upload Resume (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:

    st.info("Processing resume...")

    resume_text = extract_text(uploaded_file)

    if resume_text.strip() == "":
        st.error("Could not extract text from file.")
        st.stop()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": BRF_PROMPT},
                {"role": "user", "content": resume_text}
            ]
        )

        formatted_text = response.choices[0].message.content

    except Exception as e:
        st.error(f"OpenAI Error: {e}")
        st.stop()

    candidate_name = get_candidate_name(formatted_text)
    doc_file = generate_docx(formatted_text)

    st.success("Formatting Completed Successfully!")

    st.download_button(
        label="Download Formatted Resume",
        data=doc_file,
        file_name=f"{candidate_name}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
