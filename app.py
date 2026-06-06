import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
conn = get_connection()
cursor = conn.cursor()


st.set_page_config(
    page_title="Flight Analytics Dashboard",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Flight Analytics Dashboard")

st.markdown("""
### Transforming aviation data into actionable insights

Explore airports, monitor delays, analyze routes,
and uncover flight patterns through interactive dashboards.
""")

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
col1,col2,col3,col4 = st.columns(4)

col1.metric("Flights", total_flights)
col2.metric("Airports", total_airports)
col3.metric("Aircraft", total_aircraft)
col4.metric("Avg Delay", f"{avg_delay} mins")

#1. Flight Status Distribution (Pie Chart)
status_query = """
SELECT status, COUNT(*) AS total
FROM flights
GROUP BY status
"""

status_df = pd.read_sql(status_query, conn)

st.markdown("---")

fig_status = px.pie(
    status_df,
    names="status",
    values="total",
    hole=0.4
)

#2. Top Airlines by Flights
airline_query = """
SELECT airline_code,
       COUNT(*) AS total_flights
FROM flights
WHERE airline_code <> ''
GROUP BY airline_code
ORDER BY total_flights DESC
LIMIT 10
"""

airline_df = pd.read_sql(airline_query, conn)

fig_airline = px.bar(
    airline_df,
    x="airline_code",
    y="total_flights",
    text_auto=True
)

#3. Putting Charts Side-by-Side
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛫 Flight Status")
    st.plotly_chart(fig_status,
                     use_container_width=True)

with col2:
    st.subheader("✈ Top Airlines")
    st.plotly_chart(fig_airline,
                     use_container_width=True)
    
#4. Top Routes
route_query = """
SELECT
    origin_icao,
    destination_code,
    COUNT(*) AS flights
FROM flights
GROUP BY origin_icao,
         destination_code
ORDER BY flights DESC
LIMIT 5
"""

route_df = pd.read_sql(route_query, conn)

st.markdown("---")
st.subheader("🛣 Busiest Routes")

st.dataframe(route_df,
             use_container_width=True)

#5. Feature Cards
st.markdown("---")
st.subheader("🚀 Explore the Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.info("🔍 Search flights by airline, status, and dates.")
    st.info("🛬 Explore airports and their traffic.")

with col2:
    st.info("⏱ Analyze delays and operational performance.")
    st.info("💡 Discover SQL-driven aviation insights.")

#6. Dataset Snapshot
sample_query = """
SELECT
    flight_number,
    airline_code,
    origin_icao,
    destination_code,
    status
FROM flights
LIMIT 5
"""

sample_df = pd.read_sql(sample_query, conn)

st.markdown("---")
st.subheader("📋 Sample Flight Records")

st.dataframe(sample_df,
             use_container_width=True)

#7. Footer
st.markdown("---")

st.caption(
    "Built using AeroDataBox API • MySQL • Pandas • Plotly • Streamlit"
)