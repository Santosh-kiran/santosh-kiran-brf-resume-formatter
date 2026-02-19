import streamlit as st
from docx import Document
from docx.shared import Pt
import docx2txt
import PyPDF2
from io import BytesIO
import re

st.set_page_config(page_title="BRF Resume Formatter", page_icon="📄")
st.title("BRFv1.0 Resume Formatter (No API Version)")

# ---------------- EXTRACT TEXT ----------------
def extract_text(uploaded_file):
    try:
        if uploaded_file.name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text

        elif uploaded_file.name.endswith(".docx"):
            return docx2txt.process(uploaded_file)

        elif uploaded_file.name.endswith(".txt"):
            return uploaded_file.read().decode("utf-8")

        else:
            return ""
    except:
        return ""

# ---------------- REMOVE BULLETS ----------------
def remove_bullets(text):
    cleaned_lines = []
    for line in text.split("\n"):
        line = re.sub(r"^[\-\•\●\▪\*]+\s*", "", line.strip())
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

# ---------------- GET CANDIDATE NAME ----------------
def get_candidate_name(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if len(lines) > 0:
        words = lines[0].split()
        if len(words) >= 2:
            return words[0] + " " + words[1]
    return "Formatted Resume"

# ---------------- GENERATE DOCX ----------------
def generate_docx(content):
    doc = Document()
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(10)

    for line in content.split("\n"):
        doc.add_paragraph(line)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ---------------- UI ----------------
uploaded_file = st.file_uploader(
    "Upload Resume (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:
    st.info("Processing resume...")

    resume_text = extract_text(uploaded_file)

    if not resume_text.strip():
        st.error("Could not extract text from file.")
        st.stop()

    # Remove bullets (BRF rule)
    formatted_text = remove_bullets(resume_text)

    candidate_name = get_candidate_name(formatted_text)
    doc_file = generate_docx(formatted_text)

    st.success("Resume Processed Successfully!")

    st.download_button(
        label="Download Formatted Resume",
        data=doc_file,
        file_name=f"{candidate_name}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
