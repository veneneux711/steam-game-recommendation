"""
Evaluation Module cho Recommendation Systems
Tính các metrics chuẩn để đánh giá models
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Set


def precision_at_k(recommendations: List[Tuple], test_set: Set, k: int = 10) -> float:
    """
    Tính Precision@K
    
    Args:
        recommendations: List of (game_id, score) tuples
        test_set: Set of game_ids trong test set (ground truth)
        k: Top K recommendations
    
    Returns:
        Precision@K score (0-1)
    """
    if len(recommendations) == 0:
        return 0.0
    
    top_k = [game_id for game_id, _ in recommendations[:k]]
    relevant = len([gid for gid in top_k if gid in test_set])
    
    return relevant / min(k, len(recommendations))


def recall_at_k(recommendations: List[Tuple], test_set: Set, k: int = 10) -> float:
    """
    Tính Recall@K
    
    Args:
        recommendations: List of (game_id, score) tuples
        test_set: Set of game_ids trong test set (ground truth)
        k: Top K recommendations
    
    Returns:
        Recall@K score (0-1)
    """
    if len(test_set) == 0:
        return 0.0
    
    top_k = [game_id for game_id, _ in recommendations[:k]]
    relevant = len([gid for gid in top_k if gid in test_set])
    
    return relevant / len(test_set)


def f1_score_at_k(recommendations: List[Tuple], test_set: Set, k: int = 10) -> float:
    """
    Tính F1-Score@K
    
    Args:
        recommendations: List of (game_id, score) tuples
        test_set: Set of game_ids trong test set
        k: Top K recommendations
    
    Returns:
        F1-Score@K (0-1)
    """
    precision = precision_at_k(recommendations, test_set, k)
    recall = recall_at_k(recommendations, test_set, k)
    
    if precision + recall == 0:
        return 0.0
    
    return 2 * (precision * recall) / (precision + recall)


def mean_average_precision(recommendations: List[Tuple], test_set: Set, k: int = 10) -> float:
    """
    Tính Mean Average Precision (MAP@K)
    
    Args:
        recommendations: List of (game_id, score) tuples
        test_set: Set of game_ids trong test set
        k: Top K recommendations
    
    Returns:
        MAP@K score (0-1)
    """
    if len(test_set) == 0:
        return 0.0
    
    top_k = recommendations[:k]
    relevant_count = 0
    precision_sum = 0.0
    
    for i, (game_id, _) in enumerate(top_k):
        if game_id in test_set:
            relevant_count += 1
            precision_sum += relevant_count / (i + 1)
    
    if relevant_count == 0:
        return 0.0
    
    return precision_sum / min(len(test_set), k)


def ndcg_at_k(recommendations: List[Tuple], test_set: Set, k: int = 10) -> float:
    """
    Tính Normalized Discounted Cumulative Gain (NDCG@K)
    
    Args:
        recommendations: List of (game_id, score) tuples
        test_set: Set of game_ids trong test set
        k: Top K recommendations
    
    Returns:
        NDCG@K score (0-1)
    """
    if len(test_set) == 0:
        return 0.0
    
    top_k = recommendations[:k]
    
    # DCG: Discounted Cumulative Gain
    dcg = 0.0
    for i, (game_id, _) in enumerate(top_k):
        if game_id in test_set:
            # Relevance = 1 nếu trong test_set
            relevance = 1
            dcg += relevance / np.log2(i + 2)  # i+2 vì log2(1) = 0
    
    # IDCG: Ideal DCG (perfect ranking)
    idcg = 0.0
    num_relevant = min(len(test_set), k)
    for i in range(num_relevant):
        idcg += 1.0 / np.log2(i + 2)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def calculate_diversity(recommendations: List[Tuple], games_metadata: Dict, k: int = 10) -> float:
    """
    Tính Diversity: Độ đa dạng của recommendations
    
    Args:
        recommendations: List of (game_id, score) tuples
        games_metadata: Dict {game_id: {genres: [...], tags: [...]}}
        k: Top K recommendations
    
    Returns:
        Diversity score (0-1): Tỷ lệ unique genres/tags
    """
    if len(recommendations) == 0:
        return 0.0
    
    top_k = [game_id for game_id, _ in recommendations[:k]]
    all_genres = []
    all_tags = []
    
    for game_id in top_k:
        if game_id in games_metadata:
            metadata = games_metadata[game_id]
            if 'genres' in metadata:
                all_genres.extend(metadata['genres'])
            if 'tags' in metadata:
                all_tags.extend(metadata['tags'])
    
    if len(all_genres) == 0 and len(all_tags) == 0:
        return 0.0
    
    # Tính diversity dựa trên genres và tags
    unique_genres = len(set(all_genres))
    unique_tags = len(set(all_tags))
    total_genres = len(all_genres)
    total_tags = len(all_tags)
    
    genre_diversity = unique_genres / total_genres if total_genres > 0 else 0
    tag_diversity = unique_tags / total_tags if total_tags > 0 else 0
    
    # Average diversity
    diversity = (genre_diversity + tag_diversity) / 2 if (total_genres > 0 and total_tags > 0) else (genre_diversity or tag_diversity)
    
    return diversity


def calculate_coverage(recommendations: List[Tuple], all_games: Set, k: int = 10) -> float:
    """
    Tính Coverage: % games được recommend
    
    Args:
        recommendations: List of (game_id, score) tuples
        all_games: Set of all available game_ids
        k: Top K recommendations
    
    Returns:
        Coverage score (0-1): Tỷ lệ games được recommend
    """
    if len(all_games) == 0:
        return 0.0
    
    top_k = set([game_id for game_id, _ in recommendations[:k]])
    coverage = len(top_k) / len(all_games)
    
    return min(coverage, 1.0)  # Cap at 1.0


def evaluate_model(recommendations: List[Tuple], test_set: Set, 
                   games_metadata: Dict = None, all_games: Set = None, 
                   k: int = 10) -> Dict[str, float]:
    """
    Tính tất cả metrics cho một model
    
    Args:
        recommendations: List of (game_id, score) tuples
        test_set: Set of game_ids trong test set
        games_metadata: Dict {game_id: {genres: [...], tags: [...]}}
        all_games: Set of all available game_ids
        k: Top K recommendations
    
    Returns:
        Dict với các metrics
    """
    metrics = {
        'precision@k': precision_at_k(recommendations, test_set, k),
        'recall@k': recall_at_k(recommendations, test_set, k),
        'f1_score@k': f1_score_at_k(recommendations, test_set, k),
        'MAP@k': mean_average_precision(recommendations, test_set, k),
        'NDCG@k': ndcg_at_k(recommendations, test_set, k)
    }
    
    if games_metadata:
        metrics['diversity'] = calculate_diversity(recommendations, games_metadata, k)
    
    if all_games:
        metrics['coverage'] = calculate_coverage(recommendations, all_games, k)
    
    return metrics


def compare_models(knn_metrics: Dict, cb_metrics: Dict, hybrid_metrics: Dict) -> pd.DataFrame:
    """
    So sánh metrics giữa 3 models
    
    Args:
        knn_metrics: Metrics từ KNN model
        cb_metrics: Metrics từ Content-Based model
        hybrid_metrics: Metrics từ Hybrid model
    
    Returns:
        DataFrame với comparison
    """
    comparison = pd.DataFrame({
        'KNN': knn_metrics,
        'Content-Based': cb_metrics,
        'Hybrid': hybrid_metrics
    })
    
    return comparison


def print_evaluation_report(knn_metrics: Dict, cb_metrics: Dict, hybrid_metrics: Dict):
    """
    In evaluation report dạng bảng
    """
    comparison = compare_models(knn_metrics, cb_metrics, hybrid_metrics)
    
    print("\n" + "="*60)
    print("EVALUATION REPORT - Model Comparison")
    print("="*60)
    print(comparison.to_string())
    print("="*60)
    
    # Tìm model tốt nhất cho từng metric
    print("\nBest Models by Metric:")
    for metric in comparison.index:
        best_model = comparison.loc[metric].idxmax()
        best_score = comparison.loc[metric].max()
        print(f"  {metric:20s}: {best_model:20s} ({best_score:.4f})")


# Example usage
if __name__ == "__main__":
    # Example data
    recommendations_knn = [
        (1, 0.9), (2, 0.8), (3, 0.7), (4, 0.6), (5, 0.5),
        (6, 0.4), (7, 0.3), (8, 0.2), (9, 0.1), (10, 0.05)
    ]
    recommendations_cb = [
        (2, 0.95), (1, 0.85), (5, 0.75), (3, 0.65), (8, 0.55),
        (6, 0.45), (4, 0.35), (7, 0.25), (9, 0.15), (10, 0.05)
    ]
    recommendations_hybrid = [
        (1, 0.92), (2, 0.88), (3, 0.72), (5, 0.68), (4, 0.58),
        (6, 0.48), (8, 0.38), (7, 0.28), (9, 0.18), (10, 0.08)
    ]
    
    test_set = {1, 2, 3, 5, 7}  # Ground truth
    all_games = set(range(1, 11))
    
    # Evaluate models
    knn_metrics = evaluate_model(recommendations_knn, test_set, all_games=all_games, k=10)
    cb_metrics = evaluate_model(recommendations_cb, test_set, all_games=all_games, k=10)
    hybrid_metrics = evaluate_model(recommendations_hybrid, test_set, all_games=all_games, k=10)
    
    # Print report
    print_evaluation_report(knn_metrics, cb_metrics, hybrid_metrics)

