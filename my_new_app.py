import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="My Web App", layout="wide")

# Title
st.title("🚀 My First Streamlit Web App")
st.markdown("---")

# Sidebar
st.sidebar.header("📊 Controls")
chart_type = st.sidebar.selectbox("Chart Type", ["Line", "Bar", "Scatter"])
show_data = st.sidebar.checkbox("Show Raw Data")

# Main content tabs
tab1, tab2 = st.tabs(["📈 Dashboard", "ℹ️ About"])

with tab1:
    # Sample data
    df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Sales': [100, 120, 150, 130, 180, 200],
        'Profit': [20, 25, 35, 28, 40, 45]
    })
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${df['Sales'].sum():,}")
    col2.metric("Total Profit", f"${df['Profit'].sum():,}")
    col3.metric("Avg Profit %", f"{df['Profit'].mean():.1f}%")
    
    # Chart
    if chart_type == "Line":
        fig = px.line(df, x='Month', y='Sales', title="Sales Trend")
    elif chart_type == "Bar":
        fig = px.bar(df, x='Month', y='Sales', title="Sales by Month")
    else:
        fig = px.scatter(df, x='Sales', y='Profit', title="Sales vs Profit")
    
    st.plotly_chart(fig, use_container_width=True)
    
    if show_data:
        st.subheader("Raw Data")
        st.dataframe(df)

with tab2:
    st.header("About This App")
    st.write("""
    - Built with **Streamlit** 
    - Deployed on **Streamlit Cloud**
    - Hosted on **GitHub**
    - Fully responsive dashboard
    """)
    
    st.balloons()

# Footer
st.markdown("---")
st.markdown("⭐ **Made with ❤️ using Streamlit**")
