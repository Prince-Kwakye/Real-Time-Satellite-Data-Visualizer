import requests
import folium
import plotly.express as px
import pandas as pd
import schedule
import time
from datetime import datetime

# API Endpoints
EONET_API = "https://eonet.gsfc.nasa.gov/api/v3/events"
WEATHER_API = "https://api.openweathermap.org/data/3.0/weather"

# OpenWeatherMap API Key
WEATHER_API_KEY = "YOUR_API_KEY_HERE"

def fetch_satellite_data():
    """Fetch active natural events from NASA EONET API with better error handling."""
    try:
        # Try with both open and all events to ensure we get data
        for status in ["open", "all"]:
            response = requests.get(EONET_API, params={"status": status, "limit": 50})
            response.raise_for_status()
            data = response.json()
            
            if data['events']:
                events = []
                for event in data['events']:
                    # Some events might have geometries in different places
                    geometries = event.get('geometries', []) or event.get('geometry', [])
                    if geometries:
                        coords = geometries[0]['coordinates']
                        # Handle coordinate order (lon, lat vs lat, lon)
                        if len(coords) >= 2:
                            longitude = coords[0] if abs(coords[0]) <= 180 else coords[1]
                            latitude = coords[1] if abs(coords[1]) <= 90 else coords[0]
                            
                            events.append({
                                "title": event['title'],
                                "category": event['categories'][0]['title'] if event['categories'] else "Unknown",
                                "longitude": longitude,
                                "latitude": latitude,
                                "date": event.get('geometry', [{}])[0].get('date', 'Unknown')
                            })
                
                if events:
                    return pd.DataFrame(events)
        
        print("No events found in EONET API response.")
        return pd.DataFrame()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching satellite data: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error processing satellite data: {e}")
        return pd.DataFrame()

def fetch_weather_data(lat, lon):
    """Fetch real-time weather data for a given location with better error handling."""
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(WEATHER_API, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "temperature": data.get("main", {}).get("temp", "N/A"),
            "humidity": data.get("main", {}).get("humidity", "N/A"),
            "weather": data.get("weather", [{}])[0].get("description", "N/A"),
            "wind_speed": data.get("wind", {}).get("speed", "N/A")
        }
    except requests.exceptions.RequestException as e:
        print(f"Weather API error for ({lat}, {lon}): {e}")
        return None
    except Exception as e:
        print(f"Unexpected weather processing error: {e}")
        return None

def create_interactive_map(events_df):
    """Generate an interactive map with event markers and weather data."""
    if events_df.empty:
        print("No events to display on map.")
        return
    
    # Set initial map view based on events
    avg_lat = events_df['latitude'].mean()
    avg_lon = events_df['longitude'].mean()
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=2)

    for _, event in events_df.iterrows():
        weather = fetch_weather_data(event['latitude'], event['longitude'])
        weather_info = ""
        if weather:
            weather_info = f"""
            <br><b>Weather:</b> {weather['weather']}
            <br><b>Temp:</b> {weather['temperature']}°C
            <br><b>Humidity:</b> {weather['humidity']}%
            <br><b>Wind:</b> {weather['wind_speed']} m/s
            """
            
        date_info = f"<br><b>Date:</b> {event['date']}" if 'date' in event and event['date'] != 'Unknown' else ""
        
        popup_content = f"""
        <b>{event['title']}</b>
        <br><b>Type:</b> {event['category']}
        {date_info}
        {weather_info}
        """
        
        folium.Marker(
            location=[event['latitude'], event['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    # Add timestamp
    folium.Marker(
        location=[-60, -180],
        icon=folium.DivIcon(
            html=f'<div style="font-size: 10pt">Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>'
        )
    ).add_to(m)

    m.save("enhanced_satellite_map.html")
    print("Map saved as 'enhanced_satellite_map.html'.")

def create_plotly_chart(events_df):
    """Create a Plotly scatter map with event filters."""
    if events_df.empty:
        print("No events to display in Plotly chart.")
        return
    
    fig = px.scatter_geo(
        events_df,
        lat='latitude',
        lon='longitude',
        hover_name='title',
        hover_data=['category', 'date'],
        title=f"Real-Time Satellite Event Visualization (Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')})",
        color='category',
        template="plotly_dark"
    )
    
    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor="rgb(212, 212, 212)",
            subunitcolor="rgb(255, 255, 255)",
            countrycolor="rgb(255, 255, 255)",
            showlakes=True,
            lakecolor="rgb(255, 255, 255)",
            showsubunits=True,
            showcountries=True,
            resolution=50
        ),
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    
    fig.write_html("interactive_events_plot.html")
    print("Plotly chart saved as 'interactive_events_plot.html'")
    fig.show()

def update_visualizations():
    """Fetch new data and update the visualizations with timestamp."""
    print(f"\n=== Updating visualizations at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    events_df = fetch_satellite_data()

    if not events_df.empty:
        print(f"Found {len(events_df)} events:")
        print(events_df[['title', 'category']].to_string(index=False))
        
        create_interactive_map(events_df)
        create_plotly_chart(events_df)
    else:
        print("No active satellite events found. Trying again later...")

if __name__ == "__main__":
    # Run immediately
    update_visualizations()

    # Auto-refresh every 30 minutes
    schedule.every(30).minutes.do(update_visualizations)
    
    print("\nAuto-refresh enabled. The visualizations will update every 30 minutes.")
    print("Press Ctrl+C to stop the script.\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nScript stopped by user.")
