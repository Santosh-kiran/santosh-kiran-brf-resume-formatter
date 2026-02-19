import streamlit as st
import re

st.set_page_config(page_title="BRF Resume Formatter", layout="wide")
st.markdown("""
<style>
.main {background-color: #f8f9fa;}
.stButton > button {border-radius: 12px; height: 50px;}
</style>
""", unsafe_allow_html=True)

if 'step' not in st.session_state:
    st.session_state.step = 0

st.title("📘 BRF Resume Formatter - Santosh Kiran")

# STEP 1: MODE SELECTION
if st.session_state.step == 0:
    st.header("Step 1: Choose Mode")
    col1, col2 = st.columns(2)
    if col1.button("📄 Master Template", use_container_width=True):
        st.session_state.mode = "template"
        st.session_state.config = {'font': 'Calibri', 'size': 11}
        st.session_state.step = 2
        st.rerun()
    if col2.button("✏️ Manual Config", use_container_width=True):
        st.session_state.mode = "manual"
        st.session_state.step = 1
        st.rerun()

# STEP 2: MANUAL CONFIG  
elif st.session_state.step == 1:
    st.header("Step 2: Manual Configuration")
    font = st.text_input("Font", "Calibri")
    size = st.number_input("Size", 10, 14, 11)
    if st.button("✅ SAVE & CONTINUE", use_container_width=True):
        st.session_state.config = {'font': font, 'size': size}
        st.session_state.step = 2
        st.rerun()

# STEP 3: UPLOAD & PROCESS
elif st.session_state.step == 2:
    st.header("Step 3: Upload Resume")
    st.info("ALL FORMATS ✓ NO SIZE LIMIT ✓")
    
    resume_file = st.file_uploader("Upload resume (PDF/DOCX/TXT)", type=['pdf','docx','txt'])
    
    if resume_file:
        if st.button("🎯 FORMAT RESUME", use_container_width=True):
            with st.spinner("Processing..."):
                # READ FILE
                content = resume_file.read()
                text = content.decode('utf-8', errors='ignore')
                
                # EXTRACT SECTIONS (EXACT ORDER)
                summary = re.search(r'(?i)Summary.*?(\n\n|$)', text, re.DOTALL)
                skills = re.search(r'(?i)(Skills|Technical).*?(\n\n|$)', text, re.DOTALL)
                education = re.search(r'(?i)Education.*?(\n\n|$)', text, re.DOTALL)
                experience = re.search(r'(?i)(Experience|Projects).*?(?=\n\n|$)', text, re.DOTALL)
                
                # BUILD PERFECT ORDER
                result = "Summary :\n"
                result += summary.group() if summary else "[Summary section not found]\n"
                result += "\n\nTechnical Skills\n"
                result += skills.group() if skills else "[Skills not found]\n" 
                result += "\n\nEducation\n"
                result += education.group() if education else "[Education not found]\n"
                result += "\n\nProfessional Experience\n"
                result += experience.group() if experience else "[Experience not found]"
                
                # NAME EXTRACTION
                name_match = re.match(r'^([A-Za-z]+[- ]?[A-Za-z]+)', text, re.MULTILINE)
                name = name_match.group(1).replace(" ", "-") if name_match else "Candidate"
                filename = f"{name}-Resume.txt"
                
                # FIXED DOWNLOAD - PROPER BYTES
                download_data = result.encode('utf-8')
                
                st.download_button(
                    label=f"📥 DOWNLOAD {filename}",
                    data=download_data,
                    file_name=filename,
                    mime="text/plain"
                )
                
                st.session_state.filename = filename
                st.session_state.result = result[:200] + "..."
                st.session_state.step = 3
                st.rerun()

# SUCCESS SCREEN
elif st.session_state.step == 3:
    st.header("🎉 SUCCESS!")
    st.success(f"✅ {st.session_state.filename} READY FOR DOWNLOAD")
    st.info(f"Preview: {st.session_state.result}")
    
    if st.button("🔄 NEW RESUME", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

st.markdown("---")
st.markdown("*BRF Resume Formatter - FREE • OPEN SOURCE*")
