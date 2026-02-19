import streamlit as st

st.set_page_config(page_title="Resume Formatter", layout="wide")

st.title("📄 BRF Resume Formatter v1.0")
st.markdown("---")

col1, col2 = st.columns([3,1])

with col1:
    st.header("📎 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose PDF, DOCX, or TXT file", 
        type=['pdf', 'docx', 'txt']
    )
    
    if uploaded_file is not None:
        st.success("✅ File uploaded successfully!")
        st.info(f"📏 File size: {uploaded_file.size:,} bytes")

with col2:
    st.header("📋 Status")
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    
    if st.session_state.file_uploaded:
        st.success("🎉 Ready to format in BRF v1.0!")
        if st.button("✨ Format Resume", type="primary"):
            st.balloons()
            st.success("✅ Formatted! Download will appear here.")
    else:
        st.info("👆 Upload file first")

if uploaded_file:
    st.session_state.file_uploaded = True
