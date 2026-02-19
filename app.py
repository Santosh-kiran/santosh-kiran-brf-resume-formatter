import streamlit as st

st.set_page_config(page_title="My App", layout="wide")

st.title("🎉 My Streamlit Web App")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("📊 Dashboard")
    st.metric("Visitors", "1,234")
    st.metric("Revenue", "$12,345")

with col2:
    st.header("📈 Chart")
    st.bar_chart({"Jan": 100, "Feb": 150, "Mar": 200})

st.markdown("**Deployed on Streamlit Cloud!** 🚀")
