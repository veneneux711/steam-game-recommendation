"""
Hybrid Recommendations Reader (Final Fix)
Fixed: 
1. Tự động tìm AppID từ final_games.csv nếu file kết quả KNN bị thiếu.
2. Ghép dữ liệu bằng Tên Game (Name Matching) để khắc phục lệch ID.
"""

import pandas as pd
import os
import re
import sys

# Hàm chuẩn hóa tên để so sánh
def normalize_name(title):
    if not isinstance(title, str): return ""
    # Chuyển về chữ thường, bỏ ký tự đặc biệt
    return re.sub(r'[^a-z0-9]', '', title.lower())

def read_knn_recommendations(knn_dir, top_n=200):
    try:
        path = os.path.join(knn_dir, "rcm_games.csv")
        if not os.path.exists(path): 
            print(f"KNN file not found: {path}")
            return pd.DataFrame()
        
        df = pd.read_csv(path)
        
        # --- FIX LỖI THIẾU CỘT APP_ID ---
        if 'app_id' not in df.columns:
            print("KNN output is missing 'app_id'. Attempting to recover IDs from final_games.csv...")
            games_path = os.path.join(knn_dir, "final_games.csv")
            
            if os.path.exists(games_path):
                try:
                    # Load file gốc để lấy ID
                    games_df = pd.read_csv(games_path)
                    # Tạo từ điển: Tên Game -> ID
                    title_to_id = dict(zip(games_df['title'], games_df['app_id']))
                    # Map vào dataframe hiện tại
                    df['app_id'] = df['title'].map(title_to_id)
                except Exception as e:
                    print(f"Failed to map App IDs: {e}")
                    df['app_id'] = 0 # Fallback nếu lỗi
            else:
                print("final_games.csv not found. Setting AppID to 0.")
                df['app_id'] = 0

        # Đổi tên cột chuẩn hóa
        rename_map = {'relevance': 'knn_score', 'app_id': 'app_id_knn', 'title': 'title_knn'}
        df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
        
        # Tạo cột tên chuẩn hóa để merge
        if 'title_knn' in df.columns:
            df['normalized_title'] = df['title_knn'].apply(normalize_name)
            
        return df.head(top_n)
        
    except Exception as e:
        print(f"Error reading KNN: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def read_cb_recommendations(cb_dir, top_n=200):
    try:
        path = os.path.join(cb_dir, "cb_recommendations.csv")
        if not os.path.exists(path): return pd.DataFrame()
        
        df = pd.read_csv(path)
        # CB Score là độ tương đồng (Score)
        df = df.rename(columns={'Score': 'cb_score', 'AppID': 'app_id_cb', 'Name': 'title_cb'})
        
        # Tạo cột tên chuẩn hóa
        if 'title_cb' in df.columns:
            df['normalized_title'] = df['title_cb'].apply(normalize_name)
        
        return df.head(top_n)
    except Exception as e:
        print(f"Error reading CB: {e}")
        return pd.DataFrame()

def calculate_hybrid_ranking(knn_dir, cb_dir, top_n=50, knn_weight=0.6, cb_weight=0.4):
    print("Reading recommendations...")
    
    # 1. Đọc dữ liệu
    knn_df = read_knn_recommendations(knn_dir, top_n=200)
    cb_df = read_cb_recommendations(cb_dir, top_n=200)
    
    print(f"KNN Candidates: {len(knn_df)}")
    print(f"CB Candidates: {len(cb_df)}")
    
    # Kiểm tra nếu dataframe rỗng
    if knn_df.empty and cb_df.empty:
        return pd.DataFrame()

    # 2. Chuẩn hóa điểm số (Normalize 0-1)
    if not knn_df.empty and 'knn_score' in knn_df.columns:
        knn_max = knn_df['knn_score'].max()
        if knn_max > 0: knn_df['knn_norm'] = knn_df['knn_score'] / knn_max
        else: knn_df['knn_norm'] = 0
    
    if not cb_df.empty and 'cb_score' in cb_df.columns:
        cb_max = cb_df['cb_score'].max()
        if cb_max > 0: cb_df['cb_norm'] = cb_df['cb_score'] / cb_max
        else: cb_df['cb_norm'] = 0

    # 3. MERGE DỮ LIỆU (Full Outer Join theo Tên)
    # Nếu một trong 2 bên rỗng, trả về bên kia
    if knn_df.empty:
        merged = cb_df
        # Fake columns cho KNN để code dưới không lỗi
        merged['knn_score'] = 0
        merged['knn_norm'] = 0
        merged['title_knn'] = merged['title_cb']
        merged['app_id_knn'] = merged['app_id_cb']
    elif cb_df.empty:
        merged = knn_df
        merged['cb_score'] = 0
        merged['cb_norm'] = 0
        merged['title_cb'] = merged['title_knn']
        merged['app_id_cb'] = merged['app_id_knn']
    else:
        # Merge thật
        merged = pd.merge(knn_df, cb_df, on='normalized_title', how='outer', suffixes=('_k', '_c'))
    
    final_results = []
    
    for _, row in merged.iterrows():
        # Xử lý Title (Lấy cái nào không NaN)
        title = row.get('title_knn', '')
        if pd.isna(title) or title == '': title = row.get('title_cb', 'Unknown')
            
        # Xử lý AppID (Ưu tiên CB vì ID chuẩn)
        app_id_cb = row.get('app_id_cb', float('nan'))
        app_id_knn = row.get('app_id_knn', float('nan'))
        
        # Logic lấy ID an toàn:
        if pd.notna(app_id_cb) and app_id_cb != 0:
            app_id = app_id_cb
        elif pd.notna(app_id_knn):
            app_id = app_id_knn
        else:
            app_id = 0
            
        # Lấy điểm
        k_norm = row.get('knn_norm', 0) if pd.notna(row.get('knn_norm', 0)) else 0
        c_norm = row.get('cb_norm', 0) if pd.notna(row.get('cb_norm', 0)) else 0
        
        k_raw = row.get('knn_score', 0) if pd.notna(row.get('knn_score', 0)) else 0
        c_raw = row.get('cb_score', 0) if pd.notna(row.get('cb_score', 0)) else 0
        
        # --- CÔNG THỨC TÍNH ĐIỂM ---
        base_score = (k_norm * knn_weight) + (c_norm * cb_weight)
        
        # Synergy Boost: Nếu có cả 2 điểm -> Bonus
        if k_norm > 0 and c_norm > 0:
            boost = (k_norm * c_norm) ** 0.5
            final_score = base_score + (boost * 0.5)
        else:
            final_score = base_score * 0.8
            
        final_results.append({
            'App Id': int(app_id),
            'Title': title,
            'Hybrid Score': round(final_score * 10, 2),
            'Knn Score': round(k_raw, 2),
            'Cb Score': round(c_raw, 2)
        })
    
    # 4. Tạo bảng kết quả
    hybrid_df = pd.DataFrame(final_results)
    hybrid_df = hybrid_df.sort_values('Hybrid Score', ascending=False).head(top_n)
    
    # Reset Rank
    hybrid_df.insert(0, 'Rank', range(1, len(hybrid_df) + 1))
    
    # Debug info
    overlap = len(hybrid_df[ (hybrid_df['Knn Score'] > 0) & (hybrid_df['Cb Score'] > 0) ])
    print(f"--- SUCCESS: Found {overlap} overlapping games in Top {top_n} ---")
    
    return hybrid_df

def save_hybrid_ranking(df, path):
    try:
        df.to_csv(path, index=False)
        print(f"Saved to {path}")
        return True  
    except Exception as e:
        print(f"Error saving: {e}")
        return False 

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    knn_dir = os.path.join(project_root, "KNN_model")
    cb_dir = os.path.join(project_root, "CB_model")
    
    hybrid_ranking = calculate_hybrid_ranking(
        knn_dir, 
        cb_dir, 
        top_n=100,       # <--- Sửa từ 50 lên 100 (Lấy nhiều hơn để KNN lọt vào)
        knn_weight=0.7,  # <--- Tăng trọng số KNN (Để đẩy điểm KNN lên)
        cb_weight=0.3    # <--- Giảm trọng số CB
    )
    if not hybrid_ranking.empty:
        results_dir = os.path.join(project_root, "results")
        os.makedirs(results_dir, exist_ok=True)
        save_hybrid_ranking(hybrid_ranking, os.path.join(results_dir, "hybrid_ranking.csv"))