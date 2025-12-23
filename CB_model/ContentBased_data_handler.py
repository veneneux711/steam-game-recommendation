"""
Data Handler cho Content-Based Filtering System
Fixed: Column realignment and Data type conversion
"""

import pandas as pd
import numpy as np
import json
import os

def clean_currency(x):
    """Chuyển đổi giá tiền từ string sang float"""
    if pd.isna(x): return 0.0
    if isinstance(x, (int, float)): return float(x)
    # Xử lý các trường hợp: "$19.99", "Free", "Free to Play", "10,000"
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
    # Xử lý: "1,234", "10.5"
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
        # Load CSV với cột đầu tiên là Index (chính là AppID thật)
        df = pd.read_csv(file_path, index_col=0)
        
        # --- BƯỚC 1: SỬA TÊN CỘT BỊ LỆCH (Dựa trên ảnh CSV của bạn) ---
        # Trong file CSV của bạn: 
        # Cột header 'AppID' đang chứa Tên Game
        # Cột header 'Name' đang chứa Ngày phát hành
        # Index của DataFrame đang chứa AppID số
        
        # Đổi tên cột cho đúng ý nghĩa thực tế
        df.rename(columns={
            'AppID': 'Name',           # Cột AppID cũ thực ra là Name
            'Name': 'Release_Date'     # Cột Name cũ thực ra là Date
        }, inplace=True)
        
        # Đặt tên cho Index là AppID để dễ truy xuất
        df.index.name = 'AppID'
        
        # Tạo cột AppID riêng (nếu cần dùng như một cột bình thường)
        df['Real_AppID'] = df.index

        # --- BƯỚC 2: CHUYỂN ĐỔI DỮ LIỆU SANG SỐ (QUAN TRỌNG) ---
        if 'Price' in df.columns:
            df['Price'] = df['Price'].apply(clean_currency)
            
        if 'Positive' in df.columns:
            df['Positive'] = df['Positive'].apply(clean_number)
            
        if 'Negative' in df.columns:
            df['Negative'] = df['Negative'].apply(clean_number)
            
        print(f"Data loaded successfully. Shape: {df.shape}")
        # Debug: In ra vài dòng để kiểm tra
        print("Sample data after cleaning:")
        print(df[['Name', 'Price', 'Positive', 'Negative']].head(3))
        
        return df
        
    except FileNotFoundError:
        print(f'File {file_path} not found.')
        return None
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
        # Bây giờ cột 'Name' đã đúng là tên game (do code rename ở trên)
        game_name = str(row.get('Name', 'Unknown'))
        
        # Lấy các thông tin khác
        release_date = str(row.get('Release_Date', 'N/A'))
        price = row.get('Price', 0)
        positive = row.get('Positive', 0)
        negative = row.get('Negative', 0)
        
        if not game_name or game_name == 'Unknown':
            continue
            
        # Format hiển thị
        price_str = "Free" if price == 0 else f"${price}"
        
        game_info = f"ID: {app_id} ¬ Name: {game_name} ¬ Release: {release_date} ¬ Price: {price_str} ¬ Reviews: +{positive}/-{negative}"
        games_dict[game_name] = game_info
    
    return games_dict


def save_ratings_data(data, file_path):
    """Lưu ratings vào JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f'Error saving file: {str(e)}')
        return False


def load_ratings_data(file_path):
    """Load ratings từ JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f'File {file_path} is not valid JSON.')
        return []