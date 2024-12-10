import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

# Paths
processed_data_dir = "./processed_data"
output_dir = "./outputs/heatmaps"
os.makedirs(output_dir, exist_ok=True)

# Load Match Data
def load_gps_data(match_date):
    """
    Load GPS data for a specific match date.
    """
    gps_file = os.path.join(processed_data_dir, f"match_{match_date}/gps_location.csv")
    if not os.path.exists(gps_file):
        print(f"GPS data not found for match {match_date}. Skipping.")
        return None
    return pd.read_csv(gps_file)

def generate_heatmap(gps_data, match_date):
    """
    Generate and save a heatmap for GPS data.
    """
    if gps_data is None or gps_data.empty:
        print(f"No GPS data available for {match_date}. Heatmap not generated.")
        return

    # Convert timestamp to datetime
    gps_data['timestamp'] = pd.to_datetime(gps_data['timestamp'])

    # Extract coordinates for heatmap
    latitude = gps_data['latitude'].tolist()
    longitude = gps_data['longitude'].tolist()

    # Define the range for latitude and longitude
    latitude_range = [min(latitude), max(latitude)]
    longitude_range = [min(longitude), max(longitude)]

    # Create a 2D histogram for heatmap data
    heatmap, xedges, yedges = np.histogram2d(longitude, latitude, bins=60, range=[longitude_range, latitude_range])

    # Apply Gaussian filter for smooth shading
    heatmap = gaussian_filter(heatmap, sigma=1)

    # Plot the smooth 2D density plot
    plt.figure(figsize=(8, 6))

    # Create the density plot using imshow
    plt.imshow(heatmap.T, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], origin='lower', cmap='YlOrRd')

    # Add a color bar
    plt.colorbar(label='Density')

    # Set plot titles and labels
    plt.title(f'Heatmap for Match {match_date}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Save the plot to the output directory
    heatmap_file = os.path.join(output_dir, f"heatmap_{match_date}.png")
    plt.savefig(heatmap_file)
    plt.close()
    print(f"Heatmap for match {match_date} saved to {heatmap_file}.")

# Iterate Over Matches
schedule_path = "./reference_data/hockey_matches_schedule.csv"
schedule = pd.read_csv(schedule_path)
schedule['date'] = pd.to_datetime(schedule['date'], dayfirst=True).dt.strftime('%Y-%m-%d')

for _, match in schedule.iterrows():
    match_date = match['date']
    gps_data = load_gps_data(match_date)
    generate_heatmap(gps_data, match_date)

print("Heatmap generation completed.")