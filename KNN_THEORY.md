# Lý Thuyết KNN-Based Collaborative Filtering

## 1. Tổng Quan

**Collaborative Filtering (CF)** là một kỹ thuật recommendation dựa trên giả định: "Những người có sở thích tương tự trong quá khứ sẽ có sở thích tương tự trong tương lai."

**K-Nearest Neighbors (KNN)** là một thuật toán CF tìm K người dùng (neighbors) có sở thích gần nhất với người dùng hiện tại, sau đó dự đoán ratings dựa trên ratings của những neighbors này.

## 2. Các Bước Cơ Bản

1. **Xây dựng User-Item Matrix**: Tạo ma trận sparse với:
   - Hàng: Users
   - Cột: Items (games)
   - Giá trị: Ratings/Reviews (1: Like, 0.5: Interested, -0.5: Neutral, -1: Dislike)

2. **Tính Similarity**: Đo độ tương đồng giữa user hiện tại và các users khác
   - **Cosine Similarity**: Đo góc giữa 2 vectors
   - **Cosine Distance** = 1 - Cosine Similarity

3. **Tìm K Nearest Neighbors**: Chọn K users có distance nhỏ nhất

4. **Dự đoán Ratings**: Tính weighted average của ratings từ K neighbors

## 3. Công Thức Toán Học

### Cosine Similarity:
```
similarity(u, v) = (u · v) / (||u|| × ||v||)
```

### Cosine Distance:
```
distance(u, v) = 1 - similarity(u, v)
```

### Weighted Prediction:
```
prediction(i) = Σ(weight_k × rating_k,i) / Σ(weight_k)
```

Trong đó:
- `weight_k = user_weight_k / distance_k`
- `user_weight_k`: Trọng số của user k (dựa trên favorite games)
- `distance_k`: Khoảng cách cosine giữa user hiện tại và user k

## 4. Kiến Trúc Hệ Thống

### Bước 1: Lọc Users Liên Quan
```python
threshold = max(min(10, num_games), int(math.sqrt(num_games)))
relevant_users = users đã review >= threshold games trong my_games_id
```
- **Mục đích**: Chỉ xét users có đủ dữ liệu để so sánh

### Bước 2: Tạo User-Item Matrix (Sparse)
- Sử dụng `scipy.sparse.csr_matrix` để tiết kiệm memory
- Giá trị: 1 (Like), -1 (Dislike), 0.5 (Interested), -0.5 (Neutral)

### Bước 3: Tính Trọng Số Users
- Tăng trọng số cho users có favorite games giống nhau
- Giảm trọng số cho users có bad games giống nhau

### Bước 4: Tìm KNN và Dự Đoán
```python
distances = cosine_distances(user_vector_sparse, my_vector)
k_nearest = K users có distance nhỏ nhất
weighted_vector = Σ(weights[k] / distances[k] × user_vectors[k])
```

## 5. Điểm Mạnh

1. ✅ Sử dụng sparse matrix hiệu quả
2. ✅ Có weighting dựa trên favorite games
3. ✅ Lọc users không liên quan
4. ✅ Xử lý được cả positive và negative ratings

## 6. Điểm Yếu và Cải Thiện

1. **K cố định**: Có thể không tối ưu cho mọi trường hợp
2. **Weights initialization**: Cần đơn giản hóa và tối ưu
3. **Không có genre/tag filtering**: Recommendations có thể không liên quan về thể loại
4. **Không có popularity bias handling**: Games phổ biến có thể chiếm ưu thế
5. **Không có diversity**: Recommendations có thể quá giống nhau

## 7. Rating System

KNN sử dụng rating scale:
- **1.0 (Like)**: Game rất thích
- **0.5 (Interested)**: Game quan tâm
- **-0.5 (Neutral)**: Game bình thường
- **-1.0 (Dislike)**: Game không thích

**Lưu ý:** Ratings được chuyển đổi từ scale 1-5 trong Hybrid UI:
- 5 (Like) → 1.0
- 4 (Good) → 0.5
- 3 (Neutral) → 0.0 (ignored)
- 2 (Bad) → -0.5
- 1 (Dislike) → -1.0

## 8. Files Liên Quan

- `KNN_model/UI.py`: Main UI
- `KNN_model/Button_commands.py`: Command handlers
- `KNN_model/Data_handler.py`: Data loading/saving
- `KNN_model/UI_elements.py`: UI components

## 9. Data Files

- `final_games.csv`: Game metadata
- `final_reviews.csv`: User reviews (user_id, app_id, is_recommended)
- `your_games.csv`: User ratings
- `fav_games.csv`: Favorite games
- `rcm_games.csv`: Recommendations output

