import tkinter as tk
import Button_commands as commands

def search_frame(root, games_dict, list_frame):
    search_frame = tk.Frame(root)
    search_frame.pack(pady=10)

    search_label = tk.Label(search_frame, text='Search Games:', font=('Arial', 12, 'bold'))
    search_label.grid(row=0, column=0)

    search_entry = tk.Entry(search_frame, width=80, font=('Arial', 12))
    search_entry.grid(row=0, column=1, padx=10)
    search_entry.bind('<Return>', lambda event: commands.update_search(search_frame, games_dict, list_frame))

    search_button = tk.Button(search_frame, text='Search', 
                             command=lambda: commands.update_search(search_frame, games_dict, list_frame), 
                             font=('Arial', 11))
    search_button.grid(row=0, column=2, padx=10)

    return search_frame

def game_list_frame(root, all_games_dict):
    games_frame = tk.Frame(root)
    games_frame.pack(pady=5)

    games_label = tk.Label(games_frame, text='Available Games:', font=('Arial', 14, 'bold'), fg='blue')
    games_label.grid(row=0, column=0)

    games_listbox = tk.Listbox(games_frame, width=110, height=8, font=('Arial', 10))
    games_listbox.grid(row=1, column=0, padx=20)

    scrollbar = tk.Scrollbar(games_frame, orient=tk.VERTICAL, command=games_listbox.yview)
    scrollbar.grid(row=1, column=1, sticky=tk.NS)
    games_listbox.config(yscrollcommand=scrollbar.set)

    for game_info in all_games_dict.values():
        games_listbox.insert(tk.END, game_info)
    return games_frame

def played_games_frame(root, played_games_dict):
    played_games_frame = tk.Frame(root)
    played_games_frame.pack(pady=5)

    played_games_label = tk.Label(played_games_frame, text='Your Reviews:', font=('Arial', 14, 'bold'), fg='green')
    played_games_label.grid(row=0, column=0)

    played_games_listbox = tk.Listbox(played_games_frame, width=110, height=5, font=('Arial', 10))
    played_games_listbox.grid(row=1, column=0, padx=20)

    scrollbar = tk.Scrollbar(played_games_frame, orient=tk.VERTICAL, command=played_games_listbox.yview)
    scrollbar.grid(row=1, column=1, sticky=tk.NS)
    played_games_listbox.config(yscrollcommand=scrollbar.set)

    for game_info in played_games_dict.values():
        played_games_listbox.insert(tk.END, game_info)
    return played_games_frame

def fav_games_frame(root, fav_games_dict):
    fav_games_frame = tk.Frame(root)
    fav_games_frame.pack(pady=5)

    fav_games_label = tk.Label(fav_games_frame, text='Your Favourites:', font=('Arial', 14, 'bold'), fg='purple')
    fav_games_label.grid(row=0, column=0)

    fav_games_listbox = tk.Listbox(fav_games_frame, width=110, height=4, font=('Arial', 10))
    fav_games_listbox.grid(row=1, column=0, padx=20)

    scrollbar = tk.Scrollbar(fav_games_frame, orient=tk.VERTICAL, command=fav_games_listbox.yview)
    scrollbar.grid(row=1, column=1, sticky=tk.NS)
    fav_games_listbox.config(yscrollcommand=scrollbar.set)

    for game_info in fav_games_dict.values():
        fav_games_listbox.insert(tk.END, game_info)
    return fav_games_frame

# --- CONTROL FRAMES ---

def review_controls_frame(root, games_frame, played_games_frame, played_games_dict):
    # Lấy listbox references
    for widget in games_frame.winfo_children():
        if isinstance(widget, tk.Listbox): games_listbox = widget
    for widget in played_games_frame.winfo_children():
        if isinstance(widget, tk.Listbox): played_games_listbox = widget

    frame = tk.Frame(root)
    frame.pack(pady=5)

    lbl = tk.Label(frame, text="Add Review:", font=('Arial', 12, 'bold'))
    lbl.grid(row=0, column=0, padx=10)

    # Rating Buttons (Màu sắc giống Content Based)
    btn_like = tk.Button(frame, text='Like', bg='lightgreen', width=8,
                        command=lambda: commands.add_review('Like', games_listbox, played_games_listbox, played_games_dict))
    btn_like.grid(row=0, column=1, padx=2)

    btn_int = tk.Button(frame, text='Interested', bg='lightblue', width=10,
                       command=lambda: commands.add_review('Interested', games_listbox, played_games_listbox, played_games_dict))
    btn_int.grid(row=0, column=2, padx=2)

    btn_neu = tk.Button(frame, text='Neutral', bg='lightyellow', width=8,
                       command=lambda: commands.add_review('Neutral/Not Interested', games_listbox, played_games_listbox, played_games_dict))
    btn_neu.grid(row=0, column=3, padx=2)

    btn_dis = tk.Button(frame, text='Dislike', bg='lightpink', width=8,
                       command=lambda: commands.add_review('Dislike', games_listbox, played_games_listbox, played_games_dict))
    btn_dis.grid(row=0, column=4, padx=2)

    # Delete Buttons
    tk.Label(frame, text="  |  ").grid(row=0, column=5) # Separator

    btn_del = tk.Button(frame, text='Delete Review', bg='lightgray',
                       command=lambda: commands.remove_review(played_games_listbox, played_games_dict))
    btn_del.grid(row=0, column=6, padx=5)

    btn_del_all = tk.Button(frame, text='Clear All Reviews', bg='lightcoral', fg='white',
                           command=lambda: commands.clear_all_reviews(played_games_listbox, played_games_dict))
    btn_del_all.grid(row=0, column=7, padx=5)

    return frame

def favourite_controls_frame(root, played_games_frame, played_games_dict, fav_games_frame, fav_games_dict):
    # Lấy listbox references
    for widget in played_games_frame.winfo_children():
        if isinstance(widget, tk.Listbox): played_games_listbox = widget
    for widget in fav_games_frame.winfo_children():
        if isinstance(widget, tk.Listbox): fav_games_listbox = widget

    frame = tk.Frame(root)
    frame.pack(pady=5)

    lbl = tk.Label(frame, text="Favourite Actions:", font=('Arial', 12, 'bold'))
    lbl.grid(row=0, column=0, padx=10)

    btn_add_fav = tk.Button(frame, text='Mark as Favourite', bg='gold',
                           command=lambda: commands.add_favourite(played_games_listbox, played_games_dict, fav_games_listbox, fav_games_dict))
    btn_add_fav.grid(row=0, column=1, padx=5)

    btn_del_fav = tk.Button(frame, text='Delete Favourite', bg='lightgray',
                           command=lambda: commands.remove_favourite(fav_games_listbox, fav_games_dict))
    btn_del_fav.grid(row=0, column=2, padx=5)

    btn_clr_fav = tk.Button(frame, text='Clear All Favourites', bg='lightcoral', fg='white',
                           command=lambda: commands.clear_all_favourites(fav_games_listbox, fav_games_dict))
    btn_clr_fav.grid(row=0, column=3, padx=5)

    return frame

def system_controls_frame(root, played_games_dict, fav_games_dict, dir_path, df_all):
    frame = tk.Frame(root)
    frame.pack(pady=15)

    btn_save = tk.Button(frame, text='Save Your Data', font=('Arial', 12, 'bold'), bg='lightblue', width=20,
                        command=lambda: commands.confirm(played_games_dict, fav_games_dict, df_all, dir_path))
    btn_save.grid(row=0, column=0, padx=20)

    btn_rec = tk.Button(frame, text='Get Recommendations', font=('Arial', 12, 'bold'), bg='lightgreen', width=20,
                       command=lambda: commands.get_recommendations(dir_path))
    btn_rec.grid(row=0, column=1, padx=20)

    return frame