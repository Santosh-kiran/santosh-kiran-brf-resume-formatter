import streamlit as st
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import re
import PyPDF2

st.set_page_config(page_title="BRF Resume Formatter", page_icon="📄", layout="wide")

st.markdown("""
<style>
.main {background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);}
.stButton > button {border-radius: 20px; height: 70px; font-size: 20px; font-weight: bold;}
.stMetric {background: #4ecdc4; padding: 15px; border-radius: 15px;}
</style>
""", unsafe_allow_html=True)

if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.template_data = None
    st.session_state.mode = None

def extract_text_all_formats(file):
    """4.1 ALL FORMATS - NO REJECTION"""
    ext = file.name.lower().split('.')[-1]
    try:
        if ext == 'pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            return "".join([page.extract_text() for page in pdf_reader.pages])
        elif ext == 'docx':
            doc = Document(io.BytesIO(file.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        elif ext in ['txt', 'rtf', 'html', 'odt']:
            return file.read().decode('utf-8', errors='ignore')
        else:
            return file.read().decode('utf-8', errors='ignore')
    except:
        return file.read().decode('utf-8', errors='ignore')

def extract_template_values(docx_file):
    """OPTION 1 - AUTO DETECT"""
    try:
        doc = Document(io.BytesIO(docx_file.read()))
        template_info = {
            "font_name": "Calibri", "font_size": 11, "heading_size": 14,
            "bold_headings": True, "summary_bullets": True, "project_spacing": True,
            "line_spacing": 1.15, "margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0}
        }
        for para in doc.paragraphs[:15]:
            if para.text.strip():
                for run in para.runs:
                    if run.font.name: template_info["font_name"] = str(run.font.name)
                    if run.font.size: 
                        if run.bold: template_info["heading_size"] = int(run.font.size.pt)
                        else: template_info["font_size"] = int(run.font.size.pt)
        return template_info
    except:
        return template_info

def parse_resume_sections(text):
    """5.1 EXACT SECTION EXTRACTION & ORDERING"""
    # 8.1 NAME EXTRACTION - First non-empty line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    first_name, last_name = "Candidate", "Resume"
    if lines:
        first_line_words = lines[0].split()
        if len(first_line_words) >= 2:
            first_name = first_line_words[0]
            last_name = first_line_words[-1]
    
    # 5.1-5.5 SECTION DETECTION (preserve exact content)
    sections = {"summary": "", "skills": "", "education": "", "experience": ""}
    current_section = None
    
    for line in lines:
        line_lower = line.lower()
        
        # 5.1 SUMMARY
        if any(kw in line_lower for kw in ["summary", "profile", "overview"]):
            current_section = "summary"
        # 5.3 TECHNICAL SKILLS  
        elif any(kw in line_lower for kw in ["skill", "technical", "technology"]):
            current_section = "skills"
        # 5.4 EDUCATION
        elif any(kw in line_lower for kw in ["education", "degree", "university"]):
            current_section = "education"
        # 5.5 PROFESSIONAL EXPERIENCE
        elif any(kw in line_lower for kw in ["experience", "work", "employment", "project"]):
            current_section = "experience"
        
        if current_section:
            sections[current_section] += line + "\n"
    
    return sections, first_name, last_name

def create_formatted_doc(sections, template_data, first_name, last_name):
    """7. FORMATTING ENFORCEMENT + 5.1 FIXED ORDER"""
    doc = Document()
    
    # 7.1 MARGINS
    section = doc.sections[0]
    section.top_margin = Inches(template_data["margins"]["top"])
    section.bottom_margin = Inches(template_data["margins"]["bottom"])
    section.left_margin = Inches(template_data["margins"]["left"])
    section.right_margin = Inches(template_data["margins"]["right"])
    
    # 8.2 HEADER
    header = doc.add_heading(f"{first_name.upper()} {last_name.upper()}", 0)
    for run in header.runs:
        run.font.name = template_data["font_name"]
        run.font.size = Pt(template_data["heading_size"])
    
    # 5.1 FIXED SECTION ORDER
    section_order = [
        ("Summary :", sections["summary"]),
        ("Technical Skills", sections["skills"]),
        ("Education", sections["education"]),
        ("Professional Experience", sections["experience"])
    ]
    
    for heading_text, content in section_order:
        # 7.3 HEADING FORMATTING
        heading = doc.add_heading(heading_text, level=1)
        for run in heading.runs:
            run.font.name = template_data["font_name"]
            run.font.size = Pt(template_data["heading_size"])
            run.bold = template_data["bold_headings"]
        
        # 6. CONTENT EXACTLY PRESERVED
        if content.strip():
            for line in content.split('\n'):
                if line.strip():
                    p = doc.add_paragraph(line)
                    for run in p.runs:
                        run.font.name = template_data["font_name"]
                        run.font.size = Pt(template_data["font_size"])
                    p.paragraph_format.line_spacing = template_data["line_spacing"]
    
    return doc

# === MAIN WEB UI ===
if st.session_state.step == 0:
    st.markdown("""
    <div style='text-align: center; padding: 50px; color: white;'>
        <h1 style='font-size: 4em;'>📄 BRF Resume Formatter</h1>
        <p style='font-size: 1.8em;'>Professional formatting enforcement system</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("📁 **OPTION 1: Upload Template**", use_container_width=True):
            st.session_state.mode = "template"
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("✏️ **OPTION 2: Manual Input**", use_container_width=True):
            st.session_state.mode = "manual"
            st.session_state.step = 1
            st.rerun()

elif st.session_state.step == 1:
    # ✅ OPTION 1: AUTOMATIC TEMPLATE READING
    if st.session_state.mode == "template":
        st.header("📁 **Option 1: Upload DOCX Template**")
        template_file = st.file_uploader("Upload DOCX only", type=['docx'])
        
        if template_file:
            with st.spinner("Reading template values..."):
                template_data = extract_template_values(template_file)
                st.session_state.template_data = template_data
            
            st.success("✅ **Template values automatically detected!**")
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Font Name", template_data["font_name"])
            with col2: st.metric("Font Size", f"{template_data['font_size']}pt")
            with col3: st.metric("Heading Size", f"{template_data['heading_size']}pt")
            with col4: st.metric("Top Margin", f"{template_data['margins']['top']}\"")
            
            if st.button("➡️ **Proceed to Resume Upload**", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
    
    # ✅ OPTION 2: MANUAL INPUT FIELDS
    else:
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
                "bold_headings": True, "summary_bullets": True, "project_spacing": True,
                "line_spacing": 1.15, "margins": {"top": margin_top, "bottom": margin_bottom, "left": 1.0, "right": 1.0}
            }
            st.session_state.step = 2
            st.rerun()

elif st.session_state.step == 2:
    # ✅ RESUME UPLOAD - ALL FORMATS
    st.header("📄 **Upload Resume (Any Format)**")
    st.info("✅ PDF, DOCX, TXT, DOC, ODT, RTF, HTML - ALL accepted, NO size limits")
    
    resume_file = st.file_uploader("Choose resume file", type=['pdf','docx','txt','doc','odt','rtf','html'])
    
    if resume_file:
        with st.spinner("Extracting exact content..."):
            resume_text = extract_text_all_formats(resume_file)
        
        if resume_text:
            st.success(f"✅ **Content extracted** ({len(resume_text)} characters preserved exactly)")
            
            sections, first_name, last_name = parse_resume_sections(resume_text)
            
            col1, col2 = st.columns(2)
            with col1: first_name_input = st.text_input("First Name", value=first_name)
            with col2: last_name_input = st.text_input("Last Name", value=last_name)
            
            output_format = st.selectbox("Output Format", ["docx", "txt"])
            
            if st.button("🎨 **FORMAT & DOWNLOAD**", use_container_width=True):
                if first_name_input and last_name_input:
                    doc = create_formatted_doc(sections, st.session_state.template_data, 
                                            first_name_input, last_name_input)
                    
                    output_bytes = io.BytesIO()
                    doc.save(output_bytes)
                    output_bytes.seek(0)
                    
                    st.balloons()
                    st.success(f"✅ **{first_name_input}_{last_name_input}.{output_format}** ready!")
                    st.download_button(
                        label=f"📥 Download {first_name_input}_{last_name_input}.{output_format}",
                        data=output_bytes.getvalue(),
                        file_name=f"{first_name_input}_{last_name_input}.{output_format}",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error("Please enter both names")

if st.button("🔙 **BACK TO START**", type="secondary"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
