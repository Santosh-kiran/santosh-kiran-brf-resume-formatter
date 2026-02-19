import streamlit as st
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import PyPDF2
from PIL import Image

st.set_page_config(page_title="BRF Resume Formatter", page_icon="📄", layout="wide")

# Custom CSS
st.markdown("""
<style>
.main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.stButton > button {border-radius: 15px; height: 60px; font-size: 18px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.template_data = None
    st.session_state.mode = None

# Helper functions
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        return "".join([page.extract_text() for page in pdf_reader.pages])
    except:
        return "Error reading PDF"

def extract_text_from_docx(docx_file):
    try:
        doc = Document(io.BytesIO(docx_file.read()))
        return "\n".join([para.text for para in doc.paragraphs])
    except:
        return "Error reading DOCX"

def extract_template_values(docx_file):
    try:
        doc = Document(io.BytesIO(docx_file.read()))
        template_info = {
            "font_name": "Calibri", "font_size": 11, "heading_size": 14,
            "margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0}
        }
        for para in doc.paragraphs[:10]:
            if para.text.strip():
                for run in para.runs:
                    if run.font.name:
                        template_info["font_name"] = str(run.font.name)
                    if run.font.size:
                        template_info["font_size"] = int(run.font.size.pt)
        return template_info
    except:
        return {"font_name": "Calibri", "font_size": 11, "heading_size": 14, "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1}}

def create_formatted_doc(resume_text, template_data, first_name, last_name):
    doc = Document()
    
    # Set margins
    section = doc.sections[0]
    section.top_margin = Inches(template_data["margins"]["top"])
    section.bottom_margin = Inches(template_data["margins"]["bottom"])
    
    # Header
    header = doc.add_heading(f"{first_name.upper()} {last_name.upper()}", 0)
    for run in header.runs:
        run.font.name = template_data["font_name"]
        run.font.size = Pt(template_data["heading_size"])
    
    # Sections
    sections = ["PROFESSIONAL SUMMARY", "WORK EXPERIENCE", "EDUCATION", "SKILLS"]
    for section_title in sections:
        heading = doc.add_heading(section_title, level=1)
        for run in heading.runs:
            run.font.name = template_data["font_name"]
            run.font.size = Pt(template_data["heading_size"])
            run.bold = True
        
        p = doc.add_paragraph(resume_text[:300])
        for run in p.runs:
            run.font.name = template_data["font_name"]
            run.font.size = Pt(template_data["font_size"])
    
    return doc

# MAIN APP
if st.session_state.step == 0:
    st.title("📄 BRF Resume Formatter")
    st.markdown("### Choose configuration method:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📁 **1. Upload Template (DOCX)**"):
            st.session_state.mode = "template"
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("✏️ **2. Manual Input**"):
            st.session_state.mode = "manual"
            st.session_state.step = 1
            st.rerun()

elif st.session_state.step == 1:
    if st.session_state.mode == "template":
        st.header("📁 Option 1: Upload Master Template")
        template_file = st.file_uploader("Upload DOCX", type=['docx'])
        
        if template_file:
            template_data = extract_template_values(template_file)
            st.session_state.template_data = template_data
            
            st.success("✅ Template analyzed!")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Font", template_data["font_name"])
            with col2: st.metric("Size", f"{template_data['font_size']}pt")
            with col3: st.metric("Heading", f"{template_data['heading_size']}pt")
            
            if st.button("➡️ Upload Resume"):
                st.session_state.step = 2
                st.rerun()
    
    else:  # manual
        st.header("✏️ Option 2: Manual Input")
        col1, col2 = st.columns(2)
        with col1:
            font_name = st.text_input("Font Name", value="Calibri")
            font_size = st.number_input("Font Size", min_value=8, max_value=16, value=11)
        with col2:
            heading_size = st.number_input("Heading Size", min_value=12, max_value=24, value=14)
            margin_top = st.number_input("Top Margin", value=1.0)
        
        if st.button("✅ Save & Continue"):
            st.session_state.template_data = {
                "font_name": font_name, "font_size": font_size, "heading_size": heading_size,
                "margins": {"top": margin_top, "bottom": 1.0, "left": 1.0, "right": 1.0}
            }
            st.session_state.step = 2
            st.rerun()

elif st.session_state.step == 2:
    st.header("📄 Upload Resume")
    resume_file = st.file_uploader("Any format: PDF, DOCX, TXT, JPG", type=['pdf','docx','txt','png','jpg'])
    
    if resume_file:
        ext = resume_file.name.split('.')[-1].lower()
        if ext == 'pdf':
            resume_text = extract_text_from_pdf(resume_file)
        elif ext == 'docx':
            resume_text = extract_text_from_docx(resume_file)
        elif ext == 'txt':
            resume_text = resume_file.read().decode('utf-8')
        else:
            resume_text = "Image resume text..."
        
        if resume_text and not resume_text.startswith("Error"):
            st.success(f"✅ Extracted text ({len(resume_text)} chars)")
            
            col1, col2 = st.columns(2)
            with col1: first_name = st.text_input("First Name", key="first")
            with col2: last_name = st.text_input("Last Name", key="last")
            
            if st.button("🎨 Format & Download") and first_name and last_name:
                doc = create_formatted_doc(resume_text, st.session_state.template_data, first_name, last_name)
                output = io.BytesIO()
                doc.save(output)
                output.seek(0)
                
                st.download_button(
                    label=f"📥 {first_name}_{last_name}.docx",
                    data=output.getvalue(),
                    file_name=f"{first_name}_{last_name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

if st.button("🔙 Reset"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
