"""
Button Commands cho Content-Based Filtering System
"""

import tkinter as tk
from tkinter import messagebox
import re
import pandas as pd
import os
import threading
from ContentBased_model import ContentBasedRecommender
from ContentBased_data_handler import save_ratings_data, load_ratings_data


def update_search(search_frame, games_dict, list_frame):
    """
    Update search results
    """
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
    """
    Thêm rating cho game
    Rating: 1-5 (1=Dislike, 5=Like)
    """
    selected_game_info = games_listbox.get(tk.ACTIVE)
    if selected_game_info:
        # Extract game name từ info string
        match = re.search(r'Name:\s*(.*?)\s*¬', selected_game_info)
        if match:
            selected_game_name = match.group(1).strip()
        else:
            messagebox.showwarning('Invalid Format', 'Failed to extract game name.')
            return
        
        # Update hoặc thêm rating
        rating_text = {1: 'Dislike', 2: 'Bad', 3: 'Neutral', 4: 'Good', 5: 'Like'}
        user_ratings_dict[selected_game_name] = f"Name: {selected_game_name} ¬ Rating: {rating} ({rating_text[rating]})"
        
        # Update listbox
        ratings_listbox.delete(0, tk.END)
        for rating_info in user_ratings_dict.values():
            ratings_listbox.insert(tk.END, rating_info)
        
        print(f"Added rating {rating} for {selected_game_name}")


def remove_rating(ratings_listbox, user_ratings_dict):
    """
    Xóa rating
    """
    selected_rating = ratings_listbox.curselection()
    if selected_rating:
        index = selected_rating[0]
        item = ratings_listbox.get(index)
        
        # Delete from listbox
        ratings_listbox.delete(index)
        
        # Find và delete từ dictionary
        for key, value in user_ratings_dict.items():
            if value == item:
                del user_ratings_dict[key]
                break
        
        print(f"Removed rating: {item}")


def save_ratings(user_ratings_dict, df_games, dir_path):
    """
    Lưu ratings vào file
    """
    try:
        ratings_data = []
        
        for game_name, rating_info in user_ratings_dict.items():
            # Extract rating từ string
            match = re.search(r'Rating:\s*(\d+)', rating_info)
            if match:
                rating = int(match.group(1))
                
                # Tìm game ID từ DataFrame
                game_row = df_games[df_games['AppID'] == game_name]
                if not game_row.empty:
                    app_id = game_row.index[0]  # Index là AppID số
                    ratings_data.append({
                        'AppID': int(app_id),
                        'Name': game_name,
                        'user_rating': rating
                    })
                    print(f"Found game: {game_name} with AppID: {app_id}")
                else:
                    print(f"Warning: Could not find game '{game_name}' in DataFrame")
        
        # Lưu vào JSON file
        ratings_file = os.path.join(dir_path, "cb_user_ratings.json")
        save_ratings_data(ratings_data, ratings_file)
        
        messagebox.showinfo('Saved', f'Saved {len(ratings_data)} ratings to Content-Based system!')
        
    except Exception as e:
        messagebox.showerror('Error', f'Failed to save ratings: {str(e)}')
        import traceback
        print(traceback.format_exc())


def train_model(dir_path, root=None):
    """
    Train Content-Based model
    Chạy trong background thread
    """
    def train_thread():
        try:
            games_path = os.path.join(dir_path, "CB_games.csv")
            
            if not os.path.exists(games_path):
                if root:
                    root.after(0, lambda: messagebox.showerror('Error', 'CB_games.csv not found!'))
                return
            
            # Load data
            print("Loading games data...")
            df_games = pd.read_csv(games_path)
            
            # Train model
            print("Training Content-Based model...")
            recommender = ContentBasedRecommender()
            success = recommender.train(df_games)
            
            if success:
                # Save model
                model_path = os.path.join(dir_path, "cb_model.pkl")
                recommender.save_model(model_path)
                
                success_msg = f'Model trained successfully!\nProcessed {len(df_games)} games.'
                if root:
                    root.after(0, lambda: messagebox.showinfo('Success', success_msg))
            else:
                if root:
                    root.after(0, lambda: messagebox.showerror('Error', 'Failed to train model!'))
                
        except Exception as e:
            error_msg = f'Failed to train model: {str(e)}'
            print(error_msg)
            import traceback
            traceback.print_exc()
            if root:
                root.after(0, lambda: messagebox.showerror('Error', error_msg))
    
    # Chạy trong background thread
    thread = threading.Thread(target=train_thread, daemon=True)
    thread.start()
    return thread


def get_recommendations(dir_path, root=None, preloaded_recommender=None):
    """
    Lấy recommendations từ Content-Based model
    Chạy trong background thread
    """
    def recommendations_thread():
        try:
            # Load model
            model_path = os.path.join(dir_path, "cb_model.pkl")
            games_path = os.path.join(dir_path, "CB_games.csv")
            ratings_path = os.path.join(dir_path, "cb_user_ratings.json")
            
            if not os.path.exists(model_path):
                if root:
                    root.after(0, lambda: messagebox.showerror('Error', 'Model not found! Please train the model first.'))
                return
            
            if not os.path.exists(games_path):
                if root:
                    root.after(0, lambda: messagebox.showerror('Error', 'CB_games.csv not found!'))
                return
            
            # Sử dụng pre-loaded model nếu có, nếu không thì load mới
            if preloaded_recommender is not None and preloaded_recommender.is_trained:
                print("Using pre-loaded model (fast!)")
                recommender = preloaded_recommender
            else:
                print("Loading model...")
                recommender = ContentBasedRecommender()
                if not recommender.load_model(model_path):
                    if root:
                        root.after(0, lambda: messagebox.showerror('Error', 'Failed to load model!'))
                    return
            
            df_games = pd.read_csv(games_path)
            
            # Load ratings
            ratings_data = load_ratings_data(ratings_path)
            rated_games = {}
            if ratings_data:
                for item in ratings_data:
                    if isinstance(item, dict):
                        app_id = item.get('AppID')
                        rating = item.get('user_rating', 0)
                        if app_id is not None:
                            rated_games[app_id] = rating
            
            if not rated_games:
                if root:
                    root.after(0, lambda: messagebox.showwarning('Warning', 'No ratings found! Please rate some games first.'))
                return
            
            # Load preferences
            user_preferences = {
                'max_price': 100,
                'min_positive_ratio': 0.7
            }
            
            # Get recommendations
            recommendations = recommender.get_recommendations(
                df_games,
                rated_games,
                user_preferences,
                top_n=20
            )
            
            if recommendations.empty:
                if root:
                    root.after(0, lambda: messagebox.showwarning('Warning', 'No recommendations found!'))
                return
            
            # Save recommendations
            recommendations_path = os.path.join(dir_path, "cb_recommendations.csv")
            recommendations.to_csv(recommendations_path, index=False)
            
            # Show results
            result_text = "Top Recommendations (Content-Based):\n\n"
            for idx, row in recommendations.head(10).iterrows():
                result_text += f"{row['Name']} - Score: {row['Score']:.2f} (Similarity: {row['Similarity']:.3f})\n"
            
            if root:
                root.after(0, lambda: messagebox.showinfo('Recommendations', result_text))
            
            print(f"Saved {len(recommendations)} recommendations to {recommendations_path}")
            
        except Exception as e:
            error_msg = f'Failed to get recommendations: {str(e)}'
            print(error_msg)
            import traceback
            traceback.print_exc()
            if root:
                root.after(0, lambda: messagebox.showerror('Error', error_msg))
    
    # Chạy trong background thread
    thread = threading.Thread(target=recommendations_thread, daemon=True)
    thread.start()
    return thread

