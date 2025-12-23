"""
UI Elements cho Content-Based Filtering System
Updated: Removed Min Positive Ratio, Cleaned up Layout
"""

import tkinter as tk
import ContentBased_commands as cb_commands


def search_frame(root, games_dict, list_frame):
    """Search frame"""
    search_frame = tk.Frame(root)
    search_frame.pack(pady=10)

    search_label = tk.Label(search_frame, text='Search Games:', font=('Arial', 12, 'bold'))
    search_label.grid(row=0, column=0)

    search_entry = tk.Entry(search_frame, width=80, font=('Arial', 12))
    search_entry.grid(row=0, column=1, padx=10)
    search_entry.bind('<Return>', lambda event: cb_commands.update_search(search_frame, games_dict, list_frame))

    search_button = tk.Button(search_frame, text='Search', 
                             command=lambda: cb_commands.update_search(search_frame, games_dict, list_frame), 
                             font=('Arial', 11))
    search_button.grid(row=0, column=2, padx=10)

    return search_frame


def games_list_frame(root, games_dict):
    """Games list frame"""
    games_frame = tk.Frame(root)
    games_frame.pack(pady=10)

    games_label = tk.Label(games_frame, text='Available Games:', 
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


def user_ratings_frame(root, user_ratings_dict):
    """User ratings frame"""
    ratings_frame = tk.Frame(root)
    ratings_frame.pack(pady=10)

    ratings_label = tk.Label(ratings_frame, text='Your Ratings:', 
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


def rating_buttons_frame(root, games_frame, ratings_frame, user_ratings_dict, dir_path):
    """Rating buttons frame"""
    for widget in games_frame.winfo_children():
        if isinstance(widget, tk.Listbox):
            games_listbox = widget

    for widget in ratings_frame.winfo_children():
        if isinstance(widget, tk.Listbox):
            ratings_listbox = widget

    rating_frame = tk.Frame(root)
    rating_frame.pack(pady=5)

    rating_label = tk.Label(rating_frame, text='Rate Game:', 
                           font=('Arial', 12, 'bold'))
    rating_label.grid(row=0, column=0, padx=10)

    # Các nút đánh giá
    buttons_config = [
        ('Like (5)', 5, 'lightgreen'),
        ('Good (4)', 4, 'lightblue'),
        ('Neutral (3)', 3, 'lightyellow'),
        ('Bad (2)', 2, 'lightcoral'),
        ('Dislike (1)', 1, 'lightpink')
    ]

    col = 1
    for text, rating, color in buttons_config:
        btn = tk.Button(rating_frame, text=text, 
                       command=lambda r=rating: cb_commands.add_rating(r, games_listbox, ratings_listbox, user_ratings_dict), 
                       font=('Arial', 11), bg=color)
        btn.grid(row=0, column=col, padx=5)
        col += 1

    delete_button = tk.Button(rating_frame, text='Delete Rating',
                               command=lambda: cb_commands.remove_rating(ratings_listbox, user_ratings_dict),
                               font=('Arial', 11), bg='lightgray')
    delete_button.grid(row=0, column=col, padx=5)

    clear_all_button = tk.Button(rating_frame, text='Clear All Ratings',
                                command=lambda: cb_commands.clear_all_ratings(ratings_listbox, user_ratings_dict, dir_path),
                                font=('Arial', 11), bg='lightcoral')
    clear_all_button.grid(row=0, column=col+1, padx=5)

    return rating_frame


def recommendations_frame(root, user_ratings_dict, dir_path, df_games, recommender=None):
    """Recommendations frame - Đã thêm nút Clear Data"""
    recommendations_frame = tk.Frame(root)
    recommendations_frame.pack(pady=10)

    # 1. Save Ratings
    save_button = tk.Button(recommendations_frame, text='Save Ratings', 
                           command=lambda: cb_commands.save_ratings(user_ratings_dict, df_games, dir_path), 
                           font=('Arial', 12), bg='lightblue')
    save_button.grid(row=0, column=0, padx=10, pady=10)

    # 2. Train Model
    train_button = tk.Button(recommendations_frame, text='Train Model', 
                            command=lambda: cb_commands.train_model(dir_path, root=root), 
                            font=('Arial', 12), bg='lightgreen')
    train_button.grid(row=0, column=1, padx=10, pady=10)

    # 3. Get Recommendations
    recommend_button = tk.Button(recommendations_frame, text='Get Recommendations', 
                                command=lambda: cb_commands.get_recommendations(dir_path, root=root, preloaded_recommender=recommender), 
                                font=('Arial', 12), bg='lightyellow')
    recommend_button.grid(row=0, column=2, padx=10, pady=10)

    # 4. Clear Data (NÚT MỚI)
    clear_button = tk.Button(recommendations_frame, text='Clear Data', 
                            command=lambda: cb_commands.clear_system_data(dir_path, root=root), 
                            font=('Arial', 12), bg='lightcoral', fg='white')
    clear_button.grid(row=0, column=3, padx=10, pady=10)

    return recommendations_frame


def preferences_frame(root):
    """
    User preferences frame - Đã xóa Ratio input
    """
    prefs_frame = tk.Frame(root)
    prefs_frame.pack(pady=10)

    # Max price (Căn giữa)
    price_label = tk.Label(prefs_frame, text='Max Price ($):', font=('Arial', 11))
    price_label.grid(row=0, column=0, padx=5)
    
    price_entry = tk.Entry(prefs_frame, width=10, font=('Arial', 11))
    price_entry.grid(row=0, column=1, padx=5)
    price_entry.insert(0, '100') # Default 100$

    # Lưu ý: Hàm này bây giờ chỉ trả về 2 giá trị thay vì 3
    return prefs_frame, price_entry