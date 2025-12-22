# System Architecture - Game Recommendation System

## 📐 Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────────┐
│                    GAME RECOMMENDATION SYSTEM                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         DATA LAYER                      │
        │  ┌──────────┐  ┌──────────┐           │
        │  │ KNN Data │  │ CB Data  │           │
        │  │ - Games  │  │ - Games  │           │
        │  │ - Reviews│  │ - Genres │           │
        │  │ - Ratings│  │ - Tags   │           │
        │  └──────────┘  └──────────┘           │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │      RECOMMENDATION MODELS               │
        │  ┌──────────┐  ┌──────────┐            │
        │  │   KNN    │  │Content-  │            │
        │  │  Model   │  │  Based   │            │
        │  │          │  │  Model   │            │
        │  └──────────┘  └──────────┘            │
        │         │            │                  │
        │         └──────┬─────┘                  │
        │                ▼                        │
        │         ┌──────────┐                    │
        │         │  Hybrid  │                    │
        │         │  Model   │                    │
        │         └──────────┘                    │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         UI LAYER                        │
        │  ┌──────────┐  ┌──────────┐            │
        │  │  KNN UI  │  │   CB UI  │            │
        │  └──────────┘  └──────────┘            │
        │         │            │                  │
        │         └──────┬─────┘                  │
        │                ▼                        │
        │         ┌──────────┐                    │
        │         │ Hybrid   │                    │
        │         │ Results  │                    │
        │         │ Viewer   │                    │
        │         └──────────┘                    │
        └─────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

### KNN Model Flow

```
User Ratings (your_games.csv)
         │
         ▼
┌────────────────────┐
│  Data Handler       │
│  - Load ratings    │
│  - Create vectors  │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  KNN Algorithm     │
│  1. Build User-Item│
│     Matrix         │
│  2. Calculate      │
│     Similarity     │
│  3. Find KNN       │
│  4. Predict        │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  Recommendations   │
│  (rcm_games.csv)   │
└────────────────────┘
```

### Content-Based Model Flow

```
User Ratings (cb_user_ratings.json)
         │
         ▼
┌────────────────────┐
│  Data Handler       │
│  - Load ratings    │
│  - Load games      │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  Feature Extraction│
│  - Combine Genres  │
│    & Tags          │
│  - TF-IDF          │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  User Profile      │
│  - Weighted avg    │
│    of game features│
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  Similarity Calc   │
│  - Cosine similarity│
│  - Filter & Rank   │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  Recommendations   │
│  (cb_recommendations│
│   .csv)            │
└────────────────────┘
```

### Hybrid Model Flow

```
KNN Recommendations          CB Recommendations
     (rcm_games.csv)         (cb_recommendations.csv)
         │                            │
         └──────────┬─────────────────┘
                    ▼
         ┌────────────────────┐
         │  Hybrid Reader     │
         │  - Read both       │
         │  - Assign scores  │
         └────────────────────┘
                    │
                    ▼
         ┌────────────────────┐
         │  Hybrid Ranking    │
         │  - Calculate       │
         │    hybrid_score    │
         │  - Apply bonus/    │
         │    penalty        │
         └────────────────────┘
                    │
                    ▼
         ┌────────────────────┐
         │  Results Viewer     │
         │  - Display table    │
         │  - Highlight top   │
         └────────────────────┘
```

---

## 🧩 Component Architecture

### KNN Model Components

```
KNN_model/
├── UI.py                    # Main UI
├── UI_elements.py           # UI components
├── Button_commands.py       # Event handlers
├── Data_handler.py          # Data loading/saving
└── knn_model.ipynb          # Core algorithm
```

**Data Flow:**
```
UI.py
  │
  ├─→ UI_elements.py (create UI)
  ├─→ Button_commands.py (handle events)
  ├─→ Data_handler.py (load/save data)
  └─→ knn_model.ipynb (get recommendations)
```

### Content-Based Model Components

```
CB_model/
├── UI_ContentBased.py       # Main UI
├── ContentBased_UI_elements.py
├── ContentBased_commands.py
├── ContentBased_data_handler.py
└── ContentBased_model.py    # Core algorithm
```

**Data Flow:**
```
UI_ContentBased.py
  │
  ├─→ ContentBased_UI_elements.py
  ├─→ ContentBased_commands.py
  ├─→ ContentBased_data_handler.py
  └─→ ContentBased_model.py
      ├─→ TF-IDF Vectorization
      ├─→ User Profile Creation
      └─→ Cosine Similarity
```

### Hybrid Model Components

```
Hybrid_model/
├── run_hybrid.py            # Main script
├── Hybrid_recommendations_reader.py
├── Hybrid_results_viewer.py
└── hybrid_ranking.csv       # Output
```

---

## 🔀 Algorithm Flowcharts

### KNN Algorithm

```
START
  │
  ▼
Load User Ratings
  │
  ▼
Build User-Item Matrix
  │
  ▼
Filter Relevant Users
  │
  ▼
Calculate Cosine Similarity
  │
  ▼
Find K Nearest Neighbors
  │
  ▼
Calculate Weighted Predictions
  │
  ▼
Sort by Relevance
  │
  ▼
Return Top N Recommendations
  │
  ▼
END
```

### Content-Based Algorithm

```
START
  │
  ▼
Load Games (Genres & Tags)
  │
  ▼
Extract Features (Genres + Tags)
  │
  ▼
TF-IDF Vectorization
  │
  ▼
Load User Ratings
  │
  ▼
Create User Profile
  (Weighted avg of rated games)
  │
  ▼
Calculate Cosine Similarity
  (User profile vs All games)
  │
  ▼
Filter & Sort
  │
  ▼
Return Top N Recommendations
  │
  ▼
END
```

### Hybrid Ranking Algorithm

```
START
  │
  ▼
Read KNN Recommendations
  │
  ▼
Read CB Recommendations
  │
  ▼
Assign Scores (30-1 based on rank)
  │
  ▼
For each game:
  │
  ├─→ Has both scores?
  │   │
  │   ├─→ YES: Calculate bonus
  │   │   │
  │   │   └─→ hybrid_score = base + bonus
  │   │
  │   └─→ NO: Apply penalty
  │       │
  │       └─→ hybrid_score = base * 0.4
  │
  ▼
Sort by hybrid_score
  │
  ▼
Return Top N Recommendations
  │
  ▼
END
```

---

## 📊 Evaluation Flow

```
User Ratings (Test Set)
         │
         ▼
┌────────────────────┐
│  Run Models        │
│  - KNN             │
│  - Content-Based   │
│  - Hybrid          │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  Get Recommendations│
│  from each model   │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  Evaluation Module │
│  - Precision@K     │
│  - Recall@K        │
│  - MAP, NDCG      │
│  - Diversity       │
│  - Coverage        │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  Compare Results   │
│  - Create tables   │
│  - Generate charts │
└────────────────────┘
```

---

## 🗂️ File Structure

```
Steam ML/
│
├── KNN_model/
│   ├── Data Files
│   │   ├── final_games.csv
│   │   ├── final_reviews.csv
│   │   ├── your_games.csv
│   │   └── fav_games.csv
│   │
│   ├── Code Files
│   │   ├── UI.py
│   │   ├── UI_elements.py
│   │   ├── Button_commands.py
│   │   └── Data_handler.py
│   │
│   └── Output
│       └── rcm_games.csv
│
├── CB_model/
│   ├── Data Files
│   │   ├── CB_games.csv
│   │   └── cb_user_ratings.json
│   │
│   ├── Code Files
│   │   ├── UI_ContentBased.py
│   │   ├── ContentBased_model.py
│   │   ├── ContentBased_commands.py
│   │   └── ContentBased_data_handler.py
│   │
│   └── Output
│       ├── cb_model.pkl
│       └── cb_recommendations.csv
│
└── Hybrid_model/
    ├── Code Files
    │   ├── run_hybrid.py
    │   ├── Hybrid_recommendations_reader.py
    │   └── Hybrid_results_viewer.py
    │
    └── Output
        ├── hybrid_ranking.csv
        └── evaluation_results.csv
```

---

## 🔄 Process Flow

### Complete Recommendation Process

```
1. User Rates Games
   │
   ├─→ KNN: your_games.csv
   └─→ CB: cb_user_ratings.json
   │
   ▼
2. Train/Get Recommendations
   │
   ├─→ KNN: Find similar users → Predict
   └─→ CB: Create profile → Find similar games
   │
   ▼
3. Generate Recommendations
   │
   ├─→ KNN: rcm_games.csv
   └─→ CB: cb_recommendations.csv
   │
   ▼
4. Hybrid Ranking
   │
   └─→ Combine both → hybrid_ranking.csv
   │
   ▼
5. Display Results
   │
   └─→ UI Table with rankings
```

---

**Ngày tạo**: 2024  
**Version**: 1.0

