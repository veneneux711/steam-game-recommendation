"""
Content-Based Filtering Model cho Game Recommendation
Sử dụng Genres và Tags để tìm games tương tự
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os


class ContentBasedRecommender:
    """
    Content-Based Filtering sử dụng Genres và Tags
    """
    
    def __init__(self):
        self.vectorizer = None
        self.game_features = None
        self.game_indices = None
        self.is_trained = False
    
    def prepare_content_features(self, df):
        """
        Chuẩn bị content features từ Genres và Tags
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame chứa game data với columns 'Genres' và 'Tags'
        
        Returns:
        --------
        list : List of strings, mỗi string là genres + tags của một game
        """
        content_features = []
        
        for idx, row in df.iterrows():
            genres = str(row.get('Genres', ''))
            tags = str(row.get('Tags', ''))
            
            # Kết hợp genres và tags
            content = f"{genres} {tags}"
            content_features.append(content)
        
        return content_features
    
    def train(self, df):
        """
        Train Content-Based model
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame chứa game data
        """
        try:
            print("Preparing content features...")
            content_features = self.prepare_content_features(df)
            
            # Sử dụng TF-IDF để vectorize genres/tags
            print("Vectorizing content features...")
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )
            
            self.game_features = self.vectorizer.fit_transform(content_features)
            
            # Lưu mapping index -> AppID
            self.game_indices = df.index.tolist()
            
            self.is_trained = True
            print(f"Model trained successfully! Processed {len(df)} games.")
            print(f"Feature matrix shape: {self.game_features.shape}")
            
            return True
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_similar_games(self, game_indices, top_n=10):
        """
        Tìm games tương tự dựa trên content similarity
        
        Parameters:
        -----------
        game_indices : list
            List các index (AppID) của games đã rate
        top_n : int
            Số lượng recommendations cần lấy
        
        Returns:
        --------
        pd.DataFrame : DataFrame chứa similar games với similarity scores
        """
        if not self.is_trained:
            print("Model chưa được train!")
            return pd.DataFrame()
        
        try:
            # Tìm indices trong game_indices mapping
            feature_indices = []
            for app_id in game_indices:
                if app_id in self.game_indices:
                    idx = self.game_indices.index(app_id)
                    feature_indices.append(idx)
            
            if not feature_indices:
                print("No matching games found in trained data!")
                return pd.DataFrame()
            
            # Tính average feature vector của games đã rate
            # game_features là sparse matrix, cần convert sang dense để tính mean
            selected_features = self.game_features[feature_indices]
            
            # Convert sparse matrix sang dense array để tính mean
            if hasattr(selected_features, 'toarray'):
                selected_features_dense = selected_features.toarray()
            else:
                selected_features_dense = np.asarray(selected_features)
            
            # Tính mean và reshape thành (1, n_features)
            user_profile = selected_features_dense.mean(axis=0).reshape(1, -1)
            
            # Tính cosine similarity với tất cả games (có thể dùng sparse matrix trực tiếp)
            # cosine_similarity hỗ trợ sparse matrix
            similarities = cosine_similarity(user_profile, self.game_features).flatten()
            
            # Loại trừ games đã rate
            for idx in feature_indices:
                similarities[idx] = -1  # Set similarity thấp để loại trừ
            
            # Lấy top N games
            top_indices = np.argsort(similarities)[::-1][:top_n]
            
            # Tạo results
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Chỉ lấy games có similarity > 0
                    app_id = self.game_indices[idx]
                    results.append({
                        'AppID': app_id,
                        'Similarity': float(similarities[idx])
                    })
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Error getting similar games: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_recommendations(self, df, rated_games, user_preferences=None, top_n=20):
        """
        Lấy recommendations dựa trên rated games và preferences
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame chứa tất cả games
        rated_games : dict
            Dictionary {app_id: rating} của games đã rate
        user_preferences : dict
            Dictionary chứa preferences (max_price, min_positive_ratio)
        top_n : int
            Số lượng recommendations
        
        Returns:
        --------
        pd.DataFrame : DataFrame chứa recommendations với scores
        """
        if not self.is_trained:
            print("Model chưa được train!")
            return pd.DataFrame()
        
        try:
            # Lấy AppIDs của games đã rate (chỉ lấy games có rating >= 3)
            liked_games = [app_id for app_id, rating in rated_games.items() if rating >= 3]
            
            if not liked_games:
                print("No liked games found!")
                return pd.DataFrame()
            
            # Tìm similar games
            similar_df = self.get_similar_games(liked_games, top_n=top_n * 3)
            
            if similar_df.empty:
                return pd.DataFrame()
            
            # Merge với game data để lấy thông tin chi tiết
            recommendations = []
            for _, row in similar_df.iterrows():
                app_id = int(row['AppID'])
                similarity = row['Similarity']
                
                # Tìm game trong DataFrame
                game_row = df[df.index == app_id]
                if game_row.empty:
                    continue
                
                game_data = game_row.iloc[0]
                
                # Tính final score
                score = similarity * 10  # Scale similarity to 0-10
                
                # Apply preferences
                if user_preferences:
                    # Price filter
                    price = game_data.get('Price', 0)
                    if isinstance(price, str):
                        try:
                            price = float(price.replace('$', '').replace(',', ''))
                        except:
                            price = 0
                    
                    max_price = user_preferences.get('max_price', float('inf'))
                    if price > max_price:
                        score *= 0.5  # Penalty cho games đắt
                    elif price == 0:
                        score += 0.5  # Bonus cho free games
                    
                    # Positive ratio filter
                    positive = game_data.get('Positive', 0)
                    negative = game_data.get('Negative', 0)
                    total = positive + negative
                    if total > 0:
                        ratio = positive / total
                        min_ratio = user_preferences.get('min_positive_ratio', 0)
                        if ratio < min_ratio:
                            score *= 0.7  # Penalty cho games có tỷ lệ thấp
                        elif ratio >= 0.8:
                            score += 0.5  # Bonus cho games có tỷ lệ cao
                
                recommendations.append({
                    'AppID': app_id,
                    'Name': game_data.get('AppID', 'Unknown'),  # AppID column chứa tên game
                    'Score': score,
                    'Similarity': similarity,
                    'Price': price if 'price' in locals() else game_data.get('Price', 0),
                    'Positive': positive,
                    'Negative': negative
                })
            
            # Sort và lấy top N
            recommendations_df = pd.DataFrame(recommendations)
            recommendations_df = recommendations_df.sort_values('Score', ascending=False)
            recommendations_df = recommendations_df.head(top_n)
            
            return recommendations_df
            
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def save_model(self, file_path):
        """
        Lưu model vào file
        """
        try:
            model_data = {
                'vectorizer': self.vectorizer,
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
        """
        Load model từ file
        """
        try:
            with open(file_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.game_features = model_data['game_features']
            self.game_indices = model_data['game_indices']
            self.is_trained = model_data['is_trained']
            
            print(f"Model loaded from {file_path}")
            return True
            
        except FileNotFoundError:
            print(f"Model file not found: {file_path}")
            return False
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False

