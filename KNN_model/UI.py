import sys
import asyncio
import tkinter as tk
import os
import Data_handler
import UI_elements as elements

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Get data file paths
dir_path = os.path.dirname(os.path.abspath(__file__))
all_games_path = os.path.join(dir_path, "final_games.csv")
played_games_path = os.path.join(dir_path, "your_games.csv")
fav_games_path = os.path.join(dir_path, "fav_games.csv")

# Load data
print("Loading data...")
df_all, all_games_dict = Data_handler.load_data(all_games_path, 'all')
df_played, played_games_dict = Data_handler.load_data(played_games_path, 'played')
df_fav, fav_games_dict = Data_handler.load_data(fav_games_path, 'fav')
print(f"Data loaded. {len(all_games_dict)} games available.")

# Create the main window
root = tk.Tk()
root.title('Game Recommendation - KNN Collaborative Filtering System')
root.geometry('1200x850')

# Header
header_label = tk.Label(root, text='KNN COLLABORATIVE FILTERING SYSTEM', 
                       font=('Arial', 16, 'bold'), fg='blue', bg='#f0f0f0', pady=10)
header_label.pack(fill=tk.X)

# 1. Search & Game List
games_frame = elements.game_list_frame(root, all_games_dict)
search_frame = elements.search_frame(root, all_games_dict, games_frame)

# 2. Played Games List (Reviews)
played_games_frame = elements.played_games_frame(root, played_games_dict)

# 3. Favourite Games List
fav_games_frame = elements.fav_games_frame(root, fav_games_dict)

# 4. Review Controls (Like, Dislike, Delete Review...)
review_controls = elements.review_controls_frame(root, games_frame, played_games_frame, played_games_dict)

# 5. Favourite Controls (Mark Fav, Delete Fav...)
fav_controls = elements.favourite_controls_frame(root, played_games_frame, played_games_dict, fav_games_frame, fav_games_dict)

# 6. System Controls (Save, Get Recs)
sys_controls = elements.system_controls_frame(root, played_games_dict, fav_games_dict, dir_path, df_all)

# Footer
footer_label = tk.Label(root, text='KNN Collaborative Filtering - Uses user behavior to find similar users', 
                       font=('Arial', 9), fg='gray')
footer_label.pack(side=tk.BOTTOM, pady=5)

root.mainloop()