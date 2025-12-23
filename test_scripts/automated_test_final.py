"""
Automated Test Script for Steam ML Recommendation System (Headless Version)
Chạy trực tiếp logic Python (không qua UI/BAT) để đảm bảo tốc độ và tự động hóa.
"""

import os
import shutil
import pandas as pd
import sys
import json
import time
import re

# --- 1. SETUP ĐƯỜNG DẪN VÀ IMPORT ---
current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(current_dir)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
    sys.path.append(os.path.join(PROJECT_ROOT, 'KNN_model'))
    sys.path.append(os.path.join(PROJECT_ROOT, 'CB_model'))
    sys.path.append(os.path.join(PROJECT_ROOT, 'Hybrid_model'))

try:
    from CB_model.ContentBased_model import ContentBasedRecommender
    from KNN_model.KNN_Core import run_knn_algorithm 
    from Hybrid_model.Hybrid_recommendations_reader import calculate_hybrid_ranking, save_hybrid_ranking
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def normalize_name(title):
    if not isinstance(title, str): return ""
    return re.sub(r'[^a-z0-9]', '', title.lower())

def copy_user_data(user_folder_name, source_dir, target_knn, target_user_data):
    """Copy dữ liệu từ synthetic_data vào hệ thống"""
    user_source_dir = os.path.join(source_dir, user_folder_name)
    
    # Copy CSV cho KNN
    shutil.copy2(os.path.join(user_source_dir, "your_games.csv"), os.path.join(target_knn, "your_games.csv"))
    shutil.copy2(os.path.join(user_source_dir, "fav_games.csv"), os.path.join(target_knn, "fav_games.csv"))
    
    # Copy JSON cho CB
    shutil.copy2(os.path.join(user_source_dir, "cb_user_ratings.json"), os.path.join(target_user_data, "cb_user_ratings.json"))
    return True

def save_user_results(user_folder_name, results_dir, PROJECT_ROOT):
    """Lưu kết quả của user hiện tại vào thư mục riêng"""
    user_res_dir = os.path.join(results_dir, user_folder_name)
    os.makedirs(user_res_dir, exist_ok=True)
    
    # Copy KNN Result
    knn_src = os.path.join(PROJECT_ROOT, "KNN_model", "rcm_games.csv")
    if os.path.exists(knn_src): shutil.copy2(knn_src, os.path.join(user_res_dir, "knn_results.csv"))
    
    # Copy CB Result
    cb_src = os.path.join(PROJECT_ROOT, "CB_model", "cb_recommendations.csv")
    if os.path.exists(cb_src): shutil.copy2(cb_src, os.path.join(user_res_dir, "cb_results.csv"))
    
    # Copy Hybrid Result
    hyb_src = os.path.join(PROJECT_ROOT, "results", "hybrid_ranking.csv")
    if os.path.exists(hyb_src): shutil.copy2(hyb_src, os.path.join(user_res_dir, "hybrid_results.csv"))

def main():
    print("=" * 80)
    print("AUTOMATED TEST SCRIPT (HEADLESS MODE)")
    print("=" * 80)

    synthetic_dir = os.path.join(PROJECT_ROOT, "synthetic_data")
    if not os.path.exists(synthetic_dir):
        print("❌ Data not found.")
        return

    # Lấy danh sách user
    all_users = [d for d in os.listdir(synthetic_dir) if os.path.isdir(os.path.join(synthetic_dir, d))]
    users_to_test = all_users[:15] # Chạy 15 user đầu tiên

    # --- KHỞI TẠO CB MODEL (1 Lần duy nhất) ---
    print("\n[INIT] Loading Content-Based Model & Mapping...")
    cb_model = ContentBasedRecommender()
    cb_games_path = os.path.join(PROJECT_ROOT, "CB_model/CB_games.csv")
    
    # Load Games & Map ID
    df_cb_games = pd.read_csv(cb_games_path, index_col=0)
    
    # Logic tìm cột tên game (Fix lỗi lệch cột)
    name_col = 'Name'
    if 'AppID' in df_cb_games.columns:
        if not str(df_cb_games.iloc[0]['AppID']).replace('.', '', 1).isdigit():
            name_col = 'AppID'
    
    # Tạo từ điển mapping (Tên chuẩn hóa -> ID CB)
    cb_name_to_id = {}
    for idx, row in df_cb_games.iterrows():
        clean_name = normalize_name(str(row.get(name_col, '')))
        if clean_name: cb_name_to_id[clean_name] = idx
        
    # Train Model
    cb_model.train(df_cb_games)
    print("✅ CB Model Trained & Ready.")

    # --- ĐƯỜNG DẪN HỆ THỐNG ---
    target_knn_dir = os.path.join(PROJECT_ROOT, "KNN_model")
    target_cb_dir = os.path.join(PROJECT_ROOT, "CB_model")
    target_user_data = os.path.join(PROJECT_ROOT, "user_data")
    results_dir = os.path.join(PROJECT_ROOT, "test_results") # Thư mục kết quả tổng
    
    # --- VÒNG LẶP TEST ---
    for i, user in enumerate(users_to_test):
        print(f"\n[{i+1}/{len(users_to_test)}] Processing: {user}")
        
        try:
            # 1. Nạp dữ liệu
            copy_user_data(user, synthetic_dir, target_knn_dir, target_user_data)

            # 2. Chạy KNN (Headless)
            run_knn_algorithm(target_knn_dir)

            # 3. Chạy CB (Headless + ID Translation)
            # Đọc rating user
            with open(os.path.join(target_user_data, "cb_user_ratings.json"), 'r', encoding='utf-8') as f:
                raw_ratings = json.load(f)
            
            # Dịch ID
            rated_games = {}
            for item in raw_ratings:
                norm = normalize_name(item.get('Name', ''))
                if norm in cb_name_to_id:
                    rated_games[cb_name_to_id[norm]] = item.get('user_rating', 0)
            
            # Dự đoán & Lưu file
            cb_recs = cb_model.get_recommendations(df_cb_games, rated_games, {'max_price': 100}, top_n=200)
            cb_recs.to_csv(os.path.join(target_cb_dir, "cb_recommendations.csv"), index=False)

            # 4. Chạy Hybrid
            hybrid_df = calculate_hybrid_ranking(target_knn_dir, target_cb_dir, top_n=50)
            
            # Lưu kết quả Hybrid vào thư mục chung (cho script visualize đọc)
            hybrid_out = os.path.join(PROJECT_ROOT, "results", "hybrid_ranking.csv")
            save_hybrid_ranking(hybrid_df, hybrid_out)

            # 5. Lưu trữ kết quả riêng cho User này
            save_user_results(user, results_dir, PROJECT_ROOT)
            
            # In Top 1
            if not hybrid_df.empty:
                print(f"   -> Top 1: {hybrid_df.iloc[0]['Title']}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETED")
    print(f"Individual results saved in: {results_dir}")

if __name__ == "__main__":
    main()