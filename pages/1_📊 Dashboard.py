import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
conn = get_connection()
cursor = conn.cursor()

st.title("✈️ AeroDataBox Flight Explorer")
st.caption(
    "Explore airport networks, flight trends, and operational insights."
)

# Total Flights
cursor.execute("""
SELECT COUNT(*)
FROM flights
""")
total_flights = cursor.fetchone()[0]

# Total Airports
cursor.execute("""
SELECT COUNT(*)
FROM airport
""")
total_airports = cursor.fetchone()[0]

# Total Aircraft
cursor.execute("""
SELECT COUNT(*)
FROM aircraft
""")
total_aircraft = cursor.fetchone()[0]

#Total Airlines
cursor.execute("""
SELECT COUNT(DISTINCT airline_code)
FROM flights
WHERE airline_code IS NOT NULL
""")

total_airlines = cursor.fetchone()[0]

#Flight Status Distribution
query = """
SELECT
    status,
    COUNT(*) AS total
FROM flights
GROUP BY status
"""

status_df = pd.read_sql(query, conn)
st.dataframe(status_df)

# Flight Status Distribution Pie Chart
fig = px.pie(
    status_df,
    values='total',
    names='status',
    title='Flight Status Distribution'
)

st.plotly_chart(fig, use_container_width=True)

#Top Airlines Chart
query = """
SELECT
    airline_code,
    COUNT(*) AS total_flights
FROM flights
WHERE airline_code IS NOT NULL
GROUP BY airline_code
ORDER BY total_flights DESC
LIMIT 10
"""

airline_df = pd.read_sql(query, conn)

#Airlines Bar Chart
fig = px.bar(airline_df, x="airline_code", y="total_flights", title="Top Airlines by Flight Count")

st.plotly_chart(fig, use_container_width=True)

#Top Destination Airports
query = """
SELECT
    airport.name,
    COUNT(*) AS arrivals
FROM flights
JOIN airport
ON flights.destination_code = airport.icao_code
GROUP BY airport.name
ORDER BY arrivals DESC
LIMIT 10
"""

airport_df = pd.read_sql(query, conn)

#Bar Chart
fig = px.bar(airport_df, x='name',y='arrivals',title='Top Destination Airports')
st.plotly_chart(fig, use_container_width=True)

#Average Delay
avgd_query = '''
SELECT ROUND(
    AVG(
        TIMESTAMPDIFF(
            MINUTE,
            scheduled_arrival,
            actual_arrival
        )
    ),
    2
)
FROM flights
WHERE actual_arrival IS NOT NULL
AND scheduled_arrival IS NOT NULL
'''

cursor.execute(avgd_query)
avg_delay = cursor.fetchone()[0]



#Columns
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Flights", total_flights)
col2.metric("Airports", total_airports)
col3.metric("Aircraft", total_aircraft)
col4.metric("Airlines",total_airlines)
col5.metric("Avg Delay (min)",avg_delay)
