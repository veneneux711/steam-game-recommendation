"""
Hybrid Recommendations Reader
Đọc recommendations từ cả KNN và Content-Based models và tính toán ranking
"""

import pandas as pd
import os
import sys

# Add paths để import từ KNN và CB models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'KNN_model'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'CB_model'))

try:
    from Data_handler import load_data as load_knn_data
except ImportError as e:
    print(f"Warning: Could not import KNN handler: {str(e)}")
    load_knn_data = None


def read_knn_recommendations(knn_dir, top_n=30):
    """
    Đọc KNN recommendations từ file rcm_games.csv
    
    Parameters:
    -----------
    knn_dir : str
        Đường dẫn đến KNN_model folder
    top_n : int
        Số lượng top recommendations (default 30)
    
    Returns:
    --------
    pd.DataFrame : DataFrame với columns ['app_id', 'title', 'knn_score', 'knn_rank']
    """
    try:
        # Tìm file recommendations
        recommendations_path = os.path.join(knn_dir, "rcm_games.csv")
        if not os.path.exists(recommendations_path):
            recommendations_path = os.path.join(knn_dir, "recommendations.csv")
        
        if not os.path.exists(recommendations_path):
            print(f"KNN recommendations file not found: {recommendations_path}")
            return pd.DataFrame()
        
        # Đọc recommendations
        knn_df = pd.read_csv(recommendations_path)
        
        if knn_df.empty:
            print("KNN recommendations file is empty")
            return pd.DataFrame()
        
        # Lấy top N
        knn_df = knn_df.head(top_n).copy()
        
        # Map title sang app_id từ final_games.csv
        final_games_path = os.path.join(knn_dir, "final_games.csv")
        if os.path.exists(final_games_path):
            final_games = pd.read_csv(final_games_path)
            title_to_appid = dict(zip(final_games['title'], final_games['app_id']))
        else:
            # Fallback: dùng games.csv
            games_path = os.path.join(knn_dir, "games.csv")
            if os.path.exists(games_path):
                games_df = pd.read_csv(games_path)
                title_to_appid = dict(zip(games_df['title'], games_df['app_id']))
            else:
                title_to_appid = {}
        
        # Map title sang app_id
        if 'title' in knn_df.columns and title_to_appid:
            knn_df['app_id'] = knn_df['title'].map(title_to_appid)
            knn_df = knn_df.dropna(subset=['app_id'])
            knn_df['app_id'] = knn_df['app_id'].astype(int)
        elif 'app_id' in knn_df.columns:
            # Nếu đã có app_id
            pass
        else:
            print("Warning: Could not map titles to app_id for KNN")
            return pd.DataFrame()
        
        # Assign scores: top 1 = 30, top 2 = 29, ..., top 30 = 1
        knn_df['knn_score'] = range(len(knn_df), 0, -1)
        knn_df['knn_rank'] = range(1, len(knn_df) + 1)
        
        # Đảm bảo có title column
        if 'title' not in knn_df.columns:
            # Map app_id sang title
            appid_to_title = {v: k for k, v in title_to_appid.items()}
            knn_df['title'] = knn_df['app_id'].map(appid_to_title)
        
        # Chỉ giữ các columns cần thiết
        result = knn_df[['app_id', 'title', 'knn_score', 'knn_rank']].copy()
        
        print(f"Loaded {len(result)} KNN recommendations")
        return result
        
    except Exception as e:
        print(f"Error reading KNN recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def read_cb_recommendations(cb_dir, top_n=30):
    """
    Đọc Content-Based recommendations từ file cb_recommendations.csv
    
    Parameters:
    -----------
    cb_dir : str
        Đường dẫn đến CB_model folder
    top_n : int
        Số lượng top recommendations (default 30)
    
    Returns:
    --------
    pd.DataFrame : DataFrame với columns ['app_id', 'title', 'cb_score', 'cb_rank']
    """
    try:
        recommendations_path = os.path.join(cb_dir, "cb_recommendations.csv")
        
        if not os.path.exists(recommendations_path):
            print(f"CB recommendations file not found: {recommendations_path}")
            return pd.DataFrame()
        
        # Đọc recommendations
        cb_df = pd.read_csv(recommendations_path)
        
        if cb_df.empty:
            print("CB recommendations file is empty")
            return pd.DataFrame()
        
        # Lấy top N
        cb_df = cb_df.head(top_n).copy()
        
        # Trong CB, AppID column là tên game, index là AppID số
        # Cần map lại
        cb_results = []
        for idx, row in cb_df.iterrows():
            # AppID trong CB recommendations là tên game (string)
            # Cần tìm app_id số từ CB_games.csv
            game_name = row.get('Name', '') or row.get('AppID', '')
            
            # Tìm app_id từ CB_games.csv
            games_path = os.path.join(cb_dir, "CB_games.csv")
            if os.path.exists(games_path):
                games_df = pd.read_csv(games_path)
                game_row = games_df[games_df['AppID'] == game_name]
                if not game_row.empty:
                    app_id = game_row.index[0]  # Index là AppID số
                else:
                    # Nếu không tìm thấy, thử dùng index của row
                    app_id = idx
            else:
                app_id = idx
            
            cb_results.append({
                'app_id': int(app_id),
                'title': game_name,
                'cb_score': 0,  # Sẽ assign sau
                'cb_rank': 0    # Sẽ assign sau
            })
        
        cb_df_result = pd.DataFrame(cb_results)
        
        # Assign scores: top 1 = 30, top 2 = 29, ..., top 30 = 1
        cb_df_result['cb_score'] = range(len(cb_df_result), 0, -1)
        cb_df_result['cb_rank'] = range(1, len(cb_df_result) + 1)
        
        print(f"Loaded {len(cb_df_result)} Content-Based recommendations")
        return cb_df_result
        
    except Exception as e:
        print(f"Error reading CB recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def calculate_hybrid_ranking(knn_dir, cb_dir, top_n=20, knn_weight=0.5, cb_weight=0.5):
    """
    Đọc recommendations từ cả 2 models và tính toán hybrid ranking
    
    Parameters:
    -----------
    knn_dir : str
        Đường dẫn đến KNN_model folder
    cb_dir : str
        Đường dẫn đến CB_model folder
    top_n : int
        Số lượng recommendations cuối cùng
    knn_weight : float
        Trọng số cho KNN (default 0.5)
    cb_weight : float
        Trọng số cho Content-Based (default 0.5)
    
    Returns:
    --------
    pd.DataFrame : DataFrame với hybrid rankings
    """
    print("Reading recommendations from both models...")
    
    # Đọc recommendations từ cả 2 models
    knn_results = read_knn_recommendations(knn_dir, top_n=30)
    cb_results = read_cb_recommendations(cb_dir, top_n=30)
    
    print(f"KNN found {len(knn_results)} recommendations")
    print(f"Content-Based found {len(cb_results)} recommendations")
    
    # Merge results
    all_games = {}
    
    # Thêm KNN results
    if not knn_results.empty:
        for _, row in knn_results.iterrows():
            app_id = row['app_id']
            title = row['title']
            knn_score = row['knn_score']
            knn_rank = row['knn_rank']
            
            if app_id not in all_games:
                all_games[app_id] = {
                    'app_id': app_id,
                    'title': title,
                    'knn_score': 0,
                    'knn_rank': 0,
                    'cb_score': 0,
                    'cb_rank': 0
                }
            
            all_games[app_id]['knn_score'] = knn_score * knn_weight
            all_games[app_id]['knn_rank'] = knn_rank
            # Update title nếu chưa có
            if not all_games[app_id]['title'] or all_games[app_id]['title'] == '':
                all_games[app_id]['title'] = title
    
    # Thêm CB results
    if not cb_results.empty:
        for _, row in cb_results.iterrows():
            app_id = row['app_id']
            title = row['title']
            cb_score = row['cb_score']
            cb_rank = row['cb_rank']
            
            if app_id not in all_games:
                all_games[app_id] = {
                    'app_id': app_id,
                    'title': title,
                    'knn_score': 0,
                    'knn_rank': 0,
                    'cb_score': 0,
                    'cb_rank': 0
                }
            
            all_games[app_id]['cb_score'] = cb_score * cb_weight
            all_games[app_id]['cb_rank'] = cb_rank
            # Update title nếu chưa có
            if not all_games[app_id]['title'] or all_games[app_id]['title'] == '':
                all_games[app_id]['title'] = title
    
    # Tính hybrid score với improved ranking logic
    # Logic: knn cao + cb cao > knn cao + cb thấp > knn thấp + cb cao > knn thấp + cb thấp
    # Bonus cho games có cả 2 scores, penalty cho games chỉ có 1 score
    hybrid_results = []
    
    for app_id, game_data in all_games.items():
        knn_score = game_data['knn_score']  # Đã weighted (raw * 0.5)
        cb_score = game_data['cb_score']    # Đã weighted (raw * 0.5)
        
        # Base score: tổng 2 scores (đã weighted)
        base_score = knn_score + cb_score
        
        # Kiểm tra xem game có cả 2 scores không
        has_knn = knn_score > 0
        has_cb = cb_score > 0
        has_both = has_knn and has_cb
        
        # Improved ranking logic
        # Mục tiêu: knn cao + cb cao > knn cao + cb thấp > knn thấp + cb cao > knn thấp + cb thấp
        # Quan trọng: game có cả 2 scores (dù thấp) > game chỉ có 1 score cao
        if has_both:
            # Bonus cho games có cả 2 scores
            # Sử dụng multiplicative component để khuyến khích games có cả 2 scores
            # hybrid_score = base_score + sqrt(knn_score * cb_score) * multiplier
            # Đảm bảo: cả 2 đều cao → bonus lớn, 1 cao 1 thấp → bonus trung bình
            
            # Multiplicative bonus: sqrt(knn_score * cb_score)
            # Games có cả 2 scores đều cao sẽ có bonus lớn hơn nhiều
            multiplicative_bonus = (knn_score * cb_score) ** 0.5
            multiplier = 0.5  # 50% của multiplicative bonus
            
            # Thêm bonus nhỏ dựa trên min score để khuyến khích balance
            min_score = min(knn_score, cb_score)
            balance_bonus = min_score * 0.2  # 20% của min score
            
            # Minimum boost: Đảm bảo games có cả 2 scores luôn có điểm tối thiểu
            # Ngay cả khi cả 2 scores đều thấp (0.5, 0.5), vẫn có boost để vượt qua games chỉ có 1 score
            min_boost = 2.0  # Boost tối thiểu cho games có cả 2 scores
            
            hybrid_score = base_score + multiplicative_bonus * multiplier + balance_bonus + min_boost
        else:
            # Penalty cho games chỉ có 1 score (giảm 60% điểm)
            # Đảm bảo: game chỉ có 1 score cao không thể rank cao hơn game có cả 2 scores
            # Ví dụ: 
            #   - KNN=15, CB=0 → hybrid=15*0.4=6
            #   - KNN=0.5, CB=0.5 → hybrid=1 + sqrt(0.25)*0.5 + 0.1 + 2 = 1 + 0.25 + 0.1 + 2 = 3.35
            #   Game có cả 2 scores (3.35) vẫn thấp hơn game chỉ có 1 score rất cao (6)
            #   Nhưng nếu game chỉ có 1 score vừa phải: KNN=5, CB=0 → hybrid=5*0.4=2
            #   Thì game có cả 2 scores (3.35) sẽ cao hơn ✅
            penalty_factor = 0.6
            hybrid_score = base_score * (1 - penalty_factor)
        
        hybrid_results.append({
            'app_id': app_id,
            'title': game_data['title'],
            'knn_score': knn_score,
            'knn_rank': game_data['knn_rank'] if game_data['knn_rank'] > 0 else None,
            'cb_score': cb_score,
            'cb_rank': game_data['cb_rank'] if game_data['cb_rank'] > 0 else None,
            'hybrid_score': hybrid_score
        })
    
    # Tạo DataFrame và sort theo hybrid_score
    hybrid_df = pd.DataFrame(hybrid_results)
    if hybrid_df.empty:
        print("No hybrid recommendations found")
        return pd.DataFrame()
    
    hybrid_df = hybrid_df.sort_values('hybrid_score', ascending=False)
    hybrid_df = hybrid_df.head(top_n)
    
    # Reset index và thêm rank
    hybrid_df = hybrid_df.reset_index(drop=True)
    hybrid_df['rank'] = range(1, len(hybrid_df) + 1)
    
    # Reorder columns
    column_order = ['rank', 'app_id', 'title', 'hybrid_score', 'knn_score', 'knn_rank', 'cb_score', 'cb_rank']
    existing_columns = [col for col in column_order if col in hybrid_df.columns]
    hybrid_df = hybrid_df[existing_columns]
    
    # Debug info
    both_scores_count = len(hybrid_df[(hybrid_df['knn_rank'].notna()) & (hybrid_df['cb_rank'].notna())])
    single_score_count = len(hybrid_df) - both_scores_count
    print(f"Ranking breakdown: {both_scores_count} games with both scores, {single_score_count} games with single score")
    print(f"Calculated hybrid rankings for {len(hybrid_df)} games")
    return hybrid_df


def save_hybrid_ranking(hybrid_df, file_path):
    """
    Lưu hybrid ranking vào file CSV
    
    Parameters:
    -----------
    hybrid_df : pd.DataFrame
        DataFrame với hybrid rankings
    file_path : str
        Đường dẫn file để lưu
    """
    try:
        hybrid_df.to_csv(file_path, index=False)
        print(f"Saved hybrid rankings to {file_path}")
        return True
    except Exception as e:
        print(f"Error saving hybrid rankings: {str(e)}")
        return False


# Example usage
if __name__ == "__main__":
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    knn_dir = os.path.join(project_root, "KNN_model")
    cb_dir = os.path.join(project_root, "CB_model")
    hybrid_dir = current_dir
    
    # Calculate hybrid ranking
    hybrid_ranking = calculate_hybrid_ranking(knn_dir, cb_dir, top_n=20)
    
    if not hybrid_ranking.empty:
        print("\n" + "="*80)
        print("HYBRID RANKING RESULTS")
        print("="*80)
        print(hybrid_ranking.to_string(index=False))
        print("="*80)
        
        # Save to file
        output_path = os.path.join(hybrid_dir, "hybrid_ranking.csv")
        save_hybrid_ranking(hybrid_ranking, output_path)
    else:
        print("No hybrid ranking calculated. Make sure both KNN and CB recommendations exist.")

