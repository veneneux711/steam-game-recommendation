# Lý Thuyết và Tinh Chỉnh Hệ Thống Recommendation KNN

## 1. Lý Thuyết KNN-Based Collaborative Filtering

### 1.1. Tổng Quan

**Collaborative Filtering (CF)** là một kỹ thuật recommendation dựa trên giả định: "Những người có sở thích tương tự trong quá khứ sẽ có sở thích tương tự trong tương lai."

**K-Nearest Neighbors (KNN)** là một thuật toán CF tìm K người dùng (neighbors) có sở thích gần nhất với người dùng hiện tại, sau đó dự đoán ratings dựa trên ratings của những neighbors này.

### 1.2. Các Bước Cơ Bản

1. **Xây dựng User-Item Matrix**: Tạo ma trận sparse với:
   - Hàng: Users
   - Cột: Items (games)
   - Giá trị: Ratings/Reviews (1: Like, 0.5: Interested, -0.5: Neutral, -1: Dislike)

2. **Tính Similarity**: Đo độ tương đồng giữa user hiện tại và các users khác
   - **Cosine Similarity**: Đo góc giữa 2 vectors
   - **Cosine Distance** = 1 - Cosine Similarity

3. **Tìm K Nearest Neighbors**: Chọn K users có distance nhỏ nhất

4. **Dự đoán Ratings**: Tính weighted average của ratings từ K neighbors

### 1.3. Công Thức Toán Học

#### Cosine Similarity:
```
similarity(u, v) = (u · v) / (||u|| × ||v||)
```

#### Cosine Distance:
```
distance(u, v) = 1 - similarity(u, v)
```

#### Weighted Prediction:
```
prediction(i) = Σ(weight_k × rating_k,i) / Σ(weight_k)
```

Trong đó:
- `weight_k = user_weight_k / distance_k`
- `user_weight_k`: Trọng số của user k (dựa trên favorite games)
- `distance_k`: Khoảng cách cosine giữa user hiện tại và user k

## 2. Phân Tích Hệ Thống Hiện Tại

### 2.1. Kiến Trúc Hệ Thống

#### Bước 1: Lọc Users Liên Quan
```python
threshold = max(min(10, num_games), int(math.sqrt(num_games)))
relevant_users = users đã review >= threshold games trong my_games_id
```
- **Mục đích**: Chỉ xét users có đủ dữ liệu để so sánh
- **Vấn đề**: Threshold có thể quá thấp hoặc quá cao tùy dataset

#### Bước 2: Tạo User-Item Matrix (Sparse)
- Sử dụng `scipy.sparse.csr_matrix` để tiết kiệm memory
- Giá trị: 1 (Like), -1 (Dislike), 0.5 (Interested), -0.5 (Neutral)

#### Bước 3: Tính Trọng Số Users
```python
weights = np.ones(len(users)) / (10 ** int(len(fav_games) ** 0.5))

for user in users:
    if user có game trong fav_games:
        weights[user] *= 4
    elif user có game trong bad_games:
        weights[user] /= 2  # (Code hiện tại có bug: continue trước khi chia)
```
- **Ý tưởng**: Tăng trọng số cho users có favorite games giống nhau
- **Vấn đề**: 
  - Công thức khởi tạo weights phức tạp và có thể không tối ưu
  - Bug: `continue` trước khi chia weights cho bad games

#### Bước 4: Tìm KNN và Dự Đoán
```python
distances = cosine_distances(user_vector_sparse, my_vector)
k_nearest = K users có distance nhỏ nhất
weighted_vector = Σ(weights[k] / distances[k] × user_vectors[k])
```
- **K mặc định**: `min(30, len(users))`
- **Vấn đề**: K cố định có thể không tối ưu cho mọi trường hợp

### 2.2. Điểm Mạnh

1. ✅ Sử dụng sparse matrix hiệu quả
2. ✅ Có weighting dựa trên favorite games
3. ✅ Lọc users không liên quan
4. ✅ Xử lý được cả positive và negative ratings

### 2.3. Điểm Yếu và Vấn Đề

1. ❌ **K cố định**: Không adaptive theo dataset
2. ❌ **Weights initialization phức tạp**: `10 ** int(len(fav_games) ** 0.5)` khó hiểu và có thể không tối ưu
3. ❌ **Bug trong bad games handling**: `continue` trước khi chia weights
4. ❌ **Không có genre/tag filtering**: Recommendations có thể không liên quan về thể loại
5. ❌ **Không có popularity bias handling**: Games phổ biến có thể chiếm ưu thế
6. ❌ **Threshold có thể không tối ưu**: Công thức `sqrt(num_games)` có thể không phù hợp
7. ❌ **Không có diversity**: Recommendations có thể quá giống nhau

## 3. Đề Xuất Tinh Chỉnh

### 3.1. Cải Thiện Tính Toán Weights

#### Vấn đề Hiện Tại:
```python
weights = np.ones(len(users)) / (10 ** int(len(fav_games) ** 0.5))
```

#### Đề Xuất 1: Weights Đơn Giản và Rõ Ràng Hơn
```python
# Khởi tạo weights cơ bản
weights = np.ones(len(users))

# Tăng trọng số cho users có favorite games giống nhau
fav_weight_multiplier = 2.0  # Có thể điều chỉnh
bad_weight_multiplier = 0.5  # Giảm trọng số cho users có bad games giống nhau

for user_index, user_id in enumerate(user_id_list):
    row = user_vector_sparse[user_index]
    fav_matches = 0
    bad_matches = 0
    
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
```

**Lợi ích**:
- Dễ hiểu và điều chỉnh
- Xử lý được nhiều favorite/bad games trùng
- Tránh được bug `continue` trước khi chia

### 3.2. Adaptive K Selection

#### Vấn đề Hiện Tại:
```python
k = min(30, len(user_id_list))  # Cố định
```

#### Đề Xuất 2: K Adaptive Dựa Trên Data Quality
```python
def calculate_optimal_k(distance_list, min_k=5, max_k=50):
    """
    Tìm K tối ưu dựa trên:
    - Khoảng cách đến neighbors
    - Số lượng users có sẵn
    - Elbow method: Tìm điểm mà distance tăng đột ngột
    """
    if len(distance_list) < min_k:
        return len(distance_list)
    
    # Tính gradient của distances
    distances = [d[1] for d in distance_list[:max_k]]
    gradients = [distances[i+1] - distances[i] for i in range(len(distances)-1)]
    
    # Tìm elbow point: điểm mà gradient tăng đột ngột
    if len(gradients) > 0:
        avg_gradient = np.mean(gradients[:min_k])
        for i in range(min_k, len(gradients)):
            if gradients[i] > 2 * avg_gradient:  # Tăng đột ngột
                return i + 1
    
    # Nếu không tìm thấy elbow, dùng heuristic
    optimal_k = min(max_k, max(min_k, int(np.sqrt(len(distance_list)))))
    return optimal_k
```

**Lợi ích**:
- Tự động điều chỉnh K theo chất lượng data
- Tránh overfitting (K quá lớn) hoặc underfitting (K quá nhỏ)

### 3.3. Cải Thiện Threshold Selection

#### Vấn đề Hiện Tại:
```python
threshold = max(min(10, num_games), int(math.sqrt(num_games)))
```

#### Đề Xuất 3: Threshold Dựa Trên Percentile
```python
def calculate_optimal_threshold(my_games_id, reviews, percentile=25):
    """
    Tính threshold dựa trên phân phối số lượng reviews của users
    """
    user_review_counts = reviews[reviews['app_id'].isin(set(my_games_id))].groupby('user_id')['app_id'].size()
    
    # Lấy percentile thứ 25 (loại bỏ users có quá ít reviews)
    threshold = int(np.percentile(user_review_counts, percentile))
    
    # Đảm bảo threshold tối thiểu
    min_threshold = max(3, int(0.1 * len(my_games_id)))
    threshold = max(threshold, min_threshold)
    
    return threshold
```

**Lợi ích**:
- Tự động adapt theo phân phối data
- Loại bỏ users có quá ít reviews nhưng vẫn giữ đủ users để so sánh

### 3.4. Thêm Genre/Tag Filtering

#### Đề Xuất 4: Lọc Recommendations Theo Genre
```python
def filter_by_genre_similarity(recommendations, user_games, games_metadata, min_genre_overlap=0.3):
    """
    Lọc recommendations dựa trên genre similarity với games user đã chơi
    """
    # Lấy genres của games user đã like/favorite
    user_genres = set()
    for game_id in user_games[user_games['review'] >= 0.5]['gameID']:
        if game_id in games_metadata:
            user_genres.update(games_metadata[game_id].get('genres', []))
    
    # Tính genre overlap cho mỗi recommendation
    filtered_recommendations = []
    for game_id, relevance in recommendations:
        if game_id in games_metadata:
            game_genres = set(games_metadata[game_id].get('genres', []))
            overlap = len(user_genres & game_genres) / max(len(user_genres | game_genres), 1)
            
            if overlap >= min_genre_overlap:
                # Tăng relevance dựa trên genre overlap
                adjusted_relevance = relevance * (1 + overlap)
                filtered_recommendations.append((game_id, adjusted_relevance))
    
    return sorted(filtered_recommendations, key=lambda x: -x[1])
```

**Lợi ích**:
- Giảm recommendations không liên quan về thể loại
- Tăng relevance cho games có genre tương tự

### 3.5. Xử Lý Popularity Bias

#### Đề Xuất 5: Normalize Theo Popularity
```python
def apply_popularity_penalty(recommendations, games_metadata, penalty_factor=0.1):
    """
    Giảm relevance của games quá phổ biến để tăng diversity
    """
    # Tính popularity score (dựa trên user_reviews)
    max_reviews = max([games_metadata[gid].get('user_reviews', 0) for gid, _ in recommendations])
    
    adjusted_recommendations = []
    for game_id, relevance in recommendations:
        if game_id in games_metadata:
            reviews = games_metadata[game_id].get('user_reviews', 0)
            popularity_score = reviews / max_reviews if max_reviews > 0 else 0
            
            # Áp dụng penalty: games quá phổ biến bị giảm relevance
            # Nhưng vẫn giữ một phần để không loại bỏ hoàn toàn
            penalty = 1 - (penalty_factor * popularity_score)
            adjusted_relevance = relevance * max(penalty, 0.5)  # Tối thiểu 50%
            
            adjusted_recommendations.append((game_id, adjusted_relevance))
    
    return sorted(adjusted_recommendations, key=lambda x: -x[1])
```

**Lợi ích**:
- Tăng diversity trong recommendations
- Không loại bỏ hoàn toàn popular games (vì chúng có thể vẫn phù hợp)

### 3.6. Cải Thiện Distance Calculation

#### Đề Xuất 6: Sử Dụng Jaccard Similarity Cho Binary Ratings
```python
def jaccard_similarity(user1_vector, user2_vector):
    """
    Jaccard similarity phù hợp hơn cho binary/categorical ratings
    J(A, B) = |A ∩ B| / |A ∪ B|
    """
    # Chỉ xét games mà cả 2 users đều có review
    common_games = set(user1_vector.indices) & set(user2_vector.indices)
    
    if len(common_games) == 0:
        return 0.0
    
    # Đếm số games có cùng rating (like/like hoặc dislike/dislike)
    agreements = 0
    for game_idx in common_games:
        rating1 = user1_vector[0, game_idx] if game_idx in user1_vector.indices else 0
        rating2 = user2_vector[0, game_idx] if game_idx in user2_vector.indices else 0
        
        # Xét cùng dấu (cùng like hoặc cùng dislike)
        if (rating1 > 0 and rating2 > 0) or (rating1 < 0 and rating2 < 0):
            agreements += 1
    
    all_games = set(user1_vector.indices) | set(user2_vector.indices)
    return agreements / len(all_games) if len(all_games) > 0 else 0.0
```

**Lợi ích**:
- Phù hợp hơn với dữ liệu binary/categorical
- Tập trung vào agreements thay vì magnitude

### 3.7. Hybrid Approach: Kết Hợp Content-Based

#### Đề Xuất 7: Kết Hợp Collaborative và Content-Based
```python
def hybrid_recommendation(collaborative_scores, content_scores, alpha=0.7):
    """
    Kết hợp collaborative filtering và content-based filtering
    alpha: Trọng số cho collaborative (1-alpha cho content-based)
    """
    hybrid_scores = {}
    
    all_game_ids = set(collaborative_scores.keys()) | set(content_scores.keys())
    
    for game_id in all_game_ids:
        collab_score = collaborative_scores.get(game_id, 0)
        content_score = content_scores.get(game_id, 0)
        
        hybrid_scores[game_id] = alpha * collab_score + (1 - alpha) * content_score
    
    return hybrid_scores
```

**Lợi ích**:
- Giảm cold-start problem
- Tăng độ chính xác bằng cách kết hợp 2 phương pháp

## 4. Implementation Code Cải Tiến

### 4.1. Hàm getKnnVector Cải Tiến

```python
def getKnnVector_improved(my_vector, k=None, use_adaptive_k=True, min_k=5, max_k=50):
    """
    Version cải tiến với adaptive K và improved weighting
    """
    distance_list = getDistanceList(my_vector)
    
    # Adaptive K selection
    if use_adaptive_k and k is None:
        k = calculate_optimal_k(distance_list, min_k, max_k)
    elif k is None:
        k = min(30, len(distance_list))
    
    actual_k = min(k, len(distance_list))
    
    if actual_k == 0:
        return csr_matrix((1, my_vector.shape[1]))
    
    indices = np.array([distance_list[i][0] for i in range(actual_k)])
    distances = np.array([distance_list[i][1] for i in range(actual_k)])
    
    user_vectors = user_vector_sparse[indices]
    user_weights = weights[indices]
    
    # Improved weighting: Sử dụng inverse distance với smoothing
    # Thêm small epsilon để tránh division by zero và giảm ảnh hưởng của outliers
    epsilon = 1e-6
    safe_distances = distances + epsilon
    
    # Inverse distance weighting với exponential decay
    # Games từ users gần hơn có trọng số cao hơn
    distance_weights = 1.0 / (safe_distances ** 1.5)  # Exponent > 1 để tăng độ nhạy
    
    # Combine user weights và distance weights
    combined_weights = user_weights * distance_weights
    
    # Normalize weights
    combined_weights = combined_weights / (np.sum(combined_weights) + epsilon)
    
    # Multiply và sum
    weighted_vectors = user_vectors.multiply(combined_weights[:, None])
    vector = weighted_vectors.sum(axis=0).A1
    
    return vector
```

### 4.2. Hàm getRecommendedGameId Cải Tiến

```python
def getRecommendedGameId_improved(
    k=None, 
    test=False, 
    use_adaptive_k=True,
    apply_genre_filter=False,
    apply_popularity_penalty=False,
    games_metadata=None,
    user_games=None
):
    """
    Version cải tiến với nhiều tùy chọn filtering
    """
    print("k =", k if k else "adaptive")
    train_vector = my_vector.copy()
    
    if test:
        train_vector, test_vector = split_vector(train_vector)
    else:
        test_vector = train_vector
    
    # Get KNN vector với adaptive K
    vector = getKnnVector_improved(train_vector, k, use_adaptive_k)
    
    # Extract recommendations
    rcm_game_id = []
    for i in range(len(vector)):
        if vector[i] > 0:
            rcm_game_id.append((games_id_reviews[i], vector[i]))
    
    # Apply genre filtering nếu có metadata
    if apply_genre_filter and games_metadata is not None and user_games is not None:
        rcm_game_id = filter_by_genre_similarity(rcm_game_id, user_games, games_metadata)
    
    # Apply popularity penalty
    if apply_popularity_penalty and games_metadata is not None:
        rcm_game_id = apply_popularity_penalty(rcm_game_id, games_metadata)
    
    # Sort by relevance
    rcm_game_id = sorted(rcm_game_id, key=lambda x: -x[1])
    
    # Calculate metrics nếu test mode
    if test:
        measure = getMesure(rcm_game_id, test_vector)
        return rcm_game_id, measure
    
    return rcm_game_id, None
```

## 5. Kế Hoạch Tối Ưu Hóa

### 5.1. Thứ Tự Ưu Tiên

1. **Cao Ưu Tiên** (Cải thiện ngay):
   - ✅ Sửa bug trong weights calculation (bad games handling)
   - ✅ Cải thiện weights initialization (đơn giản hóa)
   - ✅ Thêm adaptive K selection

2. **Trung Bình** (Cải thiện chất lượng):
   - ✅ Thêm genre/tag filtering
   - ✅ Cải thiện threshold selection
   - ✅ Apply popularity penalty

3. **Thấp** (Tùy chọn, nâng cao):
   - ✅ Hybrid approach (content-based)
   - ✅ Jaccard similarity thay vì cosine
   - ✅ Diversity boosting

### 5.2. Hyperparameter Tuning

Các tham số cần điều chỉnh:

```python
HYPERPARAMETERS = {
    'fav_weight_multiplier': [1.5, 2.0, 2.5, 3.0],  # Trọng số cho favorite games
    'bad_weight_multiplier': [0.3, 0.5, 0.7],       # Penalty cho bad games
    'min_k': [3, 5, 10],                             # K tối thiểu
    'max_k': [30, 50, 100],                          # K tối đa
    'threshold_percentile': [20, 25, 30],            # Percentile cho threshold
    'genre_overlap_min': [0.2, 0.3, 0.4],           # Genre overlap tối thiểu
    'popularity_penalty': [0.05, 0.1, 0.15],        # Penalty cho popular games
}
```

**Phương pháp tuning**:
- Grid search hoặc random search
- Cross-validation với test set
- Đo lường bằng precision@k, recall@k, diversity metrics

## 6. Metrics Đánh Giá

### 6.1. Metrics Hiện Tại
- Accuracy, Precision, Recall (trong hàm `getMesure`)

### 6.2. Metrics Bổ Sung Nên Dùng

```python
def calculate_diversity(recommendations, games_metadata, top_k=10):
    """
    Tính diversity: Độ đa dạng của recommendations
    """
    top_games = recommendations[:top_k]
    genres = []
    for game_id, _ in top_games:
        if game_id in games_metadata:
            genres.extend(games_metadata[game_id].get('genres', []))
    
    unique_genres = len(set(genres))
    total_genres = len(genres)
    
    diversity = unique_genres / total_genres if total_genres > 0 else 0
    return diversity

def calculate_coverage(recommendations, all_games, top_k=10):
    """
    Tính coverage: Tỷ lệ games được recommend
    """
    recommended_ids = {game_id for game_id, _ in recommendations[:top_k]}
    coverage = len(recommended_ids) / len(all_games) if len(all_games) > 0 else 0
    return coverage
```

## 7. Kết Luận

Hệ thống KNN recommendation hiện tại đã có nền tảng tốt nhưng còn nhiều điểm cần cải thiện:

1. **Sửa bugs**: Bad games handling, weights initialization
2. **Tối ưu hyperparameters**: K, threshold, weights
3. **Thêm filtering**: Genre, popularity bias
4. **Cải thiện metrics**: Diversity, coverage

Với các cải tiến này, chất lượng recommendations sẽ được cải thiện đáng kể, đặc biệt là giảm số lượng recommendations không liên quan.

