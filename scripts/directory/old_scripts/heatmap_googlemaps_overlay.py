import os
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image

# Paths
processed_data_dir = "./processed_data"  # Directory for GPS data
output_dir = "./outputs/heatmaps"  # Directory for heatmaps
output_dir2 = "./outputs/heatmaps/centre"  # Directory for map screenshots
os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_dir2, exist_ok=True)

# Load Match Schedule
schedule_path = "./reference_data/hockey_matches_schedule.csv"
schedule = pd.read_csv(schedule_path)

# Clean column names
schedule.columns = schedule.columns.str.strip()

# Process match timings
schedule['date'] = pd.to_datetime(schedule['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
schedule['match_start'] = pd.to_datetime(schedule['date'] + ' ' + schedule['start_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
schedule['match_end'] = pd.to_datetime(schedule['date'] + ' ' + schedule['end_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Add tolerance periods
schedule['tolerance_start'] = schedule['match_start'] - timedelta(minutes=5)
schedule['tolerance_end'] = schedule['match_end'] + timedelta(minutes=10)

# Add half-time period
schedule['halftime_start'] = schedule['match_start'] + timedelta(minutes=35)
schedule['halftime_end'] = schedule['halftime_start'] + timedelta(minutes=10)

# Create match periods excluding halftime
schedule['first_half_start'] = schedule['tolerance_start']
schedule['first_half_end'] = schedule['halftime_start']
schedule['second_half_start'] = schedule['halftime_end']
schedule['second_half_end'] = schedule['tolerance_end']

# Debugging - Check the processed schedule
print(schedule.columns)  # Print column names
print(schedule.head())  # Print first few rows


# Function to load GPS data
def load_gps_data(match_date, start_time, end_time):
    """
    Load GPS data for a specific match date and filter by the match timeframe.
    """
    gps_file = os.path.join(processed_data_dir, f"match_{match_date}/gps_location.csv")
    if not os.path.exists(gps_file):
        print(f"GPS data not found for match {match_date}. Skipping.")
        return None

    gps_data = pd.read_csv(gps_file)

    # Convert timestamp to datetime
    gps_data['timestamp'] = pd.to_datetime(gps_data['timestamp'])

    # Convert GPS timestamps and match times to timezone-naive for comparison
    gps_data['timestamp'] = gps_data['timestamp'].dt.tz_localize(None)
    start_time = start_time.tz_localize(None) if start_time.tzinfo else start_time
    end_time = end_time.tz_localize(None) if end_time.tzinfo else end_time

    # Filter GPS data based on match timeframe
    gps_data = gps_data[(gps_data['timestamp'] >= start_time) & (gps_data['timestamp'] <= end_time)]
    
    if gps_data.empty:
        print(f"No GPS data within timeframe for match {match_date}.")
        return None

    return gps_data


# Function to generate a map without heatmap
def generate_map_without_heatmap(gps_data, match_date):
    """
    Generate a map centered on GPS data and save it without a heatmap overlay.
    """
    latitudes = gps_data['latitude'].tolist()
    longitudes = gps_data['longitude'].tolist()
    map_center = [np.mean(latitudes), np.mean(longitudes)]

    mymap = folium.Map(location=map_center, zoom_start=18)

    folium.TileLayer(
        tiles='https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Maps',
        overlay=False,
        control=True
    ).add_to(mymap)

    map_html_path = os.path.join(output_dir, f"map_without_heatmap_{match_date}.html")
    mymap.save(map_html_path)
    print(f"Map HTML saved for match {match_date} at {map_html_path}")

    screenshot_path = os.path.join(output_dir2, f"map_without_heatmap_{match_date}.png")
    save_map_as_image(map_html_path, screenshot_path)


# Function to save map screenshot
def save_map_as_image(html_path, screenshot_path):
    """
    Use Selenium to render the map HTML and save it as an image.
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(f"file://{os.path.abspath(html_path)}")
        time.sleep(3)
        driver.save_screenshot(screenshot_path)
        print(f"Map screenshot saved at {screenshot_path}")
    finally:
        driver.quit()


# Function to overlay heatmap on the map screenshot
def add_heatmap_to_image(screenshot_path, gps_data, match_date):
    """
    Add a heatmap to the map screenshot and save the final image.
    """
    latitudes = gps_data['latitude'].tolist()
    longitudes = gps_data['longitude'].tolist()

    mymap = folium.Map(location=[np.mean(latitudes), np.mean(longitudes)], zoom_start=18)

    folium.TileLayer(
        tiles='https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Maps',
        overlay=False,
        control=True
    ).add_to(mymap)

    heat_data = [[lat, lon] for lat, lon in zip(latitudes, longitudes)]
    HeatMap(heat_data).add_to(mymap)

    heatmap_html_path = os.path.join(output_dir2, f"temp_heatmap_{match_date}.html")
    mymap.save(heatmap_html_path)

    temp_screenshot_path = os.path.join(output_dir2, f"temp_heatmap_{match_date}.png")
    save_map_as_image(heatmap_html_path, temp_screenshot_path)

    screenshot = Image.open(screenshot_path)
    heatmap = Image.open(temp_screenshot_path).resize(screenshot.size)

    final_image = Image.blend(screenshot.convert("RGBA"), heatmap.convert("RGBA"), alpha=0.5)
    final_image_path = os.path.join(output_dir2, f"final_map_with_heatmap_{match_date}.png")
    final_image.save(final_image_path)
    print(f"Final map with heatmap saved at {final_image_path}")


# Process Matches
for idx, match in schedule.iterrows():
    match_date = match['date']
    match_start = match['tolerance_start']
    match_end = match['tolerance_end']

    gps_data = load_gps_data(match_date, match_start, match_end)
    if gps_data is None:
        continue

    generate_map_without_heatmap(gps_data, match_date)
    add_heatmap_to_image(os.path.join(output_dir2, f"map_without_heatmap_{match_date}.png"), gps_data, match_date)

print("Map generation and heatmap overlay completed.")