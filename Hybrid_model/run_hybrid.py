"""
Hybrid Recommendation System - Standalone Script
Đọc recommendations từ KNN và Content-Based models đã chạy và tính hybrid ranking
"""

import os
import sys
import tkinter as tk
# Import hàm save và calculate từ file reader (đảm bảo bạn đã sửa file này như bài trước)
from Hybrid_recommendations_reader import calculate_hybrid_ranking, save_hybrid_ranking
from Hybrid_results_viewer import show_hybrid_results

# Get paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
knn_dir = os.path.join(project_root, "KNN_model")
cb_dir = os.path.join(project_root, "CB_model")
hybrid_dir = current_dir

print("="*80)
print("HYBRID RECOMMENDATION SYSTEM")
print("="*80)
print(f"KNN directory: {knn_dir}")
print(f"CB directory: {cb_dir}")
print(f"Output directory: {hybrid_dir}")
print("="*80)
print()

# Kiểm tra recommendations files
knn_recommendations = os.path.join(knn_dir, "rcm_games.csv")
if not os.path.exists(knn_recommendations):
    knn_recommendations = os.path.join(knn_dir, "recommendations.csv")

cb_recommendations = os.path.join(cb_dir, "cb_recommendations.csv")

print("Checking recommendations files...")
if not os.path.exists(knn_recommendations):
    print(f"❌ ERROR: KNN recommendations not found!")
    print(f"   Expected: {knn_recommendations}")
    print(f"   Please run KNN model first and get recommendations.")
    sys.exit(1)
else:
    print(f"✅ Found KNN recommendations: {knn_recommendations}")

if not os.path.exists(cb_recommendations):
    print(f"❌ ERROR: Content-Based recommendations not found!")
    print(f"   Expected: {cb_recommendations}")
    print(f"   Please run Content-Based model first and get recommendations.")
    sys.exit(1)
else:
    print(f"✅ Found CB recommendations: {cb_recommendations}")

print()
print("Calculating hybrid rankings...")
print("-"*80)

# Tính hybrid ranking
hybrid_ranking = calculate_hybrid_ranking(
    knn_dir=knn_dir,
    cb_dir=cb_dir,
    top_n=50,
    knn_weight=0.5,
    cb_weight=0.5
)

if hybrid_ranking.empty:
    print("❌ ERROR: No hybrid rankings calculated!")
    print("   Make sure both KNN and CB recommendations contain valid data.")
    sys.exit(1)

# Lưu kết quả
results_dir = os.path.join(os.path.dirname(hybrid_dir), "results")
os.makedirs(results_dir, exist_ok=True)
output_path = os.path.join(results_dir, "hybrid_ranking.csv")

# Lưu file (Sử dụng hàm đã import)
if save_hybrid_ranking(hybrid_ranking, output_path):
    print(f"✅ Saved hybrid rankings to: {output_path}")
    print(f"   Total recommendations: {len(hybrid_ranking)}")
    # QUAN TRỌNG: Không dùng sys.exit(0) ở đây để code chạy tiếp xuống phần mở Window
else:
    print("❌ ERROR: Failed to save hybrid rankings!")
    # Nếu lưu lỗi thì dừng luôn cũng được, hoặc chạy tiếp tùy bạn. Ở đây ta dừng.
    sys.exit(1)

print()
print("="*80)
print("Opening results window...")
print("="*80)

# Hiển thị kết quả trong UI
try:
    # Yêu cầu phải có file Hybrid_results_viewer.py
    show_hybrid_results(hybrid_ranking)
except Exception as e:
    print(f"Error displaying UI: {str(e)}")
    print("Falling back to console output...")
    print()
    print("="*80)
    print("HYBRID RANKING RESULTS")
    print("="*80)
    print(hybrid_ranking.to_string(index=False))
    print("="*80)