"""
KNN Core Logic
Chuyển thể từ knn_model.ipynb sang Python thuần để chạy tự động.
"""

import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_distances
import os
import math

def run_knn_algorithm(knn_dir):
    print(f"--- Running KNN Algorithm in {knn_dir} ---")
    
    # 1. Load Data
    try:
        reviews_path = os.path.join(knn_dir, "final_reviews.csv")
        games_path = os.path.join(knn_dir, "final_games.csv")
        your_games_path = os.path.join(knn_dir, "your_games.csv")
        fav_games_path = os.path.join(knn_dir, "fav_games.csv")
        
        # Load dữ liệu lớn (Reviews & Games List)
        # Lưu ý: final_reviews khá nặng, trong thực tế nên load 1 lần ở ngoài rồi truyền vào
        # Nhưng để đơn giản, ta load ở đây.
        reviews = pd.read_csv(reviews_path)
        # games_details = pd.read_csv(games_path) # Không cần thiết cho tính toán, chỉ cần lúc xuất
        
        # Load User Data
        if not os.path.exists(your_games_path) or os.path.getsize(your_games_path) == 0:
            print("No user games found.")
            return pd.DataFrame()
            
        your_games = pd.read_csv(your_games_path)
        
        if os.path.exists(fav_games_path) and os.path.getsize(fav_games_path) > 0:
            fav_games = pd.read_csv(fav_games_path)
        else:
            fav_games = pd.DataFrame(columns=['gameID'])

    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

    # 2. Xử lý Input của User
    interested_games_id = your_games[your_games['review'] == 0.5]['gameID'].tolist()
    bad_games_id = set(your_games[your_games['review'] == -1]['gameID'])
    my_games_id = sorted(list(your_games['gameID'].unique()))
    not_played_games_id = [id for id in my_games_id if id not in interested_games_id]
    fav_games_set = set(fav_games['gameID']) if not fav_games.empty else set()

    if not my_games_id:
        print("User has not played any games.")
        return pd.DataFrame()

    # 3. Lọc User (Neighbors) - Logic nới lỏng 70%
    num_games = len(my_games_id)
    MATCH_PERCENTAGE = 0.7
    threshold = max(1, int(num_games * MATCH_PERCENTAGE))
    
    # Tìm user trùng game
    user_review_counts = reviews[reviews['app_id'].isin(set(my_games_id))].groupby('user_id')['app_id'].size()
    relevant_users = user_review_counts[user_review_counts >= threshold].index
    
    filtered_reviews = reviews[reviews['user_id'].isin(relevant_users)].copy()
    filtered_reviews['is_recommended'] = filtered_reviews['is_recommended'].map({True: 1, False: -1})
    
    num_unique_users = filtered_reviews['user_id'].nunique()
    
    if num_unique_users == 0:
        print("No similar users found.")
        return pd.DataFrame()

    print(f"Found {num_unique_users} neighbors.")

    # 4. Tạo Ma trận thưa (Sparse Matrix)
    user_id_list = sorted(filtered_reviews['user_id'].unique())
    games_id_reviews = sorted(filtered_reviews['app_id'].unique())
    
    user_to_index = {user_id: idx for idx, user_id in enumerate(user_id_list)}
    app_to_index = {app_id: idx for idx, app_id in enumerate(games_id_reviews)}
    
    row_indices = [user_to_index[uid] for uid in filtered_reviews['user_id']]
    col_indices = [app_to_index[aid] for aid in filtered_reviews['app_id']]
    data = filtered_reviews['is_recommended'].values
    
    user_vector_sparse = csr_matrix((data, (row_indices, col_indices)), shape=(num_unique_users, len(games_id_reviews)))

    # 5. Tạo Vector của User hiện tại
    my_vector_dict = {}
    for game_id in my_games_id:
        if game_id in app_to_index:
            review_val = your_games.loc[your_games['gameID'] == game_id, 'review'].values[0]
            my_vector_dict[app_to_index[game_id]] = review_val
            
    my_vector = csr_matrix((list(my_vector_dict.values()), ([0]*len(my_vector_dict), list(my_vector_dict.keys()))), shape=(1, len(games_id_reviews)))

    # 6. Tính toán KNN (Khoảng cách & Trọng số)
    # Tính cosine distance
    distances = cosine_distances(user_vector_sparse, my_vector).flatten()
    
    # Tính trọng số tin cậy (Base weight)
    base_weight = 1.0
    if len(fav_games_set) > 0:
        base_weight = 1.0 / (10 ** int(len(fav_games_set) ** 0.5))
    
    weights = np.full(len(user_id_list), base_weight)
    
    # Điều chỉnh trọng số dựa trên Fav/Bad games
    for user_idx in range(num_unique_users):
        row = user_vector_sparse[user_idx]
        for game_idx, rating in zip(row.indices, row.data):
            game_id = games_id_reviews[game_idx]
            if rating == 1 and game_id in fav_games_set:
                weights[user_idx] *= 4
            elif rating == 1 and game_id in bad_games_id: # Nếu neighbor thích game mình ghét
                 weights[user_idx] /= 2

    # Tổng hợp điểm (Aggregation)
    # Sửa lỗi chia cho 0 bằng epsilon
    epsilon = 1e-9
    weights_factors = weights / (distances + epsilon)
    
    # Nhân ma trận: (Neighbors x Games) * (Weights)
    # user_vector_sparse: [U x G], weights_factors: [U]
    # Ta cần nhân từng dòng của user_vector_sparse với weights_factors tương ứng
    weighted_vectors = user_vector_sparse.multiply(weights_factors[:, None])
    
    # Cộng dồn theo cột (Games)
    final_scores = weighted_vectors.sum(axis=0).A1 # Flatten ra array 1 chiều

    # 7. Xuất kết quả
    rcm_list = []
    for i, score in enumerate(final_scores):
        if score > 0:
            game_id = games_id_reviews[i]
            # Loại bỏ game đã chơi (trừ khi là Interested)
            if game_id not in not_played_games_id:
                rcm_list.append({'app_id': game_id, 'relevance': score})
    
    # Tạo DataFrame kết quả
    rcm_df = pd.DataFrame(rcm_list)
    
    if not rcm_df.empty:
        rcm_df = rcm_df.sort_values('relevance', ascending=False)
        
        # Map tên game vào (Để Hybrid đọc được)
        games_details = pd.read_csv(games_path)
        id_to_title = dict(zip(games_details['app_id'], games_details['title']))
        id_to_date = dict(zip(games_details['app_id'], games_details['date_release']))
        id_to_positive = dict(zip(games_details['app_id'], games_details['positive_ratio']))
        id_to_reviews = dict(zip(games_details['app_id'], games_details['user_reviews']))

        rcm_df['title'] = rcm_df['app_id'].map(id_to_title)
        rcm_df['date_release'] = rcm_df['app_id'].map(id_to_date)
        rcm_df['positive_ratio'] = rcm_df['app_id'].map(id_to_positive)
        rcm_df['user_reviews'] = rcm_df['app_id'].map(id_to_reviews)
        
        # Lưu file
        output_path = os.path.join(knn_dir, "rcm_games.csv")
        rcm_df.to_csv(output_path, index=False)
        print(f"KNN recommendations saved to {output_path}")
        return rcm_df
    else:
        print("No recommendations generated.")
        return pd.DataFrame()

if __name__ == "__main__":
    # Test chạy thử
    current_dir = os.path.dirname(os.path.abspath(__file__))
    run_knn_algorithm(current_dir)