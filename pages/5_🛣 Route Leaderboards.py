import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
conn = get_connection()
cursor = conn.cursor()

st.title("🏆 Route Leaderboards")
st.markdown(
    "Explore the busiest routes, compare domestic and international operations, and identify routes served by multiple aircraft models."
)

route_type = st.selectbox(
    "Select Route Type",
    ["All", "Domestic", "International"]
)

#1_Busiest Routes
query = '''
SELECT
    a1.city AS origin_city,
    a2.city AS destination_city,
    COUNT(flights.flight_id) AS total_flights

FROM flights

JOIN airport a1
    ON flights.origin_icao = a1.icao_code

JOIN airport a2
    ON flights.destination_code = a2.icao_code
'''

if route_type == "Domestic":
    query += """
    WHERE a1.country = a2.country
    """

elif route_type == "International":
    query += """
    WHERE a1.country <> a2.country
    """

query += """
GROUP BY
    a1.city,
    a2.city

ORDER BY total_flights DESC

LIMIT 10
"""

route_df = pd.read_sql(query, conn)
st.subheader(f"Top 10 {route_type} Routes")
st.dataframe(route_df)

fig = px.bar(
    route_df,
    x="total_flights",
    y=route_df["origin_city"] + " → " + route_df["destination_city"],
    orientation="h",
    title=f"Top 10 {route_type} Routes"
)

st.plotly_chart(fig, use_container_width=True)

#2_Domestic vs International Flights
distribution_query = '''
SELECT
    CASE
        WHEN a1.country = a2.country
        THEN 'Domestic'
        ELSE 'International'
    END AS flight_type,

    COUNT(*) AS total_flights

FROM flights

JOIN airport a1
    ON flights.origin_icao = a1.icao_code

JOIN airport a2
    ON flights.destination_code = a2.icao_code

GROUP BY flight_type
'''

distribution_df = pd.read_sql(distribution_query, conn)

st.subheader("🌍 Domestic vs International Flight Distribution")

st.dataframe(distribution_df)

fig = px.pie(
    distribution_df,
    names="flight_type",
    values="total_flights",
    title="Flight Type Distribution"
)

st.plotly_chart(fig, use_container_width=True)

#3_Routes Using Multiple Aircraft Models

model_query = '''
SELECT
    a1.city AS origin_city,
    a2.city AS destination_city,

    COUNT(DISTINCT aircraft.model)
        AS aircraft_models

FROM flights

JOIN airport a1
    ON flights.origin_icao = a1.icao_code

JOIN airport a2
    ON flights.destination_code = a2.icao_code

JOIN aircraft
    ON flights.aircraft_registration = aircraft.registration
'''

if route_type == "Domestic":
    model_query += """
    WHERE a1.country = a2.country
    """

elif route_type == "International":
    model_query += """
    WHERE a1.country <> a2.country
    """

model_query += """
GROUP BY
    a1.city,
    a2.city

HAVING COUNT(DISTINCT aircraft.model) > 2

ORDER BY aircraft_models DESC
"""

model_df = pd.read_sql(model_query, conn)
st.subheader("🛫 Routes with Multiple Aircraft Models")
st.dataframe(model_df)

fig = px.bar(
    model_df,
    x="aircraft_models",
    y=model_df["origin_city"] + " → " + model_df["destination_city"],
    orientation="h",
    title="Routes Served by Multiple Aircraft Models"
)

st.plotly_chart(fig, use_container_width=True)