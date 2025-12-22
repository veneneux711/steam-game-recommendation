"""
Script để tạo fake user "ma" và chạy test evaluation
Tạo user với nhiều ratings để có test set lớn hơn
"""

import os
import json
import pandas as pd
import numpy as np
import random
import shutil

def create_test_user_knn(knn_dir, num_ratings=50):
    """Tạo test user cho KNN model"""
    
    # Load games
    games_file = os.path.join(knn_dir, "final_games.csv")
    if not os.path.exists(games_file):
        print(f"Error: {games_file} not found")
        return False
    
    df_games = pd.read_csv(games_file)
    
    # Chọn random games
    sample_games = df_games.sample(n=min(num_ratings, len(df_games)))
    
    # Tạo ratings với distribution:
    # - Like (1): 40%
    # - Interested (0.5): 20%
    # - Neutral (-0.5): 20%
    # - Dislike (-1): 20%
    
    ratings = []
    for _, row in sample_games.iterrows():
        rand = random.random()
        if rand < 0.4:
            review = 1.0  # Like
        elif rand < 0.6:
            review = 0.5  # Interested
        elif rand < 0.8:
            review = -0.5  # Neutral
        else:
            review = -1.0  # Dislike
        
        ratings.append({
            'gameID': int(row['app_id']),
            'gameName': str(row['title']),
            'review': review
        })
    
    # Backup original file
    your_games_file = os.path.join(knn_dir, "your_games.csv")
    if os.path.exists(your_games_file):
        backup_file = os.path.join(knn_dir, "your_games_backup.csv")
        shutil.copy2(your_games_file, backup_file)
        print(f"✅ Backed up original to: {backup_file}")
    
    # Save new ratings
    df_ratings = pd.DataFrame(ratings)
    df_ratings.to_csv(your_games_file, index=False)
    print(f"✅ Created test user with {len(ratings)} ratings in {your_games_file}")
    
    # Create favorite games (games with review >= 0.5)
    fav_games = df_ratings[df_ratings['review'] >= 0.5][['gameID', 'gameName']].copy()
    fav_games_file = os.path.join(knn_dir, "fav_games.csv")
    if os.path.exists(fav_games_file):
        backup_file = os.path.join(knn_dir, "fav_games_backup.csv")
        shutil.copy2(fav_games_file, backup_file)
    
    fav_games.to_csv(fav_games_file, index=False)
    print(f"✅ Created {len(fav_games)} favorite games in {fav_games_file}")
    
    return True


def create_test_user_cb(cb_dir, num_ratings=50):
    """Tạo test user cho Content-Based model"""
    
    # Load games
    games_file = os.path.join(cb_dir, "CB_games.csv")
    if not os.path.exists(games_file):
        print(f"Error: {games_file} not found")
        return False
    
    # Load sample (để tránh memory issue)
    df_games = pd.read_csv(games_file, nrows=50000)
    
    # Filter out rows with invalid AppID (must be numeric and finite)
    valid_games = []
    for _, row in df_games.iterrows():
        try:
            app_id = row.get('AppID', None)
            if pd.isna(app_id):
                continue
            
            # Convert to float first to check for infinity
            app_id_float = float(str(app_id))
            
            # Check for infinity or NaN
            if not pd.notna(app_id_float) or not np.isfinite(app_id_float):
                continue
            
            # Try to convert to int to validate
            app_id_int = int(app_id_float)
            
            # Check if it's a reasonable AppID (positive integer)
            if app_id_int <= 0:
                continue
            
            valid_games.append(row)
        except (ValueError, TypeError, OverflowError):
            continue
    
    if len(valid_games) == 0:
        print("Error: No valid games found in CB_games.csv")
        return False
    
    df_valid = pd.DataFrame(valid_games)
    
    # Chọn random games từ valid games
    sample_games = df_valid.sample(n=min(num_ratings, len(df_valid)))
    
    # Tạo ratings với distribution:
    # - Like (5): 30%
    # - Good (4): 25%
    # - Neutral (3): 20%
    # - Bad (2): 15%
    # - Dislike (1): 10%
    
    ratings = []
    for _, row in sample_games.iterrows():
        # Kiểm tra và convert AppID
        try:
            app_id = row.get('AppID', None)
            if pd.isna(app_id):
                continue
            
            # Try to convert to int
            try:
                app_id_float = float(str(app_id))
                # Check for infinity or NaN
                if not pd.notna(app_id_float) or not np.isfinite(app_id_float):
                    continue
                app_id = int(app_id_float)
                # Check if it's a reasonable AppID (positive integer)
                if app_id <= 0:
                    continue
            except (ValueError, TypeError, OverflowError):
                # Skip if AppID is not a number
                continue
            
            # Kiểm tra Name
            name = row.get('Name', 'Unknown')
            if pd.isna(name):
                name = 'Unknown'
            
            rand = random.random()
            if rand < 0.3:
                rating = 5  # Like
            elif rand < 0.55:
                rating = 4  # Good
            elif rand < 0.75:
                rating = 3  # Neutral
            elif rand < 0.9:
                rating = 2  # Bad
            else:
                rating = 1  # Dislike
            
            ratings.append({
                'AppID': app_id,
                'Name': str(name),
                'user_rating': rating
            })
        except Exception as e:
            # Skip row if there's any error
            continue
    
    # Backup original file
    ratings_file = os.path.join(cb_dir, "cb_user_ratings.json")
    if os.path.exists(ratings_file):
        backup_file = os.path.join(cb_dir, "cb_user_ratings_backup.json")
        shutil.copy2(ratings_file, backup_file)
        print(f"✅ Backed up original to: {backup_file}")
    
    # Save new ratings
    with open(ratings_file, 'w', encoding='utf-8') as f:
        json.dump(ratings, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created test user with {len(ratings)} ratings in {ratings_file}")
    
    return True


def create_test_user(num_ratings=50):
    """Tạo test user cho cả 2 models"""
    
    print("="*80)
    print("CREATING TEST USER 'MA'")
    print("="*80)
    print()
    
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    knn_dir = os.path.join(current_dir, "KNN_model")
    cb_dir = os.path.join(current_dir, "CB_model")
    
    print(f"Number of ratings per model: {num_ratings}")
    print()
    
    # Create KNN test user
    print("1. Creating KNN test user...")
    success_knn = create_test_user_knn(knn_dir, num_ratings)
    print()
    
    # Create CB test user
    print("2. Creating Content-Based test user...")
    success_cb = create_test_user_cb(cb_dir, num_ratings)
    print()
    
    if success_knn and success_cb:
        print("="*80)
        print("✅ TEST USER CREATED SUCCESSFULLY!")
        print("="*80)
        print()
        print("Next steps:")
        print("1. Run KNN model: cd KNN_model && python UI.py → Get Recommendations")
        print("2. Run CB model: cd CB_model && python UI_ContentBased.py → Get Recommendations")
        print("3. Run Hybrid: python run_hybrid.py")
        print("4. Run Evaluation: python run_evaluation.py")
        print()
        print("Note: Original files have been backed up with '_backup' suffix")
    else:
        print("❌ Error creating test user. Please check the errors above.")
    
    return success_knn and success_cb


if __name__ == "__main__":
    import sys
    
    # Get number of ratings from command line or use default
    num_ratings = 50
    if len(sys.argv) > 1:
        try:
            num_ratings = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid number '{sys.argv[1]}', using default 50")
    
    create_test_user(num_ratings)

