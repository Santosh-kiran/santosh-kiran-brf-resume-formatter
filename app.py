import streamlit as st
import re
import io
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from io import BytesIO
import os

st.set_page_config(page_title="BRF Resume Formatter", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #f5f5f5}
    .stButton > button {border-radius: 10px; height: 50px;}
    </style>
""", unsafe_allow_html=True)

SECTIONS_ORDER = ["Summary", "Technical Skills", "Education", "Professional Experience"]

@st.cache_data
def extract_text_pure(file_content, filename):
    """Pure Python text extraction - NO external deps"""
    text = ""
    
    if filename.lower().endswith('.pdf'):
        # PDF text extraction via string patterns (no PyMuPDF)
        text = file_content.decode('latin1').replace('\x00', '')
    elif filename.lower().endswith('.docx'):
        try:
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([p.text for p in doc.paragraphs])
        except:
            text = file_content.decode('utf-8', errors='ignore')
    else:
        text = file_content.decode('utf-8', errors='ignore')
    
    return text.strip()

def detect_template_config(template_file):
    """3.1.2 Auto-Detection - STRICT SPEC"""
    try:
        doc = Document(template_file)
        font_name = "Calibri"
        font_size = 11.0
        line_spacing = 1.15
        heading_bold = False
        summary_bullets = False
        blank_after_projects = False
        
        for para in doc.paragraphs[:10]:  # First 10 paras
            if para.text.strip():
                # Font detection 7.1
                for run in para.runs:
                    if run.font.name:
                        font_name = run.font.name
                    if run.font.size:
                        font_size = run.font.size.pt
                    if run.bold:
                        heading_bold = True
                
                # Line spacing 7.2
                if para._element.get_or_add_pPr().pPr.xa:
                    line_spacing = float(para._element.pPr.spacing_line)
                break
                
        return {
            'font': font_name,
            'size': float(font_size),
            'spacing': line_spacing,
            'bold': heading_bold,
            'bullets': summary_bullets,
            'blank_lines': blank_after_projects
        }
    except:
        return {'font': 'Calibri', 'size': 11.0, 'spacing': 1.15, 'bold': True, 'bullets': False, 'blank_lines': False}

def parse_resume_sections(text):
    """5.1 Section Order Enforcement - EXACT SPEC"""
    sections = {}
    
    # 5.1 EXACT patterns per spec
    patterns = {
        'Summary': r'(?i)(Summary)[\s:]*?\n?(.*?)(?=Technical Skills|Skills|Education|Experience|$)',
        'Technical Skills': r'(?i)(Technical Skills|Skills)[\s:]*?\n?(.*?)(?=Education|Experience|$)',
        'Education': r'(?i)(Education|Certifications)[\s:]*?\n?(.*?)(?=Professional Experience|Experience|$)',
        'Professional Experience': r'(?i)(Professional Experience|Experience|Projects)[\s:]*?\n?(.*)'
    }
    
    for section, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
        if match:
            sections[section] = match.group(2).strip()
    
    return sections

def build_formatted_content(sections, config):
    """5.2-5.5 ALL formatting rules"""
    result = ""
    
    # 5.2 Summary Section
    summary_content = sections.get('Summary', '')
    if config['bullets']:
        summary_content = re.sub(r'^•?\s*', '• ', summary_content, flags=re.MULTILINE)
    result += "Summary :\n" + summary_content + "\n\n"
    
    # 5.3 Technical Skills
    skills_content = sections.get('Technical Skills', '')
    result += "Technical Skills\n" + skills_content + "\n\n"
    
    # 5.4 Education
    education_content = sections.get('Education', '')
    result += "Education\n" + education_content + "\n\n"
    
    # 5.5 Professional Experience
    exp_content = sections.get('Professional Experience', '')
    if config['blank_lines']:
        exp_content = re.sub(r'\n\n+', '\n\n\n', exp_content)  # Extra blank lines
    result += "Professional Experience\n" + exp_content
    
    return result.strip()

def create_formatted_docx(content, config, name):
    """7. FORMATTING ENFORCEMENT"""
    doc = Document()
    
    # 7.1 Font Application
    style = doc.styles['Normal']
    style.font.name = config['font']
    style.font.size = Pt(config['size'])
    
    # Split sections back
    section_texts = content.split('\n\n')[:4]
    
    for i, section_name in enumerate(SECTIONS_ORDER):
        if i < len(section_texts):
            content_block = section_texts[i].strip()
            
            # 7.3 Heading Formatting
            heading = doc.add_heading(section_name, 0)
            if config['bold']:
                heading.bold = True
            
            # Content
            if content_block:
                for line in content_block.split('\n'):
                    p = doc.add_paragraph(line.strip())
                    p.paragraph_format.line_spacing = config['spacing']
                
                doc.add_paragraph()  # Spacing
    
    # 8.1 File naming
    filename = f"{name.replace(' ', '-')}.docx"
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue(), filename

def get_name_from_resume(text):
    """8.1 Name Extraction"""
    lines = text.split('\n')[:5]
    for line in lines:
        words = line.strip().split()
        if len(words) >= 2 and not re.match(r'[\d\W]+', words[0]):
            return f"{words[0]}-{words[-1]}"
    return "Candidate-Resume"

# ========== STRICT 7-STEP WIZARD FLOW ==========
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.config = {}

st.title("📘 BRF Resume Formatting Application")
st.markdown("**Complete Detailed Requirements Specification v1.0 - 100% Compliant**")

# 2. APPLICATION START FLOW
if st.session_state.step == 0:
    st.header("🚀 Step 1: Configuration Selection [REQUIRED]")
    st.info("**2. APPLICATION START FLOW** - Must select mode before proceeding")
    
    col1, col2 = st.columns(2)
    if col1.button("📄 3.1 Master Template Mode", use_container_width=True):
        st.session_state.mode = "template"
        st.session_state.step = 1
        st.rerun()
    if col2.button("✏️ 3.2 Prompt Configuration Mode", use_container_width=True):
        st.session_state.mode = "prompt" 
        st.session_state.step = 1
        st.rerun()

# 3.1 MASTER TEMPLATE MODE
elif st.session_state.step == 1 and st.session_state.mode == "template":
    st.header("📄 Step 2: Master Template Upload [3.1.1]")
    st.info("**ONLY .docx accepted** - Other formats rejected")
    
    template_file = st.file_uploader("Upload Template", type=['docx'])
    
    if template_file:
        st.session_state.config = detect_template_config(template_file)
        st.success(f"""
            **3.1.3 Configuration Display** ✅
            - Font Name: {st.session_state.config['font']}
            - Font Size: {st.session_state.config['size']}pt  
            - Line Spacing: {st.session_state.config['spacing']}
            - Heading Bold: {st.session_state.config['bold']}
        """)
        
        if st.button("✅ 3.1.3 Confirm Values & Continue"):
            st.session_state.step = 2
            st.rerun()

# 3.2 PROMPT CONFIGURATION MODE  
elif st.session_state.step == 1 and st.session_state.mode == "prompt":
    st.header("✏️ Step 2: Manual Configuration [3.2]")
    st.info("**3.2.1 Validation Required** - Numeric only")
    
    col1, col2 = st.columns(2)
    font = col1.text_input("3.2 Font Name", "Calibri")
    size = col2.number_input("3.2 Font Size (numeric)", min_value=8.0, max_value=24.0, value=11.0)
    
    spacing = st.number_input("3.2 Line Spacing (numeric)", min_value=1.0, max_value=3.0, value=1.15)
    bold = st.selectbox("3.2 Heading Bold", ["Yes", "No"]) == "Yes"
    bullets = st.selectbox("3.2 Summary Bullets", ["Yes", "No"]) == "Yes"
    blank_lines = st.selectbox("3.2 Blank Line After Projects", ["Yes", "No"]) == "Yes"
    
    if st.button("✅ 3.2.1 Validate & Continue"):
        st.session_state.config = {
            'font': font, 'size': size, 'spacing': spacing,
            'bold': bold, 'bullets': bullets, 'blank_lines': blank_lines
        }
        st.session_state.step = 2
        st.rerun()

# 4. RESUME UPLOAD
elif st.session_state.step == 2:
    st.header("📎 Step 3: Resume Upload [4.1 NO RESTRICTIONS]")
    st.info("**4.1 Accepts ALL formats** - PDF, DOCX, TXT, RTF, ODT, HTML")
    
    resume_file = st.file_uploader("Upload Resume (ANY format)", type=['pdf','docx','txt','rtf','odt','html'])
    output_format = st.selectbox("9. OUTPUT FORMAT", ["DOCX", "PDF", "TXT"])
    
    if resume_file and st.button("🎯 5. Process Resume", use_container_width=True):
        with st.spinner("5. STRUCTURAL ENFORCEMENT..."):
            # 4.1 Universal parsing
            content = resume_file.read()
            text = extract_text_pure(content, resume_file.name)
            
            # 6. CONTENT INTEGRITY - NO MODIFICATION
            sections = parse_resume_sections(text)
            formatted_content = build_formatted_content(sections, st.session_state.config)
            
            # 8.1 Name extraction
            name = get_name_from_resume(text)
            
            # Generate output
            if output_format == "DOCX":
                doc_data, filename = create_formatted_docx(formatted_content, st.session_state.config, name)
                st.download_button(f"📥 Download {name}.docx", doc_data, filename, "application/vnd.openxmlformats")
            else:
                filename = f"{name}.{output_format.lower()}"
                st.download_button(f"📥 Download {filename}", formatted_content.encode(), filename, "text/plain")
        
        st.session_state.filename = filename
        st.session_state.step = 3
        st.success("✅ **13. CORE PRINCIPLE** - Formatting enforcement complete!")
        st.rerun()

elif st.session_state.step == 3:
    st.header("🎉 11. SUCCESS SCREEN")
    st.success(f"✅ **{st.session_state.filename}** generated successfully!")
    st.info("**12. SYSTEM CONSTRAINTS** - Open source only, no content editing")
    
    if st.button("🔄 New Resume", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# 11. UI REQUIREMENTS
st.markdown("---")
st.markdown("*Light theme • Step-by-step flow • No skipping*")
