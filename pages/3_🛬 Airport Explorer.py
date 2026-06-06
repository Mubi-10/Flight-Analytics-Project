import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
conn = get_connection()
cursor = conn.cursor()

#Airport Header
st.title("🏢 Airports")
st.write("Select Airports to know the status on departures and arrivals.")

#1_Airport Selection Filter
airport_query = """
SELECT name, icao_code
FROM airport
ORDER BY name
"""

airport_df = pd.read_sql(airport_query, conn)

#Creating filter
selected_airport = st.selectbox("Select Airport",airport_df["name"])
#Get the corresponding ICAO:
selected_icao = airport_df.loc[airport_df["name"] == selected_airport,"icao_code"].iloc[0]

#2_Airport Information Card
query = '''
SELECT
    name,
    icao_code,
    iata_code,
    city,
    country,
    timezone
FROM airport
WHERE icao_code = %s
'''

airport_IC_df = pd.read_sql(query, conn, params=[selected_icao])

#Display
airport_info = airport_IC_df.iloc[0]

st.subheader(airport_info['name'])

col1, col2 = st.columns(2)

col1.write(f"ICAO: {airport_info['icao_code']}")
col1.write(f"IATA: {airport_info['iata_code']}")

col2.write(f"City: {airport_info['city']}")
col2.write(f"Country: {airport_info['country']}")

st.write(f"Timezone: {airport_info['timezone']}")

#3_Airport_Traffic_Status
#Total_Departures
departure_query = """
SELECT COUNT(*) AS departures
FROM flights
WHERE origin_icao = %s
"""
departures = pd.read_sql(departure_query,conn,params=[selected_icao]).iloc[0]["departures"]

#Total Arrivals
arrival_query = """
SELECT COUNT(*) AS arrivals
FROM flights
WHERE destination_code = %s
"""

arrivals = pd.read_sql(
    arrival_query,
    conn,
    params=[selected_icao]
).iloc[0]["arrivals"]

#Delay_Percentage
delay_query = """
SELECT
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN actual_departure > scheduled_departure THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS delay_percentage
FROM flights
WHERE origin_icao = %s
"""

delay_percentage = pd.read_sql(
    delay_query,
    conn,
    params=[selected_icao]
).iloc[0]["delay_percentage"]

delay_percentage = delay_percentage or 0

col1, col2, col3 = st.columns(3)

col1.metric("✈️ Departures",departures)
col2.metric("🛬 Arrivals",arrivals)
col3.metric("⏰ Delay %",f"{delay_percentage}%")

#Recent Departures
departure_query = """
SELECT
    flight_number,
    destination_code,
    scheduled_departure,
    status
FROM flights
WHERE origin_icao = %s
ORDER BY scheduled_departure DESC
LIMIT 10
"""

departure_df = pd.read_sql(
    departure_query,
    conn,
    params=[selected_icao]
)
st.subheader("✈️ Recent Departures")
st.dataframe(departure_df,use_container_width=True)

#Recent Arrivals
arrival_query = """
SELECT
    flight_number,
    origin_icao,
    actual_arrival,
    status
FROM flights
WHERE destination_code = %s
ORDER BY actual_arrival DESC
LIMIT 10
"""

arrival_df = pd.read_sql(
    arrival_query,
    conn,
    params=[selected_icao]
)
st.subheader("🛬 Recent Arrivals")
st.dataframe(arrival_df,use_container_width=True)

#Flight Status Distribution
status_query = """
SELECT
    status,
    COUNT(*) AS total
FROM flights
WHERE origin_icao = %s
GROUP BY status
"""

status_df = pd.read_sql(status_query,conn,params=[selected_icao])

# Pie Chart
fig = px.pie(status_df,names="status",values="total",title="Flight Status Distribution")
st.plotly_chart(fig,use_container_width=True)

#Top Destinations
destination_query = """
SELECT
    destination_code,
    COUNT(*) AS total_flights
FROM flights
WHERE origin_icao = %s
GROUP BY destination_code
ORDER BY total_flights DESC
LIMIT 10
"""

destination_df = pd.read_sql(
    destination_query,
    conn,
    params=[selected_icao]
)

fig = px.bar(
    destination_df,
    x="destination_code",
    y="total_flights",
    title="Top Destinations"
)

st.plotly_chart(
    fig,
    use_container_width=True
)