"""
UI chính cho Content-Based Filtering System
Sử dụng Genres và Tags để recommend games
"""

import sys
import asyncio
import tkinter as tk
import os
import pandas as pd
import threading
import ContentBased_data_handler as cb_handler
import ContentBased_UI_elements as cb_elements
from ContentBased_model import ContentBasedRecommender

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Get data file paths
dir_path = os.path.dirname(os.path.abspath(__file__))
games_csv_path = os.path.join(dir_path, "CB_games.csv")

# Load games data
print("Loading games data...")
print("Please wait while loading data (this may take a few seconds for large files)...")

try:
    df_games = cb_handler.load_games_csv(games_csv_path)
    
    if df_games is None or df_games.empty:
        print("Warning: Could not load CB_games.csv")
        df_games = pd.DataFrame()
    
    # Create games dictionary for UI
    print(f"Processing {len(df_games)} games...")
    games_dict = cb_handler.create_games_dict(df_games)
    print(f"Successfully loaded {len(games_dict)} games")
except Exception as e:
    print(f"Error loading data: {str(e)}")
    df_games = pd.DataFrame()
    games_dict = {}

# Initialize user ratings dictionary
user_ratings_dict = {}

# Load existing ratings if available
ratings_file = os.path.join(dir_path, "cb_user_ratings.json")
if os.path.exists(ratings_file):
    ratings_data = cb_handler.load_ratings_data(ratings_file)
    if ratings_data:
        for item in ratings_data:
            if isinstance(item, dict):
                game_name = item.get('Name', '')
                rating = item.get('user_rating', 0)
                rating_text = {1: 'Dislike', 2: 'Bad', 3: 'Neutral', 4: 'Good', 5: 'Like'}
                user_ratings_dict[game_name] = f"Name: {game_name} ¬ Rating: {rating} ({rating_text.get(rating, 'Unknown')})"

# Pre-load model in background (nếu đã train)
recommender = None
model_path = os.path.join(dir_path, "cb_model.pkl")

def preload_model():
    """Pre-load model trong background để không lag khi get recommendations"""
    global recommender
    if os.path.exists(model_path):
        print("Pre-loading model in background...")
        try:
            temp_recommender = ContentBasedRecommender()
            if temp_recommender.load_model(model_path):
                recommender = temp_recommender
                print("Model pre-loaded successfully!")
            else:
                print("Failed to pre-load model (will load when needed)")
        except Exception as e:
            print(f"Error pre-loading model: {str(e)} (will load when needed)")

# Start pre-loading in background thread
if os.path.exists(model_path):
    preload_thread = threading.Thread(target=preload_model, daemon=True)
    preload_thread.start()

# Create the main window
root = tk.Tk()
root.title('Game Recommendation - Content-Based Filtering System')
root.geometry('1200x800')

# Header label
header_label = tk.Label(root, text='CONTENT-BASED FILTERING SYSTEM (Genres & Tags)', 
                       font=('Arial', 16, 'bold'), fg='blue', bg='lightgray')
header_label.pack(pady=10)

# Games List
games_frame = cb_elements.games_list_frame(root, games_dict)
search_frame = cb_elements.search_frame(root, games_dict, games_frame)

# User Ratings
user_ratings_frame = cb_elements.user_ratings_frame(root, user_ratings_dict)

# Rating Buttons
rating_buttons_frame = cb_elements.rating_buttons_frame(
    root, games_frame, user_ratings_frame, user_ratings_dict
)

# Preferences Frame
preferences_frame, price_entry, ratio_entry = cb_elements.preferences_frame(root)

# Recommendations Frame (truyền pre-loaded recommender nếu có)
recommendations_frame = cb_elements.recommendations_frame(
    root, user_ratings_dict, dir_path, df_games, recommender=recommender
)

# Footer
footer_label = tk.Label(root, text='Content-Based Filtering - Uses Genres & Tags to find similar games', 
                       font=('Arial', 10), fg='gray')
footer_label.pack(pady=5)

print("Content-Based UI initialized successfully!")
print(f"Loaded {len(games_dict)} games")

root.mainloop()

