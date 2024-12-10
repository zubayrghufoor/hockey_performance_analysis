import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.ndimage import gaussian_filter

# Constants for pitch dimensions (meters)
PITCH_LENGTH = 91.4  # Standard length of a hockey pitch
PITCH_WIDTH = 55.0   # Standard width of a hockey pitch
M_PER_LAT = 111_000  # Approx meters per degree latitude
M_PER_LON = 85_000   # Approx meters per degree longitude (varies by latitude)

# Paths
processed_data_dir = "./processed_data"
output_dir = "./outputs/heatmaps"
os.makedirs(output_dir, exist_ok=True)

def load_gps_data(match_date):
    gps_file = os.path.join(processed_data_dir, f"match_{match_date}/gps_location.csv")
    if not os.path.exists(gps_file):
        print(f"No GPS data found for {match_date}. Skipping.")
        return None
    return pd.read_csv(gps_file)

def convert_to_pitch_coords(gps_data, center_lat, center_lon):
    gps_data = gps_data.copy()  # Avoid SettingWithCopyWarning
    gps_data['latitude_m'] = (gps_data['latitude'] - center_lat) * M_PER_LAT
    gps_data['longitude_m'] = (gps_data['longitude'] - center_lon) * M_PER_LON
    return gps_data

def generate_heatmap(gps_data, match_date, match_start, match_end):
    if gps_data is None or gps_data.empty:
        print(f"No GPS data available for {match_date}. Skipping heatmap.")
        return

    # Convert timestamp to datetime and make timezone-naive
    gps_data['timestamp'] = pd.to_datetime(gps_data['timestamp'], errors='coerce').dt.tz_localize(None)

    # Filter data within match timeframe
    filtered_data = gps_data[(gps_data['timestamp'] >= match_start) & (gps_data['timestamp'] <= match_end)]

    if filtered_data.empty:
        print(f"No GPS data within match timeframe for {match_date}. Skipping heatmap.")
        return

    # Calculate pitch center and convert GPS data
    center_lat = filtered_data['latitude'].mean()
    center_lon = filtered_data['longitude'].mean()
    filtered_data = convert_to_pitch_coords(filtered_data, center_lat, center_lon)

    # Filter points within pitch dimensions
    filtered_data = filtered_data[
        (filtered_data['latitude_m'] >= -PITCH_LENGTH / 2) &
        (filtered_data['latitude_m'] <= PITCH_LENGTH / 2) &
        (filtered_data['longitude_m'] >= -PITCH_WIDTH / 2) &
        (filtered_data['longitude_m'] <= PITCH_WIDTH / 2)
    ]

    if filtered_data.empty:
        print(f"No valid GPS data within pitch dimensions for {match_date}. Skipping heatmap.")
        return

    # Create 2D histogram for heatmap
    heatmap, xedges, yedges = np.histogram2d(
        filtered_data['longitude_m'], filtered_data['latitude_m'], bins=[55, 91], range=[[-PITCH_WIDTH / 2, PITCH_WIDTH / 2], [-PITCH_LENGTH / 2, PITCH_LENGTH / 2]]
    )
    heatmap = gaussian_filter(heatmap, sigma=1)

    # Plot the heatmap
    plt.figure(figsize=(10, 7))
    plt.imshow(heatmap.T, extent=[-PITCH_WIDTH / 2, PITCH_WIDTH / 2, -PITCH_LENGTH / 2, PITCH_LENGTH / 2], origin='lower', cmap='YlOrRd')
    plt.colorbar(label='Density')

    # Add pitch markings
    plt.axhline(0, color='black', linestyle='--', linewidth=1)  # Halfway line
    plt.gca().add_patch(Circle((0, PITCH_LENGTH / 4), 9, color='black', fill=False, linewidth=1))  # Top circle
    plt.gca().add_patch(Circle((0, -PITCH_LENGTH / 4), 9, color='black', fill=False, linewidth=1))  # Bottom circle

    plt.xlim(-PITCH_WIDTH / 2, PITCH_WIDTH / 2)
    plt.ylim(-PITCH_LENGTH / 2, PITCH_LENGTH / 2)
    plt.title(f"Heatmap for Match {match_date}")
    plt.xlabel("Width (m)")
    plt.ylabel("Length (m)")

    # Save the plot
    heatmap_file = os.path.join(output_dir, f"heatmap_{match_date}.png")
    plt.savefig(heatmap_file, dpi=300)
    plt.close()
    print(f"Heatmap for match {match_date} saved to {heatmap_file}.")

# Load match schedule
schedule_path = "./reference_data/hockey_matches_schedule.csv"
schedule = pd.read_csv(schedule_path)
schedule['date'] = pd.to_datetime(schedule['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
schedule['match_start'] = pd.to_datetime(schedule['date'] + ' ' + schedule['start_time'], errors='coerce')
schedule['match_end'] = pd.to_datetime(schedule['date'] + ' ' + schedule['end_time'], errors='coerce')

# Iterate over matches
for _, match in schedule.iterrows():
    match_date = match['date']
    match_start = match['match_start']
    match_end = match['match_end']
    gps_data = load_gps_data(match_date)
    generate_heatmap(gps_data, match_date, match_start, match_end)

print("Heatmap generation completed.")