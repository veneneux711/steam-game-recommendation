"""
Data Handler cho Content-Based Filtering System
Fixed: Xử lý file CSV bị lệch cột (Header AppID chứa Tên Game)
"""

import pandas as pd
import numpy as np
import json
import os

def clean_currency(x):
    """Chuyển đổi giá tiền từ string sang float"""
    if pd.isna(x): return 0.0
    if isinstance(x, (int, float)): return float(x)
    clean_str = str(x).lower().replace('$', '').replace(',', '').strip()
    if 'free' in clean_str:
        return 0.0
    try:
        return float(clean_str)
    except:
        return 0.0

def clean_number(x):
    """Chuyển đổi số lượng review từ string sang int"""
    if pd.isna(x): return 0
    if isinstance(x, (int, float)): return int(x)
    clean_str = str(x).replace(',', '').split('.')[0].strip()
    try:
        return int(clean_str)
    except:
        return 0

def load_games_csv(file_path):
    """
    Load games từ CSV file và làm sạch dữ liệu
    """
    try:
        if not os.path.exists(file_path):
            print(f'File {file_path} not found.')
            return None

        # Load CSV. Cột đầu tiên (index_col=0) là AppID thật (số)
        df = pd.read_csv(file_path, index_col=0)
        
        # --- FIX LỖI LỆCH CỘT (Dựa trên ảnh của bạn) ---
        # Cột header 'AppID' đang chứa Tên Game -> Đổi thành 'Name'
        # Cột header 'Name' đang chứa Ngày -> Đổi thành 'Release_Date'
        if 'AppID' in df.columns and not pd.api.types.is_numeric_dtype(df['AppID']):
             df.rename(columns={
                'AppID': 'Name',
                'Name': 'Release_Date'
            }, inplace=True)
        
        # Đặt tên cho Index là AppID để dễ truy xuất
        df.index.name = 'AppID'

        # --- CHUYỂN ĐỔI DỮ LIỆU SANG SỐ ---
        if 'Price' in df.columns:
            df['Price'] = df['Price'].apply(clean_currency)
            
        if 'Positive' in df.columns:
            df['Positive'] = df['Positive'].apply(clean_number)
            
        if 'Negative' in df.columns:
            df['Negative'] = df['Negative'].apply(clean_number)
            
        # Fill NA cho Genres và Tags để tránh lỗi khi train
        df['Genres'] = df['Genres'].fillna('')
        df['Tags'] = df['Tags'].fillna('')

        print(f"Data loaded successfully. Shape: {df.shape}")
        return df
        
    except Exception as e:
        print(f'Error loading CSV: {str(e)}')
        return None

def create_games_dict(df):
    """
    Tạo dictionary từ DataFrame để hiển thị trong UI
    """
    if df is None or df.empty:
        return {}
    
    games_dict = {}
    for app_id, row in df.iterrows():
        # Lấy tên game (đã được rename ở hàm load)
        game_name = str(row.get('Name', 'Unknown'))
        
        release_date = str(row.get('Release_Date', 'N/A'))
        price = row.get('Price', 0)
        pos = row.get('Positive', 0)
        
        if not game_name or game_name == 'Unknown':
            continue
            
        price_str = "Free" if price == 0 else f"${price}"
        
        # Format hiển thị trên Listbox
        game_info = f"ID: {app_id} ¬ Name: {game_name} ¬ Release: {release_date} ¬ Price: {price_str} ¬ Reviews: {pos}+"
        games_dict[game_name] = game_info
    
    return games_dict

def save_ratings_data(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f'Error saving file: {str(e)}')
        return False

def load_ratings_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []