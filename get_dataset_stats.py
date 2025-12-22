"""
Script để lấy thống kê dataset
Tạo file dataset_statistics.txt với các thống kê cơ bản
"""

import os
import pandas as pd
import json
from collections import Counter

def get_knn_stats(knn_dir):
    """Lấy thống kê KNN dataset"""
    stats = {}
    
    # Games
    games_file = os.path.join(knn_dir, "final_games.csv")
    if os.path.exists(games_file):
        df = pd.read_csv(games_file)
        stats['total_games'] = len(df)
        stats['games_with_reviews'] = len(df[df['user_reviews'] > 0])
        stats['avg_positive_ratio'] = df['positive_ratio'].mean()
        stats['avg_user_reviews'] = df['user_reviews'].mean()
        stats['max_user_reviews'] = df['user_reviews'].max()
        
        # Release years
        if 'date_release' in df.columns:
            df['year'] = pd.to_datetime(df['date_release'], errors='coerce').dt.year
            stats['release_years'] = {
                'min': int(df['year'].min()) if pd.notna(df['year'].min()) else None,
                'max': int(df['year'].max()) if pd.notna(df['year'].max()) else None
            }
    
    # Reviews
    reviews_file = os.path.join(knn_dir, "final_reviews.csv")
    if os.path.exists(reviews_file):
        # Sample để tránh memory issue
        df = pd.read_csv(reviews_file, nrows=100000)
        stats['sample_reviews'] = len(df)
        stats['unique_users_sample'] = df['user_id'].nunique()
        stats['unique_games_sample'] = df['app_id'].nunique()
        
        # Rating distribution
        if 'is_recommended' in df.columns:
            rating_dist = df['is_recommended'].value_counts()
            stats['rating_distribution'] = {
                'like': int(rating_dist.get(1, 0)),
                'dislike': int(rating_dist.get(0, 0))
            }
    
    # User ratings
    your_games_file = os.path.join(knn_dir, "your_games.csv")
    if os.path.exists(your_games_file):
        df = pd.read_csv(your_games_file)
        stats['user_ratings_count'] = len(df)
        if 'review' in df.columns:
            stats['user_rating_distribution'] = df['review'].value_counts().to_dict()
    
    return stats


def get_cb_stats(cb_dir):
    """Lấy thống kê Content-Based dataset"""
    stats = {}
    
    # Games
    games_file = os.path.join(cb_dir, "CB_games.csv")
    if os.path.exists(games_file):
        # Sample để tránh memory issue
        df = pd.read_csv(games_file, nrows=50000)
        stats['total_games_sample'] = len(df)
        stats['games_with_genres'] = len(df[df['Genres'].notna() & (df['Genres'] != '')])
        stats['games_with_tags'] = len(df[df['Tags'].notna() & (df['Tags'] != '')])
        
        # Genres
        all_genres = []
        for genres_str in df['Genres'].dropna():
            if genres_str:
                all_genres.extend([g.strip() for g in str(genres_str).split(',')])
        
        genre_counter = Counter(all_genres)
        stats['unique_genres'] = len(genre_counter)
        stats['top_10_genres'] = dict(genre_counter.most_common(10))
        
        # Tags
        all_tags = []
        for tags_str in df['Tags'].dropna():
            if tags_str:
                all_tags.extend([t.strip() for t in str(tags_str).split(',')])
        
        tag_counter = Counter(all_tags)
        stats['unique_tags'] = len(tag_counter)
        stats['top_10_tags'] = dict(tag_counter.most_common(10))
    
    # User ratings
    ratings_file = os.path.join(cb_dir, "cb_user_ratings.json")
    if os.path.exists(ratings_file):
        with open(ratings_file, 'r', encoding='utf-8') as f:
            ratings = json.load(f)
            stats['user_ratings_count'] = len(ratings)
            
            if isinstance(ratings, list):
                rating_values = [r.get('user_rating', 0) for r in ratings if isinstance(r, dict)]
                stats['user_rating_distribution'] = dict(Counter(rating_values))
    
    return stats


def save_stats_to_file(stats, output_file):
    """Lưu stats vào file text"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("DATASET STATISTICS\n")
        f.write("="*80 + "\n\n")
        
        # KNN Stats
        if 'knn' in stats:
            f.write("KNN MODEL DATASET\n")
            f.write("-"*80 + "\n")
            knn = stats['knn']
            f.write(f"Total Games: {knn.get('total_games', 'N/A')}\n")
            f.write(f"Games with Reviews: {knn.get('games_with_reviews', 'N/A')}\n")
            f.write(f"Average Positive Ratio: {knn.get('avg_positive_ratio', 0):.2f}%\n")
            f.write(f"Average User Reviews: {knn.get('avg_user_reviews', 0):.0f}\n")
            f.write(f"Max User Reviews: {knn.get('max_user_reviews', 0)}\n")
            
            if 'release_years' in knn:
                years = knn['release_years']
                f.write(f"Release Years: {years.get('min')} - {years.get('max')}\n")
            
            if 'sample_reviews' in knn:
                f.write(f"\nReviews Sample (100K):\n")
                f.write(f"  Total Reviews: {knn.get('sample_reviews', 0):,}\n")
                f.write(f"  Unique Users: {knn.get('unique_users_sample', 0):,}\n")
                f.write(f"  Unique Games: {knn.get('unique_games_sample', 0):,}\n")
                
                if 'rating_distribution' in knn:
                    dist = knn['rating_distribution']
                    total = dist.get('like', 0) + dist.get('dislike', 0)
                    if total > 0:
                        f.write(f"  Like: {dist.get('like', 0)} ({dist.get('like', 0)/total*100:.1f}%)\n")
                        f.write(f"  Dislike: {dist.get('dislike', 0)} ({dist.get('dislike', 0)/total*100:.1f}%)\n")
            
            if 'user_ratings_count' in knn:
                f.write(f"\nUser Ratings: {knn.get('user_ratings_count', 0)}\n")
            
            f.write("\n")
        
        # CB Stats
        if 'cb' in stats:
            f.write("CONTENT-BASED MODEL DATASET\n")
            f.write("-"*80 + "\n")
            cb = stats['cb']
            f.write(f"Total Games (Sample 50K): {cb.get('total_games_sample', 'N/A'):,}\n")
            f.write(f"Games with Genres: {cb.get('games_with_genres', 0):,}\n")
            f.write(f"Games with Tags: {cb.get('games_with_tags', 0):,}\n")
            f.write(f"Unique Genres: {cb.get('unique_genres', 0)}\n")
            f.write(f"Unique Tags: {cb.get('unique_tags', 0)}\n")
            
            if 'top_10_genres' in cb:
                f.write(f"\nTop 10 Genres:\n")
                for genre, count in cb['top_10_genres'].items():
                    f.write(f"  {genre}: {count}\n")
            
            if 'top_10_tags' in cb:
                f.write(f"\nTop 10 Tags:\n")
                for tag, count in list(cb['top_10_tags'].items())[:10]:
                    f.write(f"  {tag}: {count}\n")
            
            if 'user_ratings_count' in cb:
                f.write(f"\nUser Ratings: {cb.get('user_ratings_count', 0)}\n")
                if 'user_rating_distribution' in cb:
                    f.write("Rating Distribution:\n")
                    for rating, count in sorted(cb['user_rating_distribution'].items()):
                        f.write(f"  {rating}: {count}\n")
            
            f.write("\n")
        
        f.write("="*80 + "\n")
        f.write(f"Generated: {pd.Timestamp.now()}\n")
        f.write("="*80 + "\n")


def main():
    """Main function"""
    print("="*80)
    print("GETTING DATASET STATISTICS")
    print("="*80)
    print()
    
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    knn_dir = os.path.join(current_dir, "KNN_model")
    cb_dir = os.path.join(current_dir, "CB_model")
    output_file = os.path.join(current_dir, "dataset_statistics.txt")
    
    stats = {}
    
    # Get KNN stats
    print("1. Getting KNN dataset statistics...")
    stats['knn'] = get_knn_stats(knn_dir)
    print("   ✅ Done")
    print()
    
    # Get CB stats
    print("2. Getting Content-Based dataset statistics...")
    stats['cb'] = get_cb_stats(cb_dir)
    print("   ✅ Done")
    print()
    
    # Save to file
    print("3. Saving statistics to file...")
    save_stats_to_file(stats, output_file)
    print(f"   ✅ Saved to: {output_file}")
    print()
    
    print("="*80)
    print("✅ COMPLETE!")
    print("="*80)
    print(f"\nStatistics saved to: {output_file}")
    print("You can now use this data in your report.")


if __name__ == "__main__":
    main()

