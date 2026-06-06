import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
conn = get_connection()
cursor = conn.cursor()

#Title
st.title("📊 SQL Insights")
st.write("Explore business insights generated using SQL queries.")

#Create Dropdown
analysis = st.selectbox(
    "Choose Analysis",
    [
        "Flights per Aircraft Model",
        "Aircraft Assigned to More Than 5 Flights",
        "Outbound Flights by Airport",
        "Top Destination Airports",
        "Domestic vs International Flights",
        "Recent Arrivals at DEL",
        "Airports with No Arrivals",
        "Airline Status Summary",
        "Cancelled Flights",
        "City Pairs with Multiple Aircraft Models",
        "Destination Delay Percentage"
    ]
)

#Queries execution
if analysis == "Flights per Aircraft Model":

    query = """
    SELECT
        aircraft.model,
        COUNT(*) AS total_flights
    FROM flights
    JOIN aircraft
        ON flights.aircraft_registration = aircraft.registration
    GROUP BY aircraft.model
    ORDER BY total_flights DESC
    """

    df = pd.read_sql(query, conn)
    st.subheader("Flights per Aircraft Model")
    st.dataframe(df)
    st.info(f"{len(df)} records found.")

    fig = px.bar(
    df.head(10),
    x="model",
    y="total_flights",
    title="Top Aircraft Models")

    st.plotly_chart(fig, use_container_width=True)

elif analysis == "Aircraft Assigned to More Than 5 Flights":

    query = """
    SELECT
        aircraft.registration,
        aircraft.model,
        COUNT(*) AS total_flights
    FROM aircraft
    JOIN flights
        ON aircraft.registration = flights.aircraft_registration
    GROUP BY aircraft.registration,
             aircraft.model
    HAVING COUNT(*) > 5
    ORDER BY total_flights DESC
    """

    df = pd.read_sql(query, conn)
    st.subheader("Aircraft Assigned to More Than 5 Flights")
    st.dataframe(df)
    st.info(f"{len(df)} records found.")

elif analysis == "Outbound Flights by Airport":

    query = """
    SELECT name, COUNT(flights.flight_id) AS no_of_outbound_flights FROM airport
    JOIN flights ON airport.icao_code = flights.origin_icao
    GROUP BY name
    HAVING no_of_outbound_flights > 5
    ORDER BY no_of_outbound_flights DESC
    """

    df = pd.read_sql(query, conn)
    st.subheader("Outbound Flights by Airport")
    st.dataframe(df)
    st.info(f"{len(df)} records found.")

    fig = px.bar(
    df,
    x="name",
    y="no_of_outbound_flights",
    title="Outbound Flights by Airport")

    st.plotly_chart(fig, use_container_width=True)

elif analysis == "Top Destination Airports":

    query = """
    SELECT name, city, COUNT(flights.flight_id) as no_of_arriving_flights FROM airport
    JOIN flights on airport.icao_code = flights.destination_code
    GROUP BY name, city
    ORDER BY no_of_arriving_flights DESC
    LIMIT 3
    """

    df = pd.read_sql(query, conn)
    st.subheader("Top 3 Destination Airports")
    st.dataframe(df)
    st.info(f"{len(df)} records found.")

    fig = px.bar(
    df,
    x="name",
    y="no_of_arriving_flights",
    color="city",
    title="Top Destination Airports")

    st.plotly_chart(fig, use_container_width=True)

elif analysis == "Domestic vs International Flights":

    query = """
    SELECT flight_number, origin_icao, destination_code,
        CASE 
            WHEN a1.country = a2.country THEN 'Domestic'
            ELSE 'International'
        END AS flight_type
    FROM flights
    JOIN airport a1 ON flights.origin_icao = a1.icao_code
    JOIN airport a2 ON flights.destination_code = a2.icao_code
    """

    df = pd.read_sql(query, conn)
    st.subheader("Domestic vs International Flights")
    st.dataframe(df)
    st.info(f"{len(df)} records found.")

elif analysis == "Recent Arrivals at DEL":

    query = """
    SELECT flight_number, aircraft_registration, airport.name AS departure_airport_name, actual_arrival AS arrival_time FROM flights
    JOIN airport ON flights.origin_icao = airport.icao_code
    WHERE flights.destination_code = (
        SELECT icao_code FROM airport 
        WHERE iata_code = "DEL")
    ORDER BY arrival_time DESC
    LIMIT 5
    """

    df = pd.read_sql(query, conn)
    st.subheader("Recent Arrivals at DEL")
    st.dataframe(df)
    st.info(f"{len(df)} records found.")

elif analysis == "Airports with No Arrivals":

    query = """
    SELECT airport.icao_code,
           airport.name,
           airport.city
    FROM airport
    LEFT JOIN flights
        ON airport.icao_code = flights.destination_code
    WHERE flights.destination_code IS NULL
    """

    df = pd.read_sql(query, conn)
    st.subheader("Airports with No Arriving Flights")
    st.info(f"{len(df)} records found.")

    if df.empty:
        st.success(
            "All airports in the current dataset have at least one arriving flight."
        )
    else:
        st.dataframe(df)

elif analysis == "Airline Status Summary":

    query = """
SELECT
    airline_code,

    SUM(
        CASE
            WHEN scheduled_departure = actual_departure
            THEN 1
            ELSE 0
        END
    ) AS on_time,

    SUM(
        CASE
            WHEN actual_departure > scheduled_departure
            THEN 1
            ELSE 0
        END
    ) AS delayed_flights,

    SUM(
        CASE
            WHEN actual_departure IS NULL
            THEN 1
            ELSE 0
        END
    ) AS cancelled

FROM flights
GROUP BY airline_code
    """

    df = pd.read_sql(query, conn)
    st.subheader("Airline Status Summary")
    st.dataframe(df)
    st.info(f"{len(df)} records found.")

elif analysis == "Cancelled Flights":

    query = """
    SELECT flight_id, aircraft_registration, a1.name AS departure_airport, a2.name AS arrival_airport, scheduled_departure FROM flights
    LEFT JOIN airport a1 ON flights.origin_icao = a1.icao_code
    LEFT JOIN airport a2 ON flights.destination_code = a2.icao_code
    WHERE flights.status = 'Canceled' OR flights.actual_departure IS NULL
    ORDER BY scheduled_departure DESC
    """

    df = pd.read_sql(query, conn)
    st.subheader("Cancelled Flights")
    st.dataframe(df)
    st.info(f"{len(df)} records found.")

elif analysis == "City Pairs with Multiple Aircraft Models":

    query = """
    SELECT a1.city AS departure_city, a2.city AS destination_city, COUNT(DISTINCT aircraft.model) AS model_count FROM flights
    JOIN airport a1 ON flights.origin_icao = a1.icao_code
    JOIN airport a2 ON flights.destination_code = a2.icao_code
    JOIN aircraft ON flights.aircraft_registration = aircraft.registration
    GROUP BY departure_city, destination_city
    HAVING model_count > 2
    ORDER BY model_count DESC
    """

    df = pd.read_sql(query, conn)
    st.subheader("City Pairs with Multiple Aircraft Models")
    st.dataframe(df)
    st.info(f"{len(df)} records found.")

elif analysis == "Destination Delay Percentage":

    query = """
    SELECT airport.name AS destination_airport, COUNT(*) AS total_arrivals,
    SUM(
        CASE
            WHEN actual_arrival > scheduled_arrival THEN 1
            ELSE 0
        END
    ) AS delayed_arrivals,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN actual_arrival > scheduled_arrival THEN 1
                ELSE 0
            END
        ) / COUNT(*),2
    ) AS delayed_percentage
    FROM flights
    JOIN airport on flights.destination_code = airport.icao_code
    GROUP BY airport.icao_code, destination_airport
    ORDER BY delayed_percentage DESC
    """

    df = pd.read_sql(query, conn)
    st.subheader("Destination Delay Percentage")
    st.dataframe(df)
    st.info(f"{len(df)} records found.")

    fig = px.bar(
    df.head(10),
    x="destination_airport",
    y="delayed_percentage",
    title="Top Delayed Destination Airports")

    st.plotly_chart(fig, use_container_width=True)

cursor.close()
conn.close()
