import streamlit as st
import plotly.express as px
import seaborn as sns
import numpy as np
import pandas as pd

# Title
st.title("🌧️ Rainfall Dashboard - Sri Lanka")

# getting the data
df=pd.read_csv("preprocessed_dataset.csv", parse_dates=["date"])

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to ⬇️", ["Rainfall Trends", "Overview", "Decision Support", "Multilingual", "About"])
st.sidebar.title("Languages")
language = st.sidebar.selectbox("Select Prefered Language ⬇️", ["English","Sinhala", "Tamil"])

# Backgrounds
backgrounds = {
    "Rainfall Trends": "https://images.unsplash.com/photo-1523772721666-22ad3c3b6f90?q=80&w=1770&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Overview": "https://images.unsplash.com/photo-1511634829096-045a111727eb?q=80&w=1934&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Decision Support": "https://images.unsplash.com/photo-1496034663057-6245f11be793?q=80&w=1770&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Multilingual": "https://images.unsplash.com/photo-1685430996137-b92678138c0b?q=80&w=1774&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "About": "https://images.unsplash.com/photo-1498847559558-1e4b1a7f7a2f?q=80&w=1770&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
}
# Function to set background
def set_background(image_url):
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.4); /* fading dark overlay */
            z-index: 0;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background(backgrounds[page])

# Conditional rendering
if page == "Rainfall Trends":
    st.markdown("<h2 style='color: white;'>📈 Rainfall Trends Over Time</h2>", unsafe_allow_html=True)

    # District selector
    districts = sorted(df["districts"].dropna().unique())
    selected_district = st.selectbox("Select District", districts)

    # Date slider
    start = df['date'].min().to_pydatetime()
    end = df['date'].max().to_pydatetime()
    start_date, end_date = st.slider(
    "Select Date Range",
    min_value=start,
    max_value=end,
    value=(start, end),
    format="YYYY-MM-DD")

    # Filter data
    filtered_df = df[
        (df["districts"] == selected_district) &
        (df["date"] >= start_date) &
        (df["date"] <= end_date)]
    
    # Plot with Plotly
    fig = px.line(
        filtered_df,
        x="date",
        y="r3h",
        title=f"3-Month Rolling Rainfall in {selected_district}",
        labels={"r3h": "Rainfall (mm)", "date": "Date"},
        template="plotly_white")

    fig.update_traces(line=dict(color="royalblue"))
    fig.update_layout(
        title_x=0.3,
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified",
        height=500)

    # Show chart
    st.plotly_chart(fig, use_container_width=True)
    

if page == "Overview":
    st.header("Dataset Summary")
    st.markdown("<h2 style='font-size: 30px; color: teal;'>Dataset Sample (for exploration)</h2>", unsafe_allow_html=True)
    st.write(df.head(25))
    st.subheader("Descriptive Statistics")
    st.write(df[["Year", "Month", "Day", "districts", "n_pixels", "rfh", "rfh_avg", "r1h", "r1h_avg", "r3h", "r3h_avg", "rfq", "r1q", "r3q"]].describe())