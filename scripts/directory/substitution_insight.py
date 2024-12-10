import os
import pandas as pd
from datetime import datetime, timedelta

# Step 1: Load the match schedule
schedule_path = "./reference_data/hockey_matches_schedule.csv"
schedule = pd.read_csv(schedule_path)

# Convert date and time columns into a single datetime column
schedule['date'] = pd.to_datetime(schedule['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
schedule['match_start'] = pd.to_datetime(schedule['date'] + ' ' + schedule['start_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
schedule['match_end'] = pd.to_datetime(schedule['date'] + ' ' + schedule['end_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Add tolerance periods
schedule['tolerance_start'] = schedule['match_start'] - timedelta(minutes=5)
schedule['tolerance_end'] = schedule['match_end'] + timedelta(minutes=10)

# Add half-time period
schedule['halftime_start'] = schedule['match_start'] + timedelta(minutes=35)
schedule['halftime_end'] = schedule['halftime_start'] + timedelta(minutes=10)

# Create match periods that exclude halftime
schedule['first_half_start'] = schedule['tolerance_start']
schedule['first_half_end'] = schedule['halftime_start']
schedule['second_half_start'] = schedule['halftime_end']
schedule['second_half_end'] = schedule['tolerance_end']

# Step 2: Prepare to filter match data
processed_data_dir = "./processed_data/"
output_folder = "./outputs/substitution_recommendations/"

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

def load_match_data(match_date):
    match_data_path = os.path.join(processed_data_dir, f"match_{match_date}")
    if not os.path.exists(match_data_path):
        print(f"No data folder for match {match_date}. Skipping.")
        return None

    data = {}
    data_types = ['heart_rate', 'gps_location', 'steps', 'calories', 'distance', 'active_zone_minutes_day', 'UserExercises']

    for data_type in data_types:
        file_path = os.path.join(match_data_path, f"{data_type}.csv")
        if os.path.exists(file_path):
            data[data_type] = pd.read_csv(file_path)
        else:
            print(f"File not found: {file_path}")
            data[data_type] = None

    return data

def generate_substitution_recommendations(match_date, start_time, end_time, data, age):
    recommendations = []
    min_time_on_pitch = timedelta(minutes=5)
    last_substitution_time = start_time.tz_localize(None)

    # HRmax and high-effort threshold
    hr_max = 220 - age
    high_heart_rate_threshold = 0.8 * hr_max  # Lower threshold for high effort

    # Filter heart rate data
    heart_rate = data.get("heart_rate", pd.DataFrame())
    if heart_rate is not None and not heart_rate.empty:
        heart_rate['timestamp'] = pd.to_datetime(heart_rate['timestamp']).dt.tz_localize(None)
        hr_filtered = heart_rate[(heart_rate['timestamp'] >= start_time) & 
                                  (heart_rate['timestamp'] <= end_time)].copy()

        # Identify high-effort zones
        hr_filtered['effort'] = hr_filtered['beats per minute'] > high_heart_rate_threshold
        hr_filtered['effort_period'] = hr_filtered['effort'].astype(int).rolling(window=240, min_periods=1).sum()  # Adjusted to 240 seconds
        fatigue_periods = hr_filtered[hr_filtered['effort_period'] >= 240]  # Adjusted threshold

        for _, row in fatigue_periods.iterrows():
            current_time = row['timestamp']
            if current_time - last_substitution_time >= min_time_on_pitch:
                recommendations.append(f"{current_time}: Sustained high heart rate detected. Consider substitution.")
                last_substitution_time = current_time

    # Filter and preprocess distance data
    distance = data.get("distance", pd.DataFrame())
    if distance is not None and not distance.empty:
        distance['timestamp'] = pd.to_datetime(distance['timestamp']).dt.tz_localize(None)
        dist_filtered = distance[(distance['timestamp'] >= start_time) & 
                                  (distance['timestamp'] <= end_time)].copy()

        # Calculate time differences and distance differences
        dist_filtered['time_diff'] = dist_filtered['timestamp'].diff().dt.total_seconds().fillna(0)
        dist_filtered['distance_diff'] = dist_filtered['distance'].diff().fillna(0)
        dist_filtered['rate_of_change'] = dist_filtered['distance_diff'] / dist_filtered['time_diff']

        # Define a threshold for significant drops in rate of change
        static_threshold = -0.3  # More permissive
        dynamic_threshold = dist_filtered['rate_of_change'].quantile(0.4)  # Increase dynamic threshold percentile
        drop_threshold = min(static_threshold, dynamic_threshold)

        # Identify sustained drops (rate below threshold for 2 out of 5 intervals)
        dist_filtered['drop_detected'] = dist_filtered['rate_of_change'] < drop_threshold
        dist_filtered['sustained_drop'] = dist_filtered['drop_detected'].rolling(window=5, min_periods=1).sum() >= 2  # Adjusted to require 2 intervals

        # Trigger recommendations for sustained drops
        sustained_drops = dist_filtered[dist_filtered['sustained_drop']]
        for _, row in sustained_drops.iterrows():
            current_time = row['timestamp']
            if current_time - last_substitution_time >= min_time_on_pitch:
                recommendations.append(f"{current_time}: Sustained significant drop in movement rate detected. Consider substitution.")
                last_substitution_time = current_time

    return recommendations

# Step 3: Iterate over matches and analyze data
for _, match in schedule.iterrows():
    match_date = match['date']
    tolerance_start = match['tolerance_start']
    tolerance_end = match['tolerance_end']

    # Load match data
    match_data = load_match_data(match_date)
    if match_data is None:
        continue

    # Generate recommendations
    recommendations = generate_substitution_recommendations(
        match_date,
        tolerance_start,
        tolerance_end,
        match_data,
        age=22  # Replace with the user's age
    )
    
    # Step 4: Save recommendations
    output_path = os.path.join(output_folder, f"substitution_recommendations_{match_date}.txt")
    with open(output_path, "w") as file:
        file.write("\n".join(recommendations))
    print(f"Recommendations for {match_date} saved to {output_path}.")