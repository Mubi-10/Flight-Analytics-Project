# ✈️ AeroDataBox Flight Explorer

## Project Description

AeroDataBox Flight Explorer is an interactive aviation analytics application developed using Python, MySQL, Streamlit, and Plotly. The project extracts and manages aviation data obtained from the AeroDataBox API, transforms it into a structured relational database, and presents meaningful operational insights through an intuitive web dashboard.

The application enables users to explore airport information, analyze flight schedules and statuses, monitor delays, and uncover patterns in airline operations. By combining SQL-based analysis with interactive visualizations, the dashboard supports both aviation enthusiasts and decision-makers in understanding airport networks and flight performance.

### Key Features

* **Homepage Dashboard**

  * Summary statistics including total airports, total flights, total aircraft, and average delay.
  * Visual overview of flight statuses and airline activity.

* **Flight Search**

  * Search flights by flight number or airline.
  * Filter flights based on status, origin, and other criteria.

* **Airport Explorer**

  * View airport details such as location, country, timezone, and related flight information.
  * Analyze airport activity and outbound traffic.

* **Delay Analysis**

  * Calculate and visualize delay percentages across airports.
  * Identify airports with the highest operational delays.

* **Route Leaderboards**

  * Discover the busiest routes and most frequently operated connections.
  * Compare traffic patterns between airports.

* **SQL Insights**

  * Perform advanced SQL analyses, including:

    * Flights per aircraft model
    * Aircraft assigned to multiple flights
    * Outbound and arriving flight statistics
    * Domestic vs. international flight classification
    * Recent arrivals at selected airports
    * Airline status summaries
    * Cancelled flight analysis
    * City pairs operated by multiple aircraft models
    * Destination delay percentages

## Technologies Used

* Python
* Streamlit
* MySQL
* Pandas
* Plotly Express
* AeroDataBox API
* SQL

## Business Use Cases

* Airport Exploration
* Flight Trend Analysis
* Operational Performance Monitoring
* Delay Analysis
* Scheduling and Resource Planning
* Data-Driven Decision Support

## Expected Outcome

The project delivers a fully functional aviation analytics dashboard capable of transforming raw flight data into actionable insights. Users can interactively explore airports, monitor delays, analyze routes, and generate meaningful operational intelligence through a modern web interface.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Mubi-10/Flight-Analytics-Project.git
cd Flight-Analytics-Project
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

> **Note:** Configure your database credentials in the `.env` file before running the application locally.
