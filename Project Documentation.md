#📜 Code Explanation: Real-Time Satellite Data Visualizer

This Python script fetches real-time natural disaster events from NASA’s EONET API and overlays them on an interactive map using Folium and Plotly. Additionally, it integrates OpenWeatherMap to display live weather data for each event location.


---

📌 1. Dependencies & API Endpoints

import requests
import folium
import plotly.express as px
import pandas as pd
import schedule
import time

requests → Fetch data from APIs.

folium → Create an interactive map.

plotly.express → Generate a scatter plot of events.

pandas → Store and manipulate event data.

schedule → Automate script execution every 30 minutes.

time → Add delays for smooth execution.


EONET_API = "https://eonet.gsfc.nasa.gov/api/v3/events"
WEATHER_API = "https://api.openweathermap.org/data/2.5/weather"

WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"

NASA EONET API → Fetches real-time natural disaster events.

OpenWeatherMap API → Retrieves weather details for event locations.

WEATHER_API_KEY → Replace with your OpenWeatherMap API key.



---

📌 2. Fetching Satellite Event Data

def fetch_satellite_data():
    """Fetch active natural events from NASA EONET API."""
    try:
        response = requests.get(EONET_API, params={"status": "open"})
        response.raise_for_status()
        data = response.json()
        
        events = []
        for event in data['events']:
            if 'geometries' in event and event['geometries']:
                coords = event['geometries'][0]['coordinates']
                events.append({
                    "title": event['title'],
                    "category": event['categories'][0]['title'],
                    "longitude": coords[0],
                    "latitude": coords[1]
                })
        
        return pd.DataFrame(events)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching satellite data: {e}")
        return pd.DataFrame()

Sends a request to NASA’s EONET API to retrieve active events.

Extracts title, category, latitude, and longitude of each event.

Returns a Pandas DataFrame containing the event data.

Handles API errors gracefully and returns an empty DataFrame if there’s an issue.



---

📌 3. Fetching Real-Time Weather Data

def fetch_weather_data(lat, lon):
    """Fetch real-time weather data for a given location."""
    try:
        params = {"lat": lat, "lon": lon, "appid": WEATHER_API_KEY, "units": "metric"}
        response = requests.get(WEATHER_API, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"]
        }
    except requests.exceptions.RequestException:
        return None

Sends a request to OpenWeatherMap for temperature, humidity, and weather conditions.

Uses latitude and longitude to get weather for specific event locations.

Handles API failures and returns None if the request fails.



---

📌 4. Creating an Interactive Folium Map

def create_interactive_map(events_df):
    """Generate an interactive map with event markers and weather data."""
    m = folium.Map(location=[0, 0], zoom_start=2)

    for _, event in events_df.iterrows():
        weather = fetch_weather_data(event['latitude'], event['longitude'])
        weather_info = f"<br>Temp: {weather['temperature']}°C, Humidity: {weather['humidity']}%" if weather else ""

        folium.Marker(
            location=[event['latitude'], event['longitude']],
            popup=f"{event['title']} ({event['category']}){weather_info}",
            icon=folium.Icon(color="red")
        ).add_to(m)

    m.save("enhanced_satellite_map.html")
    print("Map saved as 'enhanced_satellite_map.html'.")

Creates a world map centered at [0, 0] (equator).

Loops through all satellite events and fetches weather data.

Adds interactive markers with event and weather details.

Saves the map as an HTML file (enhanced_satellite_map.html).



---

📌 5. Creating a Plotly Scatter Map

def create_plotly_chart(events_df):
    """Create a Plotly scatter map with event filters."""
    fig = px.scatter_geo(
        events_df,
        lat='latitude',
        lon='longitude',
        text='title',
        title="Enhanced Real-Time Satellite Event Visualization",
        color='category',
        template="plotly_dark"
    )
    
    fig.update_layout(geo=dict(showland=True))
    fig.show()

Uses Plotly to generate a scatter plot of satellite events.

Color-codes events by category.

Displays the map with a dark theme.



---

📌 6. Updating Visualizations

def update_visualizations():
    """Fetch new data and update the visualizations."""
    print("Fetching updated satellite data...")
    events_df = fetch_satellite_data()

    if not events_df.empty:
        create_interactive_map(events_df)
        create_plotly_chart(events_df)
    else:
        print("No active satellite events found.")

Calls fetch_satellite_data() to get the latest event data.

If events exist, it updates the Folium and Plotly maps.



---

📌 7. Auto-Refreshing Data Every 30 Minutes

if __name__ == "__main__":
    update_visualizations()

    # Auto-refresh every 30 minutes
    schedule.every(30).minutes.do(update_visualizations)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

Runs update_visualizations() once at startup.

Uses schedule to refresh the data every 30 minutes.

Keeps the script running in a continuous loop.



---

📊 Output

enhanced_satellite_map.html → Interactive Folium map (open in browser).

Plotly map → Automatically opens with real-time event visualization.

Console Logs → Fetch status and error handling messages.



---

🎯 Summary

✅ NASA EONET API → Fetches real-time satellite events.
✅ OpenWeatherMap API → Displays live weather data for each event.
✅ Folium Map → Saves as an interactive HTML file.
✅ Plotly Scatter Map → Color-coded real-time events.
✅ Auto-refreshes every 30 minutes.
✅ Error handling for API failures.


---
