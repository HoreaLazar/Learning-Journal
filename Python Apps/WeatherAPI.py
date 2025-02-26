import requests
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime
import time

def get_coordinates(city):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "WeatherApp/1.0"}
    response = requests.get(url, params=params, headers=headers)
    time.sleep(1)  # Delay to prevent rate-limiting

    if response.status_code == 200 and response.json():
        location = response.json()[0]
        return float(location["lat"]), float(location["lon"])
    else:
        print(f"Error getting coordinates for city '{city}': {response.status_code}, {response.json()}")
        return None, None

def get_weather(latitude, longitude, date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset"],
        "current_weather": True,
        "timezone": "auto",
        "start_date": date,
        "end_date": date
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting weather data: {response.status_code}, {response.json()}")
        return None

def fetch_weather():
    print("Fetch weather function called")
    city = city_entry.get().strip()
    print(f"City entered: {city}")
    if not city:
        messagebox.showerror("Error", "Please enter a city name.")
        return
    
    latitude, longitude = get_coordinates(city)
    print(f"Coordinates for {city}: Latitude: {latitude}, Longitude: {longitude}")
    if latitude is None or longitude is None:
        messagebox.showerror("Error", "Invalid city name. Please enter a valid location.")
        return
    
    selected_date_str = cal.get_date()  # Returns in 'MM/DD/YY'
    print(f"Selected date: {selected_date_str}")
    selected_date = datetime.strptime(selected_date_str, "%m/%d/%y")
    formatted_date = selected_date.strftime("%Y-%m-%d")  # Format to 'YYYY-MM-DD'
    print(f"Formatted date: {formatted_date}")

    weather_data = get_weather(latitude, longitude, formatted_date)
    print(f"Weather data: {weather_data}")
    if weather_data and 'daily' in weather_data:
        temp_max = weather_data['daily']['temperature_2m_max'][0]
        temp_min = weather_data['daily']['temperature_2m_min'][0]
        sunrise = weather_data['daily']['sunrise'][0] if 'sunrise' in weather_data['daily'] else "N/A"
        sunset = weather_data['daily']['sunset'][0] if 'sunset' in weather_data['daily'] else "N/A"
        current_temp = weather_data['current_weather']['temperature'] if 'current_weather' in weather_data else "N/A"

        # Split date and time for sunrise and sunset
        sunrise_time = sunrise.split('T')[1] if sunrise != "N/A" else "N/A"
        sunset_time = sunset.split('T')[1] if sunset != "N/A" else "N/A"

        # Improved handling of missing temperature data
        if temp_max is None:
            temp_max_display = "Max temperature data not available for this date."
        else:
            temp_max_display = f"{temp_max}°C"

        if temp_min is None:
            temp_min_display = "Min temperature data not available for this date."
        else:
            temp_min_display = f"{temp_min}°C"

        # Create the result text
        result_text = (f"City: {city}\nDate: {formatted_date}\nCurrent Temperature: {current_temp}°C\n"
                       f"Max Temperature: {temp_max_display}\nMin Temperature: {temp_min_display}\n"
                       f"Sunrise: {sunrise_time}\nSunset: {sunset_time}")
        print(f"Updating result label with: {result_text}")

        # Show the result in a popup window
        messagebox.showinfo("Weather Information", result_text)
    else:
        messagebox.showerror("Error", "Failed to retrieve weather data. Please check the city name and try again.")

# GUI Setup
root = tk.Tk()
root.title("Weather App")
root.geometry("400x400")

# City Entry
city_label = tk.Label(root, text="Enter City:")
city_label.pack(pady=5)
city_entry = tk.Entry(root)
city_entry.pack(pady=5)

# Date Picker
date_label = tk.Label(root, text="Select Date:")
date_label.pack(pady=5)
cal = Calendar(root, selectmode='day', year=2025, month=2, day=19)  # You can set this to any valid date
cal.pack(pady=5)

# Fetch Weather Button
fetch_button = tk.Button(root, text="Get Weather", command=fetch_weather)
fetch_button.pack(pady=10)

# Result Label
result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=20)

# Start the Tkinter main loop
root.mainloop()