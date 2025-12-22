# Hướng Dẫn Lấy Data Để Viết Báo Cáo

## 📋 Checklist Data Cần Thu Thập

### 1. **Dataset Statistics** ✅

#### Chạy script để lấy thống kê:
```python
# Tạo file get_dataset_stats.py (sẽ tạo sau)
python get_dataset_stats.py
```

**Output cần có:**
- Số lượng games (KNN và CB)
- Số lượng users
- Số lượng reviews
- Distribution của ratings
- Distribution của genres/tags
- Thống kê cơ bản (mean, median, std)

**File output**: `dataset_statistics.csv` hoặc `dataset_statistics.txt`

---

### 2. **Evaluation Results** ✅

#### Đã có sẵn:
```bash
python run_evaluation.py
```

**Output files:**
- `Hybrid_model/evaluation_results.csv` - Bảng metrics
- Console output với chi tiết

**Cần extract:**
- Bảng so sánh metrics @ K=10, K=20, K=30
- Best model cho từng metric
- Overlap statistics

---

### 3. **Visualization Charts** ✅

#### Đã có sẵn:
```bash
python visualization.py
```

**Output files:**
- `Hybrid_model/model_comparison.png`
- `Hybrid_model/precision_recall_comparison.png`
- `Hybrid_model/ndcg_map_comparison.png`
- `Hybrid_model/radar_chart.png`

**Cần extract:**
- Insert charts vào báo cáo
- Thêm captions và explanations

---

### 4. **Sample Recommendations** ⚠️

#### Chạy models và lấy sample:

**KNN:**
```bash
cd KNN_model
python UI.py
# → Get Recommendations
# → Copy top 10 recommendations từ rcm_games.csv
```

**Content-Based:**
```bash
cd CB_model
python UI_ContentBased.py
# → Get Recommendations
# → Copy top 10 recommendations từ cb_recommendations.csv
```

**Hybrid:**
```bash
python run_hybrid.py
# → Copy top 10 recommendations từ hybrid_ranking.csv
```

**Cần extract:**
- Top 10 recommendations từ mỗi model
- So sánh recommendations giữa 3 models
- Phân tích tại sao recommend games này

---

### 5. **Test User Data** ✅

#### Tạo test user "ma":
```bash
python create_test_user.py [num_ratings]
# Ví dụ: python create_test_user.py 50
```

**Output:**
- `KNN_model/your_games.csv` - Test user ratings
- `CB_model/cb_user_ratings.json` - Test user ratings
- Backup files được tạo tự động

**Cần extract:**
- Số lượng ratings
- Distribution của ratings
- Sample ratings

---

### 6. **Performance Metrics** ⚠️

#### Chạy evaluation với test user:
```bash
# 1. Tạo test user
python create_test_user.py 50

# 2. Chạy KNN và get recommendations
cd KNN_model && python UI.py

# 3. Chạy CB và get recommendations
cd CB_model && python UI_ContentBased.py

# 4. Chạy Hybrid
cd .. && python run_hybrid.py

# 5. Chạy evaluation
python run_evaluation.py
```

**Cần extract:**
- Metrics từ evaluation_results.csv
- Overlap statistics
- Performance comparison

---

## 📝 Template Data Extraction

### 1. Dataset Statistics Table

```markdown
| Metric | KNN Model | Content-Based Model |
|--------|-----------|---------------------|
| Total Games | 15,080 | 111,452 |
| Total Users | ~500K | N/A |
| Total Reviews | ~10M | N/A |
| Unique Genres | N/A | ~50+ |
| Unique Tags | N/A | ~1000+ |
```

### 2. Evaluation Results Table

```markdown
| Metric | KNN | Content-Based | Hybrid | Best |
|--------|-----|---------------|--------|------|
| Precision@10 | 0.100 | 0.000 | 0.100 | KNN, Hybrid |
| Recall@10 | 0.125 | 0.000 | 0.125 | KNN, Hybrid |
| MAP@10 | 0.042 | 0.000 | 0.125 | Hybrid |
| NDCG@10 | 0.126 | 0.000 | 0.253 | Hybrid |
```

### 3. Sample Recommendations

```markdown
#### KNN Top 5:
1. Counter-Strike: Global Offensive (Score: 9.27)
2. Dota 2 (Score: 9.27)
3. ...

#### Content-Based Top 5:
1. Counter-Strike: Condition Zero (Score: 0.61)
2. Dirty Bomb (Score: 0.61)
3. ...

#### Hybrid Top 5:
1. Counter-Strike: Condition Zero (Hybrid Score: 22.31)
2. Left 4 Dead (Hybrid Score: 8.39)
3. ...
```

---

## 🔧 Scripts Hỗ Trợ

### 1. `create_test_user.py` ✅
- Tạo test user với nhiều ratings
- Backup original files
- **Usage**: `python create_test_user.py [num_ratings]`

### 2. `run_evaluation.py` ✅
- Chạy evaluation cho cả 3 models
- Tạo evaluation_results.csv
- **Usage**: `python run_evaluation.py`

### 3. `visualization.py` ✅
- Tạo charts và graphs
- **Usage**: `python visualization.py`

### 4. `get_dataset_stats.py` (Cần tạo)
- Lấy thống kê dataset
- **Usage**: `python get_dataset_stats.py`

---

## 📊 Data Files Cần Copy Vào Báo Cáo

### Bắt Buộc:
1. ✅ `evaluation_results.csv` - Metrics table
2. ✅ `model_comparison.png` - Comparison chart
3. ✅ `precision_recall_comparison.png` - Precision/Recall chart
4. ✅ `ndcg_map_comparison.png` - NDCG/MAP chart
5. ✅ `radar_chart.png` - Radar chart
6. ⚠️ Sample recommendations (copy từ CSV files)

### Optional:
7. ⚠️ Dataset statistics (từ get_dataset_stats.py)
8. ⚠️ Architecture diagrams (từ ARCHITECTURE_DIAGRAM.md)
9. ⚠️ Algorithm flowcharts (từ ARCHITECTURE_DIAGRAM.md)

---

## 🎯 Quy Trình Hoàn Chỉnh

### Bước 1: Tạo Test User
```bash
python create_test_user.py 50
```

### Bước 2: Chạy Models
```bash
# KNN
cd KNN_model
python UI.py
# → Rate games (nếu chưa có)
# → Get Recommendations
cd ..

# Content-Based
cd CB_model
python UI_ContentBased.py
# → Rate games (nếu chưa có)
# → Train Model
# → Get Recommendations
cd ..

# Hybrid
python run_hybrid.py
```

### Bước 3: Chạy Evaluation
```bash
python run_evaluation.py
```

### Bước 4: Tạo Visualization
```bash
python visualization.py
```

### Bước 5: Extract Data
- Copy metrics từ `evaluation_results.csv`
- Copy charts từ `Hybrid_model/*.png`
- Copy sample recommendations từ CSV files
- Copy dataset stats (nếu có)

### Bước 6: Viết Báo Cáo
- Sử dụng data đã extract
- Thêm analysis và discussion
- Insert charts và tables

---

## 📁 Files Cần Lưu Trữ

### Cho Báo Cáo:
```
Report/
├── figures/
│   ├── model_comparison.png
│   ├── precision_recall_comparison.png
│   ├── ndcg_map_comparison.png
│   └── radar_chart.png
├── tables/
│   └── evaluation_results.csv
├── samples/
│   ├── knn_recommendations.csv
│   ├── cb_recommendations.csv
│   └── hybrid_recommendations.csv
└── report.pdf/docx
```

---

## ✅ Checklist Trước Khi Nộp

- [ ] Dataset statistics đã có
- [ ] Evaluation results đã có
- [ ] Visualization charts đã có
- [ ] Sample recommendations đã có
- [ ] Test user data đã có
- [ ] All data files đã copy vào báo cáo
- [ ] Charts có captions và explanations
- [ ] Tables có proper formatting
- [ ] Data được reference đúng trong text

---

**Lưu ý**: 
- Backup original files trước khi tạo test user
- Chạy evaluation với test user mới để có kết quả tốt hơn
- Review kết quả trước khi viết báo cáo

