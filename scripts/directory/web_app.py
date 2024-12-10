import os
import streamlit as st
import pandas as pd
from PIL import Image

# Constants for directory paths
BASE_DIR = os.path.abspath(os.getcwd())
HEATMAP_DIR = os.path.join(BASE_DIR, "outputs", "heatmaps")
EFFORT_DIR = os.path.join(BASE_DIR, "outputs", "effort_ratings")
SUBSTITUTION_DIR = os.path.join(BASE_DIR, "outputs", "substitution_recommendations")

# Load match schedule
schedule_path = os.path.join(BASE_DIR, "reference_data", "hockey_matches_schedule.csv")
schedule = pd.read_csv(schedule_path)
schedule['date'] = pd.to_datetime(schedule['date'], dayfirst=True).dt.strftime('%Y-%m-%d')

# Add enhanced match titles
schedule['match_title'] = schedule.apply(
    lambda row: f"{row['date']} (vs {row['opponent']} - {'Home' if row['home_or_away'] == 'home' else 'Away'}, Goals: {row['user_goals_scored']})", axis=1
)

# Sidebar for match day selection
st.sidebar.title("Match Insights Viewer")
selected_match_date = st.sidebar.selectbox(
    "Select Match Date",
    options=schedule['date'],
    format_func=lambda x: schedule.loc[schedule['date'] == x, 'match_title'].values[0]
)

# Extract selected match details
selected_match_details = schedule.loc[schedule['date'] == selected_match_date].iloc[0]
match_opponent = selected_match_details['opponent']
match_location = "Home" if selected_match_details['home_or_away'] == 'home' else "Away"
user_goals = selected_match_details['user_goals_scored']
match_type = selected_match_details['match_type']
scoreline = selected_match_details['scoreline']
result = selected_match_details['result']

# Page title
st.title("Hockey Performance Analysis")
st.subheader(f"Insights for Match Date: {selected_match_date}")

# Display match details
st.markdown(
    f"""**Match Details:**

- **Opponent:** {match_opponent}  
- **Location:** {match_location}  
- **Goals Scored by You:** {user_goals}  
- **Match Type:** {match_type}  
- **Scoreline:** {scoreline}  
- **Result:** {result}
"""
)

# Function to display effort rating
def display_effort_rating(selected_match_date):
    effort_file = os.path.join(EFFORT_DIR, f"effort_rating_{selected_match_date}.csv")
    if os.path.exists(effort_file):
        effort_data = pd.read_csv(effort_file)

        # Extract the effort rating (last value in the table)
        effort_rating = effort_data.iloc[0, -1]
        st.markdown(f"### **Effort Rating: {effort_rating:.1f}/10**")

        # Dynamically generate column names
        default_columns = ["Active Zone Minutes", "Calories", "Distance (m)", "Steps", "Avg Heart Rate", "Peak Heart Rate", "Effort Rating"]
        num_columns = len(effort_data.columns)

        if num_columns <= len(default_columns):
            effort_table_columns = default_columns[:num_columns]
        else:
            effort_table_columns = [f"Column {i+1}" for i in range(num_columns)]

        effort_table = effort_data.copy()
        effort_table.columns = effort_table_columns

        # Display the table with formatting
        st.table(effort_table.style.format({
            "Calories": "{:.0f}",
            "Distance (m)": "{:.0f}",
            "Steps": "{:,}",
            "Avg Heart Rate": "{:.1f}",
            "Peak Heart Rate": "{:.0f}",
        }))
    else:
        st.warning(f"No effort rating data available for {selected_match_date}.")

# Function to load and display heatmap
def display_heatmap(selected_match_date):
    heatmap_path = os.path.join(HEATMAP_DIR, f"heatmap_{selected_match_date}.png")
    if os.path.exists(heatmap_path):
        st.subheader("Heatmap")
        st.image(Image.open(heatmap_path), caption=f"Heatmap for {selected_match_date}", use_container_width=True)
    else:
        st.warning(f"No heatmap available for {selected_match_date}.")

# Function to load and display substitution recommendations
def display_substitution_recommendations(selected_match_date):
    substitution_file = os.path.join(SUBSTITUTION_DIR, f"substitution_recommendations_{selected_match_date}.txt")
    if os.path.exists(substitution_file):
        st.subheader("Substitution Recommendations")
        with open(substitution_file, "r") as file:
            substitution_data = file.readlines()

        formatted_subs = []
        for line in substitution_data:
            time, reason = line.strip().split(": ")
            reason_text = "movement" if "movement" in reason.lower() else "heart rate"
            formatted_subs.append(f"**{time}** - Substitution recommended due to significant drop in {reason_text}.")

        for sub in formatted_subs:
            st.markdown(f"- {sub}")
    else:
        st.warning(f"No substitution recommendations available for {selected_match_date}.")

# Display all insights
display_effort_rating(selected_match_date)
display_heatmap(selected_match_date)
display_substitution_recommendations(selected_match_date)

# Footer
st.sidebar.info("Select a match day from the sidebar to view insights.")
st.sidebar.markdown("[View Documentation](#)")