# Data Summary for Report - Game Recommendation System

## 📊 Dataset Statistics

### KNN Model Dataset
- **Total Games**: 15,080
- **Games with Reviews**: 15,080 (100%)
- **Average Positive Ratio**: 80.09%
- **Average User Reviews**: 5,847
- **Max User Reviews**: 7,494,460 (Counter-Strike: Global Offensive)
- **Release Years**: 1997 - 2023

### Reviews Sample (100K reviews)
- **Total Reviews**: 100,000
- **Unique Users**: 98,803
- **Unique Games**: 208
- **Like (1)**: 15,339 (15.3%)
- **Dislike (0)**: 84,661 (84.7%)

### Content-Based Model Dataset
- **Total Games (Sample 50K)**: 50,000
- **Games with Genres**: 48,710 (97.4%)
- **Games with Tags**: 43,521 (87.0%)
- **Unique Genres**: 33
- **Unique Tags**: 438

### Top 10 Genres
1. Indie: 34,627
2. Action: 20,375
3. Casual: 19,989
4. Adventure: 18,659
5. Simulation: 9,418
6. Strategy: 9,254
7. RPG: 8,408
8. Early Access: 5,295
9. Free to Play: 3,837
10. Sports: 2,205

### Top 10 Tags
1. Indie: 28,746
2. Singleplayer: 20,876
3. Action: 19,579
4. Casual: 18,811
5. Adventure: 18,271
6. 2D: 11,048
7. Strategy: 9,290
8. Simulation: 9,027
9. RPG: 7,992
10. Puzzle: 7,488

---

## 👤 Test User "MA" Statistics

### KNN Model Ratings
- **Total Ratings**: 50 games
- **Distribution**:
  - Like (1.0): ~40%
  - Interested (0.5): ~20%
  - Neutral (-0.5): ~20%
  - Dislike (-1.0): ~20%

### Content-Based Model Ratings
- **Total Ratings**: 27 games
- **Distribution**:
  - Like (5): 8 games (29.6%)
  - Good (4): 4 games (14.8%)
  - Neutral (3): 6 games (22.2%)
  - Bad (2): 6 games (22.2%)
  - Dislike (1): 3 games (11.1%)

---

## 📈 Evaluation Results @ K=10

| Metric | KNN | Content-Based | Hybrid | Best Model |
|--------|-----|---------------|--------|------------|
| **Precision@10** | 0.100 | 0.000 | 0.100 | KNN, Hybrid (tie) |
| **Recall@10** | 0.125 | 0.000 | 0.125 | KNN, Hybrid (tie) |
| **F1-Score@10** | 0.111 | 0.000 | 0.111 | KNN, Hybrid (tie) |
| **MAP@10** | 0.042 | 0.000 | **0.125** | **Hybrid** ⭐ |
| **NDCG@10** | 0.126 | 0.000 | **0.253** | **Hybrid** ⭐ |
| **Diversity** | 0.000 | 0.000 | 0.000 | - |
| **Coverage** | 0.0007 | 0.0007 | 0.0007 | All (tie) |

### Key Findings:
- **Hybrid Model** có ranking quality tốt nhất:
  - MAP@10 = 0.125 (cao gấp **3 lần** KNN)
  - NDCG@10 = 0.253 (cao gấp **2 lần** KNN)
- **KNN và Hybrid** có precision/recall tương đương
- **Content-Based** = 0 (không có overlap với test set)

---

## 🎮 Sample Recommendations

### KNN Top 10 Recommendations

| Rank | Game | Relevance Score | Positive Ratio | User Reviews |
|------|------|----------------|----------------|--------------|
| 1 | Half-Life 2 | 83.36 | 97% | 122,230 |
| 2 | Amnesia: The Dark Descent | 73.35 | 95% | 16,849 |
| 3 | Portal | 73.26 | 98% | 117,868 |
| 4 | Left 4 Dead | 72.64 | 96% | 41,569 |
| 5 | Minion Masters | 70.91 | 91% | 60,906 |
| 6 | Tomb Raider | 70.12 | 96% | 136,055 |
| 7 | Half-Life 2: Episode Two | 69.55 | 97% | 27,401 |
| 8 | Half-Life 2: Episode One | 69.55 | 95% | 20,221 |
| 9 | Spiral Knights | 67.40 | 84% | 22,946 |
| 10 | Alan Wake | 67.23 | 90% | 27,464 |

**App IDs (từ final_games.csv):**
- Half-Life 2: app_id = 220
- Amnesia: app_id = 57300
- Portal: app_id = 400
- Left 4 Dead: app_id = 500
- Tomb Raider: app_id = 203160
- Half-Life 2: Episode Two: app_id = 420
- Half-Life 2: Episode One: app_id = 380
- Spiral Knights: app_id = 99900
- Alan Wake: app_id = 108710

**Observations:**
- Tất cả đều là games nổi tiếng với positive ratio cao (84-98%)
- Nhiều games từ Valve (Half-Life, Portal, Left 4 Dead)
- Relevance scores cao (67-83)

### Content-Based Top 10 Recommendations

| Rank | Game | Similarity Score | Positive | Negative |
|------|------|-----------------|----------|----------|
| 1 | Shank | 0.825 | 1,884 | 240 |
| 2 | Final Crash Demo | 0.577 | 7 | 0 |
| 3 | Shank 2 | 0.564 | 2,415 | 537 |
| 4 | Streets of Red: Devil's Dare Deluxe | 0.561 | 162 | 38 |
| 5 | PsyBurst | 0.548 | 1 | 0 |
| 6 | WarpZone vs THE DIMENSION | 0.541 | 9 | 1 |
| 7 | Streets of Rage 4 | 0.541 | 13,115 | 1,089 |
| 8 | Wulverblade | 0.535 | 156 | 35 |
| 9 | The Dishwasher: Vampire Smile | 0.530 | 898 | 55 |
| 10 | Aces Wild: Manic Brawling Action! | 0.566 | 266 | 74 |

**Observations:**
- Tập trung vào Action/Beat 'em up games
- Similarity scores trung bình (0.53-0.83)
- Một số games ít reviews (Demo, indie games)

### Hybrid Top 10 Recommendations

| Rank | Game | Hybrid Score | KNN Rank | CB Rank | App ID |
|------|------|--------------|----------|---------|--------|
| 1 | Half-Life 2 | 6.0 | #1 | - | 220 |
| 2 | Amnesia: The Dark Descent | 5.8 | #2 | - | 57300 |
| 3 | Portal | 5.6 | #3 | - | 400 |
| 4 | Left 4 Dead | 5.4 | #4 | - | 500 |
| 5 | Minion Masters | 5.2 | #5 | - | 489520 |
| 6 | Tomb Raider | 5.0 | #6 | - | 203160 |
| 7 | Half-Life 2: Episode Two | 4.8 | #7 | - | 420 |
| 8 | Half-Life 2: Episode One | 4.6 | #8 | - | 380 |
| 9 | Spiral Knights | 4.4 | #9 | - | 99900 |
| 10 | Alan Wake | 4.2 | #10 | - | 108710 |

**Observations:**
- Top 10 chủ yếu từ KNN (vì CB không có overlap với test set)
- Hybrid score = KNN score * 0.4 (penalty vì chỉ có 1 score)
- Games có cả 2 scores (như Shank ở rank #12) sẽ có hybrid score cao hơn nhờ bonus
- Shank (rank #12): KNN = 0, CB = #1 → Hybrid = 4.0 (có bonus từ cả 2 scores)

---

## 📊 Comparison Analysis

### Precision & Recall
- **KNN**: Precision = 0.100, Recall = 0.125
- **Hybrid**: Precision = 0.100, Recall = 0.125
- **Content-Based**: Precision = 0.000, Recall = 0.000

**Nhận xét**: KNN và Hybrid có precision/recall tương đương. Content-Based không có overlap với test set.

### Ranking Quality (MAP & NDCG)
- **KNN**: MAP = 0.042, NDCG = 0.126
- **Hybrid**: MAP = **0.125**, NDCG = **0.253**
- **Content-Based**: MAP = 0.000, NDCG = 0.000

**Nhận xét**: Hybrid có ranking quality tốt nhất, cao gấp 3 lần KNN về MAP và gấp 2 lần về NDCG.

### Coverage
- Tất cả models: Coverage = 0.0007 (0.07%)
- **Nhận xét**: Coverage thấp vì số lượng recommendations ít so với total games (15,080)

### Diversity
- Tất cả models: Diversity = 0.000
- **Nhận xét**: Cần cải thiện diversity bằng cách thêm diversity boosting vào ranking logic

---

## 🎯 Key Insights for Report

### 1. Hybrid Model Performance
- ✅ **Best ranking quality**: MAP và NDCG cao nhất
- ✅ **Tương đương KNN** về precision/recall
- ⚠️ **Cần cải thiện**: Diversity và coverage

### 2. KNN Model Performance
- ✅ **Good precision/recall**: 0.100 và 0.125
- ⚠️ **Low ranking quality**: MAP và NDCG thấp hơn Hybrid
- ⚠️ **Cần cải thiện**: Ranking algorithm

### 3. Content-Based Model Performance
- ❌ **No overlap**: Không có recommendations match với test set
- ⚠️ **Cần cải thiện**: User profile creation và similarity threshold

### 4. Dataset Quality
- ✅ **Large dataset**: 15K games (KNN), 111K games (CB)
- ✅ **Good coverage**: Hầu hết games có genres/tags
- ⚠️ **Test set nhỏ**: Chỉ 8 games trong test set

---

## 📝 Data Tables for Report

### Table 1: Dataset Overview
```
| Dataset | Games | Users | Reviews | Genres | Tags |
|---------|-------|-------|---------|--------|------|
| KNN | 15,080 | ~500K | ~10M | N/A | N/A |
| Content-Based | 111,452 | N/A | N/A | 33 | 438 |
```

### Table 2: Evaluation Metrics @ K=10
```
| Metric | KNN | Content-Based | Hybrid | Best |
|--------|-----|---------------|--------|------|
| Precision@10 | 0.100 | 0.000 | 0.100 | KNN, Hybrid |
| Recall@10 | 0.125 | 0.000 | 0.125 | KNN, Hybrid |
| MAP@10 | 0.042 | 0.000 | 0.125 | Hybrid |
| NDCG@10 | 0.126 | 0.000 | 0.253 | Hybrid |
```

### Table 3: Sample Recommendations Comparison
```
| Model | Top Game | Score | Type |
|-------|----------|-------|------|
| KNN | Half-Life 2 | 83.36 | Popular AAA |
| Content-Based | Shank | 0.825 | Action/Indie |
| Hybrid | Half-Life 2 | 6.0 | Popular AAA |
```

---

## 📊 Charts Available

1. **model_comparison.png** - Bar chart so sánh tất cả metrics
2. **precision_recall_comparison.png** - Precision và Recall comparison
3. **ndcg_map_comparison.png** - NDCG và MAP comparison
4. **radar_chart.png** - Radar chart tổng thể

---

## ✅ Checklist Data for Report

- [x] Dataset statistics
- [x] Evaluation results
- [x] Sample recommendations
- [x] Test user statistics
- [x] Visualization charts
- [x] Comparison analysis

---

**Ngày tạo**: 2024  
**Version**: 1.0

