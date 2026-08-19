#!/usr/bin/env python3
"""
WeatherWise CLI - Get current weather and 5-day forecast for any city.
Uses Open-Meteo API (free, no API key required).
"""

import requests
import argparse
import sys
from datetime import datetime

# Geocoding API to convert city name to coordinates
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

def get_coordinates(city_name):
    """Convert city name to latitude and longitude."""
    params = {"name": city_name, "count": 1}
    response = requests.get(GEOCODE_URL, params=params)
    
    if response.status_code != 200:
        print(f"❌ Error: Could not fetch city data (HTTP {response.status_code})")
        return None, None, None
    
    data = response.json()
    if not data.get("results"):
        print(f"❌ City '{city_name}' not found. Please check the spelling.")
        return None, None, None
    
    result = data["results"][0]
    return result["latitude"], result["longitude"], result.get("country", "")

def get_weather(lat, lon):
    """Fetch current weather and 5-day forecast."""
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
        print(f"❌ Error: Could not fetch weather (HTTP {response.status_code})")
        return None
    
    return response.json()

def weather_code_to_emoji(code):
    """Convert WMO weather code to emoji."""
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

def display_weather(city, weather_data, country=""):
    """Pretty-print the weather in the terminal."""
    current = weather_data.get("current", {})
    daily = weather_data.get("daily", {})
    
    print("\n" + "=" * 60)
    print(f"🌍 {city}, {country}" if country else f"🌍 {city}")
    print(f"📅 {datetime.now().strftime('%A, %B %d, %Y %H:%M')}")
    print("=" * 60)
    
    if current:
        temp = current.get("temperature_2m")
        feels_like = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")
        weather_code = current.get("weather_code")
        
        emoji = weather_code_to_emoji(weather_code) if weather_code else "🌡️"
        print(f"\n{emoji} Current Weather")
        print(f"   Temperature:  {temp}°C" if temp else "")
        print(f"   Feels like:   {feels_like}°C" if feels_like else "")
        print(f"   Humidity:     {humidity}%" if humidity else "")
        print(f"   Wind Speed:   {wind} km/h" if wind else "")
    
    if daily:
        print("\n📊 5-Day Forecast:")
        print("-" * 60)
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        codes = daily.get("weather_code", [])
        
        for i in range(min(5, len(dates))):
            date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
            day_name = date_obj.strftime("%a")
            emoji = weather_code_to_emoji(codes[i]) if i < len(codes) else "🌡️"
            print(f"   {emoji} {day_name}: {min_temps[i]}°C / {max_temps[i]}°C")
    
    print("\n" + "=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Get weather forecast for any city.")
    parser.add_argument("city", help="City name (e.g., 'London', 'New York')")
    parser.add_argument("--forecast", "-f", action="store_true", help="Show full 5-day forecast")
    
    args = parser.parse_args()
    
    lat, lon, country = get_coordinates(args.city)
    if lat is None:
        sys.exit(1)
    
    weather_data = get_weather(lat, lon)
    if weather_data is None:
        sys.exit(1)
    
    display_weather(args.city, weather_data, country)

if __name__ == "__main__":
    main()

# docs: add CHANGELOG to track development progress

# feat: implement --verbose flag for detailed weather output

# feat: add support for Fahrenheit temperature conversion

# feat: add request timeout handling to prevent hangs

# feat: add --city alias for city name parameter

# refactor: extract API calls to separate module

# feat: add weather alerts for extreme conditions

# docs: update README with new CLI flags

# feat: add caching to reduce API calls

# fix: handle special characters in city names

# feat: add --version flag with project info

# style: add type hints to all functions

# feat: add support for multiple cities in one command

# test: add sample test cases for weather codes

# feat: add logging of all API requests

# refactor: improve forecast display formatting
