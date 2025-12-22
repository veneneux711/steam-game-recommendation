"""
Button Commands riêng cho Decision Tree System
Tách biệt hoàn toàn với KNN commands
"""

import tkinter as tk
from tkinter import messagebox
import re
import pandas as pd
import os
import json
from DecisionTree_model import DecisionTreeGameRecommender
from DecisionTree_data_handler import save_decision_tree_data, load_decision_tree_data

def update_search_dt(search_frame, games_dict, list_frame):
    """
    Update search results cho Decision Tree
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

def add_rating_dt(rating, games_listbox, ratings_listbox, user_ratings_dict):
    """
    Thêm rating cho game (Decision Tree)
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

def remove_rating_dt(ratings_listbox, user_ratings_dict):
    """
    Xóa rating (Decision Tree)
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

def save_ratings_dt(user_ratings_dict, df_decision_games, dir_path):
    """
    Lưu ratings vào file (Decision Tree)
    """
    try:
        ratings_data = []
        
        for game_name, rating_info in user_ratings_dict.items():
            # Extract rating từ string
            match = re.search(r'Rating:\s*(\d+)', rating_info)
            if match:
                rating = int(match.group(1))
                
                # Tìm game ID từ DataFrame
                game_row = df_decision_games[df_decision_games['Name'] == game_name]
                if not game_row.empty:
                    app_id = game_row.iloc[0]['AppID']
                    ratings_data.append({
                        'AppID': app_id,
                        'Name': game_name,
                        'user_rating': rating
                    })
        
        # Lưu vào JSON file
        ratings_file = os.path.join(dir_path, "dt_user_ratings.json")
        save_decision_tree_data(ratings_data, ratings_file)
        
        messagebox.showinfo('Saved', f'Saved {len(ratings_data)} ratings to Decision Tree system!')
        
    except Exception as e:
        messagebox.showerror('Error', f'Failed to save ratings: {str(e)}')

def train_model_dt(dir_path):
    """
    Train Decision Tree model (Decision Tree)
    """
    try:
        # Load data
        decision_games_path = os.path.join(dir_path, "decision_games.csv")
        ratings_path = os.path.join(dir_path, "dt_user_ratings.json")
        
        if not os.path.exists(decision_games_path):
            messagebox.showerror('Error', 'decision_games.csv not found!')
            return
        
        if not os.path.exists(ratings_path):
            messagebox.showwarning('Warning', 'No ratings found! Please rate some games first.')
            return
        
        # Load data
        df_games = pd.read_csv(decision_games_path)
        ratings_data = load_decision_tree_data(ratings_path)
        
        if not ratings_data:
            messagebox.showwarning('Warning', 'No ratings data found!')
            return
        
        # Merge ratings với games
        ratings_df = pd.DataFrame(ratings_data)
        df_train = df_games.merge(ratings_df[['AppID', 'user_rating']], on='AppID', how='inner')
        
        if df_train.empty:
            messagebox.showwarning('Warning', 'No matching games found!')
            return
        
        # Train model
        recommender = DecisionTreeGameRecommender()
        train_score, test_score = recommender.train(df_train, target_column='user_rating')
        
        if train_score is not None:
            # Save model
            model_path = os.path.join(dir_path, "dt_model.pkl")
            recommender.save_model(model_path)
            
            messagebox.showinfo('Success', 
                              f'Model trained successfully!\nTrain Accuracy: {train_score:.4f}\nTest Accuracy: {test_score:.4f}')
        else:
            messagebox.showerror('Error', 'Failed to train model!')
            
    except Exception as e:
        messagebox.showerror('Error', f'Failed to train model: {str(e)}')

def get_recommendations_dt(dir_path):
    """
    Lấy recommendations từ Decision Tree model
    """
    try:
        # Load model
        model_path = os.path.join(dir_path, "dt_model.pkl")
        decision_games_path = os.path.join(dir_path, "decision_games.csv")
        
        if not os.path.exists(model_path):
            messagebox.showerror('Error', 'Model not found! Please train the model first.')
            return
        
        if not os.path.exists(decision_games_path):
            messagebox.showerror('Error', 'decision_games.csv not found!')
            return
        
        # Load model và data
        recommender = DecisionTreeGameRecommender()
        if not recommender.load_model(model_path):
            messagebox.showerror('Error', 'Failed to load model!')
            return
        
        df_games = pd.read_csv(decision_games_path)
        
        # Load preferences (có thể từ UI)
        user_preferences = {
            'max_price': 100,
            'min_positive_ratio': 0.7
        }
        
        # Get recommendations
        recommendations = recommender.get_recommendations(df_games, user_preferences, top_n=20)
        
        if recommendations.empty:
            messagebox.showwarning('Warning', 'No recommendations found!')
            return
        
        # Save recommendations
        recommendations_path = os.path.join(dir_path, "dt_recommendations.csv")
        recommendations.to_csv(recommendations_path, index=False)
        
        # Show results
        result_text = "Top Recommendations (Decision Tree):\n\n"
        for idx, row in recommendations.head(10).iterrows():
            result_text += f"{row['Name']} - Score: {row['Score']:.4f}\n"
        
        messagebox.showinfo('Recommendations', result_text)
        
        print(f"Saved {len(recommendations)} recommendations to {recommendations_path}")
        
    except Exception as e:
        messagebox.showerror('Error', f'Failed to get recommendations: {str(e)}')

