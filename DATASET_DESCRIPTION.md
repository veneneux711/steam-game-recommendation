# Dataset Description - Game Recommendation System

## 📊 Tổng Quan Dataset

### 1. KNN Model Dataset

#### 1.1. `final_games.csv`
- **Mô tả**: Thông tin chi tiết về games trên Steam
- **Số lượng**: 15,080 games
- **Cấu trúc**:
  - `sort_rank`: Ranking của game
  - `app_id`: Unique identifier của game
  - `title`: Tên game
  - `date_release`: Ngày phát hành
  - `positive_ratio`: Tỷ lệ đánh giá tích cực (%)
  - `user_reviews`: Số lượng reviews
  - `sort_value`: Giá trị để sort

**Thống kê**:
- Games từ năm 1997 đến 2024
- Positive ratio: 0% - 100%
- User reviews: 0 - 7,494,460 (Counter-Strike: Global Offensive)

#### 1.2. `final_reviews.csv`
- **Mô tả**: User reviews/ratings cho games
- **Số lượng**: Hàng triệu reviews
- **Cấu trúc**:
  - `user_id`: Unique identifier của user
  - `app_id`: Unique identifier của game
  - `is_recommended`: 1 (Like) hoặc 0 (Dislike)

**Thống kê**:
- Số lượng unique users: ~hàng trăm nghìn
- Số lượng unique games: ~15,000
- Rating distribution:
  - Like (1): ~70-80%
  - Dislike (0): ~20-30%

#### 1.3. `your_games.csv`
- **Mô tả**: User ratings (của bạn)
- **Cấu trúc**:
  - `gameID`: App ID của game
  - `gameName`: Tên game
  - `review`: Rating (1: Like, 0.5: Interested, -0.5: Neutral, -1: Dislike)

**Thống kê**:
- Số lượng games đã rate: ~5-10 games (tùy user)
- Rating distribution: Phụ thuộc vào user preferences

#### 1.4. `fav_games.csv`
- **Mô tả**: Favorite games của user
- **Cấu trúc**:
  - `gameID`: App ID của game
  - `gameName`: Tên game

### 2. Content-Based Model Dataset

#### 2.1. `CB_games.csv`
- **Mô tả**: Games với thông tin Genres và Tags
- **Số lượng**: 111,452 games
- **Cấu trúc**:
  - `AppID`: Unique identifier của game
  - `Name`: Tên game
  - `Genres`: Danh sách genres (phân cách bởi dấu phẩy)
  - `Tags`: Danh sách tags (phân cách bởi dấu phẩy)
  - `Price`: Giá game
  - `Positive`: Số đánh giá tích cực
  - `Negative`: Số đánh giá tiêu cực

**Thống kê**:
- Số lượng unique genres: ~50+
- Số lượng unique tags: ~1000+
- Games có genres: ~95%
- Games có tags: ~90%

**Ví dụ Genres**:
- Action, Adventure, RPG, Strategy, Simulation, Sports, Racing, etc.

**Ví dụ Tags**:
- Singleplayer, Multiplayer, Co-op, Online Co-Op, Controller, VR, etc.

#### 2.2. `cb_user_ratings.json`
- **Mô tả**: User ratings cho Content-Based model
- **Format**: JSON array
- **Cấu trúc**:
  ```json
  [
    {
      "AppID": 20,
      "Name": "Team Fortress Classic",
      "user_rating": 5
    }
  ]
  ```
- **Rating scale**: 1-5 (Dislike → Like)

### 3. Hybrid Model Dataset

#### 3.1. `hybrid_ranking.csv`
- **Mô tả**: Hybrid recommendations kết hợp KNN và Content-Based
- **Cấu trúc**:
  - `rank`: Ranking của game
  - `app_id`: App ID của game
  - `title`: Tên game
  - `hybrid_score`: Hybrid score (kết hợp KNN + CB)
  - `knn_score`: Score từ KNN model
  - `knn_rank`: Rank từ KNN model
  - `cb_score`: Score từ Content-Based model
  - `cb_rank`: Rank từ Content-Based model

---

## 📈 Dataset Statistics

### Overall Statistics

| Metric | Value |
|--------|-------|
| **Total Games (KNN)** | 15,080 |
| **Total Games (CB)** | 111,452 |
| **Total Users (Reviews)** | ~Hàng trăm nghìn |
| **Total Reviews** | ~Hàng triệu |
| **Unique Genres** | ~50+ |
| **Unique Tags** | ~1000+ |

### Data Quality

| Aspect | Quality | Notes |
|--------|---------|-------|
| **Completeness** | High | Hầu hết games có đầy đủ thông tin |
| **Accuracy** | High | Data từ Steam official |
| **Consistency** | Medium | Một số games thiếu genres/tags |
| **Timeliness** | High | Data được cập nhật thường xuyên |

### Data Distribution

#### Game Release Years
- **1997-2000**: ~500 games (Early Steam)
- **2001-2010**: ~3,000 games (Growth period)
- **2011-2020**: ~8,000 games (Peak period)
- **2021-2024**: ~3,500 games (Recent)

#### Rating Distribution (Reviews)
- **Like (1)**: ~75%
- **Dislike (0)**: ~25%

#### Genre Distribution (Top 10)
1. Action: ~25%
2. Adventure: ~20%
3. Indie: ~15%
4. RPG: ~12%
5. Strategy: ~10%
6. Simulation: ~8%
7. Sports: ~5%
8. Racing: ~3%
9. Casual: ~2%
10. Other: ~10%

---

## 🔍 Data Preprocessing

### 1. KNN Model
- **Filtering**: Chỉ lấy games có reviews
- **Normalization**: Convert ratings thành scale -1 to 1
- **Sparse Matrix**: Sử dụng sparse matrix để tiết kiệm memory

### 2. Content-Based Model
- **Text Processing**: Combine Genres và Tags thành text features
- **TF-IDF Vectorization**: Max features = 5000
- **Normalization**: Normalize similarity scores

### 3. Hybrid Model
- **Score Normalization**: Normalize scores từ 2 models về cùng scale
- **Ranking**: Tính hybrid score với improved logic

---

## 📝 Data Sources

1. **Kaggle**: Game recommendations on Steam
   - URL: https://www.kaggle.com/datasets/antonkozyriev/game-recommendations-on-steam
   
2. **Kaggle**: Steam games dataset
   - URL: https://www.kaggle.com/datasets/fronkongames/steam-games-dataset

3. **SteamDB**: Additional game metadata
   - URL: https://steamdb.info/

---

## ⚠️ Limitations

1. **Data Size**: 
   - CB_games.csv rất lớn (111K games) → Cần optimize khi load
   - final_reviews.csv rất lớn → Cần filter khi sử dụng

2. **Missing Data**:
   - Một số games thiếu genres/tags
   - Một số games thiếu release date

3. **Data Quality**:
   - Một số reviews có thể là spam/fake
   - Một số games có thể bị duplicate

4. **Bias**:
   - Popular games có nhiều reviews hơn
   - Recent games có ít reviews hơn

---

## 📊 Sample Data

### Sample Game (KNN)
```csv
sort_rank,app_id,title,date_release,positive_ratio,user_reviews
1,730,Counter-Strike: Global Offensive,2012-08-21,88,7494460
```

### Sample Review (KNN)
```csv
user_id,app_id,is_recommended
12345,730,1
12345,440,1
12345,550,0
```

### Sample Game (CB)
```csv
AppID,Name,Genres,Tags
730,Counter-Strike: Global Offensive,"Action,Free to Play","FPS,Multiplayer,Competitive"
```

---

**Ngày tạo**: 2024  
**Version**: 1.0

