# Cấu Trúc Thư Mục Chi Tiết

## 📂 KNN_model/

Chứa tất cả files liên quan đến KNN Recommendation System.

### Core Files
- `UI.py` - UI chính
- `UI_elements.py` - UI elements
- `Button_commands.py` - Button commands
- `Data_handler.py` - Data handler

### Model Files
- `knn_model.ipynb` - KNN model notebook
- `knn_improvements.py` - KNN improvements module

### Data Files
- `final_games.csv` - Games data
- `final_reviews.csv` - Reviews data
- `your_games.csv` - User games (input)
- `fav_games.csv` - Favorite games (input)

### Output Files
- `rcm_games.csv` - Recommendations output
- `rcm_wish.csv` - Wishlist recommendations

### Documentation
- `USAGE_GUIDE.md` - Hướng dẫn sử dụng
- `KNN_Recommendation_Theory_and_Improvements.md` - Lý thuyết và cải tiến
- `CHANGES_APPLIED.md` - Các thay đổi đã áp dụng

## 📂 DT_model/

Chứa tất cả files liên quan đến Decision Tree Recommendation System.

### Core Files
- `UI_DecisionTree.py` - UI chính
- `DecisionTree_UI_elements.py` - UI elements
- `DecisionTree_commands.py` - Button commands
- `DecisionTree_data_handler.py` - Data handler
- `DecisionTree_model.py` - Decision Tree model

### Data Files
- `decision_games.csv` - Games data
- `decision_games.json` - Games JSON data

### Output Files (tự động tạo)
- `dt_user_ratings.json` - User ratings
- `dt_model.pkl` - Trained model
- `dt_recommendations.csv` - Recommendations output

### Documentation
- `README_DecisionTree.md` - Hướng dẫn Decision Tree

## 📂 Root Directory

Chứa các files chung hoặc scripts.

### Scripts
- `run_KNN.bat` - Chạy KNN system
- `run_DT.bat` - Chạy Decision Tree system
- `run_this.bat` - Script cũ (có thể dùng cho KNN)
- `setup.bat` - Setup script

### Common Files
- `data_preprocessing_1.ipynb` - Data preprocessing notebook
- `games.csv` - Games data chung
- `games_metadata.json` - Games metadata
- `recommendations.csv` - Recommendations cũ (nếu có)

### Documentation
- `README.md` - README chính
- `STRUCTURE.md` - File này
- `Source.txt` - Source information

## 🔄 Workflow

### KNN Workflow
1. Chạy `KNN_model/UI.py`
2. Rate games trong UI
3. Save ratings → `your_games.csv`, `fav_games.csv`
4. Get recommendations → Chạy `knn_model.ipynb` → `rcm_games.csv`

### Decision Tree Workflow
1. Chạy `DT_model/UI_DecisionTree.py`
2. Rate games (1-5) trong UI
3. Save ratings → `dt_user_ratings.json`
4. Train model → `dt_model.pkl`
5. Get recommendations → `dt_recommendations.csv`

## 📝 Notes

- **Tách biệt hoàn toàn**: 2 models không chia sẻ files
- **Import paths**: Tất cả imports đều relative trong cùng folder
- **Data isolation**: Mỗi model có data riêng
- **Output isolation**: Mỗi model có output riêng

