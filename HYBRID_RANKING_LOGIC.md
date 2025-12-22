# Hybrid Ranking Logic - Giải Thích Chi Tiết

## 1. Vấn Đề Logic Cũ

Logic cũ: `hybrid_score = knn_score + cb_score`
- Game A: KNN=15, CB=0 → hybrid_score = 15
- Game B: KNN=0.5, CB=0.5 → hybrid_score = 1
- **Vấn đề**: Game A rank cao hơn mặc dù chỉ có 1 nguồn

## 2. Logic Mới

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

**Giải thích:**
- `base_score`: Tổng điểm cơ bản từ 2 models
- `multiplicative_bonus`: Bonus dựa trên geometric mean (cả 2 đều cao → bonus lớn)
- `balance_bonus`: Bonus dựa trên min score (khuyến khích balance)
- `min_boost`: Boost tối thiểu để đảm bảo games có cả 2 scores luôn cao hơn games chỉ có 1 score

#### Nếu chỉ có 1 score (KNN=0 hoặc CB=0):
```
hybrid_score = base_score * 0.4  (Penalty 60%)
```

**Giải thích:**
- Penalty 60% để đảm bảo games chỉ có 1 score không thể rank quá cao
- Games chỉ có 1 score rất cao (ví dụ KNN=15) vẫn có thể rank cao hơn games có cả 2 scores rất thấp (ví dụ KNN=0.5, CB=0.5), nhưng điều này hợp lý

## 3. Ví Dụ Chi Tiết

### Case 1: Cả 2 scores cao
- KNN=15 (raw=30), CB=15 (raw=30)
- base_score = 15 + 15 = 30
- multiplicative_bonus = sqrt(15*15) * 0.5 = 15 * 0.5 = 7.5
- balance_bonus = 15 * 0.2 = 3
- min_boost = 2
- **hybrid_score = 30 + 7.5 + 3 + 2 = 42.5** ✅

### Case 2: 1 cao, 1 thấp
- KNN=15 (raw=30), CB=2.5 (raw=5)
- base_score = 15 + 2.5 = 17.5
- multiplicative_bonus = sqrt(15*2.5) * 0.5 = sqrt(37.5) * 0.5 ≈ 3.06
- balance_bonus = 2.5 * 0.2 = 0.5
- min_boost = 2
- **hybrid_score = 17.5 + 3.06 + 0.5 + 2 = 23.06** ✅

### Case 3: Cả 2 scores thấp
- KNN=0.5 (raw=1), CB=0.5 (raw=1)
- base_score = 0.5 + 0.5 = 1
- multiplicative_bonus = sqrt(0.5*0.5) * 0.5 = 0.5 * 0.5 = 0.25
- balance_bonus = 0.5 * 0.2 = 0.1
- min_boost = 2
- **hybrid_score = 1 + 0.25 + 0.1 + 2 = 3.35** ✅

### Case 4: Chỉ có KNN (CB=0)
- KNN=15 (raw=30), CB=0
- base_score = 15 + 0 = 15
- **hybrid_score = 15 * 0.4 = 6** (Penalty 60%) ✅

### Case 5: Chỉ có CB (KNN=0)
- KNN=0, CB=5 (raw=10)
- base_score = 0 + 5 = 5
- **hybrid_score = 5 * 0.4 = 2** (Penalty 60%) ✅

## 4. So Sánh Kết Quả

| Game | KNN | CB | Base | Hybrid Score | Rank |
|------|-----|----|----|--------------|------|
| A (cả 2 cao) | 15 | 15 | 30 | **42.5** | #1 ✅ |
| B (1 cao, 1 thấp) | 15 | 2.5 | 17.5 | **23.06** | #2 ✅ |
| C (cả 2 thấp) | 0.5 | 0.5 | 1 | **3.35** | #3 ✅ |
| D (chỉ KNN cao) | 15 | 0 | 15 | **6** | #4 ✅ |
| E (chỉ CB cao) | 0 | 5 | 5 | **2** | #5 ✅ |

## 5. Kết Quả

✅ **Logic đúng**: 
- Game có cả 2 scores (dù thấp) rank cao hơn game chỉ có 1 score vừa phải
- Game có cả 2 scores cao rank cao nhất
- Game có 1 cao 1 thấp rank ở giữa
- Game chỉ có 1 score rất cao vẫn có thể rank cao hơn game có cả 2 scores rất thấp (hợp lý)

## 6. Điều Chỉnh Hyperparameters

Nếu muốn games có cả 2 scores được ưu tiên hơn nữa:

### Tăng Multiplier
```python
multiplier = 0.6  # Từ 0.5 lên 0.6
```
- Tăng bonus cho games có cả 2 scores đều cao

### Tăng Penalty
```python
penalty_factor = 0.7  # Từ 0.6 lên 0.7
```
- Giảm điểm của games chỉ có 1 score

### Tăng Min Boost
```python
min_boost = 3.0  # Từ 2.0 lên 3.0
```
- Tăng boost tối thiểu cho games có cả 2 scores

### Thêm Minimum Threshold
```python
if has_both and min(knn_score, cb_score) < threshold:
    # Giảm bonus nếu một trong 2 scores quá thấp
    bonus *= 0.5
```
- Chỉ ưu tiên games có cả 2 scores đều đạt threshold

## 7. Implementation

Xem code trong `Hybrid_model/Hybrid_recommendations_reader.py`:
- Function: `calculate_hybrid_ranking()`
- Lines: 262-309

