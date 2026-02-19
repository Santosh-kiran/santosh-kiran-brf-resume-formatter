import streamlit as st
from docx import Document
from docx.shared import Pt
import openai
import os
import docx2txt
import PyPDF2
import re
from io import BytesIO

# ----------------- CONFIG -----------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

BRF_PROMPT = """PASTE YOUR COMPLETE BRFv1.0 MASTER PROMPT HERE EXACTLY"""

# ----------------- FUNCTIONS -----------------

def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif uploaded_file.name.endswith(".docx"):
        return docx2txt.process(uploaded_file)
    else:
        return uploaded_file.read().decode("utf-8")

def get_candidate_name(text):
    first_line = text.strip().split("\n")[0]
    words = first_line.strip().split()
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
        p = doc.add_paragraph(line)

    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ----------------- UI -----------------

st.title("BRFv1.0 Resume Formatter")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

if uploaded_file:
    st.info("Processing... Please wait.")

    resume_text = extract_text(uploaded_file)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": BRF_PROMPT},
            {"role": "user", "content": resume_text}
        ]
    )

    formatted_text = response['choices'][0]['message']['content']

    candidate_name = get_candidate_name(formatted_text)

    doc_file = generate_docx(formatted_text)

    st.success("Formatting Complete!")

    st.download_button(
        label="Download Formatted Resume",
        data=doc_file,
        file_name=f"{candidate_name}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
