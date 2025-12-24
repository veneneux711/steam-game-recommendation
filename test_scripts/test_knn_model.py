import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_distances
import random
import os
import time
from datetime import datetime

# --- CẤU HÌNH ---
DATA_FILE = "final_reviews.csv"
TEST_USER_COUNT = 50    # Số lượng user để test
MIN_REVIEWS = 50        # Số review tối thiểu để được chọn
TOP_K = 10              # Số lượng game gợi ý
MATCH_PERCENTAGE = 0.5  # Ngưỡng lọc hàng xóm (Giữ 0.3-0.5 để có kết quả tốt)

def get_project_root():
    """Lấy đường dẫn thư mục gốc dự án"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)

def load_data():
    project_root = get_project_root()
    file_path = os.path.join(project_root, "KNN_model", DATA_FILE)
    
    print(f"[1] Loading data from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        # Chuyển đổi True/False sang 1/-1
        if 'is_recommended' in df.columns:
            df['is_recommended'] = df['is_recommended'].map({True: 1, False: -1})
        return df
    except Exception as e:
        print(f"Lỗi: {e}")
        return None
    
def run_test_for_single_user(target_user_id, user_history_df, full_df):
    """Chạy thuật toán KNN cho 1 user cụ thể"""
    liked_games = user_history_df[user_history_df['is_recommended'] == 1]
    
    if len(liked_games) < 5: return 0, 0 
    
    # Shuffle và chia 80/20
    liked_games_list = liked_games['app_id'].tolist()
    random.shuffle(liked_games_list)
    
    split_point = int(len(liked_games_list) * 0.8)
    train_game_ids = set(liked_games_list[:split_point]) 
    test_game_ids = set(liked_games_list[split_point:])  
    
    if not test_game_ids: return 0, 0

    # Tìm Hàng xóm
    threshold = max(1, int(len(train_game_ids) * MATCH_PERCENTAGE))
    
    potential_neighbors = full_df[
        (full_df['app_id'].isin(train_game_ids)) & 
        (full_df['user_id'] != target_user_id)
    ]
    
    user_counts = potential_neighbors.groupby('user_id')['app_id'].size()
    relevant_users_idx = user_counts[user_counts >= threshold].index
    
    if len(relevant_users_idx) == 0:
        return 0, 0 
        
    neighbor_reviews = full_df[full_df['user_id'].isin(relevant_users_idx)]
    
    # Tạo Matrix
    user_list = sorted(neighbor_reviews['user_id'].unique())
    game_list = sorted(neighbor_reviews['app_id'].unique())
    
    user_map = {u: i for i, u in enumerate(user_list)}
    game_map = {g: i for i, g in enumerate(game_list)}
    
    row_ind = [user_map[u] for u in neighbor_reviews['user_id']]
    col_ind = [game_map[g] for g in neighbor_reviews['app_id']]
    data = neighbor_reviews['is_recommended'].values
    
    sparse_matrix = csr_matrix((data, (row_ind, col_ind)), shape=(len(user_list), len(game_list)))
    
    # Tạo Vector User
    my_vector_dict = {}
    for gid in train_game_ids:
        if gid in game_map:
            my_vector_dict[game_map[gid]] = 1 
            
    if not my_vector_dict: return 0, 0
    
    my_vector = csr_matrix(
        (list(my_vector_dict.values()), ([0]*len(my_vector_dict), list(my_vector_dict.keys()))), 
        shape=(1, len(game_list))
    )
    
    # Tính khoảng cách
    dists = cosine_distances(sparse_matrix, my_vector).flatten()
    epsilon = 1e-9
    weights = 1.0 / (dists + epsilon)
    
    weighted_matrix = sparse_matrix.multiply(weights[:, None])
    scores = weighted_matrix.sum(axis=0).A1
    
    top_indices = np.argsort(scores)[::-1]
    
    recommendations = []
    count = 0
    for idx in top_indices:
        if scores[idx] <= 0: break 
        game_id = game_list[idx]
        if game_id in train_game_ids: continue
        
        recommendations.append(game_id)
        count += 1
        if count >= TOP_K: break
        
    # Đánh giá
    hits = 0
    for rec_id in recommendations:
        if rec_id in test_game_ids:
            hits += 1
            
    precision = (hits / len(recommendations)) * 100 if recommendations else 0
    recall = (hits / len(test_game_ids)) * 100 if test_game_ids else 0
    
    return precision, recall

def evaluate_model():
    print("-" * 50)
    print("BẮT ĐẦU KIỂM THỬ KNN MODEL (Collaborative Filtering)")
    print("-" * 50)
    
    df = load_data()
    if df is None: return

    print(f"[2] Đang lọc danh sách User tiềm năng (> {MIN_REVIEWS} reviews)...")
    user_counts = df['user_id'].value_counts()
    valid_users = user_counts[user_counts >= MIN_REVIEWS].index.tolist()
    
    print(f"    -> Tìm thấy {len(valid_users)} user đủ điều kiện.")
    
    # Chọn ngẫu nhiên
    actual_test_count = min(TEST_USER_COUNT, len(valid_users))
    test_users = random.sample(valid_users, actual_test_count)
    print(f"[3] Đã chọn ngẫu nhiên {actual_test_count} user để chạy test sâu.")
    print("-" * 50)
    
    total_precision = 0
    total_recall = 0
    successful_tests = 0
    
    # Danh sách để lưu kết quả xuất file
    export_data = []
    
    start_time = time.time()
    
    for i, uid in enumerate(test_users):
        user_history = df[df['user_id'] == uid]
        prec, rec = run_test_for_single_user(uid, user_history, df)
        
        status = "No Match"
        if prec > 0 or rec > 0:
            total_precision += prec
            total_recall += rec
            successful_tests += 1
            status = "Success"
            print(f"User {i+1}/{len(test_users)} (ID: {uid}): Precision={prec:.1f}%, Recall={rec:.1f}%")
        else:
            print(f"User {i+1}/{len(test_users)} (ID: {uid}): No match")
            
        # Lưu vào list để xuất file
        export_data.append({
            "User_ID": uid,
            "Precision": round(prec, 2),
            "Recall": round(rec, 2),
            "Status": status,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # Tính toán kết quả trung bình
    avg_precision = total_precision / successful_tests if successful_tests > 0 else 0
    avg_recall = total_recall / successful_tests if successful_tests > 0 else 0
    
    # In báo cáo ra màn hình
    print("\n" + "=" * 50)
    print("KẾT QUẢ ĐÁNH GIÁ KNN (EVALUATION REPORT)")
    print("=" * 50)
    print(f"Thời gian chạy: {time.time() - start_time:.2f} giây")
    print(f"Số user được test: {len(test_users)}")
    print(f"Số user tìm được gợi ý: {successful_tests}")
    print("-" * 50)
    print(f"1. Average Precision@{TOP_K}: {avg_precision:.2f}%")
    print(f"2. Average Recall@{TOP_K}   : {avg_recall:.2f}%")
    print("=" * 50)

    # --- XUẤT FILE CSV ---
    project_root = get_project_root()
    results_dir = os.path.join(project_root, "test_results")
    
    # Tạo thư mục nếu chưa có
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"[INFO] Đã tạo thư mục: {results_dir}")
        
    output_path = os.path.join(results_dir, "knn_evaluation_details.csv")
    
    try:
        # Tạo DataFrame và lưu
        df_export = pd.DataFrame(export_data)
        
        # Thêm dòng tổng kết vào cuối file CSV luôn cho tiện
        summary_row = {
            "User_ID": "AVERAGE",
            "Precision": round(avg_precision, 2),
            "Recall": round(avg_recall, 2),
            "Status": f"Found {successful_tests}/{len(test_users)}",
            "Timestamp": ""
        }
        # Nối dòng tổng kết (sử dụng pd.concat thay vì append sắp bị loại bỏ)
        df_summary = pd.DataFrame([summary_row])
        df_export = pd.concat([df_export, df_summary], ignore_index=True)
        
        df_export.to_csv(output_path, index=False)
        print(f"\n[OK] Đã xuất file kết quả chi tiết tại:")
        print(f"     {output_path}")
    except Exception as e:
        print(f"\n[ERROR] Không thể lưu file CSV: {e}")

if __name__ == "__main__":
    evaluate_model()