#!/usr/bin/env python3
"""
WeatherWise Web Dashboard - Flask server with live weather.
"""

from flask import Flask, render_template, request, jsonify
import requests
import datetime

app = Flask(__name__)

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

def get_coordinates(city_name):
    params = {"name": city_name, "count": 1}
    response = requests.get(GEOCODE_URL, params=params)
    if response.status_code != 200:
        return None, None, None
    data = response.json()
    if not data.get("results"):
        return None, None, None
    result = data["results"][0]
    return result["latitude"], result["longitude"], result.get("country", "")

def fetch_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 5
    }
    response = requests.get(WEATHER_URL, params=params)
    if response.status_code != 200:
        return None
    return response.json()

def weather_code_to_emoji(code):
    weather_map = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌧️", 55: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "⛈️",
        71: "❄️", 73: "❄️", 75: "❄️",
        80: "🌦️", 81: "🌧️", 82: "⛈️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return weather_map.get(code, "🌡️")

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    city = None
    country = None
    
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            lat, lon, country = get_coordinates(city)
            if lat:
                data = fetch_weather(lat, lon)
                if data:
                    current = data.get("current", {})
                    daily = data.get("daily", {})
                    
                    # Build forecast list
                    forecast = []
                    for i in range(min(5, len(daily.get("time", [])))):
                        forecast.append({
                            "date": daily["time"][i],
                            "min": daily["temperature_2m_min"][i],
                            "max": daily["temperature_2m_max"][i],
                            "emoji": weather_code_to_emoji(daily["weather_code"][i])
                        })
                    
                    weather = {
                        "temp": current.get("temperature_2m"),
                        "feels_like": current.get("apparent_temperature"),
                        "humidity": current.get("relative_humidity_2m"),
                        "wind": current.get("wind_speed_10m"),
                        "emoji": weather_code_to_emoji(current.get("weather_code")),
                        "forecast": forecast
                    }
    
    return render_template('index.html', city=city, country=country, weather=weather)

@app.route('/api/weather/<city>')
def api_weather(city):
    """JSON API endpoint for programmatic access."""
    lat, lon, country = get_coordinates(city)
    if lat is None:
        return jsonify({"error": "City not found"}), 404
    data = fetch_weather(lat, lon)
    if data is None:
        return jsonify({"error": "Weather fetch failed"}), 500
    return jsonify({"city": city, "country": country, "data": data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    
# docs: add CHANGELOG to track development progress

# feat: implement --verbose flag for detailed weather output

# feat: add support for Fahrenheit temperature conversion
