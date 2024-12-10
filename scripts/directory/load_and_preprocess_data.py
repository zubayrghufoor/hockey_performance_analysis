import os
import pandas as pd

def load_and_preprocess_data(raw_data_path, processed_data_path):
    """
    Load and preprocess match day data, then save it separately for each match day.

    Args:
        raw_data_path (str): Path to the raw_data/game_data directory.
        processed_data_path (str): Path to save the processed data.
    """
    # Get a list of all match folders
    match_folders = [f for f in os.listdir(raw_data_path) if f.startswith('match_')]

    # Loop through each match folder
    for match_folder in match_folders:
        match_path = os.path.join(raw_data_path, match_folder)
        match_date = match_folder.split('_')[-1]  # Extract the date from the folder name

        # Create a directory to save processed data for this match day
        match_processed_path = os.path.join(processed_data_path, f"match_{match_date}")
        os.makedirs(match_processed_path, exist_ok=True)

        print(f"Processing data for {match_date}...")

        # Load and save each data type
        data_types = ['heart_rate', 'gps_location', 'steps', 'calories', 'distance', 'active_zone_minutes_day', 'UserExercises']
        for data_type in data_types:
            file_name = f"{data_type}_{match_date}.csv"
            file_path = os.path.join(match_path, file_name)

            try:
                # Load the data
                data = pd.read_csv(file_path)
                # Save the data in the processed folder
                processed_file_path = os.path.join(match_processed_path, f"{data_type}.csv")
                data.to_csv(processed_file_path, index=False)
                print(f"Saved {data_type} data for {match_date}.")
            except FileNotFoundError:
                print(f"File not found: {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    print("Finished processing all matches.")

# Paths to raw and processed data
raw_data_path = './raw_data/game_data'
processed_data_path = './processed_data'

# Run the function
load_and_preprocess_data(raw_data_path, processed_data_path)