# HockeyPerformanceAnalysis

This repository provides tools to analyze hockey performance data, including effort ratings, heatmaps, and 
substitution recommendations. The outputs are accessible through a user-friendly web application.

---

## Project Structure

- **docs/**
  - `readme.txt`: This file.

- **scripts/**
  - **directory/**
    - 'scripts/directory/load_and_preprocess_data.py': Loads and preprocesses data
    - `substitution_insight.py`: Generates substitution recommendations.
    - `effort_rating.py`: Computes effort ratings.
    - `heatmap_arbitrary_pitch.py`: Generates heatmaps for matches.
    - `web_app.py`: The main web application to view insights.

- **raw_data/**
  - Contains raw data files for each match.
  - Folder structure: `match_<YYYY-MM-DD>/gps_location.csv`, etc.

- **processed_data/**
  - Contains processed data files for each match.
  - Folder structure: `match_<YYYY-MM-DD>/gps_location.csv`, etc.

- **outputs/**
  - **substitution_recommendations/**: Text files with substitution recommendations.
  - **effort_ratings/**: CSV files with effort ratings.
  - **heatmaps/**: PNG files for match heatmaps.

- **reference_data/**
  - `hockey_matches_schedule.csv`: Match schedule and metadata.

---

## Prerequisites

### Software Requirements

- Python 3.10 or later
- Installed Python packages:
  - `streamlit`
  - `pandas`
  - `numpy`
  - `matplotlib`
  - `scipy`


### Data Requirements

For each match day, the following files should be uploaded into the `processed_data/match_<YYYY-MM-DD>` folder, containing only data about the specific match day. Ensure the files are formatted and named correctly:

1. **`gps_location.csv`**  
   - GPS data containing:  
     | `timestamp`          | `latitude` | `longitude` | `altitude` |  
     |-----------------------|------------|-------------|------------|  
     Example: Timestamps in ISO 8601 format, latitude/longitude in decimal degrees.

2. **`heart_rate.csv`**  
   - Heart rate data containing:  
     | `timestamp`          | `heart_rate` |  
     |-----------------------|--------------|  
     Example: Timestamp in ISO 8601 format, heart rate in beats per minute.

3. **`active_zone_minutes.csv`**  
   - Active zone minutes data containing:  
     | `timestamp`          | `heart_rate_zone` | `total_minutes` |  
     |-----------------------|-------------------|-----------------|  

4. **`calories.csv`**  
   - Calories burned data containing:  
     | `timestamp`          | `calories` |  
     |-----------------------|-----------|  

5. **`distance.csv`**  
   - Distance data containing:  
     | `timestamp`          | `distance` |  
     |-----------------------|-----------|  
     Example: Distance in meters.

6. **`steps.csv`**  
   - Steps data containing:  
     | `timestamp`          | `steps` |  
     |-----------------------|--------|  

7. **`user_exercises.csv`**  
   - User exercises data containing:  
     | `exercise_id` | `exercise_start` | `exercise_end` | `activity_name` | `distance_units` | `tracker_avg_heart_rate` | `tracker_total_distance_mm` | ... |  
     |---------------|------------------|----------------|-----------------|------------------|-------------------------|---------------------------|-----|  
     Example: A comprehensive exercise log with fields like start/end times, distance, and heart rate metrics.

---

Ensure that all the required files are available in the `processed_data/match_<YYYY-MM-DD>` folder before running the analysis scripts. Missing or incorrectly formatted files may lead to errors during processing.

## How to Run the Analysis

### Step 1: Generate Insights

Run the following Python files in sequence to generate the required outputs:

1. **Substitution Insights:**
   ```bash
   python ./scripts/directory/substitution_insight.py
   ```
   This will generate substitution recommendations in `outputs/substitution_recommendations/`.

2. **Effort Ratings:**
   ```bash
   python ./scripts/directory/effort_rating.py
   ```
   This will generate effort ratings in `outputs/effort_ratings/`.

3. **Heatmaps:**
   ```bash
   python ./scripts/directory/heatmap_arbitrary_pitch.py
   ```
   This will generate heatmaps in `outputs/heatmaps/`.

### Step 2: Launch the Web App

To view all insights in a web interface, run the following command:

```bash
streamlit run ./scripts/directory/web_app.py
```

This will launch the web application, accessible via your browser. You can use the dropdown menu to select specific match days and view detailed insights, including:

- Match details (opponent, home/away, goals scored, etc.).
- Effort ratings and contributing metrics.
- Heatmaps of player activity.
- Substitution recommendations with detailed reasons.

---

## Tips and Troubleshooting

### File Structure
Ensure all files are placed in the correct folders as per the project structure. Mismatched file names or missing data can lead to errors.

### Running Python Scripts
Always activate your Python environment (`hockeyenv`) before running scripts:

```bash
conda activate hockeyenv
```

### Common Errors
- **"No data available" in the web app:** Ensure the `processed_data/` folder contains the required files for each match day.
- **Heatmaps not generated:** Check if `gps_location.csv` contains valid GPS data.
- **Substitution recommendations not generated:** Ensure `heart_rate.csv` and `activity_summary.csv` have all required columns.


## Contact

For questions or contributions, please reach out to zubayrghufoor1@gmail.com.
