import tkinter as tk
from tkinter import messagebox
import re
import pandas as pd
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

def update_search(search_frame, games_dict, list_frame):
    games_listbox = None
    search_entry = None
    for widget in search_frame.winfo_children():
        if isinstance(widget,tk.Entry):
            search_entry = widget
    for widget in list_frame.winfo_children():
        if isinstance(widget,tk.Listbox):
            games_listbox = widget
    search_query = search_entry.get().strip().lower()
    games_listbox.delete(0, tk.END)
    if search_query == '':
        for game_info in games_dict.values():
            games_listbox.insert(tk.END, game_info)
    else:
        for game_name, game_info in games_dict.items():
            if search_query in game_name.lower():
                games_listbox.insert(tk.END, game_info)

def add_review(review, games_listbox, played_games_listbox, played_games_dict):
    selected_game_info = games_listbox.get(tk.ACTIVE)
    if selected_game_info:
        match = re.search(r'Name:\s*(.*?)\s*¬', selected_game_info)
        if match:
            selected_game_name = match.group(1).strip()
        else:
            # Fallback nếu string không khớp regex (trường hợp tên game đơn giản)
            selected_game_name = selected_game_info.split('¬')[0].replace('Name: ', '').strip()
        
        # Add or Update review
        played_games_dict[selected_game_name] = f"Name: {selected_game_name} ¬ Review: {review}"

        # Update Listbox
        played_games_listbox.delete(0, tk.END)
        for game_review in played_games_dict.values():
            played_games_listbox.insert(tk.END, game_review)

def remove_review(played_games_listbox, played_games_dict):
    selected_indices = played_games_listbox.curselection()
    if selected_indices:
        index = selected_indices[0]
        item = played_games_listbox.get(index)
        
        # Extract name to delete from dict
        match = re.search(r'Name:\s*(.*?)\s*¬', item)
        if match:
            game_name = match.group(1).strip()
            if game_name in played_games_dict:
                del played_games_dict[game_name]
        
        # Delete from listbox
        played_games_listbox.delete(index)

def clear_all_reviews(played_games_listbox, played_games_dict):
    if not played_games_dict:
        return
    if messagebox.askyesno("Clear All", "Are you sure you want to delete ALL reviews?"):
        played_games_dict.clear()
        played_games_listbox.delete(0, tk.END)

def add_favourite(played_games_listbox, played_games_dict, fav_games_listbox, fav_games_dict):
    selected_indices = played_games_listbox.curselection()
    if selected_indices:
        item = played_games_listbox.get(selected_indices[0])
        
        # Extract name
        match = re.search(r'Name:\s*(.*?)\s*¬', item)
        if match:
            selected_game_name = match.group(1).strip()
            
            if selected_game_name in fav_games_dict:
                messagebox.showinfo('Info', 'This game is already in your favorites!')
                return
            
            # Add to fav dict and listbox
            fav_games_dict[selected_game_name] = selected_game_name
            fav_games_listbox.insert(tk.END, selected_game_name)
    else:
        messagebox.showwarning("Selection", "Please select a game from 'Played Games' to mark as favourite.")

def remove_favourite(fav_games_listbox, fav_games_dict):
    selected_indices = fav_games_listbox.curselection()
    if selected_indices:
        index = selected_indices[0]
        game_name = fav_games_listbox.get(index)
        
        # Delete from dict
        if game_name in fav_games_dict:
            del fav_games_dict[game_name]
        
        # Delete from listbox
        fav_games_listbox.delete(index)

def clear_all_favourites(fav_games_listbox, fav_games_dict):
    if not fav_games_dict:
        return
    if messagebox.askyesno("Clear All", "Are you sure you want to delete ALL favourites?"):
        fav_games_dict.clear()
        fav_games_listbox.delete(0, tk.END)

def confirm(played_games_dict, fav_games_dict, df_all, dir_path):
    try:
        played_data = []
        review_numerical_value = {'Like': 1, 'Interested': 0.5, 'Neutral/Not Interested': -0.5, 'Dislike': -1}
        
        for gameName, gameReview in played_games_dict.items():
            # Extract review text safely
            try:
                review_text = gameReview.split('Review: ')[1]
                review_val = review_numerical_value.get(review_text, 0)
                
                # Find ID
                game_row = df_all[df_all['title'] == gameName]
                if not game_row.empty:
                    game_id = game_row['app_id'].values[0]
                    played_data.append({'gameID': game_id, 'gameName': gameName, 'review': review_val})
            except Exception as e:
                print(f"Error processing {gameName}: {e}")
                continue

        reviews_df = pd.DataFrame(played_data)
        reviews_df.to_csv(os.path.join(dir_path, "your_games.csv"), index=False)

        fav_data = []
        for gameName in fav_games_dict.keys():
            game_row = df_all[df_all['title'] == gameName]
            if not game_row.empty:
                game_id = game_row['app_id'].values[0]
                fav_data.append({'gameID': game_id, 'gameName': gameName})
        
        # Fix lỗi EmptyDataError bằng cách luôn tạo DataFrame có cột
        fav_df = pd.DataFrame(fav_data, columns=['gameID', 'gameName'])
        fav_df.to_csv(os.path.join(dir_path, "fav_games.csv"), index=False)
        
        messagebox.showinfo('Success', 'Data saved successfully!')
    except Exception as e:
        messagebox.showerror('Error', f"Failed to save data: {e}")

def get_recommendations(dir_path):
    try:
        notebook_path = os.path.join(dir_path, "knn_model.ipynb")
        if not os.path.exists(notebook_path):
            messagebox.showerror("Error", "knn_model.ipynb not found!")
            return

        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        ep = ExecutePreprocessor(timeout=6000, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': dir_path}})

        messagebox.showinfo('Success', 'Recommendations generated successfully.\nCheck rcm_games.csv')

    except Exception as e:
        messagebox.showerror('Error', f'Failed to run recommendations: {str(e)}')