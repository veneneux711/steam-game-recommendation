import pandas as pd
import numpy as np
import random
import sys
import os
import time

# --- 1. THIẾT LẬP ĐƯỜNG DẪN MODULE ---
# Lấy đường dẫn thư mục hiện tại (test_scripts)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Lấy đường dẫn thư mục gốc dự án (Steam ML - Sửa lại CB)
project_root = os.path.dirname(current_dir)
# Đường dẫn đến CB_model để import
cb_model_path = os.path.join(project_root, "CB_model")

# Thêm đường dẫn để Python tìm thấy file model
sys.path.append(cb_model_path)

# --- 2. IMPORT MODULE TỪ CB_MODEL ---
try:
    from ContentBased_model import ContentBasedRecommender
    from ContentBased_data_handler import load_games_csv
except ImportError as e:
    print(f"Lỗi Import: {e}")
    print(f"Đường dẫn đang thử: {cb_model_path}")
    sys.exit(1)

# --- 3. CẤU HÌNH ---
# File dữ liệu nằm trong CB_model
DATA_PATH = os.path.join(cb_model_path, "CB_games.csv")

TEST_RATIO = 0.2            # Lấy 20% dataset để test
TOP_K = 10                  # Số lượng game recommend mỗi lần test

def calculate_jaccard_similarity(str1, str2):
    """Tính độ tương đồng tập hợp giữa 2 chuỗi tags/genres"""
    set1 = set([x.strip().lower() for x in str(str1).split(',') if x.strip()])
    set2 = set([x.strip().lower() for x in str(str2).split(',') if x.strip()])
    
    if not set1 or not set2:
        return 0.0
        
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union

def evaluate_model():
    print("-" * 50)
    print("BẮT ĐẦU QUÁ TRÌNH KIỂM THỬ MODEL (EVALUATION)")
    print("-" * 50)

    # 1. Load Data
    print(f"[1] Loading Data from: {DATA_PATH}...")
    df = load_games_csv(DATA_PATH)
    if df is None or df.empty:
        print("Lỗi: Không tìm thấy dữ liệu hoặc file rỗng.")
        return

    # 2. Train Model
    print(f"[2] Training Model trên toàn bộ {len(df)} games...")
    recommender = ContentBasedRecommender()
    recommender.train(df)

    if not recommender.is_trained:
        print("Lỗi: Train thất bại.")
        return

    # 3. Tạo Test Set (Lấy ngẫu nhiên 20%)
    num_test = int(len(df) * TEST_RATIO)
    test_indices = random.sample(list(df.index), num_test)
    print(f"[3] Đã chọn ngẫu nhiên {num_test} games ({TEST_RATIO*100}%) để chạy test.")

    # Các biến lưu kết quả
    total_genre_match = 0
    total_tag_similarity = 0
    total_recommendations = 0
    
    # 4. Chạy vòng lặp test
    print(f"[4] Đang tính toán (Dự kiến mất vài phút)...")
    start_time_loop = time.time()
    
    for i, app_id in enumerate(test_indices):
        # --- HIỂN THỊ TIẾN ĐỘ (Cứ 50 game báo 1 lần) ---
        if (i + 1) % 50 == 0:
            percent = ((i + 1) / num_test) * 100
            elapsed = time.time() - start_time_loop
            print(f"    -> Progress: {i + 1}/{num_test} ({percent:.1f}%) - Time: {elapsed:.0f}s")
        # -----------------------------------------------

        # Lấy thông tin game gốc (Query Game)
        try:
            query_game = df.loc[app_id]
        except KeyError:
            continue

        query_genres = str(query_game.get('Genres', ''))
        query_tags = str(query_game.get('Tags', ''))
        
        # Giả lập rating 5 sao
        rated_games = {app_id: 5}
        
        # Lấy Recommendations
        try:
            recs = recommender.get_recommendations(df, rated_games, user_preferences=None, top_n=TOP_K)
        except Exception:
            continue
        
        if recs.empty:
            continue

        # Đánh giá từng game được recommend
        for _, rec_row in recs.iterrows():
            rec_id = rec_row['AppID']
            
            if rec_id not in df.index: continue

            target_game = df.loc[rec_id]
            target_genres = str(target_game.get('Genres', ''))
            target_tags = str(target_game.get('Tags', ''))

            # --- METRIC 1: GENRE MATCH ---
            main_genre = query_genres.split(',')[0].strip() if query_genres else ""
            if main_genre and main_genre in target_genres:
                total_genre_match += 1
            
            # --- METRIC 2: TAG SIMILARITY ---
            sim_score = calculate_jaccard_similarity(query_tags, target_tags)
            total_tag_similarity += sim_score
            
            total_recommendations += 1

    # 5. Tính toán kết quả cuối cùng
    if total_recommendations == 0:
        print("Không có recommendation nào được tạo ra.")
        return

    avg_genre_match = (total_genre_match / total_recommendations) * 100
    avg_tag_sim = (total_tag_similarity / total_recommendations) * 100

    report_content = f"""
    ==================================================
    KẾT QUẢ ĐÁNH GIÁ MODEL (EVALUATION REPORT)
    ==================================================
    Thời gian chạy: {time.strftime("%Y-%m-%d %H:%M:%S")}
    Dataset Size: {len(df)} games
    Test Set Size: {num_test} games ({(num_test/len(df))*100:.0f}%)
    Recommendations per game: {TOP_K}
    --------------------------------------------------
    1. Genre Match Score : {avg_genre_match:.2f}%
       (Tỷ lệ game được gợi ý đúng thể loại chính)
       
    2. Tag Consistency   : {avg_tag_sim:.2f}%
       (Độ trùng khớp về nhãn dán - Jaccard Index)
    --------------------------------------------------
    NHẬN XÉT:
    - Genre > 70%: Model phân loại tốt.
    - Tag > 40%: Model hiểu được ngữ cảnh nội dung.
    ==================================================
    """

    # In ra màn hình
    print(report_content)

    # --- LƯU VÀO FOLDER TEST_RESULTS ---
    results_dir = os.path.join(project_root, "test_results")
    
    # Tạo folder nếu chưa có
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"[INFO] Đã tạo thư mục: {results_dir}")

    output_file = os.path.join(results_dir, "cb_evaluation_report.txt")
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"\n[OK] Đã lưu báo cáo chi tiết vào file:\n     {output_file}")
    except Exception as e:
        print(f"\n[!] Lỗi không lưu được file: {e}")

if __name__ == "__main__":
    evaluate_model()