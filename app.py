import streamlit as st

st.set_page_config(page_title="Resume Formatter", layout="wide")

st.title("📄 BRF Resume Formatter")
st.markdown("---")

col1, col2 = st.columns([2,1])

with col1:
    st.header("Upload Resume")
    uploaded_file = st.file_uploader("Choose PDF/DOCX", type=['pdf','docx'])
    
with col2:
    st.header("Status")
    if uploaded_file:
        st.success("✅ File uploaded!")
        st.info("Ready to format...")

st.markdown("**Beeline Resume Format v1.0** - Deployed on Streamlit Cloud 🚀")
