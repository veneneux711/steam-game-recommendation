# Lý Thuyết Hybrid Recommendation System

## 1. Tổng Quan

Hệ thống **Hybrid Recommendation** kết hợp **KNN (Collaborative Filtering)** và **Content-Based Filtering** để tạo recommendations tốt nhất, vừa dựa trên trải nghiệm users (KNN) vừa dựa trên similarity về content (Genres/Tags).

**Lưu ý:** Hybrid system chỉ **đọc recommendations** từ 2 models đã chạy, không tự động chạy models.

## 2. Nguyên Lý Hoạt Động

### Quy Trình:

1. **Đọc Recommendations**: Đọc top 30 recommendations từ cả KNN và Content-Based models
2. **Scoring**: Gán điểm cho mỗi game dựa trên rank (rank #1 = 30 điểm, rank #30 = 1 điểm)
3. **Weighting**: Áp dụng weights cho mỗi model (default: 0.5 cho mỗi)
4. **Hybrid Scoring**: Tính hybrid score với improved ranking logic
5. **Ranking**: Sort và lấy top N recommendations

## 3. Scoring System

### KNN Scoring
- Top 30 games từ KNN
- Điểm: 30, 29, 28, ..., 3, 2, 1
- Weighted: `knn_score * knn_weight` (default weight = 0.5)

### Content-Based Scoring
- Top 30 games từ Content-Based
- Điểm: 30, 29, 28, ..., 3, 2, 1
- Weighted: `cb_score * cb_weight` (default weight = 0.5)

## 4. Hybrid Ranking Logic

### Mục Tiêu
- **knn cao + cb cao** > **knn cao + cb thấp** > **knn thấp + cb cao** > **knn thấp + cb thấp**
- **Nhưng**: Game có cả 2 scores (dù thấp) > Game chỉ có 1 score cao

### Công Thức

#### Nếu có cả 2 scores (KNN > 0 và CB > 0):
```
base_score = knn_score + cb_score
multiplicative_bonus = sqrt(knn_score * cb_score) * 0.5
balance_bonus = min(knn_score, cb_score) * 0.2
min_boost = 2.0
hybrid_score = base_score + multiplicative_bonus + balance_bonus + min_boost
```

#### Nếu chỉ có 1 score (KNN=0 hoặc CB=0):
```
hybrid_score = base_score * 0.4  (Penalty 60%)
```

### Ví Dụ

#### Case 1: Cả 2 scores cao
- KNN=15, CB=15
- hybrid_score = 30 + sqrt(225)*0.5 + 15*0.2 + 2 = 30 + 7.5 + 3 + 2 = **42.5** ✅

#### Case 2: 1 cao, 1 thấp
- KNN=15, CB=2.5
- hybrid_score = 17.5 + sqrt(37.5)*0.5 + 2.5*0.2 + 2 = 17.5 + 3.06 + 0.5 + 2 = **23.06** ✅

#### Case 3: Cả 2 scores thấp
- KNN=0.5, CB=0.5
- hybrid_score = 1 + sqrt(0.25)*0.5 + 0.5*0.2 + 2 = 1 + 0.25 + 0.1 + 2 = **3.35** ✅

#### Case 4: Chỉ có KNN (CB=0)
- KNN=15, CB=0
- hybrid_score = 15 * 0.4 = **6** ✅

#### Case 5: Chỉ có CB (KNN=0)
- KNN=0, CB=5
- hybrid_score = 5 * 0.4 = **2** ✅

## 5. Điểm Mạnh

1. ✅ **Cân bằng**: Kết hợp cả user behavior và content similarity
2. ✅ **Đa dạng**: Games được recommend từ 2 góc độ khác nhau
3. ✅ **Chính xác**: Games xuất hiện trong cả 2 lists có độ tin cậy cao
4. ✅ **Linh hoạt**: Có thể điều chỉnh weights (KNN vs CB)
5. ✅ **Improved ranking**: Games có cả 2 scores được ưu tiên

## 6. Cách Sử Dụng

### Bước 1: Chạy KNN Model
```bash
cd KNN_model
python UI.py
```
1. Rate games (nếu chưa có)
2. Click "Get Recommendations"
3. Đảm bảo file `rcm_games.csv` hoặc `recommendations.csv` được tạo

### Bước 2: Chạy Content-Based Model
```bash
cd CB_model
python UI_ContentBased.py
```
1. Rate games (nếu chưa có)
2. Train model (nếu chưa train)
3. Click "Get Recommendations"
4. Đảm bảo file `cb_recommendations.csv` được tạo

### Bước 3: Chạy Hybrid Ranking
```bash
cd Hybrid_model
run_Hybrid.bat
```
hoặc
```bash
cd Hybrid_model
python run_hybrid.py
```

### Kết Quả
- Hybrid rankings được lưu vào `hybrid_ranking.csv`
- UI window tự động mở hiển thị kết quả trong bảng
- Top 3 games: highlight xanh lá
- Top 10 games: highlight xanh dương
- Games có cả 2 scores: chữ xanh

## 7. Files Liên Quan

- `Hybrid_model/run_hybrid.py`: Main script
- `Hybrid_model/Hybrid_recommendations_reader.py`: Core logic
- `Hybrid_model/Hybrid_results_viewer.py`: UI viewer
- `Hybrid_model/run_Hybrid.bat`: Batch file

## 8. Data Files

- `KNN_model/rcm_games.csv` hoặc `recommendations.csv`: KNN recommendations
- `CB_model/cb_recommendations.csv`: Content-Based recommendations
- `Hybrid_model/hybrid_ranking.csv`: Hybrid rankings output

## 9. Lưu Ý

1. **Phải chạy models trước**: Hybrid system chỉ đọc recommendations, không tự chạy models
2. **File requirements**: Cần cả 2 recommendations files
3. **AppID mapping**: Cần đảm bảo AppID giữa 2 systems tương thích
4. **Weights**: Có thể điều chỉnh `knn_weight` và `cb_weight` trong `run_hybrid.py`

## 10. Troubleshooting

### Lỗi: "KNN recommendations not found"
- Chạy KNN model trước và get recommendations

### Lỗi: "Content-Based recommendations not found"
- Chạy Content-Based model trước và get recommendations

### Lỗi: "No hybrid rankings calculated"
- Kiểm tra cả 2 recommendations files có data không

### Recommendations không đa dạng
- Rate games đa dạng trong cả 2 systems
- Rate cả games thích và không thích để KNN hoạt động tốt hơn

Xem `HYBRID_RANKING_LOGIC.md` để biết chi tiết về ranking logic.

