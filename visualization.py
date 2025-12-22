"""
Visualization Module cho Evaluation Results
Tạo charts và graphs để hiển thị kết quả evaluation
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_evaluation_results(results_file):
    """Load evaluation results từ CSV"""
    if not os.path.exists(results_file):
        print(f"Error: {results_file} not found")
        return None
    
    df = pd.read_csv(results_file)
    return df


def plot_model_comparison(results_df, output_dir="Hybrid_model"):
    """Vẽ bar chart so sánh metrics giữa 3 models"""
    
    # Filter out diversity và coverage (có thể scale khác)
    metrics_to_plot = ['precision@k', 'recall@k', 'f1_score@k', 'MAP@k', 'NDCG@k']
    df_plot = results_df[results_df['Metric'].isin(metrics_to_plot)].copy()
    
    # Prepare data
    models = ['KNN', 'Content-Based', 'Hybrid']
    metrics = df_plot['Metric'].values
    knn_values = df_plot['KNN'].values
    cb_values = df_plot['Content-Based'].values
    hybrid_values = df_plot['Hybrid'].values
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = np.arange(len(metrics))
    width = 0.25
    
    bars1 = ax.bar(x - width, knn_values, width, label='KNN', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x, cb_values, width, label='Content-Based', color='#e74c3c', alpha=0.8)
    bars3 = ax.bar(x + width, hybrid_values, width, label='Hybrid', color='#2ecc71', alpha=0.8)
    
    # Customize
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Model Comparison - Evaluation Metrics @ K=10', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace('@k', '@10').replace('_', ' ').title() for m in metrics], rotation=15, ha='right')
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim([0, max(max(knn_values), max(cb_values), max(hybrid_values)) * 1.2])
    
    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(output_dir, "model_comparison.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def plot_precision_recall_curve(results_df, k_values=[10, 20, 30], output_dir="Hybrid_model"):
    """Vẽ line chart Precision và Recall@K cho các K values khác nhau"""
    
    # Note: Cần có data từ nhiều K values
    # Tạm thời chỉ plot với K=10, có thể mở rộng sau
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Precision@K
    models = ['KNN', 'Content-Based', 'Hybrid']
    precision_values = [
        results_df[results_df['Metric'] == 'precision@k']['KNN'].values[0],
        results_df[results_df['Metric'] == 'precision@k']['Content-Based'].values[0],
        results_df[results_df['Metric'] == 'precision@k']['Hybrid'].values[0]
    ]
    recall_values = [
        results_df[results_df['Metric'] == 'recall@k']['KNN'].values[0],
        results_df[results_df['Metric'] == 'recall@k']['Content-Based'].values[0],
        results_df[results_df['Metric'] == 'recall@k']['Hybrid'].values[0]
    ]
    
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    # Precision bar chart
    bars1 = ax1.bar(models, precision_values, color=colors, alpha=0.8)
    ax1.set_ylabel('Precision@10', fontsize=12, fontweight='bold')
    ax1.set_title('Precision@10 Comparison', fontsize=13, fontweight='bold')
    ax1.set_ylim([0, max(precision_values) * 1.3])
    ax1.grid(axis='y', alpha=0.3)
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Recall bar chart
    bars2 = ax2.bar(models, recall_values, color=colors, alpha=0.8)
    ax2.set_ylabel('Recall@10', fontsize=12, fontweight='bold')
    ax2.set_title('Recall@10 Comparison', fontsize=13, fontweight='bold')
    ax2.set_ylim([0, max(recall_values) * 1.3])
    ax2.grid(axis='y', alpha=0.3)
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, "precision_recall_comparison.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def plot_ndcg_map_comparison(results_df, output_dir="Hybrid_model"):
    """Vẽ comparison cho NDCG và MAP"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    models = ['KNN', 'Content-Based', 'Hybrid']
    ndcg_values = [
        results_df[results_df['Metric'] == 'NDCG@k']['KNN'].values[0],
        results_df[results_df['Metric'] == 'NDCG@k']['Content-Based'].values[0],
        results_df[results_df['Metric'] == 'NDCG@k']['Hybrid'].values[0]
    ]
    map_values = [
        results_df[results_df['Metric'] == 'MAP@k']['KNN'].values[0],
        results_df[results_df['Metric'] == 'MAP@k']['Content-Based'].values[0],
        results_df[results_df['Metric'] == 'MAP@k']['Hybrid'].values[0]
    ]
    
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    # NDCG bar chart
    bars1 = ax1.bar(models, ndcg_values, color=colors, alpha=0.8)
    ax1.set_ylabel('NDCG@10', fontsize=12, fontweight='bold')
    ax1.set_title('NDCG@10 Comparison', fontsize=13, fontweight='bold')
    ax1.set_ylim([0, max(ndcg_values) * 1.3])
    ax1.grid(axis='y', alpha=0.3)
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # MAP bar chart
    bars2 = ax2.bar(models, map_values, color=colors, alpha=0.8)
    ax2.set_ylabel('MAP@10', fontsize=12, fontweight='bold')
    ax2.set_title('MAP@10 Comparison', fontsize=13, fontweight='bold')
    ax2.set_ylim([0, max(map_values) * 1.3])
    ax2.grid(axis='y', alpha=0.3)
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, "ndcg_map_comparison.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def plot_radar_chart(results_df, output_dir="Hybrid_model"):
    """Vẽ radar chart so sánh tổng thể 3 models"""
    
    from math import pi
    
    # Prepare data
    metrics = ['Precision', 'Recall', 'F1-Score', 'MAP', 'NDCG']
    knn_values = [
        results_df[results_df['Metric'] == 'precision@k']['KNN'].values[0],
        results_df[results_df['Metric'] == 'recall@k']['KNN'].values[0],
        results_df[results_df['Metric'] == 'f1_score@k']['KNN'].values[0],
        results_df[results_df['Metric'] == 'MAP@k']['KNN'].values[0],
        results_df[results_df['Metric'] == 'NDCG@k']['KNN'].values[0]
    ]
    cb_values = [
        results_df[results_df['Metric'] == 'precision@k']['Content-Based'].values[0],
        results_df[results_df['Metric'] == 'recall@k']['Content-Based'].values[0],
        results_df[results_df['Metric'] == 'f1_score@k']['Content-Based'].values[0],
        results_df[results_df['Metric'] == 'MAP@k']['Content-Based'].values[0],
        results_df[results_df['Metric'] == 'NDCG@k']['Content-Based'].values[0]
    ]
    hybrid_values = [
        results_df[results_df['Metric'] == 'precision@k']['Hybrid'].values[0],
        results_df[results_df['Metric'] == 'recall@k']['Hybrid'].values[0],
        results_df[results_df['Metric'] == 'f1_score@k']['Hybrid'].values[0],
        results_df[results_df['Metric'] == 'MAP@k']['Hybrid'].values[0],
        results_df[results_df['Metric'] == 'NDCG@k']['Hybrid'].values[0]
    ]
    
    # Number of variables
    N = len(metrics)
    
    # Compute angle for each metric
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]  # Complete the circle
    
    # Add values
    knn_values += knn_values[:1]
    cb_values += cb_values[:1]
    hybrid_values += hybrid_values[:1]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Plot
    ax.plot(angles, knn_values, 'o-', linewidth=2, label='KNN', color='#3498db')
    ax.fill(angles, knn_values, alpha=0.25, color='#3498db')
    
    ax.plot(angles, cb_values, 'o-', linewidth=2, label='Content-Based', color='#e74c3c')
    ax.fill(angles, cb_values, alpha=0.25, color='#e74c3c')
    
    ax.plot(angles, hybrid_values, 'o-', linewidth=2, label='Hybrid', color='#2ecc71')
    ax.fill(angles, hybrid_values, alpha=0.25, color='#2ecc71')
    
    # Customize
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, fontsize=11)
    ax.set_ylim([0, 0.3])
    ax.set_title('Model Performance Radar Chart @ K=10', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
    ax.grid(True)
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, "radar_chart.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def create_all_visualizations(results_file="Hybrid_model/evaluation_results.csv", output_dir="Hybrid_model"):
    """Tạo tất cả visualizations"""
    
    print("="*80)
    print("CREATING VISUALIZATIONS")
    print("="*80)
    print()
    
    # Load results
    results_df = load_evaluation_results(results_file)
    if results_df is None:
        return
    
    print(f"Loaded evaluation results: {len(results_df)} metrics")
    print()
    
    # Create visualizations
    print("1. Creating model comparison chart...")
    plot_model_comparison(results_df, output_dir)
    
    print("2. Creating precision/recall comparison...")
    plot_precision_recall_curve(results_df, output_dir=output_dir)
    
    print("3. Creating NDCG/MAP comparison...")
    plot_ndcg_map_comparison(results_df, output_dir)
    
    print("4. Creating radar chart...")
    plot_radar_chart(results_df, output_dir)
    
    print()
    print("="*80)
    print("✅ ALL VISUALIZATIONS CREATED!")
    print("="*80)
    print(f"Output directory: {output_dir}")
    print("Files created:")
    print("  - model_comparison.png")
    print("  - precision_recall_comparison.png")
    print("  - ndcg_map_comparison.png")
    print("  - radar_chart.png")


if __name__ == "__main__":
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_file = os.path.join(current_dir, "Hybrid_model", "evaluation_results.csv")
    output_dir = os.path.join(current_dir, "Hybrid_model")
    
    create_all_visualizations(results_file, output_dir)

