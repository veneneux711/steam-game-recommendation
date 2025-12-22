"""
UI Elements riêng cho Decision Tree System
Tách biệt hoàn toàn với KNN UI
"""

import tkinter as tk
import DecisionTree_commands as dt_commands

def search_frame_dt(root, games_dict, list_frame):
    """
    Search frame riêng cho Decision Tree
    """
    search_frame = tk.Frame(root)
    search_frame.pack(pady=10)

    search_label = tk.Label(search_frame, text='Search Games (Decision Tree):', font=('Arial', 12, 'bold'))
    search_label.grid(row=0, column=0)

    search_entry = tk.Entry(search_frame, width=80, font=('Arial', 12))
    search_entry.grid(row=0, column=1, padx=10)
    search_entry.bind('<Return>', lambda event: dt_commands.update_search_dt(search_frame, games_dict, list_frame))

    search_button = tk.Button(search_frame, text='Search', 
                             command=lambda: dt_commands.update_search_dt(search_frame, games_dict, list_frame), 
                             font=('Arial', 11))
    search_button.grid(row=0, column=2, padx=10)

    return search_frame

def games_list_frame_dt(root, games_dict):
    """
    Games list frame riêng cho Decision Tree
    """
    games_frame = tk.Frame(root)
    games_frame.pack(pady=10)

    games_label = tk.Label(games_frame, text='Available Games (Decision Tree):', 
                          font=('Arial', 14, 'bold'), fg='blue')
    games_label.grid(row=0, column=0)

    games_listbox = tk.Listbox(games_frame, width=120, height=12, font=('Arial', 10))
    games_listbox.grid(row=1, column=0, padx=20)

    scrollbar = tk.Scrollbar(games_frame, orient=tk.VERTICAL, command=games_listbox.yview)
    scrollbar.grid(row=1, column=1, sticky=tk.NS)
    games_listbox.config(yscrollcommand=scrollbar.set)

    for game_info in games_dict.values():
        games_listbox.insert(tk.END, game_info)
    
    return games_frame

def user_ratings_frame_dt(root, user_ratings_dict):
    """
    User ratings frame riêng cho Decision Tree
    """
    ratings_frame = tk.Frame(root)
    ratings_frame.pack(pady=10)

    ratings_label = tk.Label(ratings_frame, text='Your Ratings (Decision Tree):', 
                            font=('Arial', 14, 'bold'), fg='green')
    ratings_label.grid(row=0, column=0)

    ratings_listbox = tk.Listbox(ratings_frame, width=120, height=6, font=('Arial', 10))
    ratings_listbox.grid(row=1, column=0, padx=20)

    scrollbar_ratings = tk.Scrollbar(ratings_frame, orient=tk.VERTICAL, command=ratings_listbox.yview)
    scrollbar_ratings.grid(row=1, column=1, sticky=tk.NS)
    ratings_listbox.config(yscrollcommand=scrollbar_ratings.set)

    for rating_info in user_ratings_dict.values():
        ratings_listbox.insert(tk.END, rating_info)
    
    return ratings_frame

def rating_buttons_frame_dt(root, games_frame, ratings_frame, user_ratings_dict):
    """
    Rating buttons frame riêng cho Decision Tree
    """
    for widget in games_frame.winfo_children():
        if isinstance(widget, tk.Listbox):
            games_listbox = widget

    for widget in ratings_frame.winfo_children():
        if isinstance(widget, tk.Listbox):
            ratings_listbox = widget

    rating_frame = tk.Frame(root)
    rating_frame.pack(pady=5)

    rating_label = tk.Label(rating_frame, text='Rate Game (Decision Tree):', 
                           font=('Arial', 12, 'bold'))
    rating_label.grid(row=0, column=0, padx=10)

    like_button = tk.Button(rating_frame, text='Like (5)', 
                           command=lambda: dt_commands.add_rating_dt(5, games_listbox, ratings_listbox, user_ratings_dict), 
                           font=('Arial', 11), bg='lightgreen')
    like_button.grid(row=0, column=1, padx=5)

    good_button = tk.Button(rating_frame, text='Good (4)', 
                           command=lambda: dt_commands.add_rating_dt(4, games_listbox, ratings_listbox, user_ratings_dict), 
                           font=('Arial', 11), bg='lightblue')
    good_button.grid(row=0, column=2, padx=5)

    neutral_button = tk.Button(rating_frame, text='Neutral (3)', 
                              command=lambda: dt_commands.add_rating_dt(3, games_listbox, ratings_listbox, user_ratings_dict), 
                              font=('Arial', 11), bg='lightyellow')
    neutral_button.grid(row=0, column=3, padx=5)

    bad_button = tk.Button(rating_frame, text='Bad (2)', 
                          command=lambda: dt_commands.add_rating_dt(2, games_listbox, ratings_listbox, user_ratings_dict), 
                          font=('Arial', 11), bg='lightcoral')
    bad_button.grid(row=0, column=4, padx=5)

    dislike_button = tk.Button(rating_frame, text='Dislike (1)', 
                              command=lambda: dt_commands.add_rating_dt(1, games_listbox, ratings_listbox, user_ratings_dict), 
                              font=('Arial', 11), bg='lightpink')
    dislike_button.grid(row=0, column=5, padx=5)

    delete_button = tk.Button(rating_frame, text='Delete Rating', 
                              command=lambda: dt_commands.remove_rating_dt(ratings_listbox, user_ratings_dict), 
                              font=('Arial', 11), bg='lightgray')
    delete_button.grid(row=0, column=6, padx=5)

    return rating_frame

def recommendations_frame_dt(root, user_ratings_dict, dir_path, df_decision_games):
    """
    Recommendations frame riêng cho Decision Tree
    """
    recommendations_frame = tk.Frame(root)
    recommendations_frame.pack(pady=10)

    # Buttons
    save_button = tk.Button(recommendations_frame, text='Save Ratings (DT)', 
                           command=lambda: dt_commands.save_ratings_dt(user_ratings_dict, df_decision_games, dir_path), 
                           font=('Arial', 12), bg='lightblue')
    save_button.grid(row=0, column=0, padx=10, pady=10)

    train_button = tk.Button(recommendations_frame, text='Train Model (DT)', 
                            command=lambda: dt_commands.train_model_dt(dir_path), 
                            font=('Arial', 12), bg='lightgreen')
    train_button.grid(row=0, column=1, padx=10, pady=10)

    recommend_button = tk.Button(recommendations_frame, text='Get Recommendations (DT)', 
                                command=lambda: dt_commands.get_recommendations_dt(dir_path), 
                                font=('Arial', 12), bg='lightyellow')
    recommend_button.grid(row=0, column=2, padx=10, pady=10)

    return recommendations_frame

def preferences_frame_dt(root):
    """
    User preferences frame cho Decision Tree
    """
    prefs_frame = tk.Frame(root)
    prefs_frame.pack(pady=10)

    prefs_label = tk.Label(prefs_frame, text='Preferences (Decision Tree):', 
                           font=('Arial', 12, 'bold'))
    prefs_label.grid(row=0, column=0, columnspan=3, pady=5)

    # Max price
    price_label = tk.Label(prefs_frame, text='Max Price ($):')
    price_label.grid(row=1, column=0, padx=5)
    price_entry = tk.Entry(prefs_frame, width=10)
    price_entry.grid(row=1, column=1, padx=5)
    price_entry.insert(0, '100')

    # Min positive ratio
    ratio_label = tk.Label(prefs_frame, text='Min Positive Ratio:')
    ratio_label.grid(row=1, column=2, padx=5)
    ratio_entry = tk.Entry(prefs_frame, width=10)
    ratio_entry.grid(row=1, column=3, padx=5)
    ratio_entry.insert(0, '0.7')

    return prefs_frame, price_entry, ratio_entry

