"""
Script để chạy evaluation cho cả 3 models và tạo báo cáo kết quả
"""

import os
import sys
import pandas as pd
import numpy as np
from evaluation import (
    evaluate_model, 
    compare_models, 
    print_evaluation_report,
    precision_at_k,
    recall_at_k,
    f1_score_at_k,
    mean_average_precision,
    ndcg_at_k,
    calculate_diversity,
    calculate_coverage
)

def load_knn_recommendations(knn_dir):
    """Load KNN recommendations"""
    rcm_file = os.path.join(knn_dir, "rcm_games.csv")
    if not os.path.exists(rcm_file):
        rcm_file = os.path.join(knn_dir, "recommendations.csv")
    
    if not os.path.exists(rcm_file):
        print(f"Warning: KNN recommendations not found at {rcm_file}")
        return []
    
    df = pd.read_csv(rcm_file)
    # Convert to list of (game_id, score) tuples
    recommendations = []
    
    # Try to find game_id column (could be app_id, game_id, or need to match by title)
    game_id_col = None
    for col in ['app_id', 'game_id', 'gameID']:
        if col in df.columns:
            game_id_col = col
            break
    
    # If no game_id column, try to match by title with final_games.csv
    if game_id_col is None:
        final_games_file = os.path.join(knn_dir, "final_games.csv")
        if os.path.exists(final_games_file):
            final_games = pd.read_csv(final_games_file)
            title_to_id = dict(zip(final_games['title'], final_games['app_id']))
            
            for _, row in df.iterrows():
                title = row.get('title', None)
                if title and title in title_to_id:
                    game_id = title_to_id[title]
                    score = row.get('relevance', row.get('score', 1.0))
                    recommendations.append((game_id, score))
        else:
            print(f"Warning: Cannot load KNN recommendations - no game_id column and final_games.csv not found")
            return []
    else:
        for _, row in df.iterrows():
            game_id = row.get(game_id_col, None)
            score = row.get('relevance', row.get('score', 1.0))
            if game_id:
                recommendations.append((int(game_id), float(score)))
    
    return recommendations


def load_cb_recommendations(cb_dir):
    """Load Content-Based recommendations"""
    rcm_file = os.path.join(cb_dir, "cb_recommendations.csv")
    
    if not os.path.exists(rcm_file):
        print(f"Warning: CB recommendations not found at {rcm_file}")
        return []
    
    df = pd.read_csv(rcm_file)
    recommendations = []
    
    # Try different column name variations
    game_id_col = None
    for col in ['AppID', 'app_id', 'game_id', 'gameID']:
        if col in df.columns:
            game_id_col = col
            break
    
    score_col = None
    for col in ['Similarity', 'similarity', 'score', 'Score', 'relevance']:
        if col in df.columns:
            score_col = col
            break
    
    if game_id_col and score_col:
        for _, row in df.iterrows():
            game_id = row.get(game_id_col, None)
            score = row.get(score_col, 1.0)
            if game_id and pd.notna(game_id):
                try:
                    recommendations.append((int(game_id), float(score)))
                except (ValueError, TypeError):
                    continue
    
    return recommendations


def load_hybrid_recommendations(hybrid_dir):
    """Load Hybrid recommendations"""
    rcm_file = os.path.join(hybrid_dir, "hybrid_ranking.csv")
    
    if not os.path.exists(rcm_file):
        print(f"Warning: Hybrid recommendations not found at {rcm_file}")
        return []
    
    df = pd.read_csv(rcm_file)
    recommendations = []
    for _, row in df.iterrows():
        game_id = row.get('app_id', None)
        score = row.get('hybrid_score', 1.0)
        if game_id:
            recommendations.append((game_id, score))
    
    return recommendations


def create_test_set_from_ratings(knn_dir, cb_dir):
    """
    Tạo test set từ user ratings (ground truth)
    Lấy một phần ratings làm test set
    """
    test_set = set()
    
    # Load từ KNN ratings
    your_games_file = os.path.join(knn_dir, "your_games.csv")
    if os.path.exists(your_games_file):
        df = pd.read_csv(your_games_file)
        # Check column name (could be gameID or app_id)
        id_col = 'gameID' if 'gameID' in df.columns else 'app_id'
        review_col = 'review' if 'review' in df.columns else 'rating'
        
        if id_col in df.columns and review_col in df.columns:
            # Lấy games có rating >= 0.5 (Like hoặc Interested)
            liked_games = df[df[review_col] >= 0.5][id_col].tolist()
            test_set.update([int(gid) for gid in liked_games if pd.notna(gid)])
    
    # Load từ CB ratings
    cb_ratings_file = os.path.join(cb_dir, "cb_user_ratings.json")
    if os.path.exists(cb_ratings_file):
        import json
        try:
            with open(cb_ratings_file, 'r', encoding='utf-8') as f:
                ratings = json.load(f)
                # Xử lý cả dict và list format
                if isinstance(ratings, dict):
                    # Format: {"app_id": rating, ...}
                    for game_id, rating in ratings.items():
                        try:
                            if isinstance(rating, (int, float)) and rating >= 3:
                                test_set.add(int(game_id))
                        except (ValueError, TypeError):
                            continue
                elif isinstance(ratings, list):
                    # Format: [{"AppID": ..., "user_rating": ...}, ...]
                    for item in ratings:
                        if isinstance(item, dict):
                            game_id = item.get('app_id', item.get('AppID', item.get('game_id', None)))
                            rating = item.get('rating', item.get('user_rating', item.get('Rating', 0)))
                            try:
                                if isinstance(rating, (int, float)) and rating >= 3:
                                    test_set.add(int(game_id))
                            except (ValueError, TypeError):
                                continue
        except Exception as e:
            print(f"Warning: Could not load CB ratings: {e}")
    
    return test_set


def load_games_metadata(knn_dir, cb_dir):
    """Load games metadata cho diversity calculation"""
    metadata = {}
    
    # Load từ KNN
    games_file = os.path.join(knn_dir, "final_games.csv")
    if os.path.exists(games_file):
        df = pd.read_csv(games_file)
        for _, row in df.iterrows():
            game_id = row.get('app_id', None)
            if game_id and pd.notna(game_id):
                metadata[int(game_id)] = {
                    'genres': [],  # Có thể extract từ data nếu có
                    'tags': []
                }
    
    # Load từ CB games (có genres và tags)
    cb_games_file = os.path.join(cb_dir, "CB_games.csv")
    if os.path.exists(cb_games_file):
        try:
            df = pd.read_csv(cb_games_file, nrows=1000)  # Load sample để tránh memory issue
            for _, row in df.iterrows():
                game_id = row.get('app_id', None)
                if game_id and pd.notna(game_id):
                    game_id = int(game_id)
                    genres = str(row.get('Genres', '')).split(',') if pd.notna(row.get('Genres')) else []
                    tags = str(row.get('Tags', '')).split(',') if pd.notna(row.get('Tags')) else []
                    
                    if game_id not in metadata:
                        metadata[game_id] = {'genres': [], 'tags': []}
                    metadata[game_id]['genres'] = [g.strip() for g in genres if g.strip()]
                    metadata[game_id]['tags'] = [t.strip() for t in tags if t.strip()]
        except Exception as e:
            print(f"Warning: Could not load CB games metadata: {e}")
    
    return metadata


def get_all_games(knn_dir, cb_dir):
    """Get set of all available games"""
    all_games = set()
    
    # From KNN
    games_file = os.path.join(knn_dir, "final_games.csv")
    if os.path.exists(games_file):
        try:
            df = pd.read_csv(games_file)
            if 'app_id' in df.columns:
                all_games.update([int(gid) for gid in df['app_id'].tolist() if pd.notna(gid)])
        except Exception as e:
            print(f"Warning: Could not load KNN games: {e}")
    
    # From CB (sample only to avoid memory issue)
    cb_games_file = os.path.join(cb_dir, "CB_games.csv")
    if os.path.exists(cb_games_file):
        try:
            df = pd.read_csv(cb_games_file, nrows=50000)  # Sample
            if 'app_id' in df.columns:
                all_games.update([int(gid) for gid in df['app_id'].tolist() if pd.notna(gid)])
        except Exception as e:
            print(f"Warning: Could not load CB games: {e}")
    
    return all_games


def evaluate_all_models(knn_dir, cb_dir, hybrid_dir, k_values=[10, 20, 30]):
    """Evaluate all 3 models với nhiều K values"""
    
    print("="*80)
    print("EVALUATION REPORT - Game Recommendation System")
    print("="*80)
    print()
    
    # Load recommendations
    print("Loading recommendations...")
    knn_recommendations = load_knn_recommendations(knn_dir)
    cb_recommendations = load_cb_recommendations(cb_dir)
    hybrid_recommendations = load_hybrid_recommendations(hybrid_dir)
    
    print(f"KNN: {len(knn_recommendations)} recommendations")
    print(f"Content-Based: {len(cb_recommendations)} recommendations")
    print(f"Hybrid: {len(hybrid_recommendations)} recommendations")
    print()
    
    # Debug: Show sample recommendations
    if knn_recommendations:
        print(f"Sample KNN recommendations (first 3): {knn_recommendations[:3]}")
    if cb_recommendations:
        print(f"Sample CB recommendations (first 3): {cb_recommendations[:3]}")
    if hybrid_recommendations:
        print(f"Sample Hybrid recommendations (first 3): {hybrid_recommendations[:3]}")
    print()
    
    # Load test set và metadata
    print("Loading test set and metadata...")
    test_set = create_test_set_from_ratings(knn_dir, cb_dir)
    games_metadata = load_games_metadata(knn_dir, cb_dir)
    all_games = get_all_games(knn_dir, cb_dir)
    
    print(f"Test set size: {len(test_set)} games")
    print(f"Test set sample: {list(test_set)[:10] if test_set else 'Empty'}")
    print(f"All games: {len(all_games)} games")
    
    # Check overlap between recommendations and test set
    if knn_recommendations:
        knn_game_ids = {int(gid) for gid, _ in knn_recommendations}
        knn_overlap = len(knn_game_ids & test_set)
        print(f"KNN overlap with test set: {knn_overlap}/{len(knn_game_ids)} games")
    
    if cb_recommendations:
        cb_game_ids = {int(gid) for gid, _ in cb_recommendations}
        cb_overlap = len(cb_game_ids & test_set)
        print(f"CB overlap with test set: {cb_overlap}/{len(cb_game_ids)} games")
    
    if hybrid_recommendations:
        hybrid_game_ids = {int(gid) for gid, _ in hybrid_recommendations}
        hybrid_overlap = len(hybrid_game_ids & test_set)
        print(f"Hybrid overlap with test set: {hybrid_overlap}/{len(hybrid_game_ids)} games")
    
    print()
    
    # Evaluate với nhiều K values
    results = {}
    
    for k in k_values:
        print(f"\n{'='*80}")
        print(f"EVALUATION RESULTS @ K={k}")
        print(f"{'='*80}\n")
        
        # Evaluate KNN
        knn_metrics = evaluate_model(
            knn_recommendations, 
            test_set, 
            games_metadata=games_metadata,
            all_games=all_games,
            k=k
        )
        
        # Evaluate CB
        cb_metrics = evaluate_model(
            cb_recommendations,
            test_set,
            games_metadata=games_metadata,
            all_games=all_games,
            k=k
        )
        
        # Evaluate Hybrid
        hybrid_metrics = evaluate_model(
            hybrid_recommendations,
            test_set,
            games_metadata=games_metadata,
            all_games=all_games,
            k=k
        )
        
        # Store results
        results[k] = {
            'KNN': knn_metrics,
            'Content-Based': cb_metrics,
            'Hybrid': hybrid_metrics
        }
        
        # Print comparison
        print_evaluation_report(knn_metrics, cb_metrics, hybrid_metrics)
    
    # Create summary table
    print("\n" + "="*80)
    print("SUMMARY TABLE - All Metrics @ K=10")
    print("="*80)
    
    summary_data = []
    for metric in ['precision@k', 'recall@k', 'f1_score@k', 'MAP@k', 'NDCG@k', 'diversity', 'coverage']:
        row = {'Metric': metric}
        if 10 in results:
            row['KNN'] = results[10]['KNN'].get(metric, 'N/A')
            row['Content-Based'] = results[10]['Content-Based'].get(metric, 'N/A')
            row['Hybrid'] = results[10]['Hybrid'].get(metric, 'N/A')
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    
    # Save to CSV
    output_file = os.path.join(hybrid_dir, "evaluation_results.csv")
    summary_df.to_csv(output_file, index=False)
    print(f"\n✅ Saved evaluation results to: {output_file}")
    
    return results


if __name__ == "__main__":
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    knn_dir = os.path.join(project_root, "KNN_model")
    cb_dir = os.path.join(project_root, "CB_model")
    hybrid_dir = os.path.join(project_root, "Hybrid_model")
    
    # Run evaluation
    results = evaluate_all_models(knn_dir, cb_dir, hybrid_dir, k_values=[10, 20, 30])
    
    print("\n" + "="*80)
    print("EVALUATION COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("1. Review evaluation_results.csv")
    print("2. Create visualization charts")
    print("3. Write analysis in report")

