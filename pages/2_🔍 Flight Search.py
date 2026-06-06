import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
conn = get_connection()
cursor = conn.cursor()

st.title("🛫 Discover Flights")

#1_Fetch_flight numbers
query = """
SELECT DISTINCT flight_number
FROM flights
WHERE flight_number IS NOT NULL
ORDER BY flight_number
"""

flight_df = pd.read_sql(query, conn)

#Creating filter
selected_flights = st.multiselect("Select Flight Number(s)",flight_df["flight_number"].tolist())

#2_AIRLINE FILTER
query = """
SELECT DISTINCT airline_code
FROM flights
WHERE airline_code IS NOT NULL
ORDER BY airline_code
"""

airline_df = pd.read_sql(query, conn)

#Creating filter
selected_airline = st.selectbox("Select Airline",["All"] + airline_df['airline_code'].tolist())

#3_FLIGHT STATUS FILTER
status_query = """
SELECT DISTINCT status
FROM flights
ORDER BY status
"""

status_df = pd.read_sql(status_query, conn)

#Creating filter
selected_status = st.selectbox("Flight Status",["All"] + status_df['status'].tolist())

#4_ORIGIN AIRPORT FILTER
origin_query = """
SELECT DISTINCT origin_icao
FROM flights
WHERE origin_icao IS NOT NULL
ORDER BY origin_icao
"""

origin_df = pd.read_sql(origin_query, conn)

#Creating filter
selected_origin = st.selectbox("Origin Airport",["All"] + origin_df['origin_icao'].tolist())

#5_DESTINATION AIRPORT FILTER
destination_query = """
SELECT DISTINCT destination_code
FROM flights
ORDER BY destination_code
"""

destination_df = pd.read_sql(destination_query, conn)

#Creating filter
selected_destination = st.selectbox("Destination Airport",["All"] + destination_df["destination_code"].tolist())


#BUILD CONDITIONS
conditions = []
params = []

#Flight Number
if selected_flights:
    placeholders = ",".join(["%s"] * len(selected_flights))
    conditions.append(
        f"flight_number IN ({placeholders})"
    )
    params.extend(selected_flights)

#Airline
if selected_airline != "All":
    conditions.append("airline_code = %s")
    params.append(selected_airline)

#Status
if selected_status != "All":
    conditions.append("status = %s")
    params.append(selected_status)

#Origin
if selected_origin != "All":
    conditions.append("origin_icao = %s")
    params.append(selected_origin)

#Destination
if selected_destination != "All":
    conditions.append("destination_code = %s")
    params.append(selected_destination)


##FINAL QUERY
query = """
SELECT
    flight_number,
    aircraft_registration,
    origin_icao,
    destination_code,
    status,
    scheduled_departure,
    actual_departure,
    scheduled_arrival,
    actual_arrival
FROM flights
"""

#Adding Conditions
if conditions:
    query += " WHERE " + " AND ".join(conditions)

results_df = pd.read_sql(query,conn,params=params)

#Display Results
st.dataframe(results_df,use_container_width=True)
st.metric("Matching Flights",len(results_df))