"""
UI chính riêng cho Decision Tree System
Hoàn toàn tách biệt với KNN UI
"""

import sys
import asyncio
import tkinter as tk
import os
import pandas as pd
import DecisionTree_data_handler as dt_handler
import DecisionTree_UI_elements as dt_elements

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Get data file paths
dir_path = os.path.dirname(os.path.abspath(__file__))
decision_games_csv_path = os.path.join(dir_path, "decision_games.csv")
decision_games_json_path = os.path.join(dir_path, "decision_games.json")

# Load decision games data
print("Loading Decision Tree data...")
df_decision_games = dt_handler.load_decision_games_csv(decision_games_csv_path)

if df_decision_games is None or df_decision_games.empty:
    print("Warning: Could not load decision_games.csv")
    df_decision_games = pd.DataFrame()

# Create games dictionary for UI
decision_games_dict = dt_handler.create_decision_games_dict(df_decision_games)

# Initialize user ratings dictionary
user_ratings_dict = {}

# Load existing ratings if available
ratings_file = os.path.join(dir_path, "dt_user_ratings.json")
if os.path.exists(ratings_file):
    ratings_data = dt_handler.load_decision_tree_data(ratings_file)
    if ratings_data:
        for item in ratings_data:
            if isinstance(item, dict):
                game_name = item.get('Name', '')
                rating = item.get('user_rating', 0)
                rating_text = {1: 'Dislike', 2: 'Bad', 3: 'Neutral', 4: 'Good', 5: 'Like'}
                user_ratings_dict[game_name] = f"Name: {game_name} ¬ Rating: {rating} ({rating_text.get(rating, 'Unknown')})"

# Create the main window
root = tk.Tk()
root.title('Game Recommendation - Decision Tree System')
root.geometry('1200x800')

# Header label để phân biệt với KNN
header_label = tk.Label(root, text='DECISION TREE RECOMMENDATION SYSTEM', 
                       font=('Arial', 16, 'bold'), fg='blue', bg='lightgray')
header_label.pack(pady=10)

# Games List (Decision Tree)
games_frame_dt = dt_elements.games_list_frame_dt(root, decision_games_dict)
search_frame_dt = dt_elements.search_frame_dt(root, decision_games_dict, games_frame_dt)

# User Ratings (Decision Tree)
user_ratings_frame_dt = dt_elements.user_ratings_frame_dt(root, user_ratings_dict)

# Rating Buttons (Decision Tree)
rating_buttons_frame_dt = dt_elements.rating_buttons_frame_dt(
    root, games_frame_dt, user_ratings_frame_dt, user_ratings_dict
)

# Preferences Frame (Decision Tree)
preferences_frame_dt, price_entry, ratio_entry = dt_elements.preferences_frame_dt(root)

# Recommendations Frame (Decision Tree)
recommendations_frame_dt = dt_elements.recommendations_frame_dt(
    root, user_ratings_dict, dir_path, df_decision_games
)

# Footer
footer_label = tk.Label(root, text='This is the Decision Tree System - Separate from KNN System', 
                       font=('Arial', 10), fg='gray')
footer_label.pack(pady=5)

print("Decision Tree UI initialized successfully!")
print(f"Loaded {len(decision_games_dict)} games")

root.mainloop()

