"""
Decision Tree Model cho Game Recommendation
Sử dụng scikit-learn DecisionTreeClassifier
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os

class DecisionTreeGameRecommender:
    """
    Class để train và sử dụng Decision Tree cho game recommendation
    """
    
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.feature_columns = []
        self.is_trained = False
    
    def prepare_features(self, df):
        """
        Chuẩn bị features từ DataFrame
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame chứa game data
        
        Returns:
        --------
        pd.DataFrame : DataFrame với features đã được xử lý
        """
        features_df = df.copy()
        
        # Chọn các features quan trọng
        feature_cols = [
            'Price', 'Positive', 'Negative', 'Metacritic score',
            'Average playtime forever', 'Required age'
        ]
        
        # Chỉ lấy các cột có sẵn
        available_cols = [col for col in feature_cols if col in features_df.columns]
        features_df = features_df[available_cols]
        
        # Xử lý missing values
        features_df = features_df.fillna(0)
        
        # Xử lý các giá trị không phải số
        for col in features_df.columns:
            if features_df[col].dtype == 'object':
                # Thử convert sang số, nếu không được thì bỏ qua
                try:
                    features_df[col] = pd.to_numeric(features_df[col], errors='coerce')
                    features_df[col] = features_df[col].fillna(0)
                except:
                    features_df[col] = 0
        
        return features_df
    
    def train(self, df, target_column='user_rating', test_size=0.2):
        """
        Train Decision Tree model
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame chứa training data
        target_column : str
            Tên cột target (user rating)
        test_size : float
            Tỷ lệ test set
        """
        try:
            # Chuẩn bị features
            X = self.prepare_features(df)
            self.feature_columns = X.columns.tolist()
            
            # Lấy target
            if target_column in df.columns:
                y = df[target_column]
            else:
                # Nếu không có target, tạo dummy target
                print("Warning: No target column found. Creating dummy target.")
                y = pd.Series([1] * len(df))
            
            # Encode target nếu cần
            if y.dtype == 'object':
                le = LabelEncoder()
                y = le.fit_transform(y)
                self.label_encoders['target'] = le
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            # Train model
            self.model = DecisionTreeClassifier(
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            self.model.fit(X_train, y_train)
            
            # Tính accuracy
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            self.is_trained = True
            
            print(f"Model trained successfully!")
            print(f"Train accuracy: {train_score:.4f}")
            print(f"Test accuracy: {test_score:.4f}")
            
            return train_score, test_score
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return None, None
    
    def predict(self, game_data):
        """
        Dự đoán rating cho một game
        
        Parameters:
        -----------
        game_data : pd.DataFrame hoặc dict
            Dữ liệu game cần dự đoán
        
        Returns:
        --------
        int hoặc str : Predicted rating
        """
        if not self.is_trained:
            print("Model chưa được train!")
            return None
        
        try:
            # Convert dict thành DataFrame nếu cần
            if isinstance(game_data, dict):
                game_data = pd.DataFrame([game_data])
            
            # Chuẩn bị features
            X = self.prepare_features(game_data)
            
            # Đảm bảo có đủ columns
            for col in self.feature_columns:
                if col not in X.columns:
                    X[col] = 0
            
            X = X[self.feature_columns]
            
            # Predict
            prediction = self.model.predict(X)
            
            # Decode nếu cần
            if 'target' in self.label_encoders:
                prediction = self.label_encoders['target'].inverse_transform(prediction)
            
            return prediction[0] if len(prediction) == 1 else prediction
            
        except Exception as e:
            print(f"Error predicting: {str(e)}")
            return None
    
    def get_recommendations(self, df, user_preferences, top_n=10):
        """
        Lấy recommendations dựa trên user preferences
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame chứa tất cả games
        user_preferences : dict
            Dictionary chứa preferences của user
        top_n : int
            Số lượng recommendations cần lấy
        
        Returns:
        --------
        pd.DataFrame : DataFrame chứa top N recommendations
        """
        if not self.is_trained:
            print("Model chưa được train!")
            return pd.DataFrame()
        
        try:
            # Tính scores cho mỗi game
            scores = []
            for idx, row in df.iterrows():
                # Chuẩn bị game data
                game_data = row.to_dict()
                
                # Predict
                prediction = self.predict(game_data)
                
                # Tính score dựa trên prediction và preferences
                score = self._calculate_score(row, prediction, user_preferences)
                
                scores.append({
                    'AppID': row.get('AppID', idx),
                    'Name': row.get('Name', 'Unknown'),
                    'Score': score,
                    'Prediction': prediction
                })
            
            # Tạo DataFrame và sort
            recommendations_df = pd.DataFrame(scores)
            recommendations_df = recommendations_df.sort_values('Score', ascending=False)
            
            # Lấy top N
            top_recommendations = recommendations_df.head(top_n)
            
            return top_recommendations
            
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_score(self, game_row, prediction, user_preferences):
        """
        Tính score cho một game dựa trên prediction và preferences
        """
        score = float(prediction) if isinstance(prediction, (int, float, np.number)) else 0.5
        
        # Thêm bonus dựa trên preferences
        if 'max_price' in user_preferences:
            price = game_row.get('Price', 0)
            if isinstance(price, str):
                try:
                    price = float(price.replace('$', '').replace(',', ''))
                except:
                    price = 0
            if price <= user_preferences.get('max_price', float('inf')):
                score += 0.1
        
        if 'min_positive_ratio' in user_preferences:
            positive = game_row.get('Positive', 0)
            negative = game_row.get('Negative', 0)
            total = positive + negative
            if total > 0:
                ratio = positive / total
                if ratio >= user_preferences.get('min_positive_ratio', 0):
                    score += 0.1
        
        return score
    
    def save_model(self, file_path):
        """
        Lưu model vào file
        """
        try:
            model_data = {
                'model': self.model,
                'label_encoders': self.label_encoders,
                'feature_columns': self.feature_columns,
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
            
            self.model = model_data['model']
            self.label_encoders = model_data['label_encoders']
            self.feature_columns = model_data['feature_columns']
            self.is_trained = model_data['is_trained']
            
            print(f"Model loaded from {file_path}")
            return True
            
        except FileNotFoundError:
            print(f"Model file not found: {file_path}")
            return False
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False

