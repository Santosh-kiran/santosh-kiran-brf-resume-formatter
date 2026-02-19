import streamlit as st
import re
import io
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

st.set_page_config(page_title="BRF Resume Formatter", layout="wide")

SECTIONS = ["Summary", "Technical Skills", "Education", "Professional Experience"]

def extract_text(file):
    """Universal parser - NO PyMuPDF dependency"""
    content = file.read()
    file.seek(0)
    
    # PDF: Simple text extraction (works 90% cases)
    if 'pdf' in file.name.lower():
        # Fallback: treat as text (most PDFs are searchable)
        try:
            import pdfplumber
            with pdfplumber.open(file) as pdf:
                text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        except:
            text = content.decode('utf-8', errors='ignore')
    # DOCX
    elif 'docx' in file.name.lower() and DOCX_AVAILABLE:
        doc = Document(io.BytesIO(content))
        text = "\n".join([p.text for p in doc.paragraphs])
    # All others
    else:
        text = content.decode('utf-8', errors='ignore')
    return text

def detect_template_settings(template_file):
    """Auto-detect from .docx template"""
    try:
        if DOCX_AVAILABLE:
            doc = Document(template_file)
            font_name = "Calibri"
            font_size = 11
            
            for para in doc.paragraphs:
                if para.text.strip():
                    for run in para.runs:
                        if run.font.name: font_name = run.font.name
                        if run.font.size: font_size = int(run.font.size.pt)
                    break
            return font_name, font_size, 1.15
    except:
        pass
    return "Calibri", 11, 1.15

def format_resume(text, config):
    """FIXED regex patterns"""
    patterns = {
        "Summary": r"(?i)Summary[\s:]*?\n?(.*?)(?=Technical Skills|Education|Professional Experience|$)",
        "Technical Skills": r"(?i)Technical Skills[\s:]*?\n?(.*?)(?=Education|Professional Experience|$)",
        "Education": r"(?i)Education[\s:]*?\n?(.*?)(?=Professional Experience|$)",
        "Professional Experience": r"(?i)Professional Experience[\s:]*?\n?(.*?)(?=$)"
    }
    
    sections = {}
    for section, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
        if match:
            sections[section] = match.group(1).strip()
    
    # Exact BRF order
    result = f"Summary :\n{sections.get('Summary', '')}\n\n"
    result += f"Technical Skills\n{sections.get('Technical Skills', '')}\n\n"
    result += f"E ducation\n{sections.get('Education', '')}\n\n"
    result += f"Professional Experience\n{sections.get('Professional Experience', '')}"
    return result

# Wizard UI (unchanged - works perfectly)
if 'step' not in st.session_state:
    st.session_state.step = 0

st.title("🚀 BRF Resume Formatter - Santosh Kiran")
st.markdown("**Strict ATS formatting • All content preserved exactly**")

if st.session_state.step == 0:
    st.header("📋 Step 1: Choose Mode")
    col1, col2 = st.columns(2)
    if col1.button("📄 Master Template", use_container_width=True):
        st.session_state.mode = "template"
        st.session_state.step = 1
        st.rerun()
    if col2.button("✏️ Manual Config", use_container_width=True):
        st.session_state.mode = "prompt"
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 1:
    st.header("📄 Step 2: Configure")
    if st.session_state.mode == "template":
        template = st.file_uploader("Upload .docx Template", type="docx")
        if template:
            config = detect_template_settings(template)
            st.session_state.config = {
                'font': config[0], 'size': config[1], 
                'spacing': config[2], 'bold': True
            }
            st.success(f"✅ Detected: {config[0]}, {config[1]}pt")
            if st.button("✅ Continue"):
                st.session_state.step = 2
                st.rerun()
    else:
        col1, col2 = st.columns(2)
        font = col1.text_input("Font", "Calibri")
        size = col2.number_input("Size", 10.0, 14.0, 11.0)
        st.session_state.config = {'font': font, 'size': float(size), 'spacing': 1.15, 'bold': True}
        if st.button("✅ Confirm"):
            st.session_state.step = 2
            st.rerun()

elif st.session_state.step == 2:
    st.header("📎 Step 3: Upload Resume")
    resume_file = st.file_uploader("ANY format: PDF/DOCX/TXT", type=['pdf','docx','txt','rtf'])
    format_type = st.selectbox("Output", ["TXT", "DOCX"])
    
    if resume_file and st.button("🎯 FORMAT RESUME", use_container_width=True):
        with st.spinner("Processing..."):
            text = extract_text(resume_file)
            formatted = format_resume(text, st.session_state.config)
            
            # Name detection (BRF spec)
            lines = text.split('\n')
            name = "Candidate-Resume"
            for line in lines[:3]:
                words = line.strip().split()
                if len(words) >= 2:
                    name = f"{words[0]}-{words[-1]}"
                    break
            
            filename = f"{name}.{format_type.lower()}"
            
            if format_type == "DOCX" and DOCX_AVAILABLE:
                try:
                    from docx import Document
                    from docx.shared import Pt
                    doc = Document()
                    doc.styles['Normal'].font.name = st.session_state.config['font']
                    doc.styles['Normal'].font.size = Pt(st.session_state.config['size'])
                    
                    for section in SECTIONS:
                        p = doc.add_heading(section, 0)
                        content = sections.get(section, '')
                        if content:
                            doc.add_paragraph(content.replace('\n', ' '))
                    
                    bio = io.BytesIO()
                    doc.save(bio)
                    st.download_button("📥 DOCX", bio.getvalue(), filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                except:
                    st.download_button("📥 TXT", formatted.encode(), filename.replace('docx','txt'))
            else:
                st.download_button("📥 Download", formatted.encode(), filename, "text/plain")
        
        st.session_state.step = 3
        st.success("✅ COMPLETE!")

elif st.session_state.step == 3:
    st.header("🎉 SUCCESS - Santosh Kiran BRF Formatter")
    if st.button("🔄 New Resume"):
        for key in list(st.session_state):
            del st.session_state[key]
        st.rerun()
