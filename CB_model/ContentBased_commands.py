"""
Commands cho Content-Based System
"""
import tkinter as tk
from tkinter import messagebox
import re
import pandas as pd
import os
import threading
from ContentBased_model import ContentBasedRecommender
# Import hàm load chuẩn từ Data Handler
from ContentBased_data_handler import save_ratings_data, load_ratings_data, load_games_csv

MODEL_JUST_TRAINED = False

def update_search(search_frame, games_dict, list_frame):
    games_listbox = None
    search_entry = None
    for widget in search_frame.winfo_children():
        if isinstance(widget, tk.Entry): search_entry = widget
    for widget in list_frame.winfo_children():
        if isinstance(widget, tk.Listbox): games_listbox = widget
    
    if not games_listbox or not search_entry: return
    
    query = search_entry.get().strip().lower()
    games_listbox.delete(0, tk.END)
    
    if query == '':
        for info in games_dict.values(): games_listbox.insert(tk.END, info)
    else:
        for name, info in games_dict.items():
            if query in name.lower(): games_listbox.insert(tk.END, info)

def add_rating(rating, games_listbox, ratings_listbox, user_ratings_dict):
    # (Giữ nguyên code cũ)
    # ...
    selected = games_listbox.get(tk.ACTIVE)
    if selected:
        match = re.search(r'Name:\s*(.*?)\s*¬', selected)
        if match:
            name = match.group(1).strip()
            txt_map = {1: 'Dislike', 2: 'Bad', 3: 'Neutral', 4: 'Good', 5: 'Like'}
            user_ratings_dict[name] = f"Name: {name} ¬ Rating: {rating} ({txt_map[rating]})"
            
            ratings_listbox.delete(0, tk.END)
            for info in user_ratings_dict.values(): ratings_listbox.insert(tk.END, info)

def remove_rating(ratings_listbox, user_ratings_dict):
    # (Giữ nguyên code cũ)
    sel = ratings_listbox.curselection()
    if sel:
        item = ratings_listbox.get(sel[0])
        ratings_listbox.delete(sel[0])
        for k, v in list(user_ratings_dict.items()):
            if v == item: del user_ratings_dict[k]

def save_ratings(user_ratings_dict, df_games, dir_path):
    try:
        ratings_data = []
        for name, info in user_ratings_dict.items():
            match = re.search(r'Rating:\s*(\d+)', info)
            if match:
                rating = int(match.group(1))
                # Tìm ID dựa trên cột Name (vì đã rename chuẩn)
                rows = df_games[df_games['Name'] == name]
                if not rows.empty:
                    # Index chính là AppID
                    app_id = rows.index[0]
                    ratings_data.append({'AppID': int(app_id), 'Name': name, 'user_rating': rating})
        
        user_dir = os.path.join(os.path.dirname(dir_path), "user_data")
        os.makedirs(user_dir, exist_ok=True)
        save_ratings_data(ratings_data, os.path.join(user_dir, "cb_user_ratings.json"))
        messagebox.showinfo('Success', 'Ratings saved successfully!')
    except Exception as e:
        messagebox.showerror('Error', str(e))

def clear_all_ratings(ratings_listbox, user_ratings_dict, dir_path):
    # (Giữ nguyên code cũ)
    if messagebox.askyesno("Confirm", "Clear all ratings?"):
        user_ratings_dict.clear()
        ratings_listbox.delete(0, tk.END)
        path = os.path.join(os.path.dirname(dir_path), "user_data", "cb_user_ratings.json")
        save_ratings_data([], path)

def clear_system_data(dir_path, root=None):
    # (Giữ nguyên code cũ - Hàm xóa model)
    if messagebox.askyesno("Confirm", "Delete trained model and cache?"):
        try:
            for f in ["cb_model.pkl", "cb_recommendations.csv"]:
                p = os.path.join(dir_path, f)
                if os.path.exists(p): os.remove(p)
            
            global MODEL_JUST_TRAINED
            MODEL_JUST_TRAINED = True
            messagebox.showinfo("Success", "System data cleared. Please Train Model again.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def train_model(dir_path, root=None):
    def _train():
        global MODEL_JUST_TRAINED
        try:
            # Dùng hàm load chuẩn để lấy dữ liệu sạch
            df = load_games_csv(os.path.join(dir_path, "CB_games.csv"))
            if df is None: return
            
            recommender = ContentBasedRecommender()
            if recommender.train(df):
                recommender.save_model(os.path.join(dir_path, "cb_model.pkl"))
                MODEL_JUST_TRAINED = True
                if root: root.after(0, lambda: messagebox.showinfo('Success', 'Model trained!'))
        except Exception as e:
            if root: root.after(0, lambda: messagebox.showerror('Error', str(e)))
    
    threading.Thread(target=_train, daemon=True).start()

def get_recommendations(dir_path, root=None, preloaded_recommender=None):
    def _recommend():
        global MODEL_JUST_TRAINED
        try:
            model_path = os.path.join(dir_path, "cb_model.pkl")
            if not os.path.exists(model_path):
                if root: root.after(0, lambda: messagebox.showerror('Error', 'Please train model first!'))
                return

            # Load Data & Model
            df = load_games_csv(os.path.join(dir_path, "CB_games.csv"))
            
            recommender = None
            # Logic reload thông minh
            if MODEL_JUST_TRAINED or not preloaded_recommender:
                recommender = ContentBasedRecommender()
                recommender.load_model(model_path)
                if MODEL_JUST_TRAINED: MODEL_JUST_TRAINED = False
            else:
                recommender = preloaded_recommender

            # Load Ratings
            ratings_path = os.path.join(os.path.dirname(dir_path), "user_data", "cb_user_ratings.json")
            ratings_data = load_ratings_data(ratings_path)
            rated_games = {item['AppID']: item['user_rating'] for item in ratings_data if 'AppID' in item}

            if not rated_games:
                if root: root.after(0, lambda: messagebox.showwarning('Warning', 'Please rate some games!'))
                return

            # Get Recs
            prefs = {'max_price': 100}
            recs = recommender.get_recommendations(df, rated_games, prefs, top_n=200)
            
            if recs.empty:
                if root: root.after(0, lambda: messagebox.showwarning('Info', 'No recommendations found.'))
                return

            # Save & Show
            recs.to_csv(os.path.join(dir_path, "cb_recommendations.csv"), index=False)
            
            msg = "Top Recommendations:\n"
            for _, row in recs.head(10).iterrows():
                msg += f"{row['Name']} - Score: {row['Score']:.2f}\n"
            
            if root: root.after(0, lambda: messagebox.showinfo('Result', msg))

        except Exception as e:
            if root: root.after(0, lambda: messagebox.showerror('Error', str(e)))
            print(e)

    threading.Thread(target=_recommend, daemon=True).start()