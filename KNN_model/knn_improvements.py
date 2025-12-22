"""
Các hàm cải tiến cho hệ thống KNN Recommendation
Import và sử dụng trong knn_model.ipynb
"""

import numpy as np
from scipy.sparse import csr_matrix
import pandas as pd


def calculate_optimal_threshold(my_games_id, reviews, percentile=25):
    """
    Tính threshold tối ưu dựa trên phân phối số lượng reviews của users
    
    Parameters:
    -----------
    my_games_id : list
        Danh sách game IDs của user hiện tại
    reviews : DataFrame
        DataFrame chứa reviews
    percentile : int, default=25
        Percentile để tính threshold (loại bỏ users có quá ít reviews)
    
    Returns:
    --------
    int : Threshold tối ưu
    """
    user_review_counts = reviews[reviews['app_id'].isin(set(my_games_id))].groupby('user_id')['app_id'].size()
    
    if len(user_review_counts) == 0:
        return max(3, int(0.1 * len(my_games_id)))
    
    # Lấy percentile thứ 25 (loại bỏ users có quá ít reviews)
    threshold = int(np.percentile(user_review_counts, percentile))
    
    # Đảm bảo threshold tối thiểu
    min_threshold = max(3, int(0.1 * len(my_games_id)))
    threshold = max(threshold, min_threshold)
    
    return threshold


def calculate_optimal_k(distance_list, min_k=5, max_k=50):
    """
    Tìm K tối ưu dựa trên elbow method
    
    Parameters:
    -----------
    distance_list : list
        Danh sách tuples (index, distance, vector) đã sắp xếp theo distance
    min_k : int, default=5
        K tối thiểu
    max_k : int, default=50
        K tối đa
    
    Returns:
    --------
    int : K tối ưu
    """
    if len(distance_list) < min_k:
        return len(distance_list)
    
    # Tính gradient của distances
    distances = [d[1] for d in distance_list[:max_k]]
    
    if len(distances) < 2:
        return min_k
    
    gradients = [distances[i+1] - distances[i] for i in range(len(distances)-1)]
    
    # Tìm elbow point: điểm mà gradient tăng đột ngột
    if len(gradients) >= min_k:
        avg_gradient = np.mean(gradients[:min_k])
        for i in range(min_k, len(gradients)):
            if gradients[i] > 2 * avg_gradient:  # Tăng đột ngột
                return i + 1
    
    # Nếu không tìm thấy elbow, dùng heuristic
    optimal_k = min(max_k, max(min_k, int(np.sqrt(len(distance_list)))))
    return optimal_k


def calculate_weights_improved(user_vector_sparse, games_id_reviews, fav_games_set, bad_games_id, 
                                fav_weight_multiplier=2.0, bad_weight_multiplier=0.5):
    """
    Tính weights cải tiến cho users dựa trên favorite và bad games
    
    Parameters:
    -----------
    user_vector_sparse : csr_matrix
        Sparse matrix chứa user vectors
    games_id_reviews : list
        Danh sách game IDs trong reviews
    fav_games_set : set
        Set các favorite game IDs
    bad_games_id : set
        Set các bad game IDs
    fav_weight_multiplier : float, default=2.0
        Hệ số nhân cho mỗi favorite game trùng
    bad_weight_multiplier : float, default=0.5
        Hệ số nhân cho mỗi bad game trùng
    
    Returns:
    --------
    np.array : Array chứa weights cho từng user
    """
    num_users = user_vector_sparse.shape[0]
    weights = np.ones(num_users)
    
    for user_index in range(num_users):
        row = user_vector_sparse[user_index]
        fav_matches = 0
        bad_matches = 0
        
        # Đếm số favorite và bad games trùng
        for game_index, game_review in zip(row.indices, row.data):
            if game_review == 1:  # User like game này
                if games_id_reviews[game_index] in fav_games_set:
                    fav_matches += 1
                elif games_id_reviews[game_index] in bad_games_id:
                    bad_matches += 1
        
        # Tăng weights dựa trên số lượng favorite games trùng
        if fav_matches > 0:
            weights[user_index] *= (1 + fav_weight_multiplier * fav_matches)
        
        # Giảm weights nếu có bad games trùng
        if bad_matches > 0:
            weights[user_index] *= (bad_weight_multiplier ** bad_matches)
    
    return weights


def getKnnVector_improved(my_vector, user_vector_sparse, weights, distance_list, 
                          k=None, use_adaptive_k=True, min_k=5, max_k=50, distance_exponent=1.5):
    """
    Tính KNN vector với các cải tiến
    
    Parameters:
    -----------
    my_vector : csr_matrix
        Vector của user hiện tại
    user_vector_sparse : csr_matrix
        Sparse matrix chứa tất cả user vectors
    weights : np.array
        Weights cho từng user
    distance_list : list
        Danh sách (index, distance, vector) đã sắp xếp
    k : int, optional
        Số neighbors cố định (nếu None sẽ dùng adaptive)
    use_adaptive_k : bool, default=True
        Có dùng adaptive K không
    min_k : int, default=5
        K tối thiểu
    max_k : int, default=50
        K tối đa
    distance_exponent : float, default=1.5
        Exponent cho inverse distance weighting (>1 để tăng độ nhạy)
    
    Returns:
    --------
    np.array : Vector dự đoán
    """
    # Adaptive K selection
    if use_adaptive_k and k is None:
        k = calculate_optimal_k(distance_list, min_k, max_k)
    elif k is None:
        k = min(30, len(distance_list))
    
    actual_k = min(k, len(distance_list))
    
    if actual_k == 0:
        return np.zeros(my_vector.shape[1])
    
    indices = np.array([distance_list[i][0] for i in range(actual_k)])
    distances = np.array([distance_list[i][1] for i in range(actual_k)])
    
    user_vectors = user_vector_sparse[indices]
    user_weights = weights[indices]
    
    # Improved weighting: Sử dụng inverse distance với smoothing
    epsilon = 1e-6
    safe_distances = distances + epsilon
    
    # Inverse distance weighting với exponential decay
    distance_weights = 1.0 / (safe_distances ** distance_exponent)
    
    # Combine user weights và distance weights
    combined_weights = user_weights * distance_weights
    
    # Normalize weights
    combined_weights = combined_weights / (np.sum(combined_weights) + epsilon)
    
    # Multiply và sum
    weighted_vectors = user_vectors.multiply(combined_weights[:, None])
    vector = weighted_vectors.sum(axis=0).A1
    
    return vector


def filter_by_genre_similarity(recommendations, user_games, games_metadata, min_genre_overlap=0.3):
    """
    Lọc recommendations dựa trên genre similarity
    
    Parameters:
    -----------
    recommendations : list
        Danh sách tuples (game_id, relevance)
    user_games : DataFrame
        DataFrame chứa games user đã chơi với reviews
    games_metadata : dict hoặc DataFrame
        Metadata của games (cần có 'genres' field)
    min_genre_overlap : float, default=0.3
        Genre overlap tối thiểu (0-1)
    
    Returns:
    --------
    list : Danh sách recommendations đã lọc và điều chỉnh relevance
    """
    # Lấy genres của games user đã like/favorite
    user_genres = set()
    liked_games = user_games[user_games['review'] >= 0.5]['gameID'].tolist()
    
    for game_id in liked_games:
        if isinstance(games_metadata, dict):
            if game_id in games_metadata:
                genres = games_metadata[game_id].get('genres', [])
                if isinstance(genres, str):
                    genres = [g.strip() for g in genres.split(',')]
                user_genres.update(genres)
        elif isinstance(games_metadata, pd.DataFrame):
            game_row = games_metadata[games_metadata['app_id'] == game_id]
            if not game_row.empty:
                genres = game_row.iloc[0].get('genres', '')
                if isinstance(genres, str):
                    genres = [g.strip() for g in genres.split(',')]
                user_genres.update(genres)
    
    if len(user_genres) == 0:
        return recommendations  # Không có genre info, trả về nguyên bản
    
    # Tính genre overlap cho mỗi recommendation
    filtered_recommendations = []
    for game_id, relevance in recommendations:
        game_genres = set()
        
        if isinstance(games_metadata, dict):
            if game_id in games_metadata:
                genres = games_metadata[game_id].get('genres', [])
                if isinstance(genres, str):
                    genres = [g.strip() for g in genres.split(',')]
                game_genres = set(genres)
        elif isinstance(games_metadata, pd.DataFrame):
            game_row = games_metadata[games_metadata['app_id'] == game_id]
            if not game_row.empty:
                genres = game_row.iloc[0].get('genres', '')
                if isinstance(genres, str):
                    genres = [g.strip() for g in genres.split(',')]
                game_genres = set(genres)
        
        if len(game_genres) == 0:
            # Không có genre info, giữ nguyên nhưng giảm relevance một chút
            filtered_recommendations.append((game_id, relevance * 0.9))
            continue
        
        # Tính overlap
        intersection = user_genres & game_genres
        union = user_genres | game_genres
        overlap = len(intersection) / len(union) if len(union) > 0 else 0
        
        if overlap >= min_genre_overlap:
            # Tăng relevance dựa trên genre overlap
            adjusted_relevance = relevance * (1 + overlap * 0.5)  # Tăng tối đa 50%
            filtered_recommendations.append((game_id, adjusted_relevance))
    
    return sorted(filtered_recommendations, key=lambda x: -x[1])


def apply_popularity_penalty(recommendations, games_metadata, penalty_factor=0.1):
    """
    Áp dụng penalty cho games quá phổ biến để tăng diversity
    
    Parameters:
    -----------
    recommendations : list
        Danh sách tuples (game_id, relevance)
    games_metadata : dict hoặc DataFrame
        Metadata của games (cần có 'user_reviews' field)
    penalty_factor : float, default=0.1
        Hệ số penalty (0-1)
    
    Returns:
    --------
    list : Danh sách recommendations đã điều chỉnh relevance
    """
    # Tìm max reviews để normalize
    max_reviews = 0
    for game_id, _ in recommendations:
        if isinstance(games_metadata, dict):
            reviews = games_metadata.get(game_id, {}).get('user_reviews', 0)
        elif isinstance(games_metadata, pd.DataFrame):
            game_row = games_metadata[games_metadata['app_id'] == game_id]
            reviews = game_row.iloc[0].get('user_reviews', 0) if not game_row.empty else 0
        max_reviews = max(max_reviews, reviews)
    
    if max_reviews == 0:
        return recommendations
    
    adjusted_recommendations = []
    for game_id, relevance in recommendations:
        if isinstance(games_metadata, dict):
            reviews = games_metadata.get(game_id, {}).get('user_reviews', 0)
        elif isinstance(games_metadata, pd.DataFrame):
            game_row = games_metadata[games_metadata['app_id'] == game_id]
            reviews = game_row.iloc[0].get('user_reviews', 0) if not game_row.empty else 0
        
        popularity_score = reviews / max_reviews
        
        # Áp dụng penalty: games quá phổ biến bị giảm relevance
        # Nhưng vẫn giữ một phần để không loại bỏ hoàn toàn
        penalty = 1 - (penalty_factor * popularity_score)
        adjusted_relevance = relevance * max(penalty, 0.5)  # Tối thiểu 50%
        
        adjusted_recommendations.append((game_id, adjusted_relevance))
    
    return sorted(adjusted_recommendations, key=lambda x: -x[1])


def calculate_diversity(recommendations, games_metadata, top_k=10):
    """
    Tính diversity: Độ đa dạng của recommendations
    
    Parameters:
    -----------
    recommendations : list
        Danh sách tuples (game_id, relevance)
    games_metadata : dict hoặc DataFrame
        Metadata của games (cần có 'genres' field)
    top_k : int, default=10
        Số recommendations đầu tiên để tính diversity
    
    Returns:
    --------
    float : Diversity score (0-1)
    """
    top_games = recommendations[:top_k]
    genres = []
    
    for game_id, _ in top_games:
        if isinstance(games_metadata, dict):
            game_genres = games_metadata.get(game_id, {}).get('genres', [])
        elif isinstance(games_metadata, pd.DataFrame):
            game_row = games_metadata[games_metadata['app_id'] == game_id]
            game_genres = game_row.iloc[0].get('genres', '') if not game_row.empty else ''
        
        if isinstance(game_genres, str):
            game_genres = [g.strip() for g in game_genres.split(',')]
        
        genres.extend(game_genres)
    
    if len(genres) == 0:
        return 0.0
    
    unique_genres = len(set(genres))
    diversity = unique_genres / len(genres) if len(genres) > 0 else 0
    
    return diversity


def calculate_coverage(recommendations, all_games, top_k=10):
    """
    Tính coverage: Tỷ lệ games được recommend
    
    Parameters:
    -----------
    recommendations : list
        Danh sách tuples (game_id, relevance)
    all_games : list hoặc set
        Tất cả games có sẵn
    top_k : int, default=10
        Số recommendations đầu tiên để tính coverage
    
    Returns:
    --------
    float : Coverage score (0-1)
    """
    recommended_ids = {game_id for game_id, _ in recommendations[:top_k]}
    
    if isinstance(all_games, (list, set)):
        total_games = len(all_games)
    else:
        total_games = len(all_games) if hasattr(all_games, '__len__') else 0
    
    coverage = len(recommended_ids) / total_games if total_games > 0 else 0
    
    return coverage

