# Lý Thuyết Content-Based Filtering

## 1. Tổng Quan

Hệ thống **Content-Based Filtering** sử dụng **Genres và Tags** để tìm games tương tự với games bạn đã đánh giá. Đây là phương pháp phù hợp nhất cho bài toán recommend game dựa trên content (genres/tags).

## 2. Nguyên Lý Hoạt Động

Content-Based Filtering dựa trên giả định: "Nếu user thích một item, họ sẽ thích các items tương tự về mặt nội dung."

### Quy Trình:

1. **Feature Extraction**: Trích xuất features từ game content (Genres, Tags)
2. **Vectorization**: Chuyển đổi features thành vectors sử dụng TF-IDF
3. **User Profile**: Tạo user profile từ ratings của user
4. **Similarity Calculation**: Tính độ tương đồng giữa user profile và game features
5. **Recommendation**: Recommend games có similarity cao nhất

## 3. Công Thức Toán Học

### TF-IDF (Term Frequency-Inverse Document Frequency):
```
TF(t, d) = số lần term t xuất hiện trong document d
IDF(t, D) = log(N / số documents chứa term t)
TF-IDF(t, d) = TF(t, d) × IDF(t, D)
```

### User Profile:
```
user_profile = Σ(rating_i × game_features_i) / Σ(rating_i)
```

### Cosine Similarity:
```
similarity(user_profile, game_features) = (user_profile · game_features) / (||user_profile|| × ||game_features||)
```

## 4. Kiến Trúc Hệ Thống

### Bước 1: Data Preprocessing
- Load games data từ `CB_games.csv`
- Extract Genres và Tags
- Combine Genres và Tags thành text features

### Bước 2: Feature Vectorization
- Sử dụng **TF-IDF Vectorizer** để vectorize features
- Max features: 5000 (có thể điều chỉnh)
- Tạo feature matrix cho tất cả games

### Bước 3: User Profile Creation
- Load user ratings từ `cb_user_ratings.json`
- Chỉ sử dụng ratings >= 3 (Like/Good)
- Tính weighted average của game features dựa trên ratings

### Bước 4: Similarity Calculation
- Tính cosine similarity giữa user profile và tất cả game features
- Loại trừ games đã được rate
- Áp dụng filters (max price, min positive ratio)

### Bước 5: Ranking và Recommendation
- Sort games theo similarity score
- Lấy top N recommendations
- Lưu vào `cb_recommendations.csv`

## 5. Điểm Mạnh

1. ✅ **Không cần nhiều data**: Hoạt động tốt với ít ratings
2. ✅ **Không có cold-start problem**: Có thể recommend ngay khi có ít ratings
3. ✅ **Transparent**: Dễ giải thích tại sao recommend game này
4. ✅ **Dựa trên content**: Recommendations phù hợp với sở thích về thể loại

## 6. Điểm Yếu

1. ❌ **Limited diversity**: Có thể recommend games quá giống nhau
2. ❌ **Không học được serendipity**: Khó recommend games bất ngờ
3. ❌ **Phụ thuộc vào features**: Cần features chất lượng (genres/tags)

## 7. Rating System

Content-Based sử dụng rating 1-5:
- **5 (Like)**: Game rất thích
- **4 (Good)**: Game tốt
- **3 (Neutral)**: Game bình thường
- **2 (Bad)**: Game không tốt
- **1 (Dislike)**: Game không thích

**Lưu Ý:** Chỉ games có rating >= 3 sẽ được dùng để tìm recommendations.

## 8. Features

### Content-Based Model
- Sử dụng **TF-IDF Vectorizer** để vectorize Genres và Tags
- Sử dụng **Cosine Similarity** để tìm games tương tự
- Tự động loại trừ games đã rate
- Áp dụng user preferences (max price, min positive ratio)

### UI Features
- **Search Games**: Tìm kiếm games trong danh sách
- **Rate Games**: Đánh giá games với 5 mức độ
- **View Ratings**: Xem tất cả ratings đã đánh giá
- **Preferences**: Thiết lập preferences (max price, min positive ratio)
- **Recommendations**: Xem recommendations từ model

## 9. Files Liên Quan

- `CB_model/UI_ContentBased.py`: Main UI
- `CB_model/ContentBased_model.py`: Core model logic
- `CB_model/ContentBased_commands.py`: Command handlers
- `CB_model/ContentBased_data_handler.py`: Data loading/saving
- `CB_model/ContentBased_UI_elements.py`: UI components

## 10. Data Files

- `CB_games.csv`: Game data với Genres và Tags (111,452 games)
- `cb_user_ratings.json`: User ratings (tự động tạo)
- `cb_model.pkl`: Trained model (tự động tạo)
- `cb_recommendations.csv`: Recommendations output (tự động tạo)

## 11. Dependencies

```python
pandas
numpy
scikit-learn
tkinter (built-in với Python)
```

## 12. So Sánh với KNN

| Feature | KNN (Collaborative) | Content-Based |
|---------|-------------------|---------------|
| **Dựa trên** | User behavior | Game content (genres/tags) |
| **Cần nhiều ratings** | ✅ Cần | ❌ Không cần |
| **Tốt với ít data** | ❌ Không | ✅ Tốt |
| **Diversity** | ✅ Cao | ⚠️ Trung bình |
| **Phù hợp cho** | User-based recommendation | Content-based recommendation |

