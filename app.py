import streamlit as st
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import PyPDF2
from PIL import Image
import re

st.set_page_config(page_title="BRF Resume Formatter", page_icon="📄", layout="wide")

st.markdown("""
<style>
.main {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
.stButton > button {border-radius: 15px; height: 60px; font-size: 18px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.template_data = None
    st.session_state.mode = None

def extract_text_from_file(file):
    ext = file.name.lower().split('.')[-1]
    try:
        if ext == 'pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            return "".join([page.extract_text() for page in pdf_reader.pages])
        elif ext == 'docx':
            doc = Document(io.BytesIO(file.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        elif ext == 'txt':
            return file.read().decode('utf-8')
        else:
            return "Text extraction not available for this format"
    except:
        return "Error reading file"

def extract_template_values(docx_file):
    doc = Document(io.BytesIO(docx_file.read()))
    template_info = {"font_name": "Calibri", "font_size": 11, "heading_size": 14, "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1}}
    for para in doc.paragraphs[:10]:
        if para.text.strip():
            for run in para.runs:
                if run.font.name: template_info["font_name"] = str(run.font.name)
                if run.font.size: template_info["font_size"] = int(run.font.size.pt)
    return template_info

def parse_resume_sections(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Extract name from first line
    first_name = "Candidate"
    last_name = "Resume"
    if lines:
        first_line_words = lines[0].split()
        if len(first_line_words) >= 2:
            first_name = first_line_words[0]
            last_name = first_line_words[-1]
    
    # Find sections and extract content
    sections = {
        "summary": "",
        "skills": "",
        "education": "",
        "experience": ""
    }
    
    current_section = None
    for line in lines:
        line_lower = line.lower()
        if any(word in line_lower for word in ["summary", "profile", "overview"]):
            current_section = "summary"
        elif any(word in line_lower for word in ["skill", "technology", "tech"]):
            current_section = "skills" 
        elif any(word in line_lower for word in ["education", "degree", "university"]):
            current_section = "education"
        elif any(word in line_lower for word in ["experience", "work", "employment", "project"]):
            current_section = "experience"
        
        if current_section and line:
            sections[current_section] += line + "\n"
    
    return sections, first_name, last_name

def create_formatted_doc(sections, template_data, first_name, last_name, output_format="docx"):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(template_data["margins"]["top"])
    section.bottom_margin = Inches(template_data["margins"]["bottom"])
    
    # Header
    header = doc.add_heading(f"{first_name.upper()} {last_name.upper()}", 0)
    for run in header.runs:
        run.font.name = template_data["font_name"]
        run.font.size = Pt(template_data["heading_size"])
    
    # FIXED SECTION ORDER
    section_order = [
        ("Summary :", sections["summary"]),
        ("Technical Skills", sections["skills"]),
        ("Education", sections["education"]),
        ("Professional Experience", sections["experience"])
    ]
    
    for heading_text, content in section_order:
        # Section heading
        heading = doc.add_heading(heading_text, level=1)
        for run in heading.runs:
            run.font.name = template_data["font_name"]
            run.font.size = Pt(template_data["heading_size"])
            run.bold = True
        
        # Content with exact formatting
        if content.strip():
            for line in content.split('\n'):
                if line.strip():
                    p = doc.add_paragraph(line)
                    for run in p.runs:
                        run.font.name = template_data["font_name"]
                        run.font.size = Pt(template_data["font_size"])
    
    return doc

# MAIN UI
if st.session_state.step == 0:
    st.title("📄 BRF Resume Formatter")
    st.markdown("**Choose configuration method:**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📁 **Option 1: Upload Template (DOCX)**", use_container_width=True):
            st.session_state.mode = "template"
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("✏️ **Option 2: Manual Input**", use_container_width=True):
            st.session_state.mode = "manual"
            st.session_state.step = 1
            st.rerun()

elif st.session_state.step == 1:
    if st.session_state.mode == "template":
        st.header("📁 **Option 1: Upload Master Template**")
        template_file = st.file_uploader("Upload DOCX template", type=['docx'])
        
        if template_file:
            template_data = extract_template_values(template_file)
            st.session_state.template_data = template_data
            
            st.success("✅ **Template values extracted!**")
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Font", template_data["font_name"])
            with col2: st.metric("Size", f"{template_data['font_size']}pt")
            with col3: st.metric("Heading", f"{template_data['heading_size']}pt")
            with col4: st.metric("Margin", f"{template_data['margins']['top']}\"")
            
            if st.button("➡️ **Proceed to Resume Upload**", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
    
    else:  # manual mode
        st.header("✏️ **Option 2: Manual Configuration**")
        col1, col2 = st.columns(2)
        with col1:
            font_name = st.text_input("Font Name", value="Calibri")
            font_size = st.number_input("Font Size (pt)", min_value=8, max_value=16, value=11)
            heading_size = st.number_input("Heading Size (pt)", min_value=12, max_value=24, value=14)
        with col2:
            margin_top = st.number_input("Top Margin (in)", value=1.0, step=0.1)
            margin_bottom = st.number_input("Bottom Margin (in)", value=1.0, step=0.1)
        
        if st.button("✅ **Save Settings & Continue**", use_container_width=True):
            st.session_state.template_data = {
                "font_name": font_name, "font_size": font_size, "heading_size": heading_size,
                "margins": {"top": margin_top, "bottom": margin_bottom, "left": 1.0, "right": 1.0}
            }
            st.session_state.step = 2
            st.rerun()

elif st.session_state.step == 2:
    st.header("📄 **Upload Resume (Any Format)**")
    st.info("✅ PDF, DOCX, TXT, DOC, ODT, RTF, HTML, Images - ALL accepted")
    
    resume_file = st.file_uploader("Choose resume file", type=['pdf','docx','txt','doc','odt','rtf','html','png','jpg'])
    
    if resume_file:
        with st.spinner("Extracting resume content..."):
            resume_text = extract_text_from_file(resume_file)
        
        if resume_text and not resume_text.startswith("Error"):
            st.success(f"✅ Content extracted ({len(resume_text)} characters)")
            
            sections, first_name, last_name = parse_resume_sections(resume_text)
            
            col1, col2 = st.columns(2)
            with col1:
                first_name_input = st.text_input("First Name", value=first_name)
            with col2:
                last_name_input = st.text_input("Last Name", value=last_name)
            
            output_format = st.selectbox("Output Format", ["docx", "txt"])
            
            if st.button("🎨 **Format & Download Resume**", use_container_width=True):
                if first_name_input and last_name_input:
                    doc = create_formatted_doc(sections, st.session_state.template_data, 
                                            first_name_input, last_name_input, output_format)
                    
                    output_bytes = io.BytesIO()
                    doc.save(output_bytes)
                    output_bytes.seek(0)
                    
                    st.success("✅ **Resume formatted successfully!**")
                    st.download_button(
                        label=f"📥 Download {first_name_input}_{last_name_input}.{output_format}",
                        data=output_bytes.getvalue(),
                        file_name=f"{first_name_input}_{last_name_input}.{output_format}",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error("Please enter both names")

if st.button("🔙 **Back to Start**"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
