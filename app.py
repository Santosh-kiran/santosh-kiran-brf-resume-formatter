import streamlit as st

st.set_page_config(page_title="BRF Resume Formatter", layout="wide")

st.title("📄 Beeline Resume Format v1.0")
st.markdown("---")

# File uploader
uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX/TXT)", 
                                type=['pdf','docx','txt'])

if uploaded_file is not None:
    st.success("✅ File uploaded!")
    st.info(f"📁 Filename: {uploaded_file.name}")
    st.info(f"📏 Size: {uploaded_file.size:,} bytes")
    
    if st.button("✨ Format to BRF v1.0", type="primary"):
        st.success("🎉 Resume formatted successfully!")
        st.balloons()
        st.download_button(
            label="📥 Download BRF Resume",
            data="Formatted resume content here",
            file_name="BRF_Resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
else:
    st.info("👆 Please upload your resume to continue")
