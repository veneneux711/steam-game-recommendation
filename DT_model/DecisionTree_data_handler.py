"""
Data Handler riêng cho Decision Tree System
Xử lý dữ liệu từ decision_games.csv và decision_games.json
"""

import pandas as pd
import json
import os

def load_decision_games_csv(file_path):
    """
    Load decision games từ CSV file
    
    Parameters:
    -----------
    file_path : str
        Đường dẫn đến file decision_games.csv
    
    Returns:
    --------
    pd.DataFrame : DataFrame chứa decision games data
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

def load_decision_games_json(file_path):
    """
    Load decision games từ JSON file
    
    Parameters:
    -----------
    file_path : str
        Đường dẫn đến file decision_games.json
    
    Returns:
    --------
    dict hoặc list : Dữ liệu từ JSON file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f'File {file_path} not found.')
        return None
    except json.JSONDecodeError:
        print(f'File {file_path} is not valid JSON.')
        return None

def create_decision_games_dict(df):
    """
    Tạo dictionary từ DataFrame để hiển thị trong UI
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame chứa decision games
    
    Returns:
    --------
    dict : Dictionary với key là game name, value là thông tin game
    """
    if df is None or df.empty:
        return {}
    
    games_dict = {}
    for idx, row in df.iterrows():
        # Trong CSV này, AppID cột thực sự chứa tên game, Name chứa date
        app_id_col = row.get('AppID', 'N/A')
        name_col = row.get('Name', 'Unknown')
        release_date = row.get('Release date', 'N/A')
        
        # Kiểm tra xem AppID có phải là tên game (string) hay số
        if isinstance(app_id_col, str) and not app_id_col.replace('.', '').replace('-', '').isdigit():
            # AppID là tên game
            game_name = str(app_id_col)
            # Tìm AppID thực từ index hoặc cột khác
            app_id = str(idx) if idx else 'N/A'
        elif isinstance(name_col, str) and not any(char.isdigit() for char in name_col[:5]):
            # Name là tên game (không bắt đầu bằng số)
            game_name = str(name_col)
            app_id = str(app_id_col) if app_id_col != 'N/A' else str(idx)
        else:
            # Cả hai đều không phải tên game, skip
            continue
        
        # Đảm bảo game_name hợp lệ
        if not game_name or game_name == 'Unknown' or game_name == 'N/A':
            continue
        
        # Tạo thông tin game
        price = row.get('Price', 'N/A')
        positive = row.get('Positive', 0)
        negative = row.get('Negative', 0)
        
        game_info = f"ID: {app_id} ¬ Name: {game_name} ¬ Release: {release_date} ¬ Price: {price} ¬ Reviews: +{positive}/-{negative}"
        games_dict[game_name] = game_info
    
    return games_dict

def save_decision_tree_data(data, file_path):
    """
    Lưu dữ liệu Decision Tree vào file
    
    Parameters:
    -----------
    data : dict hoặc list
        Dữ liệu cần lưu
    file_path : str
        Đường dẫn file để lưu
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f'Error saving file: {str(e)}')
        return False

def load_decision_tree_data(file_path):
    """
    Load dữ liệu Decision Tree từ file
    
    Parameters:
    -----------
    file_path : str
        Đường dẫn file cần load
    
    Returns:
    --------
    dict hoặc list : Dữ liệu đã load
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f'File {file_path} is not valid JSON.')
        return {}

