# Giải Thích Metrics: MAP vs NDCG

## 📊 MAP (Mean Average Precision)

### Định nghĩa
**MAP (Mean Average Precision)** đo lường **độ chính xác trung bình** của ranking, tập trung vào **vị trí của relevant items** trong danh sách.

### Công thức
```
AP@K = (1/|relevant_items|) × Σ(Precision@i × rel(i))
MAP@K = Mean(AP@K của tất cả users)
```

Trong đó:
- `Precision@i`: Precision tại vị trí i
- `rel(i)`: 1 nếu item ở vị trí i là relevant, 0 nếu không
- Chỉ tính cho các vị trí có relevant items

### Đặc điểm
- ✅ **Tập trung vào vị trí**: Relevant items càng ở trên càng tốt
- ✅ **Penalty cho vị trí thấp**: Items relevant ở vị trí thấp bị penalty
- ✅ **Phù hợp cho**: Binary relevance (relevant/not relevant)

### Ví dụ
```
Recommendations: [Relevant, Not Relevant, Relevant, Not Relevant, Relevant]
Precision@1 = 1/1 = 1.0
Precision@3 = 2/3 = 0.67
Precision@5 = 3/5 = 0.60

AP@5 = (1.0 + 0.67 + 0.60) / 3 = 0.76
```

---

## 📈 NDCG (Normalized Discounted Cumulative Gain)

### Định nghĩa
**NDCG (Normalized Discounted Cumulative Gain)** đo lường **chất lượng ranking** với **discount factor** cho vị trí, và **normalize** với ideal ranking.

### Công thức
```
DCG@K = Σ(relevance_i / log2(i+1))
IDCG@K = DCG của perfect ranking
NDCG@K = DCG@K / IDCG@K
```

Trong đó:
- `relevance_i`: Relevance score của item ở vị trí i
- `log2(i+1)`: Discount factor (vị trí càng thấp, giá trị càng nhỏ)
- `IDCG`: Ideal DCG (perfect ranking)

### Đặc điểm
- ✅ **Discount factor**: Vị trí càng thấp, đóng góp càng ít
- ✅ **Normalized**: So sánh với perfect ranking (0-1)
- ✅ **Phù hợp cho**: Graded relevance (có nhiều mức độ relevance)

### Ví dụ
```
Recommendations: [Relevance=3, Relevance=2, Relevance=1, Relevance=0, Relevance=2]

DCG@5 = 3/log2(2) + 2/log2(3) + 1/log2(4) + 0/log2(5) + 2/log2(6)
      = 3/1 + 2/1.58 + 1/2 + 0/2.32 + 2/2.58
      = 3 + 1.27 + 0.5 + 0 + 0.78 = 5.55

Ideal ranking: [3, 2, 2, 1, 0]
IDCG@5 = 3/1 + 2/1.58 + 2/2 + 1/2.32 + 0/2.58 = 3 + 1.27 + 1 + 0.43 + 0 = 5.70

NDCG@5 = 5.55 / 5.70 = 0.97
```

---

## 🔍 So Sánh MAP vs NDCG

| Aspect | MAP | NDCG |
|--------|-----|------|
| **Focus** | Vị trí của relevant items | Chất lượng ranking với discount |
| **Relevance** | Binary (0/1) | Graded (có thể có nhiều mức) |
| **Penalty** | Penalty cho vị trí thấp | Discount factor (log) |
| **Normalization** | Không normalize | Normalize với ideal ranking |
| **Range** | 0 - 1 | 0 - 1 |
| **Interpretation** | "Có bao nhiêu relevant items ở trên?" | "Ranking tốt đến mức nào so với perfect?" |

---

## 📊 Trong Kết Quả Của Bạn

### KNN Model
- **MAP@10 = 0.042**: Relevant items ở vị trí thấp → MAP thấp
- **NDCG@10 = 0.126**: Ranking quality trung bình

### Hybrid Model
- **MAP@10 = 0.125**: Relevant items được đưa lên cao hơn → MAP cao hơn **3 lần**
- **NDCG@10 = 0.253**: Ranking quality tốt hơn nhiều → NDCG cao hơn **2 lần**

### Tại Sao Hybrid Tốt Hơn?

1. **MAP cao hơn**:
   - Hybrid ranking logic đưa relevant items lên vị trí cao hơn
   - Games có cả 2 scores được ưu tiên → relevant items được rank cao
   - Penalty cho games chỉ có 1 score → giảm noise

2. **NDCG cao hơn**:
   - Discount factor: Relevant items ở vị trí cao đóng góp nhiều hơn
   - Hybrid có nhiều relevant items ở top positions
   - Normalization: So với perfect ranking, Hybrid gần hơn KNN

---

## 🎯 Kết Luận

**MAP và NDCG là 2 metrics khác nhau:**

1. **MAP**: Đo "relevant items có ở trên không?"
   - Hybrid = 0.125 vs KNN = 0.042 → **Gấp 3 lần**
   - Có nghĩa: Hybrid đưa relevant items lên cao hơn KNN

2. **NDCG**: Đo "ranking tốt đến mức nào?"
   - Hybrid = 0.253 vs KNN = 0.126 → **Gấp 2 lần**
   - Có nghĩa: Hybrid có ranking quality tốt hơn KNN

**Cả 2 đều quan trọng:**
- **MAP**: Quan trọng khi bạn chỉ quan tâm "có relevant không?"
- **NDCG**: Quan trọng khi bạn quan tâm "ranking tốt đến mức nào?"

**Trong trường hợp của bạn:**
- Hybrid tốt hơn KNN về **cả 2 metrics**
- Điều này chứng tỏ Hybrid ranking logic hoạt động tốt!

---

## 📝 Cách Viết Trong Báo Cáo

### Cách 1: Tách riêng
```
MAP@10: Hybrid (0.125) cao gấp 3 lần KNN (0.042), cho thấy Hybrid đưa relevant items 
lên vị trí cao hơn đáng kể.

NDCG@10: Hybrid (0.253) cao gấp 2 lần KNN (0.126), chứng tỏ ranking quality của 
Hybrid tốt hơn nhiều so với KNN.
```

### Cách 2: Kết hợp
```
Về ranking quality, Hybrid model vượt trội so với KNN:
- MAP@10: 0.125 vs 0.042 (cao gấp 3 lần) - Relevant items được đưa lên cao hơn
- NDCG@10: 0.253 vs 0.126 (cao gấp 2 lần) - Ranking quality tốt hơn đáng kể

Cả 2 metrics đều cho thấy Hybrid ranking logic với improved bonus/penalty system 
đã cải thiện đáng kể chất lượng recommendations.
```

---

**Lưu ý**: Cả 2 metrics đều quan trọng và bổ sung cho nhau. MAP tập trung vào vị trí, NDCG tập trung vào chất lượng tổng thể.

