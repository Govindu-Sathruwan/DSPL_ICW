import streamlit as st
import plotly.express as px
import seaborn as sns
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import calendar
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Title
st.markdown("<h1 style='text-align: center; color: white;'>🌧️ Rainfall Dashboard - Sri Lanka</h1>", unsafe_allow_html=True)

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
    # First Plot
    st.subheader("📈 Rainfall Trends Over Time")

    # District selector
    districts = sorted(df["districts"].dropna().unique())
    selected_district = st.selectbox("Select District", districts, key="dist1")

    # Date slider
    start = df['date'].min().to_pydatetime()
    end = df['date'].max().to_pydatetime()
    start_date, end_date = st.slider(
    "Select Date Range",
    min_value=start,
    max_value=end,
    value=(start, end),
    format="YYYY-MM-DD", key="date1")

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
        title = {"text": f"3-Month Rolling Rainfall in {selected_district}", "x": 0.5,"xanchor": "center"},
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified",
        height=500)

    # Show chart
    st.plotly_chart(fig, use_container_width=True)

    # Second Plot
    st.subheader("📉 Actual Vs Historical Average Rainfall")

    # Dropdowns side-by-side
    col1, col2 = st.columns(2)
    with col1:
        selected_district = st.selectbox("Select District", sorted(df["districts"].dropna().unique()), key="dist2")
    with col2:
        selected_year = st.selectbox("Select Year", sorted(df["Year"].unique(), reverse=True))
    
    # Filter data
    filtered_df2 = df[(df["districts"] == selected_district) & (df["Year"] == selected_year)]
    
    # Manual month name mapping
    month_map = {
        "January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr",
        "May": "May", "June": "Jun", "July": "Jul", "August": "Aug",
        "September": "Sep", "October": "Oct", "November": "Nov", "December": "Dec"}
    
    # Monthly aggregation
    month_order = list(calendar.month_abbr)[1:]
    monthly_df = filtered_df2.groupby("Month")[["r3h", "r3h_avg"]].mean().reset_index()
    # Apply mapping
    monthly_df["Month"] = monthly_df["Month"].map(month_map)
    monthly_df["Month"] = monthly_df["Month"].astype(CategoricalDtype(categories=month_order, ordered=True))
    monthly_df = monthly_df.sort_values("Month")
    
    # Plotly Bar Chart: Actual vs Average
    bar_fig = px.bar(
    monthly_df,
    x="Month",
    y=["r3h", "r3h_avg"],
    barmode="group",
    labels={"value": "Rainfall (mm)", "Month": "Month"},
    title="Actual vs Historical Average Rainfall",
    color_discrete_map={"r3h": "royalblue", "r3h_avg": "darkorange"})

    bar_fig.update_traces( selector=dict(name='r3h'), name="Actual")
    bar_fig.update_traces( selector=dict(name='r3h_avg'), name="Historical Average")

    bar_fig.update_layout(
        title = {"text": "Actual vs Historical Average Rainfall", "x": 0.5,"xanchor": "center"},
        margin=dict(l=20, r=20, t=60, b=20), height=400)

    # Plotly Line Chart
    line_fig = px.line(
    monthly_df,
    x="Month",
    y=["r3h", "r3h_avg"],
    labels={"value": "Rainfall (mm)", "Month": "Month"},
    title="Actual vs Historical Average Rainfall",
    markers=True,
    color_discrete_map={"r3h": "royalblue", "r3h_avg": "darkorange"})

    line_fig.update_traces( selector=dict(name='r3h'), name="Actual")
    line_fig.update_traces( selector=dict(name='r3h_avg'), name="Historical Average")

    line_fig.update_layout(
        title = {"text": "Actual vs Historical Average Rainfall", "x": 0.5,"xanchor": "center"},
        margin=dict(l=20, r=20, t=60, b=20), height=400)

    # Display side-by-side
    col1, col2 = st.columns([1,1])
    with col1:
        st.plotly_chart(bar_fig, use_container_width=True)
    with col2:
        st.plotly_chart(line_fig, use_container_width=True)

    # Third Plot
    st.subheader("🌧️ Rainfall Anomalies")

    # District selector
    districts = sorted(df["districts"].dropna().unique())
    selected_district = st.selectbox("Select District", districts, key="dist3")

    # Year selector (slider)
    start = df['date'].min().to_pydatetime()
    end = df['date'].max().to_pydatetime()
    start_date, end_date = st.slider(
    "Select Date Range",
    min_value=start,
    max_value=end,
    value=(start, end),
    format="YYYY-MM-DD", key="date2")

    # Filter and sort data
    anomaly_df = df[
        (df["districts"] == selected_district) & (df["date"] >= start_date) & (df["date"] <= end_date)]
    anomaly_df = anomaly_df.sort_values("date")

    # Create combined figure
    fig = go.Figure()

    # Anomaly line
    fig.add_trace(go.Scatter(
        x=anomaly_df["date"],
        y=anomaly_df["r3q"],
        mode='lines+markers',
        name='r3q Anomaly',
        line=dict(color='royalblue', width=2),
        marker=dict(size=4)))

    # Baseline at 0.5
    fig.add_shape(
        type='line',
        x0=anomaly_df["date"].min(),
        x1=anomaly_df["date"].max(),
        y0=100,
        y1=100,
        line=dict(color='red', dash='dash'),
        name="Normal Line")

    # Layout tweaks
    fig.update_layout(
        title={"text": f"Rainfall Anomalies Over Time - {selected_district}", "x": 0.5, "xanchor": "center"},
        xaxis_title="Date",
        yaxis_title="Anomaly % (r3q)",
        yaxis_range=[0, 350],
        hovermode="x unified",
        showlegend=False,
        height=500,
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20))

    # Show chart
    st.plotly_chart(fig, use_container_width=True)
    

if page == "Overview":
    st.header("Dataset Summary")
    st.markdown("<h2 style='font-size: 30px; color: teal;'>Dataset Sample (for exploration)</h2>", unsafe_allow_html=True)
    st.write(df.head(25))
    st.subheader("Descriptive Statistics")
    st.write(df[["Year", "Month", "Day", "districts", "n_pixels", "rfh", "rfh_avg", "r1h", "r1h_avg", "r3h", "r3h_avg", "rfq", "r1q", "r3q"]].describe())