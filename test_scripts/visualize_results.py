import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

def visualize():
    # --- CẤU HÌNH ĐƯỜNG DẪN TUYỆT ĐỐI ---
    # Lấy đường dẫn của file script này (nằm trong test_scripts)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Trỏ trực tiếp vào file CSV nằm cùng thư mục
    report_path = os.path.join(current_dir, "benchmark_report.csv")
    
    print(f"🔍 Đang tìm file báo cáo tại: {report_path}")

    if not os.path.exists(report_path):
        print("❌ LỖI: Không tìm thấy file 'benchmark_report.csv'.")
        print("   Hãy chắc chắn bạn đã chạy 'run_benchmark.py' thành công.")
        return

    # Load dữ liệu
    try:
        df = pd.read_csv(report_path)
    except Exception as e:
        print(f"❌ Lỗi đọc file CSV: {e}")
        return
    
    print(f"✅ Đã load {len(df)} dòng dữ liệu. Đang vẽ biểu đồ...")

    # Làm sạch tên Persona (VD: 'user_01_RPG_Fan' -> 'RPG_Fan')
    # Xử lý lỗi nếu tên không đúng định dạng
    def clean_persona(x):
        parts = str(x).split('_')
        if len(parts) > 2:
            return '_'.join(parts[2:])
        return str(x)

    df['Simple_Persona'] = df['User_Persona'].apply(clean_persona)

    # Cấu hình giao diện biểu đồ
    sns.set_theme(style="whitegrid")
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Steam Hybrid Recommender System - Benchmark Results', fontsize=16, fontweight='bold')

    # --- BIỂU ĐỒ 1: ĐỘ ĐỒNG THUẬN GIỮA KNN VÀ CB (Scatter Plot) ---
    plt.subplot(2, 2, 1)
    sns.scatterplot(data=df, x='KNN_Score', y='CB_Score', hue='Simple_Persona', s=100, alpha=0.7, palette='deep')
    plt.title('Sự phân bổ điểm số: KNN vs Content-Based', fontsize=11, fontweight='bold')
    plt.xlabel('KNN Score (Cộng đồng)')
    plt.ylabel('Content-Based Score (Nội dung)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, title="Persona")

    # --- BIỂU ĐỒ 2: ĐIỂM HYBRID TRUNG BÌNH THEO NHÓM (Bar Chart) ---
    plt.subplot(2, 2, 2)
    avg_scores = df.groupby('Simple_Persona')['Hybrid_Score'].mean().sort_values(ascending=False)
    sns.barplot(x=avg_scores.values, y=avg_scores.index, palette='viridis', hue=avg_scores.index, legend=False)
    plt.title('Hiệu quả gợi ý theo nhóm người chơi (Mean Hybrid Score)', fontsize=11, fontweight='bold')
    plt.xlabel('Hybrid Score trung bình')

    # --- BIỂU ĐỒ 3: TOP GAME ĐƯỢC GỢI Ý NHIỀU NHẤT (Horizontal Bar) ---
    plt.subplot(2, 2, 3)
    top_games = df['Top_1_Game'].value_counts().head(8)
    sns.barplot(x=top_games.values, y=top_games.index, palette='magma', hue=top_games.index, legend=False)
    plt.title('Top Games phổ biến nhất (Diversity Check)', fontsize=11, fontweight='bold')
    plt.xlabel('Số lần xuất hiện ở Top 1')

    # --- BIỂU ĐỒ 4: PHÂN BỐ ĐIỂM SỐ (KDE Plot) ---
    plt.subplot(2, 2, 4)
    sns.kdeplot(data=df, x='Hybrid_Score', hue='Simple_Persona', fill=True, common_norm=False, alpha=0.3)
    plt.title('Phân bố mật độ điểm số theo nhóm', fontsize=11, fontweight='bold')
    plt.xlabel('Hybrid Score')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Chừa chỗ cho title
    
    # Lưu ảnh vào cùng thư mục với script
    output_img = os.path.join(current_dir, "benchmark_analysis.png")
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    print(f"✅ Đã lưu biểu đồ phân tích vào: {output_img}")
    
    # Hiển thị
    plt.show()

if __name__ == "__main__":
    visualize()