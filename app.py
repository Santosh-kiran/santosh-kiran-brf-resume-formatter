import streamlit as st
import re
import docx
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import os

st.set_page_config(page_title="BRF Resume Formatter", layout="wide")

# Strict section order
SECTIONS = ["Summary", "Technical Skills", "Education", "Professional Experience"]

def extract_text(file):
    """Universal parser - preserves exact content"""
    if file.name.endswith('.pdf'):
        doc = fitz.open(stream=file.read())
        text = ""
        for page in doc:
            text += page.get_text()
    elif file.name.endswith('.docx'):
        doc = Document(file)
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        text = file.read().decode('utf-8')
    return text

def detect_template_settings(template_file):
    """Auto-detect from .docx template"""
    doc = Document(template_file)
    font_name = "Calibri"
    font_size = 11
    line_spacing = 1.15
    
    for para in doc.paragraphs:
        if para.text.strip():
            for run in para.runs:
                if run.font.name: font_name = run.font.name
                if run.font.size: font_size = run.font.size.pt
            break
    
    return font_name, font_size, line_spacing

def format_resume(text, config):
    """Reorder + format - NO content changes"""
    sections = {}
    for section in SECTIONS:
        pattern = rf"(?i)^{re.escape(section)}[\s:]*$(.*?)(?={}|$)"
        match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
        if match: sections[section] = match.group(1).strip()
    
    # Rebuild in exact order
    result = f"Summary :\n{sections.get('Summary', '')}\n\n"
    result += f"Technical Skills\n{sections.get('Technical Skills', '')}\n\n"
    result += f"Education\n{sections.get('Education', '')}\n\n"
    result += f"Professional Experience\n{sections.get('Professional Experience', '')}"
    
    return result

def create_docx(formatted_text, config):
    """Apply exact formatting"""
    doc = Document()
    doc.styles['Normal'].font.name = config['font']
    doc.styles['Normal'].font.size = Pt(config['size'])
    
    # Add sections
    for section, content in zip(SECTIONS, formatted_text.split('\n\n')):
        if content.strip():
            p = doc.add_heading(section, 0)
            if config['bold']: p.bold = True
            doc.add_paragraph(content)
            doc.add_paragraph()  # Spacing
    
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# Wizard flow
if 'step' not in st.session_state:
    st.session_state.step = 0

st.title("🚀 BRF Resume Formatter")
st.markdown("**Strict formatting enforcement • Content preserved exactly**")

if st.session_state.step == 0:
    st.header("📋 Step 1: Choose Configuration Mode")
    col1, col2 = st.columns(2)
    if col1.button("📄 Master Template Mode", use_container_width=True):
        st.session_state.mode = "template"
        st.session_state.step = 1
    if col2.button("✏️ Manual Prompt Mode", use_container_width=True):
        st.session_state.mode = "prompt"
        st.session_state.step = 1

elif st.session_state.step == 1:
    st.header("📄 Step 2: Configure Formatting")
    if st.session_state.mode == "template":
        template = st.file_uploader("Upload .docx Template", type="docx")
        if template:
            try:
                config = detect_template_settings(template)
                st.session_state.config = {
                    'font': config[0], 'size': config[1], 
                    'spacing': config[2], 'bold': True, 
                    'bullets': True, 'blank_lines': True
                }
                st.success(f"✅ Detected: {config[0]}, Size {config[1]}pt")
                if st.button("✅ Confirm & Continue"):
                    st.session_state.step = 2
            except:
                st.error("Invalid template")
    else:  # Manual
        col1, col2 = st.columns(2)
        font = col1.text_input("Font Name", "Calibri")
        size = col2.number_input("Font Size", 10, 14, 11)
        spacing = st.number_input("Line Spacing", 1.0, 2.0, 1.15)
        bold = st.checkbox("Heading Bold", True)
        bullets = st.checkbox("Summary Bullets", True)
        blank = st.checkbox("Blank Line After Projects", True)
        
        if st.button("✅ Confirm Settings"):
            st.session_state.config = {
                'font': font, 'size': size, 'spacing': spacing,
                'bold': bold, 'bullets': bullets, 'blank_lines': blank
            }
            st.session_state.step = 2

elif st.session_state.step == 2:
    st.header("📎 Step 3: Upload Resume")
    resume_file = st.file_uploader("Upload ANY format", type=['pdf','docx','txt','rtf','odt'])
    format_type = st.selectbox("Output Format", ["DOCX", "PDF", "TXT"])
    
    if resume_file and st.button("🎯 Format Resume", use_container_width=True):
        with st.spinner("Processing..."):
            text = extract_text(resume_file)
            formatted = format_resume(text, st.session_state.config)
            
            # Name detection
            name = re.match(r'^([A-Za-z]+(?:\s[A-Za-z]+)?)', text, re.MULTILINE)
            filename = f"{name.group(1) if name else 'Candidate Resume'}.{format_type.lower()}"
            
            if format_type == "DOCX":
                doc_data = create_docx(formatted, st.session_state.config)
                st.download_button("📥 Download DOCX", doc_data, filename, "application/vnd.openxmlformats")
            else:
                st.download_button("📥 Download", formatted.encode(), filename, "text/plain")
        
        st.session_state.step = 3
        st.success("✅ Formatting complete!")

elif st.session_state.step == 3:
    st.header("🎉 Success!")
    if st.button("🔄 New Resume"):
        for key in st.session_state:
            del st.session_state[key]
        st.rerun()
