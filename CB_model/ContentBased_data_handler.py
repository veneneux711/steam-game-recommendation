"""
Data Handler cho Content-Based Filtering System
"""

import pandas as pd
import json
import os


def load_games_csv(file_path):
    """
    Load games từ CSV file
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f'File {file_path} not found.')
        return None
    except pd.errors.EmptyDataError:
        print(f'File {file_path} is empty.')
        return None


def create_games_dict(df):
    """
    Tạo dictionary từ DataFrame để hiển thị trong UI
    """
    if df is None or df.empty:
        return {}
    
    games_dict = {}
    for idx, row in df.iterrows():
        # Trong CSV này, AppID column chứa tên game, index là AppID số
        game_name = str(row.get('AppID', 'Unknown'))
        release_date = row.get('Name', 'N/A')  # Name column chứa release date
        price = row.get('Price', 'N/A')
        positive = row.get('Positive', 0)
        negative = row.get('Negative', 0)
        
        if not game_name or game_name == 'Unknown':
            continue
        
        game_info = f"ID: {idx} ¬ Name: {game_name} ¬ Release: {release_date} ¬ Price: {price} ¬ Reviews: +{positive}/-{negative}"
        games_dict[game_name] = game_info
    
    return games_dict


def save_ratings_data(data, file_path):
    """
    Lưu ratings vào JSON file
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f'Error saving file: {str(e)}')
        return False


def load_ratings_data(file_path):
    """
    Load ratings từ JSON file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f'File {file_path} is not valid JSON.')
        return []

