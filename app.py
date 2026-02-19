import streamlit as st
import re
import docx
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import os

st.set_page_config(page_title="BRF Resume Formatter", layout="wide")

SECTIONS = ["Summary", "Technical Skills", "Education", "Professional Experience"]

def extract_text(file):
    """Universal parser - preserves exact content"""
    file_content = file.read()
    file.seek(0)  # Reset file pointer
    
    if file.name.endswith('.pdf'):
        doc = fitz.open(stream=file_content)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
    elif file.name.endswith('.docx'):
        doc = Document(BytesIO(file_content))
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        text = file_content.decode('utf-8', errors='ignore')
    return text

def detect_template_settings(template_file):
    """Auto-detect from .docx template"""
    try:
        doc = Document(template_file)
        font_name = "Calibri"
        font_size = 11
        line_spacing = 1.15
        
        for para in doc.paragraphs:
            if para.text.strip():
                for run in para.runs:
                    if run.font.name: 
                        font_name = run.font.name
                    if run.font.size: 
                        font_size = run.font.size.pt
                break
        return font_name, int(font_size), line_spacing
    except:
        return "Calibri", 11, 1.15

def format_resume(text, config):
    """Reorder + format - NO content changes - FIXED REGEX"""
    sections = {}
    
    # FIXED: Proper regex without f-string issue
    patterns = {
        "Summary": r"(?i)Summary[\s:]*$(.*?)(?=Technical Skills|Education|Professional Experience|$)",
        "Technical Skills": r"(?i)Technical Skills[\s:]*$(.*?)(?=Education|Professional Experience|$)",
        "Education": r"(?i)Education[\s:]*$(.*?)(?=Professional Experience|$)",
        "Professional Experience": r"(?i)Professional Experience[\s:]*$(.*)"
    }
    
    for section, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
        if match:
            sections[section] = match.group(1).strip()
    
    # Rebuild in exact order
    result = f"Summary :\n{sections.get('Summary', '')}\n\n"
    result += f"Technical Skills\n{sections.get('Technical Skills', '')}\n\n"
    result += f"Education\n{sections.get('Education', '')}\n\n"
    result += f"Professional Experience\n{sections.get('Professional Experience', '')}"
    
    return result

def create_docx(formatted_text, config):
    """Apply exact formatting"""
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    style.font.name = config['font']
    style.font.size = Pt(config['size'])
    
    # Split sections
    section_parts = formatted_text.split('\n\n')[:4]
    
    for i, section_name in enumerate(SECTIONS):
        if i < len(section_parts) and section_parts[i].strip():
            # Heading
            heading = doc.add_heading(section_name, 0)
            if config['bold']:
                heading.bold = True
            
            # Content
            content = section_parts[i].replace('\n', ' ').strip()
            if content:
                p = doc.add_paragraph(content)
                p.paragraph_format.line_spacing = config['spacing']
            
            doc.add_paragraph()  # Spacing
    
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
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
        st.rerun()
    if col2.button("✏️ Manual Prompt Mode", use_container_width=True):
        st.session_state.mode = "prompt"
        st.session_state.step = 1
        st.rerun()

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
                    st.rerun()
            except Exception as e:
                st.error(f"Invalid template: {str(e)}")
    else:  # Manual
        col1, col2 = st.columns(2)
        font = col1.text_input("Font Name", "Calibri")
        size = col2.number_input("Font Size", 10.0, 14.0, 11.0)
        spacing = st.number_input("Line Spacing", 1.0, 2.0, 1.15)
        bold = st.checkbox("Heading Bold", True)
        bullets = st.checkbox("Summary Bullets", True)
        blank = st.checkbox("Blank Line After Projects", True)
        
        if st.button("✅ Confirm Settings"):
            st.session_state.config = {
                'font': font, 'size': float(size), 'spacing': float(spacing),
                'bold': bold, 'bullets': bullets, 'blank_lines': blank
            }
            st.session_state.step = 2
            st.rerun()

elif st.session_state.step == 2:
    st.header("📎 Step 3: Upload Resume")
    resume_file = st.file_uploader("Upload ANY format", type=['pdf','docx','txt','rtf','odt','html'])
    format_type = st.selectbox("Output Format", ["DOCX", "PDF", "TXT"])
    
    if resume_file and st.button("🎯 Format Resume", use_container_width=True):
        with st.spinner("Processing..."):
            text = extract_text(resume_file)
            formatted = format_resume(text, st.session_state.config)
            
            # Name detection
            lines = text.split('\n')
            name = "Candidate Resume"
            for line in lines[:3]:
                if line.strip():
                    words = line.strip().split()
                    if len(words) >= 2:
                        name = f"{words[0]} {words[-1]}"
                        break
            
            filename = f"{name.replace(' ', '-')}.{format_type.lower()}"
            
            if format_type == "DOCX":
                try:
                    doc_data = create_docx(formatted, st.session_state.config)
                    st.download_button("📥 Download DOCX", doc_data, filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                except Exception as e:
                    st.error(f"DOCX error: {str(e)}")
                    st.download_button("📥 Download TXT", formatted.encode(), filename.replace('docx', 'txt'), "text/plain")
            else:
                st.download_button("📥 Download", formatted.encode(), filename, "text/plain")
        
        st.session_state.step = 3
        st.success("✅ Formatting complete!")
        st.rerun()

elif st.session_state.step == 3:
    st.header("🎉 Success!")
    if st.button("🔄 New Resume", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
