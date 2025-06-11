import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pyproj import Transformer
import pyodbc
import os

st.title("UK Road Safety Dashboard - From Azure SQL")

# Database connection settings
server = 'hackathon25.database.windows.net'
database = 'hackathon_database'
username = os.getenv("DB_USER", "").strip()
password = os.getenv("DB_PASS", "").strip()
driver = '{ODBC Driver 18 for SQL Server}'

@st.cache_data
def load_data():
    conn_str = (
        f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};'
        f'UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    conn = pyodbc.connect(conn_str)
    df = pd.read_sql("SELECT * FROM [dbo].[Traffic_Accidents_2019_Leeds]", conn)
    conn.close()
    return df

# Load data
df = load_data()

# Clean and convert date
df['Accident Date'] = pd.to_datetime(df['Accident Date'], dayfirst=True)

# Sidebar Filters
st.sidebar.header("Filters")

# Date Filter
min_date = df['Accident Date'].min()
max_date = df['Accident Date'].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

# Vehicle Filter
df['Number of Vehicles'] = df['Number of Vehicles'].astype(int)
min_vehicles = int(df['Number of Vehicles'].min())
max_vehicles = int(df['Number of Vehicles'].max())
vehicle_range = st.sidebar.slider("Number of Vehicles", min_vehicles, max_vehicles, (min_vehicles, max_vehicles))

# Apply Filters
filtered_df = df[
    (df['Accident Date'] >= pd.to_datetime(date_range[0])) & 
    (df['Accident Date'] <= pd.to_datetime(date_range[1])) & 
    (df['Number of Vehicles'] >= vehicle_range[0]) & 
    (df['Number of Vehicles'] <= vehicle_range[1])
]

# Dataset preview
st.subheader("Filtered Data Preview")
st.dataframe(filtered_df.head())

# Summary Stats
st.subheader("Quick Summary Stats")
col1, col2, col3 = st.columns(3)

with col1:
    total_accidents = filtered_df['Reference Number'].drop_duplicates().count()
    st.metric("Total Accidents", total_accidents)

with col2:
    total_vehicles = filtered_df['Number of Vehicles'].sum()
    st.metric("Total Vehicles Involved", total_vehicles)

with col3:
    if 'Casualty Severity' in filtered_df.columns:
        total_casualties = filtered_df['Casualty Severity'].count()
        st.metric("Total Casualties", total_casualties)

# Casualty Severity Breakdown
st.subheader("Casualty Severity Breakdown")
if 'Casualty Severity' in filtered_df.columns:
    severity_counts = filtered_df['Casualty Severity'].value_counts().sort_index()
    severity_labels = {1: "Fatal", 2: "Serious", 3: "Slight"}
    severity_counts.index = severity_counts.index.map(severity_labels)

    fig, ax = plt.subplots()
    severity_counts.plot(kind='bar', ax=ax)
    ax.set_xlabel("Casualty Severity")
    ax.set_ylabel("Number of Casualties")
    ax.set_title("Number of Casualties by Severity")
    st.pyplot(fig)
else:
    st.warning("Casualty_Severity column not found.")

# Weather Conditions
st.subheader("Accidents by Weather Conditions")
if 'Weather Conditions' in filtered_df.columns:
    weather_counts = filtered_df['Weather Conditions'].value_counts()
    st.bar_chart(weather_counts)

# Road Surface Conditions
st.subheader("Accidents by Road Surface Conditions")
if 'Road Surface' in filtered_df.columns:
    surface_counts = filtered_df['Road Surface'].value_counts()
    st.bar_chart(surface_counts)

# Map Visualisation
st.subheader("Accident Locations on Map")
if 'Grid Ref: Easting' in filtered_df.columns and 'Grid Ref: Northing' in filtered_df.columns:
    try:
        coords_df = filtered_df[['Grid Ref: Easting', 'Grid Ref: Northing']].dropna()
        coords_df = coords_df.astype({'Grid Ref: Easting': 'float', 'Grid Ref: Northing': 'float'})

        transformer = Transformer.from_crs("epsg:27700", "epsg:4326", always_xy=True)
        lons, lats = transformer.transform(coords_df['Grid Ref: Easting'].values, coords_df['Grid Ref: Northing'].values)

        map_df = pd.DataFrame({'lat': lats, 'lon': lons})

        if map_df.empty:
            st.warning("No valid coordinates to plot.")
        else:
            st.map(map_df)
    except Exception as e:
        st.warning(f"Could not convert coordinates to map format. Error: {e}")
else:
    st.warning("Easting/Northing data not available.")

# Line Chart
st.subheader("Daily Accident Trends")
daily_counts = filtered_df.groupby('Accident Date').size()
st.line_chart(daily_counts)
