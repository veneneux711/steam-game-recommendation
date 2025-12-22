# Game Recommendation System

Hệ thống recommendation games với **3 models**: **KNN** (Collaborative Filtering), **Content-Based Filtering** (Genres & Tags), và **Hybrid System** (kết hợp cả 2).

## 📁 Cấu Trúc Thư Mục

```
Steam ML/
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
├── CB_model/                      # Hệ thống Content-Based Filtering
│   ├── UI_ContentBased.py        # UI chính cho Content-Based
│   ├── ContentBased_UI_elements.py
│   ├── ContentBased_commands.py
│   ├── ContentBased_data_handler.py
│   ├── ContentBased_model.py     # Content-Based model (Genres & Tags)
│   ├── CB_games.csv              # Games data (111K+ games)
│   └── ...
│
├── Hybrid_model/                 # Hệ thống Hybrid (KNN + Content-Based)
│   ├── run_hybrid.py             # Main script
│   ├── Hybrid_recommendations_reader.py  # Core logic
│   ├── Hybrid_results_viewer.py  # UI viewer
│   ├── run_Hybrid.bat            # Batch file
│   └── hybrid_ranking.csv        # Output file
│
│
├── evaluation.py                 # Evaluation metrics module
├── Source.txt                    # Nguồn dữ liệu
├── setup.bat                     # Setup script
├── run_KNN.bat                   # Run KNN
├── run_CB.bat                    # Run Content-Based
│
├── Documentation Files (Root)    # Tài liệu lý thuyết
│   ├── KNN_THEORY.md             # Lý thuyết KNN
│   ├── CB_THEORY.md              # Lý thuyết Content-Based
│   ├── HYBRID_THEORY.md          # Lý thuyết Hybrid
│   ├── HYBRID_RANKING_LOGIC.md   # Logic ranking chi tiết
│   ├── PROJECT_EVALUATION.md     # Đánh giá project
│   ├── PROJECT_SUMMARY.md        # Tóm tắt project
│   └── GITHUB_SETUP.md          # Hướng dẫn GitHub
│
└── README.md                     # This file
```

## 🚀 Cách Sử Dụng

### Quick Start

**Hybrid System (Recommended):**
```bash
cd Hybrid_model
run_Hybrid.bat
```
hoặc
```bash
cd Hybrid_model
python run_hybrid.py
```

**KNN Model:**
```bash
run_KNN.bat
```
hoặc
```bash
cd KNN_model
python UI.py
```

**Content-Based Model:**
```bash
run_CB.bat
```
hoặc
```bash
cd CB_model
python UI_ContentBased.py
```

### Quy Trình Sử Dụng

#### 1. KNN Model
- Rate games (Like/Interested/Neutral/Dislike)
- Save ratings
- Get recommendations từ KNN model
- Output: `rcm_games.csv` hoặc `recommendations.csv`

#### 2. Content-Based Model
- Rate games (1-5: Dislike → Like)
- Save ratings
- Train model (sử dụng Genres & Tags)
- Get recommendations dựa trên similarity với games đã rate
- Output: `cb_recommendations.csv`

#### 3. Hybrid System
- **Bước 1**: Chạy KNN model và get recommendations
- **Bước 2**: Chạy Content-Based model và get recommendations
- **Bước 3**: Chạy Hybrid system để kết hợp cả 2
- Output: `hybrid_ranking.csv` (hiển thị trong UI window)

## 📊 So Sánh 3 Models

| Feature | KNN Model | Content-Based Model | Hybrid Model |
|---------|-----------|---------------------|--------------|
| **Location** | `KNN_model/` | `CB_model/` | `Hybrid_model/` |
| **UI File** | `UI.py` | `UI_ContentBased.py` | `run_hybrid.py` |
| **Rating System** | Like/Interested/Neutral/Dislike | 1-5 (Dislike→Like) | Đọc từ 2 models |
| **Model Type** | Collaborative Filtering | Content-Based | Kết hợp cả 2 |
| **Data Files** | `final_games.csv`, `your_games.csv` | `CB_games.csv` | Từ cả 2 systems |
| **Output** | `rcm_games.csv` | `cb_recommendations.csv` | `hybrid_ranking.csv` |
| **Based On** | User behavior | Game content (Genres/Tags) | Cả 2 |
| **UI Display** | ✅ Có | ✅ Có | ✅ Có (Table view) |

## 📝 Lưu Ý

- **3 Models**: KNN, Content-Based, và Hybrid
- **Hybrid System**: Kết hợp cả 2 approaches, đọc recommendations từ 2 models
- **Chạy độc lập**: Có thể chạy từng model riêng
- **Hybrid UI**: Tự động hiển thị kết quả trong bảng giao diện sau khi tính toán

## 🔧 Dependencies

```bash
pip install pandas numpy scikit-learn tkinter nbformat nbconvert
```

## 📚 Documentation

Tất cả tài liệu lý thuyết đã được di chuyển ra root folder:

- **KNN Theory**: `KNN_THEORY.md` - Lý thuyết và kiến trúc KNN Collaborative Filtering
- **Content-Based Theory**: `CB_THEORY.md` - Lý thuyết Content-Based Filtering
- **Hybrid Theory**: `HYBRID_THEORY.md` - Lý thuyết Hybrid System
- **Hybrid Ranking Logic**: `HYBRID_RANKING_LOGIC.md` - Giải thích chi tiết ranking logic
- **Project Evaluation**: `PROJECT_EVALUATION.md` - Đánh giá project
- **Project Summary**: `PROJECT_SUMMARY.md` - Tóm tắt project
- **GitHub Setup**: `GITHUB_SETUP.md` - Hướng dẫn setup GitHub

## 🔧 Dependencies

```bash
pip install pandas numpy scikit-learn nbformat nbconvert
```

Hoặc chạy:
```bash
setup.bat
```

## 📖 Nguồn Dữ Liệu

Xem `Source.txt` để biết nguồn dữ liệu:
- Kaggle: Game recommendations on Steam
- Kaggle: Steam games dataset
- SteamDB

