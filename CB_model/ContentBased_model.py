"""
Content-Based Filtering Model (TF-IDF + SVD)
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import pickle
import os

class ContentBasedRecommender:
    def __init__(self):
        self.vectorizer = None
        self.svd = None 
        self.game_features = None
        self.game_indices = None
        self.is_trained = False
    
    def prepare_content_features(self, df):
        content_features = []
        for idx, row in df.iterrows():
            genres = str(row.get('Genres', '')).replace(',', ' ')
            tags = str(row.get('Tags', '')).replace(',', ' ')
            
            # Trọng số: Genres quan trọng gấp 4 lần
            weighted_content = (genres + " ") * 4 + tags
            content_features.append(weighted_content)
        return content_features
    
    def train(self, df):
        try:
            print("Preparing features...")
            features = self.prepare_content_features(df)
            
            print("Vectorizing (TF-IDF)...")
            self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', min_df=2, max_df=0.7)
            tfidf_matrix = self.vectorizer.fit_transform(features)
            
            print("Reducing dimensions (SVD)...")
            # Giảm xuống 100 chiều để hiểu ngữ nghĩa tốt hơn
            self.svd = TruncatedSVD(n_components=100, random_state=42)
            self.game_features = self.svd.fit_transform(tfidf_matrix)
            
            self.game_indices = df.index.tolist()
            self.is_trained = True
            print(f"Training complete. Matrix shape: {self.game_features.shape}")
            return True
        except Exception as e:
            print(f"Training failed: {e}")
            return False
    
    def get_recommendations(self, df, rated_games, user_preferences=None, top_n=20):
        if not self.is_trained: return pd.DataFrame()

        # Lấy game user thích (Rating >= 3)
        liked_games = {aid: r for aid, r in rated_games.items() if r >= 3}
        if not liked_games: return pd.DataFrame()

        # Tìm index và trọng số
        indices = []
        weights = []
        played_names = set()
        
        for app_id, rating in liked_games.items():
            if app_id in self.game_indices:
                idx = self.game_indices.index(app_id)
                indices.append(idx)
                # Rating 5->3 điểm, 4->2 điểm, 3->1 điểm
                weights.append(max(1, rating - 2))
                
                # Lưu tên để lọc trùng
                row = df[df.index == app_id]
                if not row.empty:
                    played_names.add(row.iloc[0].get('Name', ''))

        if not indices: return pd.DataFrame()

        # Tính User Profile (Trung bình cộng có trọng số)
        user_profile = np.average(self.game_features[indices], axis=0, weights=weights).reshape(1, -1)
        
        # Tính độ tương đồng (Cosine Similarity)
        # Vì game_features đã qua SVD (dense matrix) nên tính toán rất nhanh
        similarities = cosine_similarity(user_profile, self.game_features).flatten()
        
        # Lọc kết quả
        results = []
        # Quét top N * 10 để lọc sau
        top_indices = np.argsort(similarities)[::-1][:top_n*10]
        
        for idx in top_indices:
            app_id = self.game_indices[idx]
            score = similarities[idx]
            
            # Bỏ qua game đã chơi
            row = df[df.index == app_id]
            if row.empty: continue
            
            name = row.iloc[0].get('Name', 'Unknown')
            if name in played_names: continue
            if score < 0.1: continue # Bỏ qua nếu không giống lắm

            # --- Shovelware Filter (Lọc rác) ---
            pos = float(row.iloc[0].get('Positive', 0))
            neg = float(row.iloc[0].get('Negative', 0))
            price = float(row.iloc[0].get('Price', 0))
            total_reviews = pos + neg

            # Logic: Game ít review (<100) VÀ giá rẻ (<$10) -> Phạt nặng
            final_score = score
            if total_reviews < 100:
                if price < 9.99:
                    final_score *= 0.25 # Phạt 75%
                else:
                    final_score *= 0.9  # Phạt nhẹ

            # Cộng điểm Popularity (Log scale)
            pop_score = np.log10(total_reviews + 1) / 10.0
            final_score = (final_score * 0.85) + (pop_score * 0.15)
            
            # Lọc theo Preference (Max Price)
            if user_preferences:
                max_p = user_preferences.get('max_price', 1000)
                if price > max_p: final_score *= 0.5

            results.append({
                'AppID': app_id,
                'Name': name,
                'Score': final_score,
                'Similarity': score,
                'Price': price
            })

            if len(results) >= top_n: break
        
        return pd.DataFrame(results)

    def save_model(self, path):
        try:
            data = {
                'vec': self.vectorizer, 'svd': self.svd, 
                'feats': self.game_features, 'inds': self.game_indices, 
                'trained': self.is_trained
            }
            with open(path, 'wb') as f: pickle.dump(data, f)
            print(f"Model saved to {path}")
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False

    def load_model(self, path):
        try:
            with open(path, 'rb') as f: data = pickle.load(f)
            self.vectorizer = data['vec']
            self.svd = data['svd']
            self.game_features = data['feats']
            self.game_indices = data['inds']
            self.is_trained = data['trained']
            print(f"Model loaded form {path}")
            return True
        except Exception as e:
            print(f"Load failed: {e}")
            return False