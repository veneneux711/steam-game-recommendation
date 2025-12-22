# Decision Tree Recommendation System

## Tổng Quan

Hệ thống Decision Tree Recommendation hoàn toàn **TÁCH BIỆT** với hệ thống KNN. Tất cả các file và UI đều riêng biệt để dễ phân biệt.

## Cấu Trúc Files

### Core Files (Decision Tree)
- **`DecisionTree_model.py`**: Model Decision Tree sử dụng scikit-learn
- **`DecisionTree_data_handler.py`**: Xử lý dữ liệu từ `decision_games.csv` và `decision_games.json`
- **`DecisionTree_UI_elements.py`**: Các UI elements riêng cho Decision Tree
- **`DecisionTree_commands.py`**: Các button commands riêng cho Decision Tree
- **`UI_DecisionTree.py`**: UI chính cho Decision Tree System

### Data Files
- **`decision_games.csv`**: Dữ liệu games cho Decision Tree
- **`decision_games.json`**: Dữ liệu JSON cho Decision Tree
- **`dt_user_ratings.json`**: Ratings của user (tự động tạo)
- **`dt_model.pkl`**: Model đã train (tự động tạo)
- **`dt_recommendations.csv`**: Recommendations kết quả (tự động tạo)

## So Sánh với KNN System

| Component | KNN System | Decision Tree System |
|-----------|------------|---------------------|
| **UI File** | `UI.py` | `UI_DecisionTree.py` |
| **UI Elements** | `UI_elements.py` | `DecisionTree_UI_elements.py` |
| **Commands** | `Button_commands.py` | `DecisionTree_commands.py` |
| **Data Handler** | `Data_handler.py` | `DecisionTree_data_handler.py` |
| **Model** | `knn_model.ipynb` | `DecisionTree_model.py` |
| **Data Files** | `your_games.csv`, `fav_games.csv` | `dt_user_ratings.json` |
| **Output** | `rcm_games.csv` | `dt_recommendations.csv` |

## Cách Sử Dụng

### 1. Chạy Decision Tree UI

```bash
python UI_DecisionTree.py
```

### 2. Quy Trình Sử Dụng

1. **Rate Games**: 
   - Chọn game từ danh sách
   - Click vào button rating (1-5): Dislike, Bad, Neutral, Good, Like
   - Ratings sẽ hiển thị trong "Your Ratings" section

2. **Save Ratings**:
   - Click "Save Ratings (DT)" để lưu ratings vào `dt_user_ratings.json`

3. **Train Model**:
   - Click "Train Model (DT)" để train Decision Tree model
   - Model sẽ được lưu vào `dt_model.pkl`

4. **Get Recommendations**:
   - Click "Get Recommendations (DT)" để lấy recommendations
   - Kết quả sẽ được lưu vào `dt_recommendations.csv`

### 3. Rating System

Decision Tree sử dụng rating 1-5:
- **5 (Like)**: Game rất thích
- **4 (Good)**: Game tốt
- **3 (Neutral)**: Game bình thường
- **2 (Bad)**: Game không tốt
- **1 (Dislike)**: Game không thích

## Features

### Decision Tree Model
- Sử dụng `DecisionTreeClassifier` từ scikit-learn
- Features: Price, Positive/Negative reviews, Metacritic score, Playtime, etc.
- Tự động train/test split và tính accuracy

### UI Features
- **Search Games**: Tìm kiếm games trong danh sách
- **Rate Games**: Đánh giá games với 5 mức độ
- **View Ratings**: Xem tất cả ratings đã đánh giá
- **Preferences**: Thiết lập preferences (max price, min positive ratio)
- **Recommendations**: Xem recommendations từ model

## Dependencies

```python
pandas
numpy
scikit-learn
tkinter (built-in với Python)
```

## Lưu Ý

1. **Tách biệt hoàn toàn**: Decision Tree system không ảnh hưởng đến KNN system
2. **Data files riêng**: Tất cả data files đều có prefix `dt_` hoặc từ `decision_games.*`
3. **UI riêng**: Chạy `UI_DecisionTree.py` thay vì `UI.py` để dùng Decision Tree
4. **Model training**: Cần ít nhất một số ratings trước khi train model

## Troubleshooting

### Lỗi: "decision_games.csv not found"
- Đảm bảo file `decision_games.csv` nằm cùng thư mục với script

### Lỗi: "No ratings found"
- Cần rate ít nhất một số games trước khi train model

### Lỗi: "Model not found"
- Cần train model trước khi get recommendations

## Tương Lai

Có thể mở rộng:
- Thêm nhiều features cho model
- Tuning hyperparameters
- Ensemble methods
- Cross-validation
- Feature importance visualization

