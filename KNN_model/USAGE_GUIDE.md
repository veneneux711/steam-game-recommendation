# Hướng Dẫn Sử Dụng Các Cải Tiến KNN

## 1. Cách Import và Sử Dụng

### Bước 1: Import module
```python
import knn_improvements as knn_imp
```

### Bước 2: Áp dụng các cải tiến trong notebook

## 2. Các Cải Tiến Có Thể Áp Dụng Ngay

### 2.1. Cải Thiện Threshold Selection

**Thay thế cell 11 trong knn_model.ipynb:**

```python
# OLD CODE:
threshold = max(min(10, num_games), int(math.sqrt(num_games)))

# NEW CODE:
threshold = knn_imp.calculate_optimal_threshold(my_games_id, reviews, percentile=25)
print("Optimal threshold:", threshold)
```

### 2.2. Cải Thiện Weights Calculation

**Thay thế cell 16 trong knn_model.ipynb:**

```python
# OLD CODE:
weights = np.ones(len(user_id_list)) / (10 ** int(len(fav_games) ** 0.5))
for user_index, user_id in enumerate(user_id_list):
    row = user_vector_sparse[user_index]
    for game_index, game_review in zip(row.indices, row.data):
        if game_review == 1:
            if games_id_reviews[game_index] in fav_games_set:
                weights[user_index] *= 4
            elif games_id_reviews[game_index] in bad_games_id:
                continue  # BUG: continue trước khi chia
                weights[user_index] /= 2

# NEW CODE:
weights = knn_imp.calculate_weights_improved(
    user_vector_sparse, 
    games_id_reviews, 
    fav_games_set, 
    bad_games_id,
    fav_weight_multiplier=2.0,  # Có thể điều chỉnh
    bad_weight_multiplier=0.5   # Có thể điều chỉnh
)
print(weights)
```

### 2.3. Cải Thiện getKnnVector với Adaptive K

**Thay thế hàm getKnnVector trong cell 19:**

```python
# OLD CODE:
def getKnnVector(my_vector, k=len(user_id_list)):
    distance_list = getDistanceList(my_vector)
    actual_k = min(k, len(distance_list))
    # ... rest of code

# NEW CODE:
def getKnnVector(my_vector, k=None, use_adaptive_k=True):
    from sklearn.metrics.pairwise import cosine_distances
    distances = cosine_distances(user_vector_sparse, my_vector).flatten()
    distance_list = [(i, distances[i], user_vector_sparse[i]) 
                     for i in range(user_vector_sparse.shape[0])]
    distance_list = sorted(distance_list, key=lambda x: x[1])
    
    # Sử dụng hàm cải tiến
    vector = knn_imp.getKnnVector_improved(
        my_vector,
        user_vector_sparse,
        weights,
        distance_list,
        k=k,
        use_adaptive_k=use_adaptive_k,
        min_k=5,
        max_k=50,
        distance_exponent=1.5
    )
    return vector
```

### 2.4. Thêm Genre Filtering

**Sau khi có recommendations, thêm cell mới:**

```python
# Load games metadata nếu có genre information
games_details = pd.read_csv("final_games.csv")

# Áp dụng genre filtering
rcm_filtered = knn_imp.filter_by_genre_similarity(
    rcm,  # recommendations từ getRecommendedGameId
    your_games,  # DataFrame chứa games user đã chơi
    games_details,  # Metadata với genres
    min_genre_overlap=0.3  # Có thể điều chỉnh (0.2-0.4)
)

print("Recommendations sau genre filtering:", len(rcm_filtered))
```

### 2.5. Áp Dụng Popularity Penalty

**Sau genre filtering hoặc thay thế:**

```python
# Áp dụng popularity penalty
rcm_final = knn_imp.apply_popularity_penalty(
    rcm_filtered,  # hoặc rcm nếu không dùng genre filter
    games_details,  # Metadata với user_reviews
    penalty_factor=0.1  # Có thể điều chỉnh (0.05-0.15)
)

print("Recommendations sau popularity penalty:", len(rcm_final))
```

### 2.6. Tính Metrics Bổ Sung

**Thêm cell để đánh giá:**

```python
# Tính diversity
diversity = knn_imp.calculate_diversity(
    rcm_final,
    games_details,
    top_k=10
)

# Tính coverage
coverage = knn_imp.calculate_coverage(
    rcm_final,
    games_id_reviews,  # hoặc list tất cả game IDs
    top_k=10
)

print(f"Diversity (top 10): {diversity:.3f}")
print(f"Coverage (top 10): {coverage:.3f}")
```

## 3. Ví Dụ Hoàn Chỉnh - getRecommendedGameId Cải Tiến

**Thay thế cell 22:**

```python
def getRecommendedGameId_improved(
    k=None, 
    test=False, 
    use_adaptive_k=True,
    apply_genre_filter=False,
    apply_popularity_penalty=False,
    min_genre_overlap=0.3,
    popularity_penalty_factor=0.1
):
    print("k =", k if k else "adaptive")
    train_vector = my_vector.copy()
    
    if test:
        train_vector, test_vector = split_vector(train_vector)
    else:
        test_vector = train_vector
    
    # Get distance list
    from sklearn.metrics.pairwise import cosine_distances
    distances = cosine_distances(user_vector_sparse, train_vector).flatten()
    distance_list = [(i, distances[i], user_vector_sparse[i]) 
                     for i in range(user_vector_sparse.shape[0])]
    distance_list = sorted(distance_list, key=lambda x: x[1])
    
    # Get KNN vector với adaptive K
    vector = knn_imp.getKnnVector_improved(
        train_vector,
        user_vector_sparse,
        weights,
        distance_list,
        k=k,
        use_adaptive_k=use_adaptive_k
    )
    
    # Extract recommendations
    rcm_game_id = []
    for i in range(len(vector)):
        if vector[i] > 0:
            rcm_game_id.append((games_id_reviews[i], vector[i]))
    
    # Apply genre filtering
    if apply_genre_filter:
        games_details = pd.read_csv("final_games.csv")
        rcm_game_id = knn_imp.filter_by_genre_similarity(
            rcm_game_id, 
            your_games, 
            games_details, 
            min_genre_overlap
        )
    
    # Apply popularity penalty
    if apply_popularity_penalty:
        if 'games_details' not in locals():
            games_details = pd.read_csv("final_games.csv")
        rcm_game_id = knn_imp.apply_popularity_penalty(
            rcm_game_id, 
            games_details, 
            popularity_penalty_factor
        )
    
    # Sort by relevance
    rcm_game_id = sorted(rcm_game_id, key=lambda x: -x[1])
    
    # Calculate metrics nếu test mode
    if test:
        measure = getMesure(rcm_game_id, test_vector)
        return rcm_game_id, measure
    
    return rcm_game_id, None

# Sử dụng:
rcm, measure = getRecommendedGameId_improved(
    k=None,  # Dùng adaptive K
    test=False,
    use_adaptive_k=True,
    apply_genre_filter=True,  # Bật genre filtering
    apply_popularity_penalty=True,  # Bật popularity penalty
    min_genre_overlap=0.3,
    popularity_penalty_factor=0.1
)
```

## 4. Hyperparameter Tuning

### 4.1. Tìm Tham Số Tối Ưu

```python
# Test các giá trị khác nhau
best_params = {
    'fav_weight_multiplier': 2.0,
    'bad_weight_multiplier': 0.5,
    'min_genre_overlap': 0.3,
    'popularity_penalty': 0.1
}

# Test với các giá trị
for fav_mult in [1.5, 2.0, 2.5, 3.0]:
    weights = knn_imp.calculate_weights_improved(
        user_vector_sparse, 
        games_id_reviews, 
        fav_games_set, 
        bad_games_id,
        fav_weight_multiplier=fav_mult
    )
    
    # Chạy recommendation và đánh giá
    # ... (code để test và so sánh kết quả)
```

## 5. So Sánh Kết Quả

### 5.1. Trước và Sau Cải Tiến

```python
# Chạy với code cũ
rcm_old, _ = getRecommendedGameId(test=False)

# Chạy với code mới
rcm_new, _ = getRecommendedGameId_improved(
    use_adaptive_k=True,
    apply_genre_filter=True,
    apply_popularity_penalty=True
)

# So sánh
print("Old recommendations (top 10):")
for i, (game_id, rel) in enumerate(rcm_old[:10]):
    print(f"{i+1}. Game ID: {game_id}, Relevance: {rel:.3f}")

print("\nNew recommendations (top 10):")
for i, (game_id, rel) in enumerate(rcm_new[:10]):
    print(f"{i+1}. Game ID: {game_id}, Relevance: {rel:.3f}")

# Tính diversity
diversity_old = knn_imp.calculate_diversity(rcm_old, games_details)
diversity_new = knn_imp.calculate_diversity(rcm_new, games_details)

print(f"\nDiversity - Old: {diversity_old:.3f}, New: {diversity_new:.3f}")
```

## 6. Lưu Ý

1. **Thứ tự áp dụng**: Genre filter → Popularity penalty
2. **Hyperparameters**: Bắt đầu với giá trị mặc định, điều chỉnh dần
3. **Performance**: Các cải tiến có thể làm chậm một chút, nhưng chất lượng tốt hơn
4. **Dữ liệu**: Cần có genre information trong games_metadata để dùng genre filtering

## 7. Troubleshooting

### Lỗi: "games_metadata không có genres"
- Kiểm tra xem `final_games.csv` có cột `genres` không
- Nếu không có, tắt `apply_genre_filter=False`

### Lỗi: "K quá nhỏ/lớn"
- Điều chỉnh `min_k` và `max_k` trong `getKnnVector_improved`
- Hoặc set `use_adaptive_k=False` và dùng K cố định

### Recommendations quá ít
- Giảm `min_genre_overlap` (ví dụ: 0.2)
- Giảm `popularity_penalty_factor` (ví dụ: 0.05)
- Tăng `max_k` trong adaptive K

