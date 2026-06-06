import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
conn = get_connection()
cursor = conn.cursor()

#Delay Analysis Header
st.title("⏱️ Delay Analysis")
st.write("Analyze delays across airports and airlines.")

#Get airlines
airline_query = """
SELECT DISTINCT airline_code
FROM flights
WHERE airline_code IS NOT NULL
ORDER BY airline_code
"""
airline_df = pd.read_sql(airline_query, conn)

# Airline Filter
airlines = ["All Airlines"] + airline_df["airline_code"].tolist()
selected_airline = st.selectbox("Select Airline",airlines)

# Delay Query
if selected_airline == "All Airlines":

    query = '''
        SELECT
            airport.name AS destination_airport,
            COUNT(*) AS total_arrivals,

            SUM(
                CASE
                    WHEN actual_arrival > scheduled_arrival
                    THEN 1
                    ELSE 0
                END
            ) AS delayed_arrivals,

            ROUND(
                100.0 *
                SUM(
                    CASE
                        WHEN actual_arrival > scheduled_arrival
                        THEN 1
                        ELSE 0
                    END
                ) / COUNT(*),
                2
            ) AS delayed_percentage

        FROM flights

        JOIN airport
            ON flights.destination_code = airport.icao_code

        WHERE actual_arrival IS NOT NULL AND scheduled_arrival IS NOT NULL    
        GROUP BY airport.icao_code, airport.name

        ORDER BY delayed_percentage DESC
    '''

    delay_df = pd.read_sql(query, conn)

else:

    query = '''
        SELECT
            airport.name AS destination_airport,
            COUNT(*) AS total_arrivals,

            SUM(
                CASE
                    WHEN actual_arrival > scheduled_arrival
                    THEN 1
                    ELSE 0
                END
            ) AS delayed_arrivals,

            ROUND(
                100.0 *
                SUM(
                    CASE
                        WHEN actual_arrival > scheduled_arrival
                        THEN 1
                        ELSE 0
                    END
                ) / COUNT(*),
                2
            ) AS delayed_percentage

        FROM flights

        JOIN airport
            ON flights.destination_code = airport.icao_code

        WHERE flights.airline_code = %s AND actual_arrival IS NOT NULL AND scheduled_arrival IS NOT NULL

        GROUP BY airport.icao_code, airport.name

        ORDER BY delayed_percentage DESC
    '''
    delay_df = pd.read_sql(query,conn,params=[selected_airline])

#Total Flights
total_flights = delay_df["total_arrivals"].sum()
#Delayed Flights
total_delayed = delay_df["delayed_arrivals"].sum()
#Delay %
#Prevent Division by Zero
if total_flights > 0:
    delay_percentage = round(
        total_delayed * 100 / total_flights,
        2
    )
else:
    delay_percentage = 0


#Columns
col1,col2,col3 = st.columns(3)

col1.metric("Total Arrivals",total_flights)
col2.metric("Delayed Arrivals",total_delayed)
col3.metric("Delay %",f"{delay_percentage}%")

#Display
st.subheader("Delay Percentage by Destination Airport")
st.dataframe(delay_df)

fig = px.bar(
    delay_df,
    x="destination_airport",
    y="delayed_percentage",
    text="delayed_percentage",
    color="delayed_percentage",
    title=f"Delay Percentage for {selected_airline}"
)
st.plotly_chart(fig,use_container_width=True)

#Average Delay

if selected_airline == "All Airlines":

    avg_delay_query = '''
    SELECT
        airport.name,

        ROUND(
            AVG(
                TIMESTAMPDIFF(
                    MINUTE,
                    scheduled_arrival,
                    actual_arrival
                )
            ),
            2
        ) AS avg_delay

    FROM flights

    JOIN airport
        ON flights.destination_code = airport.icao_code

    WHERE actual_arrival IS NOT NULL AND scheduled_arrival IS NOT NULL

    GROUP BY airport.name

    ORDER BY avg_delay DESC
    '''

    avg_delay_df = pd.read_sql(
        avg_delay_query,
        conn
    )

else:

    avg_delay_query = '''
    SELECT
        airport.name,

        ROUND(
            AVG(
                TIMESTAMPDIFF(
                    MINUTE,
                    scheduled_arrival,
                    actual_arrival
                )
            ),
            2
        ) AS avg_delay

    FROM flights

    JOIN airport
        ON flights.destination_code = airport.icao_code

    WHERE
        airline_code = %s
        AND actual_arrival IS NOT NULL
        AND scheduled_arrival IS NOT NULL
        AND actual_arrival > scheduled_arrival
         
    GROUP BY airport.name

    ORDER BY avg_delay DESC
    '''

    avg_delay_df = pd.read_sql(avg_delay_query,conn,params=[selected_airline])

fig2 = px.bar(
    avg_delay_df,
    x="avg_delay",
    y="name",
    text="avg_delay",
    orientation="h",
    title="Average Delay (Minutes)"
)

st.plotly_chart(fig2)

#Top 10 Most Delayed Flights Table
most_delayed_flights_tab = '''
SELECT
    flight_number,
    airline_code,

    TIMESTAMPDIFF(
        MINUTE,
        scheduled_arrival,
        actual_arrival
    ) AS delay_minutes

FROM flights

WHERE
    actual_arrival > scheduled_arrival

ORDER BY delay_minutes DESC

LIMIT 10
'''

top_delay_df = pd.read_sql(most_delayed_flights_tab, conn)

st.subheader("Top 10 Most Delayed Flights")
st.dataframe(top_delay_df)