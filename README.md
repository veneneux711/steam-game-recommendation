# Game Recommendation System

Hệ thống recommendation games với 2 models riêng biệt: **KNN** và **Decision Tree**.

## 📁 Cấu Trúc Thư Mục

```
Steam-Game-Recommendation-KNN-main/
│
├── KNN_model/                    # Hệ thống KNN Recommendation
│   ├── UI.py                     # UI chính cho KNN
│   ├── UI_elements.py            # UI elements
│   ├── Button_commands.py        # Button commands
│   ├── Data_handler.py           # Data handler
│   ├── knn_model.ipynb           # KNN model notebook
│   ├── knn_improvements.py       # KNN improvements
│   ├── final_games.csv           # Games data
│   ├── final_reviews.csv         # Reviews data
│   ├── your_games.csv            # User games
│   ├── fav_games.csv             # Favorite games
│   └── ... (other KNN files)
│
├── DT_model/                     # Hệ thống Decision Tree Recommendation
│   ├── UI_DecisionTree.py        # UI chính cho Decision Tree
│   ├── DecisionTree_UI_elements.py
│   ├── DecisionTree_commands.py
│   ├── DecisionTree_data_handler.py
│   ├── DecisionTree_model.py      # Decision Tree model
│   ├── decision_games.csv         # Games data
│   ├── decision_games.json       # Games JSON data
│   └── README_DecisionTree.md    # Hướng dẫn Decision Tree
│
└── (root files)                  # Files chung
    ├── data_preprocessing_1.ipynb
    ├── games.csv
    ├── games_metadata.json
    └── ...
```

## 🚀 Cách Sử Dụng

### KNN Model

1. **Chạy KNN UI:**
   ```bash
   cd KNN_model
   python UI.py
   ```

2. **Quy trình:**
   - Rate games (Like/Interested/Neutral/Dislike)
   - Save ratings
   - Get recommendations từ KNN model

### Decision Tree Model

1. **Chạy Decision Tree UI:**
   ```bash
   cd DT_model
   python UI_DecisionTree.py
   ```

2. **Quy trình:**
   - Rate games (1-5: Dislike → Like)
   - Save ratings
   - Train model
   - Get recommendations từ Decision Tree model

## 📊 So Sánh 2 Models

| Feature | KNN Model | Decision Tree Model |
|---------|-----------|---------------------|
| **Location** | `KNN_model/` | `DT_model/` |
| **UI File** | `UI.py` | `UI_DecisionTree.py` |
| **Rating System** | Like/Interested/Neutral/Dislike | 1-5 (Dislike→Like) |
| **Model Type** | Collaborative Filtering (KNN) | Decision Tree Classifier |
| **Data Files** | `final_games.csv`, `your_games.csv` | `decision_games.csv` |
| **Output** | `rcm_games.csv` | `dt_recommendations.csv` |

## 📝 Lưu Ý

- **Hoàn toàn tách biệt**: 2 models không ảnh hưởng lẫn nhau
- **Data riêng**: Mỗi model có data files riêng
- **UI riêng**: Mỗi model có UI riêng biệt
- **Chạy độc lập**: Có thể chạy cả 2 models cùng lúc

## 🔧 Dependencies

```bash
pip install pandas numpy scikit-learn tkinter nbformat nbconvert
```

## 📚 Documentation

- **KNN Model**: Xem `KNN_model/USAGE_GUIDE.md` và `KNN_model/KNN_Recommendation_Theory_and_Improvements.md`
- **Decision Tree Model**: Xem `DT_model/README_DecisionTree.md`

## 🎯 Quick Start

### KNN
```bash
cd KNN_model
python UI.py
```

### Decision Tree
```bash
cd DT_model
python UI_DecisionTree.py
```

