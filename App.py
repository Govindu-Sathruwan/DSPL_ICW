import streamlit as st
import plotly.express as px
import seaborn as sns
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import calendar
import plotly.graph_objects as go
import json 
import geopandas as gpd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Title
st.markdown("<h1 style='text-align: center; color: white;'>Rainfall Dashboard - Sri Lanka</h1>", unsafe_allow_html=True)

# getting the data
df=pd.read_csv("preprocessed_dataset.csv", parse_dates=["date"])

with open("geoBoundaries-LKA-ADM2.geojson", "r") as f: 
    geojson_data = json.load(f)

# Sidebar
sidebar_image = "https://images.unsplash.com/photo-1647884203284-ba16820086ed?q=80&w=1770&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
st.markdown(f"""
    <style>
        .stSidebar{{
            background-image: url("{sidebar_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;}}
        .stSidebar::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.3);  /* black tint, 0.5 opacity */
            z-index: 0;}}
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to ⬇️", ["Rainfall Trends", "Overview", "About"])
st.sidebar.markdown("<br>" "<br>" "<br>", unsafe_allow_html=True)
st.sidebar.title("Languages")
language = st.sidebar.selectbox("Select Prefered Language ⬇️", ["English","Sinhala", "Tamil"])

# Backgrounds
backgrounds = {
    "Rainfall Trends": "https://images.unsplash.com/photo-1523772721666-22ad3c3b6f90?q=80&w=1770&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "Overview": "https://images.unsplash.com/photo-1685430996137-b92678138c0b?q=80&w=1774&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
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

    # KPI Cards
    st.subheader("🌧️ Rainfall Summary")

    #Year selector
    selected_year = st.selectbox("Select Year", sorted(df["Year"].unique(), reverse=True), key="year7")

    #Filter data for selected year
    year_df = df[df["Year"] == selected_year]

    total_rainfall = year_df["r3h"].sum()

    # Wettest and driest month
    monthly_rain = year_df.groupby("Month")["r3h"].sum()
    wettest_month = monthly_rain.idxmax()
    wettest_month_val = monthly_rain.max()
    driest_month = monthly_rain.idxmin()
    driest_month_val = monthly_rain.min()

    # Wettest and driest district
    district_rain = year_df.groupby("districts")["r3h"].sum()
    wettest_district = district_rain.idxmax()
    wettest_district_val = district_rain.max()
    driest_district = district_rain.idxmin()
    driest_district_val = district_rain.min()

    # Display as KPI cards
    spacer1, col1, col2, col3 = st.columns([1, 2, 2, 2])
    with col1:
        st.metric("💧 Total Rainfall (mm)", f"{total_rainfall:,.0f}")
    with col2:
        st.metric("🌧️ Wettest Month", f"{wettest_month}", f"{wettest_month_val:.1f} mm")
    with col3:
        st.metric("🌤️ Driest Month", f"{driest_month}", f"{driest_month_val:.1f} mm")

    spacer1, col4, col5 = st.columns([2, 3, 3])
    with col4:
        st.metric("🌊 Wettest District", f"{wettest_district}", f"{wettest_district_val:.1f} mm")
    with col5:
        st.metric("🌵 Driest District", f"{driest_district}", f"{driest_district_val:.1f} mm")



    #First Plot
    st.subheader(" 🌧️ Rainfall By District")

    # correct month ordering
    month_order = list(calendar.month_name)[1:]
    df["Month"] = df["Month"].astype(CategoricalDtype(categories=month_order, ordered=True))
    sorted_months = df["Month"].dropna().unique().tolist()

    # Selectboxes
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Select Year", sorted(df["Year"].unique(), reverse=True), key="yearM")
    with col2:
        selected_month = st.selectbox("Select Month", sorted_months, key="monthM")

    # Clean shapeISO 
    for f in geojson_data["features"]:
        if "shapeISO" in f["properties"]:
            f["properties"]["shapeISO"] = f["properties"]["shapeISO"].replace("-", "")

    # Filter and group your data
    filtered_df4 = df[(df["Year"] == selected_year) & (df["Month"] == selected_month)]
    monthly_avg = filtered_df4.groupby("ADM2_PCODE", as_index=False)["r3h"].mean()

    # Create mapbox choropleth
    fig_map = px.choropleth_mapbox(
        monthly_avg,
        geojson=geojson_data,
        locations="ADM2_PCODE",
        featureidkey="properties.shapeISO",
        color="r3h",
        labels={"r3h": "Rainfall(mm)"},
        color_continuous_scale="Blues",
        range_color=(0, 1000),
        mapbox_style="carto-darkmatter",
        zoom=6,
        center={"lat": 7.8731, "lon": 80.7718}, 
        opacity=0.85,
        hover_data={"ADM2_PCODE": True, "r3h": ":.2f"},
        title=f"Rainfall Distribution - {selected_month} {selected_year}")

    # Layout
    fig_map.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        title={
        "text": f"Rainfall Distribution - {selected_month} {selected_year}","x": 0.5,"xanchor": "center"})
    st.plotly_chart(fig_map, use_container_width=True)

    # Second Plot
    st.subheader("📈 Rainfall Trends Over Time")

    # District selector
    col1, col2 = st.columns(2)
    with col1:
        districts = sorted(df["districts"].dropna().unique())
        selected_district = st.selectbox("Select District", districts, key="dist1")
    with col2:
        measure_options = {"3-Month Rolling": "r3h", "1-Month Rolling": "r1h", "10-Day": "rfh"}
        selected_measure_label = st.selectbox("Select Rainfall Measure", list(measure_options.keys()), key="measure1")
        selected_measure = measure_options[selected_measure_label]

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
    filtered_df = df[(df["districts"] == selected_district) & (df["date"] >= start_date) & (df["date"] <= end_date)]
    
    # Plot with Plotly
    fig = px.line(
    filtered_df,
    x="date",
    y=selected_measure,
    title=f"{selected_measure_label} Rainfall in {selected_district}",
    labels={selected_measure: "Rainfall (mm)", "date": "Date"},
    template="plotly_white")

    fig.update_traces(line=dict(color="royalblue"))
    fig.update_layout(
        title = {"text": f"{selected_measure_label} Rainfall in {selected_district}", "x": 0.5,"xanchor": "center"},
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified",
        height=500)

    st.plotly_chart(fig, use_container_width=True)

    # Third Plot
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

    # Fourth Plot
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
    
    # Fifth Plot
    st.subheader("📊 Rainfall Distribution for Selected Month and District")

    #Dropdowns: District and Month
    col1, col2 = st.columns(2)
    with col1:
        selected_district = st.selectbox("Select District", sorted(df["districts"].dropna().unique()), key="dist4")
    with col2:
        selected_month = st.selectbox("Select Month", sorted_months, key="month4")

    #Filter Data
    violin_df = df[(df["districts"] == selected_district) & (df["Month"] == selected_month)].copy()

    #Plotly Violin Plot
    fig = px.violin(
        violin_df,
        x="Month",
        y="r3h", 
        box=True,
        points="all",
        color_discrete_sequence=["royalblue"],
        title=f"Rainfall Distribution for {selected_month} in the {selected_district} District through the years",
        hover_data=["Year"])

    fig.update_layout(
        height=500,
        title= {
        "text": f"Rainfall Distribution for {selected_month} in the {selected_district} District through the years","x": 0.5,"xanchor": "center"},
        yaxis_title="Rainfall (mm)",
        margin={"l": 20, "r": 20, "t": 60, "b": 20})

    st.plotly_chart(fig, use_container_width=True)

    # Sixth plot
    st.subheader("📆 Monthly Rainfall Heatmap")
    selected_district = st.selectbox("Select District", sorted(df["districts"].dropna().unique()), key="dist6")
    heatmap_df = df[df["districts"] == selected_district].copy()
    month_order = list(calendar.month_name)[1:]
    heatmap_df["Month"] = heatmap_df["Month"].astype(CategoricalDtype(categories=month_order, ordered=True))
    
    matrix_df = heatmap_df.pivot_table(
        index="Month",
        columns="Year",
        values="r3h",
        aggfunc="mean").reindex(month_order)

    # Plot as a heatmap
    fig = px.imshow(
        matrix_df,
        labels=dict(x="Year", y="Month", color="Rainfall (mm)"),
        x=matrix_df.columns,
        y=matrix_df.index,
        color_continuous_scale="Blues",
        zmin=0,
        zmax=1250)

    fig.update_layout(
        title={"text": f"Rainfall Heatmap Calendar - {selected_district}", "x": 0.5, "xanchor": "center"},
        height=500,
        margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

if page == "Overview":

    st.metric("📅 Date Range", f"{df['date'].min().date()} → {df['date'].max().date()}")
    st.metric("📍 Districts Covered", df['districts'].nunique())
    st.metric("🧮 Total Records", len(df))

    st.header("Dataset Overview")

    with st.expander("ℹ️ Rainfall Variable Descriptions"):
        st.markdown("""
        **rfh**:       10-day rainfall total [mm]  
        **r1h**:       1-month rolling rainfall total [mm]  
        **r3h**:       3-month rolling rainfall total [mm]  
        **rfh_avg**:   Long-term average of 10-day rainfall [mm]  
        **r1h_avg**:   Long-term average of 1-month rainfall [mm]  
        **r3h_avg**:   Long-term average of 3-month rainfall [mm]  
        **rfq**:       Rainfall anomaly [%]  
        **r1q**:       1-month rainfall anomaly [%]  
        **r3q**:       3-month rainfall anomaly [%]
        """)

    st.markdown("<h2 style='font-size: 30px; color: white; text-align: center'>Dataset Sample (for exploration)</h2>", unsafe_allow_html=True)
    st.write(df.head(30))

    st.markdown("<h2 style='font-size: 30px; color: white; text-align: center'>Descriptive Statistics</h2>", unsafe_allow_html=True)
    st.write(df[["Year", "Month", "Day", "districts", "n_pixels", "rfh", "rfh_avg", "r1h", "r1h_avg", "r3h", "r3h_avg", "rfq", "r1q", "r3q"]].describe())

    st.markdown("<h2 style='text-align: center; color: white;'>Data Types</h2>", unsafe_allow_html=True)
    dtypes_df = pd.DataFrame(df.dtypes, columns=["Data Type"])
    st.dataframe(dtypes_df)

    st.markdown("<h2 style='text-align: center; color: white;'>Rainfall Distribution</h2>", unsafe_allow_html=True)
    selected_col = st.selectbox("Select a Rainfall Column", [ "rfh", "rfh_avg", "r1h", "r1h_avg", "r3h", "r3h_avg", "rfq", "r1q", "r3q"], key="measure02")
    fig = px.histogram(df, x=selected_col, nbins=50, title=f"Distribution of {selected_col}")
    fig.update_layout(title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

if page == "About":

    st.markdown("""
        <div style='color: white; font-size: 16px; line-height: 1.7;'>

        ### Objectives of the Dashboard  
        The primary objectives of this dashboard are to:

        -  **Analyze temporal and spatial rainfall trends** across Sri Lanka to identify patterns and deviations.  
        -  **Highlight anomalies and extreme events** (droughts or unusually wet periods) to be prepared.  
        -  **Visualize district-level rainfall** to help understand localized impacts on agriculture and water availability.  
        -  **Compare actual rainfall with long-term historical averages** to assess the severity of climate variation.  
        -  **Assist policymakers, farmers, and energy planners** by providing accessible insights into rainfall behavior.  

        These objectives align with the broader goal of supporting **climate resilience, food security**, and **hydropower management** in Sri Lanka.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: left; color: white;'>About This Project</h3>", unsafe_allow_html=True)

    st.markdown("""
    <div style='color: white; font-size: 16px; line-height: 1.7;'>

    Built using **Streamlit**, it includes visualizations like:
    - Rainfall trends over time
    - Rainfall anomalies
    - Choropleth maps by district
    - Heatmaps and summary KPIs

    ### Data Sources  
    - **Rainfall data:** https://data.humdata.org/dataset/lka-rainfall-subnational  
    - **Geospatial data:** https://data.humdata.org/dataset/cod-ab-lka
    - **Background Images:** https://unsplash.com/s/photos/rain?orientation=landscape&license=free
    
    <Br>
    <Br>
    <Br>
    <Br>
                    
    #### 👤 Created By  
    **Govindu Sathruwan**  
    BSc (Hons) Business Data Analytics  
    University of Westminster | IIT Sri Lanka <Br>
    GitHub: https://github.com/Govindu-Sathruwan 
    </div>
    """, unsafe_allow_html=True)

