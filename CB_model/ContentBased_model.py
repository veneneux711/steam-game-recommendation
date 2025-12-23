"""
Content-Based Filtering Model cho Game Recommendation (Advanced Version)
Features:
1. TF-IDF + TruncatedSVD (LSA) để hiểu ngữ nghĩa (Semantic Matching).
2. Positional Weighting: Ưu tiên Genre và Top Tags.
3. Shovelware Filter: Lọc game rác dựa trên giá tiền và review.
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
        self.svd = None  # Thêm thành phần giảm chiều dữ liệu
        self.game_features = None
        self.game_indices = None
        self.is_trained = False
    
    def prepare_content_features(self, df):
        """
        Chuẩn bị features với quy tắc "Tag đầu quan trọng hơn" (Positional Weighting).
        Mô phỏng cách Steam xếp hạng Tag theo số lượng vote.
        """
        content_features = []
        
        for idx, row in df.iterrows():
            # 1. Lấy dữ liệu thô và tách thành list
            genres_str = str(row.get('Genres', ''))
            tags_str = str(row.get('Tags', ''))
            
            genres_list = [x.strip() for x in genres_str.split(',') if x.strip()]
            tags_list = [x.strip() for x in tags_str.split(',') if x.strip()]
            
            weighted_words = []
            
            # --- CẤU HÌNH TRỌNG SỐ ---
            
            # 1. GENRES (Thể loại chính): Luôn quan trọng nhất -> Lặp lại 4 lần
            for g in genres_list:
                weighted_words.extend([g] * 4)
            
            # 2. TAGS (Nhãn phụ): Quan trọng theo thứ tự
            for i, tag in enumerate(tags_list):
                if i < 3:
                    # Top 3 Tags đầu tiên (Core Tags): Quan trọng ngang ngửa Genre
                    weighted_words.extend([tag] * 3)
                elif i < 10:
                    # Top 4-10 (Support Tags): Quan trọng vừa phải
                    weighted_words.extend([tag] * 2)
                else:
                    # Các tags còn lại: Chỉ để bổ trợ
                    weighted_words.append(tag)
            
            # 3. Nối lại thành chuỗi văn bản
            final_content = " ".join(weighted_words)
            content_features.append(final_content)
        
        return content_features
    
    def train(self, df):
        """
        Train Model sử dụng TF-IDF kết hợp SVD (LSA)
        """
        try:
            print("Preparing content features (Weighted)...")
            content_features = self.prepare_content_features(df)
            
            # 1. TF-IDF: Chuyển văn bản thành số
            print("Vectorizing content features...")
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                min_df=2, 
                # Loại bỏ từ xuất hiện ở quá 60% game (từ quá phổ biến như "Singleplayer")
                max_df=0.6  
            )
            tfidf_matrix = self.vectorizer.fit_transform(content_features)
            
            # 2. SVD: Giảm chiều dữ liệu để bắt "ngữ nghĩa" (Semantic)
            # Giúp tìm ra các game "giống nhau về bản chất" dù tag không khớp 100%
            print("Applying SVD (Latent Semantic Analysis)...")
            self.svd = TruncatedSVD(n_components=100, random_state=42)
            
            # Ma trận đặc (Dense Matrix) chứa ý nghĩa tiềm ẩn của game
            self.game_features = self.svd.fit_transform(tfidf_matrix)
            
            self.game_indices = df.index.tolist()
            self.is_trained = True
            
            print(f"Model trained successfully! Features shape: {self.game_features.shape}")
            print(f"Explained Variance: {self.svd.explained_variance_ratio_.sum():.2f}")
            
            return True
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_similar_games(self, rated_games_dict, top_n=20, df_games=None):
        """
        Tìm games tương tự dựa trên vector SVD
        """
        if not self.is_trained: return pd.DataFrame()
        
        try:
            feature_indices = []
            weights = []
            
            # Tạo profile trọng số dựa trên rating
            for app_id, rating in rated_games_dict.items():
                if app_id in self.game_indices:
                    idx = self.game_indices.index(app_id)
                    feature_indices.append(idx)
                    # Rating càng cao, đóng góp vào vector sở thích càng lớn
                    # 5 sao = 3 điểm, 4 sao = 2 điểm, 3 sao = 1 điểm
                    weights.append(max(1, rating - 2))
            
            if not feature_indices: return pd.DataFrame()
            
            # Tính User Profile Vector (Weighted Average)
            selected_features = self.game_features[feature_indices]
            weights = np.array(weights).reshape(-1, 1)
            
            # Công thức trung bình cộng có trọng số
            user_profile = np.sum(selected_features * weights, axis=0) / np.sum(weights)
            user_profile = user_profile.reshape(1, -1)
            
            # Tính Cosine Similarity trên không gian SVD
            similarities = cosine_similarity(user_profile, self.game_features).flatten()
            
            # Loại trừ game đã rate
            for idx in feature_indices:
                similarities[idx] = -1
            
            # Lấy kết quả (Quét sâu hơn vì SVD cho kết quả rộng hơn)
            scan_limit = top_n * 50 
            top_indices = np.argsort(similarities)[::-1][:scan_limit]
            
            results = []
            seen_names = set()
            
            for idx in top_indices:
                score = similarities[idx]
                
                # Với SVD, điểm số sẽ "mềm" hơn. 0.4 là mức khá cao.
                if score > 0.3: 
                    app_id = self.game_indices[idx]
                    
                    # Lọc trùng tên
                    game_name = "Unknown"
                    if df_games is not None:
                        row = df_games[df_games.index == app_id]
                        if not row.empty:
                            game_name = row.iloc[0].get('Name', 'Unknown')
                    
                    if game_name in seen_names: continue
                    seen_names.add(game_name)
                    
                    results.append({
                        'AppID': app_id, 
                        'Similarity': float(score)
                    })
                    
                    if len(results) >= top_n * 3: break
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Error getting similar games: {str(e)}")
            return pd.DataFrame()
    
    def get_recommendations(self, df, rated_games, user_preferences=None, top_n=20):
        """
        Lấy recommendations với bộ lọc Shovelware (Game rác)
        """
        if not self.is_trained: return pd.DataFrame()

        liked_games_dict = {aid: r for aid, r in rated_games.items() if r >= 3}
        if not liked_games_dict: return pd.DataFrame()

        # Lấy tên game đã chơi để loại trừ
        played_names = set()
        for app_id in rated_games.keys():
            row = df[df.index == app_id]
            if not row.empty:
                played_names.add(row.iloc[0].get('Name', 'Unknown'))

        # Tìm game tương tự (Lấy dư ra nhiều để lọc)
        similar_df = self.get_similar_games(liked_games_dict, top_n=top_n * 5, df_games=df)
        if similar_df.empty: return pd.DataFrame()

        recommendations = []
        
        # --- CẤU HÌNH BỘ LỌC SHOVELWARE ---
        SAFE_PRICE_THRESHOLD = 9.99   # Dưới mức này mà ít review là nghi ngờ
        MIN_TRUSTED_REVIEWS = 100     # Ngưỡng tin cậy review
        
        for _, row in similar_df.iterrows():
            app_id = int(row['AppID'])
            similarity = row['Similarity']
            
            game_row = df[df.index == app_id]
            if game_row.empty: continue
            data = game_row.iloc[0]
            name = data.get('Name', 'Unknown')
            
            if name in played_names: continue
            
            # Lấy thông tin
            pos = float(data.get('Positive', 0))
            neg = float(data.get('Negative', 0))
            total = pos + neg
            price = data.get('Price', 0)
            
            # --- TÍNH ĐIỂM ---
            # Popularity Score (Log scale)
            pop_score = np.log10(total + 1) / 10.0
            
            # Base Score: 85% Similarity + 15% Popularity
            final_score = (similarity * 0.85) + (pop_score * 0.15)
            
            # --- BỘ LỌC CHẤT LƯỢNG (Dựa trên Price nếu Review thấp/lỗi) ---
            if total < MIN_TRUSTED_REVIEWS:
                # Nếu game rẻ bèo (< 10$) hoặc Free -> Nghi ngờ rác -> Phạt nặng
                if price < SAFE_PRICE_THRESHOLD:
                    # Trừ khi nó siêu giống (SVD Similarity > 0.8)
                    if similarity < 0.8:
                        final_score *= 0.25 
                    else:
                        final_score *= 0.6
                else:
                    # Game đắt tiền (> 10$) nhưng ít review -> Phạt nhẹ
                    final_score *= 0.9
            
            # --- PREFERENCES USER ---
            if user_preferences:
                max_price = user_preferences.get('max_price', float('inf'))
                if price > max_price:
                    final_score *= 0.5
            
            recommendations.append({
                'AppID': app_id,
                'Name': name,
                'Score': final_score,
                'Similarity': similarity,
                'Price': price
            })
            
            if len(recommendations) >= top_n:
                break
            
        # Sort kết quả
        df_result = pd.DataFrame(recommendations)
        if not df_result.empty:
            df_result = df_result.sort_values('Score', ascending=False).head(top_n)
            
        return df_result
    
    def save_model(self, file_path):
        """Lưu model bao gồm cả SVD"""
        try:
            model_data = {
                'vectorizer': self.vectorizer,
                'svd': self.svd,  # Lưu SVD
                'game_features': self.game_features,
                'game_indices': self.game_indices,
                'is_trained': self.is_trained
            }
            with open(file_path, 'wb') as f:
                pickle.dump(model_data, f)
            print(f"Model saved to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, file_path):
        """Load model bao gồm cả SVD"""
        try:
            with open(file_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.svd = model_data.get('svd', None) # Load SVD
            self.game_features = model_data['game_features']
            self.game_indices = model_data['game_indices']
            self.is_trained = model_data['is_trained']
            
            print(f"Model loaded from {file_path}")
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False