import requests
import folium
import plotly.express as px
import pandas as pd
import schedule
import time

# API Endpoints
EONET_API = "https://eonet.gsfc.nasa.gov/api/v3/events"
WEATHER_API = "https://api.openweathermap.org/data/2.5/weather"

# OpenWeatherMap API Key
WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"

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

def update_visualizations():
    """Fetch new data and update the visualizations."""
    print("Fetching updated satellite data...")
    events_df = fetch_satellite_data()

    if not events_df.empty:
        create_interactive_map(events_df)
        create_plotly_chart(events_df)
    else:
        print("No active satellite events found.")

if __name__ == "__main__":
    update_visualizations()

    # Auto-refresh every 30 minutes
    schedule.every(30).minutes.do(update_visualizations)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
