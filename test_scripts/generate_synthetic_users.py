"""
Generate Synthetic Users (Improved)
Fixed: Chỉ chọn game phổ biến có trong final_reviews.csv để đảm bảo tìm được hàng xóm.
"""
import pandas as pd
import numpy as np
import json
import os
import random
import re

# --- CẤU HÌNH ---
NUM_USERS = 50
MIN_GAMES_PER_USER = 5  # Giảm xuống để dễ tìm trùng khớp
MAX_GAMES_PER_USER = 15
OUTPUT_DIR = "synthetic_data"
KNN_DIR = "KNN_model"

# Định nghĩa Persona với ID game cụ thể (nếu biết) hoặc từ khóa
PERSONAS = {
    "RPG_Fan": ["witcher", "scrolls", "fallout", "mass effect", "divinity", "souls", "elden"],
    "FPS_Fan": ["counter-strike", "doom", "left 4 dead", "bioshock", "borderlands", "destiny", "half-life"],
    "Strategy_Fan": ["civilization", "total war", "xcom", "age of empires", "stellaris", "dota", "cities"],
    "Indie_Cozy": ["stardew", "terraria", "hollow knight", "celeste", "hades", "rimworld", "factorio"],
    "Action_Adventure": ["tomb raider", "assassin", "batman", "god of war", "portal", "gta", "grand theft auto"],
    "Random_Player": []
}

def normalize_name(title):
    if not isinstance(title, str): return ""
    return re.sub(r'[^a-z0-9]', '', title.lower())

def load_popular_games():
    """
    Load danh sách game từ final_games.csv nhưng CHỈ LẤY những game 
    xuất hiện nhiều trong final_reviews.csv
    """
    games_path = os.path.join(KNN_DIR, "final_games.csv")
    reviews_path = os.path.join(KNN_DIR, "final_reviews.csv")
    
    if not os.path.exists(games_path) or not os.path.exists(reviews_path):
        print(f"❌ Thiếu file data trong {KNN_DIR}")
        return pd.DataFrame()
    
    print("Đang đọc dữ liệu game và reviews để lọc game phổ biến...")
    df_games = pd.read_csv(games_path)
    
    # Đọc review để đếm số lượng người chơi cho mỗi game
    # Chỉ đọc 2 cột cần thiết cho nhẹ
    df_reviews = pd.read_csv(reviews_path, usecols=['app_id'])
    
    # Đếm số review cho mỗi app_id
    game_counts = df_reviews['app_id'].value_counts()
    
    # Chỉ lấy Top 1000 game phổ biến nhất để tạo user ảo
    # Điều này đảm bảo khi chạy KNN sẽ luôn tìm thấy người chơi cùng
    top_game_ids = game_counts.head(1000).index
    
    # Lọc df_games chỉ giữ lại top games
    popular_games = df_games[df_games['app_id'].isin(top_game_ids)].copy()
    popular_games['norm_title'] = popular_games['title'].apply(normalize_name)
    
    print(f"✅ Đã chọn lọc {len(popular_games)} game phổ biến nhất để tạo dữ liệu ảo.")
    return popular_games

def generate_user_data(user_id, persona_name, keywords, all_games_df):
    """Tạo dữ liệu cho 1 user"""
    
    selected_games = pd.DataFrame()
    
    if persona_name == "Random_Player":
        selected_games = all_games_df.sample(random.randint(MIN_GAMES_PER_USER, MAX_GAMES_PER_USER))
    else:
        # Tìm game khớp từ khóa trong danh sách game phổ biến
        mask = all_games_df['norm_title'].str.contains('|'.join(keywords), case=False)
        genre_games = all_games_df[mask]
        
        # Nếu tìm được ít nhất 3 game đúng gu
        if len(genre_games) >= 3:
            # Lấy tối đa số lượng cần thiết
            n_take = min(len(genre_games), random.randint(MIN_GAMES_PER_USER, MAX_GAMES_PER_USER))
            selected_games = genre_games.sample(n_take)
        else:
            # Nếu không tìm thấy game đúng gu trong top popular, lấy random
            # (Trường hợp này hiếm nếu keywords chuẩn)
            selected_games = all_games_df.sample(MIN_GAMES_PER_USER)

    # --- Phần tạo rating giữ nguyên như cũ ---
    knn_data = [] 
    fav_data = [] 
    cb_data = [] 
    
    for _, game in selected_games.iterrows():
        # Logic rating giả lập (Thích game đúng gu, random game khác)
        is_preferred = True # Mặc định thích vì đã lọc theo persona
        
        rating_num = random.choice([4, 5]) if is_preferred else random.choice([1, 2, 3])
        review_text = "Like" if rating_num == 5 else "Interested"
        
        # KNN Data
        knn_val = 1 if rating_num >= 4 else 0.5 if rating_num == 3 else -1
        knn_data.append({
            "gameID": int(game['app_id']),
            "gameName": game['title'],
            "review": knn_val
        })
        
        # Fav Data
        if rating_num == 5 and random.random() < 0.4:
            fav_data.append({
                "gameID": int(game['app_id']),
                "gameName": game['title']
            })
            
        # CB Data
        cb_data.append({
            "AppID": int(game['app_id']),
            "Name": game['title'],
            "user_rating": rating_num
        })

    return knn_data, fav_data, cb_data

def main():
    print(f"🚀 Bắt đầu tạo {NUM_USERS} user ảo (Dựa trên Game Phổ Biến)...")
    
    # Load game phổ biến (QUAN TRỌNG)
    df_games = load_popular_games()
    
    if df_games.empty: return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    summary = []

    for i in range(NUM_USERS):
        persona = random.choice(list(PERSONAS.keys()))
        user_id = f"user_{i+1:02d}_{persona}"
        
        # In ra dòng này để biết đang chạy
        # print(f"-> Generating {user_id}...", end="\r")
        
        knn_rows, fav_rows, cb_rows = generate_user_data(
            user_id, persona, PERSONAS[persona], df_games
        )
        
        user_dir = os.path.join(OUTPUT_DIR, user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        pd.DataFrame(knn_rows).to_csv(os.path.join(user_dir, "your_games.csv"), index=False)
        pd.DataFrame(fav_rows, columns=['gameID', 'gameName']).to_csv(os.path.join(user_dir, "fav_games.csv"), index=False)
        
        with open(os.path.join(user_dir, "cb_user_ratings.json"), 'w', encoding='utf-8') as f:
            json.dump(cb_rows, f, indent=2, ensure_ascii=False)

        summary.append({
            "user_id": user_id,
            "persona": persona,
            "games_count": len(knn_rows)
        })

    pd.DataFrame(summary).to_csv(os.path.join(OUTPUT_DIR, "users_summary.csv"), index=False)
    print(f"\n✅ Đã tạo xong {NUM_USERS} user tại '{OUTPUT_DIR}/'")

if __name__ == "__main__":
    main()