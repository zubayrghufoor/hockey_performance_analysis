import os
import pandas as pd

def calculate_effort_rating(match_date, data_folder, output_folder, global_max_min):
    """
    Calculate an effort rating (out of 10) for a given match day based on various metrics.

    Args:
        match_date (str): The date of the match (YYYY-MM-DD).
        data_folder (str): Path to the folder containing the match data.
        output_folder (str): Path to the folder where results will be saved.
        global_max_min (dict): Global max and min values for normalization.

    Returns:
        None: Saves the effort rating to a CSV file.
    """
    match_data_path = os.path.join(data_folder, f"match_{match_date}")
    if not os.path.exists(match_data_path):
        print(f"No data folder for match {match_date}. Skipping.")
        return

    # Ensure the effort ratings folder exists
    effort_ratings_folder = os.path.join(output_folder, "effort_ratings")
    os.makedirs(effort_ratings_folder, exist_ok=True)

    # Initialize effort components
    effort_components = {}

    # Load and process data
    def load_and_sum(file_path, column, key):
        if os.path.exists(file_path):
            data = pd.read_csv(file_path)
            effort_components[key] = data[column].sum()
        else:
            effort_components[key] = 0

    load_and_sum(os.path.join(match_data_path, "active_zone_minutes_day.csv"), "total minutes", "active_zone_minutes")
    load_and_sum(os.path.join(match_data_path, "calories.csv"), "calories", "calories")
    load_and_sum(os.path.join(match_data_path, "distance.csv"), "distance", "distance")
    load_and_sum(os.path.join(match_data_path, "steps.csv"), "steps", "steps")

    # Load heart rate data
    hr_path = os.path.join(match_data_path, "heart_rate.csv")
    if os.path.exists(hr_path):
        hr_data = pd.read_csv(hr_path)
        effort_components['avg_heart_rate'] = hr_data['beats per minute'].mean()
    else:
        effort_components['avg_heart_rate'] = 0

    # Load User Exercises
    exercises_path = os.path.join(match_data_path, "UserExercises.csv")
    if os.path.exists(exercises_path):
        exercises_data = pd.read_csv(exercises_path)
        effort_components['peak_exercise_heart_rate'] = exercises_data['tracker_peak_heart_rate'].max()
    else:
        effort_components['peak_exercise_heart_rate'] = 0

    # Global normalization
    normalized_components = {
        key: (value - global_max_min[key]['min']) / (global_max_min[key]['max'] - global_max_min[key]['min'])
        if global_max_min[key]['max'] > global_max_min[key]['min'] else 0
        for key, value in effort_components.items()
    }

    # Weighted combination with adjusted weights
    effort_rating = (
        (normalized_components.get('active_zone_minutes', 0) * 0.35) +
        (normalized_components.get('calories', 0) * 0.3) +
        (normalized_components.get('distance', 0) * 0.25) +
        (normalized_components.get('steps', 0) * 0.05) +
        (normalized_components.get('avg_heart_rate', 0) * 0.025) +
        (normalized_components.get('peak_exercise_heart_rate', 0) * 0.025)
    ) * 10  # Scale to 10

    # Add a boost factor without lower clipping
    boost_factor = 0.3
    effort_rating = round(effort_rating + boost_factor, 2)

    # Save the result
    output_path = os.path.join(effort_ratings_folder, f"effort_rating_{match_date}.csv")
    pd.DataFrame([{**effort_components, 'effort_rating': effort_rating}]).to_csv(output_path, index=False)
    print(f"Effort rating for {match_date} saved to {output_path}.")

def calculate_global_max_min(match_dates, data_folder):
    """
    Calculate global max and min values for each metric across all matches.

    Args:
        match_dates (list): List of match dates (YYYY-MM-DD).
        data_folder (str): Path to the folder containing the match data.

    Returns:
        dict: Dictionary with global max and min values for each metric.
    """
    metrics = ['active_zone_minutes', 'calories', 'distance', 'steps', 'avg_heart_rate', 'peak_exercise_heart_rate']
    global_max_min = {metric: {'max': float('-inf'), 'min': float('inf')} for metric in metrics}

    for match_date in match_dates:
        match_data_path = os.path.join(data_folder, f"match_{match_date}")
        if not os.path.exists(match_data_path):
            continue

        effort_components = {}

        # Load and sum data
        def load_and_sum(file_path, column, key):
            if os.path.exists(file_path):
                data = pd.read_csv(file_path)
                effort_components[key] = data[column].sum()
            else:
                effort_components[key] = 0

        load_and_sum(os.path.join(match_data_path, "active_zone_minutes_day.csv"), "total minutes", "active_zone_minutes")
        load_and_sum(os.path.join(match_data_path, "calories.csv"), "calories", "calories")
        load_and_sum(os.path.join(match_data_path, "distance.csv"), "distance", "distance")
        load_and_sum(os.path.join(match_data_path, "steps.csv"), "steps", "steps")

        # Heart rate
        hr_path = os.path.join(match_data_path, "heart_rate.csv")
        if os.path.exists(hr_path):
            hr_data = pd.read_csv(hr_path)
            effort_components['avg_heart_rate'] = hr_data['beats per minute'].mean()
        else:
            effort_components['avg_heart_rate'] = 0

        # User Exercises
        exercises_path = os.path.join(match_data_path, "UserExercises.csv")
        if os.path.exists(exercises_path):
            exercises_data = pd.read_csv(exercises_path)
            effort_components['peak_exercise_heart_rate'] = exercises_data['tracker_peak_heart_rate'].max()
        else:
            effort_components['peak_exercise_heart_rate'] = 0

        # Update global max and min
        for key, value in effort_components.items():
            if key in global_max_min:
                global_max_min[key]['max'] = max(global_max_min[key]['max'], value)
                global_max_min[key]['min'] = min(global_max_min[key]['min'], value)

    return global_max_min

# Example usage
if __name__ == "__main__":
    data_folder = "./processed_data"
    output_folder = "./outputs"
    os.makedirs(output_folder, exist_ok=True)
    match_dates = ["2024-10-09", "2024-10-16", "2024-10-30", "2024-11-06", "2024-11-13", "2024-11-27"]

    global_max_min = calculate_global_max_min(match_dates, data_folder)

    for match_date in match_dates:
        calculate_effort_rating(match_date, data_folder, output_folder, global_max_min)