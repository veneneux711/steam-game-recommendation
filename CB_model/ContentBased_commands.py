"""
Button Commands cho Content-Based Filtering System
Fixed: Tự động reload model sau khi train xong để tránh lỗi Dimension Mismatch
"""

import tkinter as tk
from tkinter import messagebox
import re
import pandas as pd
import os
import threading
import json
from ContentBased_model import ContentBasedRecommender
from ContentBased_data_handler import save_ratings_data, load_ratings_data, load_games_csv

# Biến toàn cục để đánh dấu model vừa được train lại
MODEL_JUST_TRAINED = False

def update_search(search_frame, games_dict, list_frame):
    """Update search results"""
    games_listbox = None
    search_entry = None
    
    for widget in search_frame.winfo_children():
        if isinstance(widget, tk.Entry):
            search_entry = widget
    
    for widget in list_frame.winfo_children():
        if isinstance(widget, tk.Listbox):
            games_listbox = widget
    
    if games_listbox is None or search_entry is None:
        return
    
    search_query = search_entry.get().strip().lower()
    games_listbox.delete(0, tk.END)
    
    if search_query == '':
        for game_info in games_dict.values():
            games_listbox.insert(tk.END, game_info)
    else:
        for game_name, game_info in games_dict.items():
            if search_query in game_name.lower():
                games_listbox.insert(tk.END, game_info)


def add_rating(rating, games_listbox, ratings_listbox, user_ratings_dict):
    """Thêm rating cho game"""
    selected_game_info = games_listbox.get(tk.ACTIVE)
    if selected_game_info:
        match = re.search(r'Name:\s*(.*?)\s*¬', selected_game_info)
        if match:
            selected_game_name = match.group(1).strip()
        else:
            messagebox.showwarning('Invalid Format', 'Failed to extract game name.')
            return
        
        rating_text = {1: 'Dislike', 2: 'Bad', 3: 'Neutral', 4: 'Good', 5: 'Like'}
        user_ratings_dict[selected_game_name] = f"Name: {selected_game_name} ¬ Rating: {rating} ({rating_text[rating]})"
        
        ratings_listbox.delete(0, tk.END)
        for rating_info in user_ratings_dict.values():
            ratings_listbox.insert(tk.END, rating_info)
        
        print(f"Added rating {rating} for {selected_game_name}")


def remove_rating(ratings_listbox, user_ratings_dict):
    """Xóa rating"""
    selected_rating = ratings_listbox.curselection()
    if selected_rating:
        index = selected_rating[0]
        item = ratings_listbox.get(index)
        ratings_listbox.delete(index)
        
        for key, value in user_ratings_dict.items():
            if value == item:
                del user_ratings_dict[key]
                break
        print(f"Removed rating: {item}")


def save_ratings(user_ratings_dict, df_games, dir_path):
    """Lưu ratings vào file"""
    try:
        ratings_data = []
        for game_name, rating_info in user_ratings_dict.items():
            match = re.search(r'Rating:\s*(\d+)', rating_info)
            if match:
                rating = int(match.group(1))
                # Tìm game ID dựa trên cột Name
                game_row = df_games[df_games['Name'] == game_name]
                
                if not game_row.empty:
                    app_id = game_row.index[0]
                    ratings_data.append({
                        'AppID': int(app_id),
                        'Name': game_name,
                        'user_rating': rating
                    })
                    print(f"Found game: {game_name} with AppID: {app_id}")
                else:
                    print(f"Warning: Could not find game '{game_name}' in DataFrame")
        
        user_data_dir = os.path.join(os.path.dirname(dir_path), "user_data")
        os.makedirs(user_data_dir, exist_ok=True)
        ratings_file = os.path.join(user_data_dir, "cb_user_ratings.json")
        save_ratings_data(ratings_data, ratings_file)
        
        messagebox.showinfo('Saved', f'Saved {len(ratings_data)} ratings to Content-Based system!')
        
    except Exception as e:
        messagebox.showerror('Error', f'Failed to save ratings: {str(e)}')
        import traceback
        traceback.print_exc()


def clear_all_ratings(ratings_listbox, user_ratings_dict, dir_path):
    """Clear all user ratings"""
    result = tk.messagebox.askyesno('Clear All Ratings',
                                   'Are you sure you want to clear all ratings?\n\nThis action cannot be undone.')

    if not result:
        return

    user_ratings_dict.clear()
    ratings_listbox.delete(0, tk.END)

    try:
        ratings_file = os.path.join(os.path.dirname(dir_path), "user_data", "cb_user_ratings.json")
        if not os.path.exists(os.path.dirname(ratings_file)):
             os.makedirs(os.path.dirname(ratings_file))
             
        with open(ratings_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)

        tk.messagebox.showinfo('Ratings Cleared', 'All ratings have been cleared successfully!')
        print("All user ratings cleared")
    except Exception as e:
        tk.messagebox.showerror('Error', f'Failed to clear ratings file: {str(e)}')


def clear_system_data(dir_path, root=None):
    """Xóa Model đã train và File kết quả cũ"""
    if not messagebox.askyesno("Clear Data", 
                               "Bạn có chắc muốn xóa Model đã train và Kết quả cũ?\n\n(Hành động này sẽ buộc bạn phải Train lại Model từ đầu)."):
        return

    try:
        files_to_delete = [
            os.path.join(dir_path, "cb_model.pkl"),
            os.path.join(dir_path, "cb_recommendations.csv")
        ]
        
        deleted_count = 0
        for file_path in files_to_delete:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Cannot delete {file_path}: {e}")

        # Reset cờ hiệu
        global MODEL_JUST_TRAINED
        MODEL_JUST_TRAINED = True 

        msg = f"Đã xóa {deleted_count} file dữ liệu hệ thống.\nHãy bấm 'Train Model' để tạo lại."
        if root: messagebox.showinfo("Success", msg)
            
    except Exception as e:
        if root: messagebox.showerror("Error", f"Lỗi khi xóa dữ liệu: {str(e)}")


def train_model(dir_path, root=None):
    """Train model (Background thread)"""
    def train_thread():
        global MODEL_JUST_TRAINED
        try:
            games_path = os.path.join(dir_path, "CB_games.csv")
            
            print("Loading games data (Cleaned)...")
            df_games = load_games_csv(games_path)
            
            if df_games is None or df_games.empty:
                if root: root.after(0, lambda: messagebox.showerror('Error', 'Failed to load games data!'))
                return
            
            print("Training Content-Based model...")
            recommender = ContentBasedRecommender()
            success = recommender.train(df_games)
            
            if success:
                model_path = os.path.join(dir_path, "cb_model.pkl")
                recommender.save_model(model_path)
                
                # Đánh dấu là vừa train xong -> Cần reload
                MODEL_JUST_TRAINED = True
                print("Flag MODEL_JUST_TRAINED set to True")
                
                success_msg = f'Model trained successfully!\nProcessed {len(df_games)} games.'
                if root: root.after(0, lambda: messagebox.showinfo('Success', success_msg))
            else:
                if root: root.after(0, lambda: messagebox.showerror('Error', 'Failed to train model!'))
                
        except Exception as e:
            error_msg = f'Failed to train model: {str(e)}'
            print(error_msg)
            if root: root.after(0, lambda: messagebox.showerror('Error', error_msg))
    
    thread = threading.Thread(target=train_thread, daemon=True)
    thread.start()
    return thread


def get_recommendations(dir_path, root=None, preloaded_recommender=None):
    """Lấy recommendations từ Content-Based model"""
    
    def recommend_thread():
        global MODEL_JUST_TRAINED
        try:
            print("Starting recommendations thread...")
            
            model_path = os.path.join(dir_path, "cb_model.pkl")
            games_path = os.path.join(dir_path, "CB_games.csv")
            ratings_path = os.path.join(os.path.dirname(dir_path), "user_data", "cb_user_ratings.json")
            
            if not os.path.exists(model_path):
                if root: root.after(0, lambda: messagebox.showerror('Error', 'Model not found! Please train first.'))
                return

            print("Loading games data...")
            df_games = load_games_csv(games_path)
            if df_games is None:
                if root: root.after(0, lambda: messagebox.showerror('Error', 'Could not load games data.'))
                return

            # --- LOGIC RELOAD MODEL THÔNG MINH ---
            recommender = None
            
            # Nếu vừa train xong hoặc không có preloaded -> Load mới từ đĩa
            if MODEL_JUST_TRAINED or preloaded_recommender is None:
                print("Model was updated or not preloaded. Loading fresh from disk...")
                recommender = ContentBasedRecommender()
                if not recommender.load_model(model_path):
                    if root: root.after(0, lambda: messagebox.showerror('Error', 'Failed to load model!'))
                    return
                # Reset cờ sau khi đã load mới
                if MODEL_JUST_TRAINED:
                    MODEL_JUST_TRAINED = False
            
            # Nếu chưa train lại -> Dùng bản preloaded cho nhanh
            elif preloaded_recommender and preloaded_recommender.is_trained:
                print("Using pre-loaded model (Cached)")
                recommender = preloaded_recommender
            
            # Fallback
            if recommender is None:
                print("Fallback loading...")
                recommender = ContentBasedRecommender()
                recommender.load_model(model_path)
            # -------------------------------------

            # Load ratings
            ratings_data = load_ratings_data(ratings_path)
            rated_games = {}
            if ratings_data:
                for item in ratings_data:
                    app_id = item.get('AppID')
                    rating = item.get('user_rating', 0)
                    if app_id: rated_games[app_id] = rating

            if not rated_games:
                if root: root.after(0, lambda: messagebox.showwarning('Warning', 'No ratings found!'))
                return
            
            # Preferences
            user_preferences = {'max_price': 100}
            
            recommendations = recommender.get_recommendations(df_games, rated_games, user_preferences, top_n=200)
            
            if recommendations.empty:
                if root: root.after(0, lambda: messagebox.showwarning('Warning', 'No recommendations found!'))
                return
            
            # Save results
            out_path = os.path.join(dir_path, "cb_recommendations.csv")
            recommendations.to_csv(out_path, index=False)
            
            # Show results
            result_text = "Top Recommendations:\n\n"
            for _, row in recommendations.head(10).iterrows():
                result_text += f"{row['Name']} - Score: {row['Score']:.2f}\n"
            
            if root: root.after(0, lambda: messagebox.showinfo('Recommendations', result_text))
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            if root: root.after(0, lambda: messagebox.showerror('Error', f'Error: {str(e)}'))

    threading.Thread(target=recommend_thread, daemon=True).start()