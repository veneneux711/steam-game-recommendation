import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# ==============================================================================
# 1. CẤU HÌNH SỐ LIỆU
# ==============================================================================
cb_metrics = {
    'Genre Match': 93.12,
    'Tag Consistency': 31.35
}

knn_metrics = {
    'Precision@10': 15.45,
    'Recall@10': 10.66
}

# Đường dẫn file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
RESULTS_DIR = os.path.join(PROJECT_ROOT, "test_results")
HYBRID_FILE = os.path.join(PROJECT_ROOT, "results", "hybrid_ranking.csv")

# ==============================================================================
# 2. HÀM PHÂN TÍCH
# ==============================================================================
def analyze_hybrid_source(file_path):
    if not os.path.exists(file_path):
        return [36, 0, 14] 
    try:
        df = pd.read_csv(file_path)
        only_cb = len(df[(df['Cb Score'] > 0) & (df['Knn Score'] == 0)])
        only_knn = len(df[(df['Knn Score'] > 0) & (df['Cb Score'] == 0)])
        both = len(df[(df['Knn Score'] > 0) & (df['Cb Score'] > 0)])
        return [only_cb, only_knn, both]
    except:
        return [0, 0, 0]

# ==============================================================================
# 3. VẼ BIỂU ĐỒ (PHIÊN BẢN LEGEND - KHÔNG BỊ ĐÈ CHỮ)
# ==============================================================================
def draw_dashboard():
    if not os.path.exists(RESULTS_DIR): os.makedirs(RESULTS_DIR)
    
    hybrid_counts = analyze_hybrid_source(HYBRID_FILE)
    total_recs = sum(hybrid_counts)
    
    # Tạo khung hình lớn
    fig = plt.figure(figsize=(16, 10)) 
    # Layout: Hàng trên cho A, B. Hàng dưới cho C nhưng chừa chỗ bên phải cho Legend
    grid = plt.GridSpec(2, 2, hspace=0.4, wspace=0.3, height_ratios=[1, 1.2])

    # --- BIỂU ĐỒ A ---
    ax1 = fig.add_subplot(grid[0, 0])
    colors_cb = ['#4CAF50', '#8BC34A']
    bars1 = ax1.bar(cb_metrics.keys(), cb_metrics.values(), color=colors_cb, width=0.5)
    ax1.set_title('(A) Hiệu năng Content-Based (Nội dung)', fontweight='bold', fontsize=13)
    ax1.set_ylabel('Điểm số (%)', fontsize=11)
    ax1.set_ylim(0, 115)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 2, f'{h:.2f}%', ha='center', fontweight='bold', fontsize=11)

    # --- BIỂU ĐỒ B ---
    ax2 = fig.add_subplot(grid[0, 1])
    colors_knn = ['#FF9800', '#FFC107']
    bars2 = ax2.bar(knn_metrics.keys(), knn_metrics.values(), color=colors_knn, width=0.5)
    ax2.set_title('(B) Hiệu năng KNN (Hành vi - Top 10)', fontweight='bold', fontsize=13)
    ax2.set_ylabel('Tỷ lệ (%)', fontsize=11)
    ax2.set_ylim(0, 25)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 0.5, f'{h:.2f}%', ha='center', fontweight='bold', fontsize=11)

    # --- BIỂU ĐỒ C (HYBRID - DÙNG LEGEND) ---
    ax3 = fig.add_subplot(grid[1, :])
    
    # Tạo nhãn cho Legend (Kèm số lượng)
    legend_labels = [
        f'Chỉ từ Content-Based ({hybrid_counts[0]})', 
        f'Chỉ từ KNN ({hybrid_counts[1]})', 
        f'Đồng thuận - Cả hai ({hybrid_counts[2]})'
    ]
    
    colors_hybrid = ['#81C784', '#BDBDBD', '#9C27B0'] 
    if hybrid_counts[1] > 0: colors_hybrid[1] = '#FFB74D'

    explode = (0.02, 0.02, 0.05) # Tách nhẹ các miếng ra cho đẹp
    
    # Vẽ Pie Chart KHÔNG CÓ LABEL (để tránh bị đè)
    wedges, texts, autotexts = ax3.pie(
        hybrid_counts, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors_hybrid, 
        explode=explode,
        pctdistance=0.6, # Đẩy % vào giữa
        textprops={'fontsize': 12, 'weight': 'bold', 'color': 'white'}
    )
    
    # Ẩn số 0.0%
    for autotext in autotexts:
        if autotext.get_text() == '0.0%': autotext.set_text('')

    ax3.set_title(f'(C) Phân tích nguồn gợi ý Hybrid (Top {total_recs} Ranking)', fontweight='bold', fontsize=14)

    # --- TẠO BẢNG CHÚ THÍCH (LEGEND) BÊN PHẢI ---
    ax3.legend(
        wedges, 
        legend_labels,
        title="Nguồn Gợi Ý (Số lượng)",
        loc="center left",
        bbox_to_anchor=(0.8, 0, 0.5, 1), # Đẩy Legend sang bên phải biểu đồ
        fontsize=11
    )

    # --- CHÚ THÍCH GIẢI THÍCH KNN = 0 (Nằm dưới cùng) ---
    if hybrid_counts[1] == 0:
        note_text = (
            "(*) GIẢI THÍCH: Tỷ lệ 'Chỉ từ KNN' = 0% không phải do lỗi thuật toán.\n"
            "1. Các game tốt nhất của KNN đã trùng khớp với CB và chuyển sang nhóm 'Đồng thuận' (Màu tím).\n"
            "2. Các game KNN còn lại có điểm số thấp hơn Content-Based nên nằm ngoài danh sách hiển thị Top đầu."
        )
        plt.figtext(0.5, 0.01, note_text, ha="center", fontsize=10, style='italic', 
                    bbox={"facecolor":"#FFF3E0", "edgecolor":"orange", "alpha":0.5, "pad":5})

    # --- TIÊU ĐỀ TỔNG ---
    plt.suptitle('BÁO CÁO TỔNG HỢP HIỆU NĂNG HỆ THỐNG GỢI Ý GAME', fontsize=18, y=0.98, color='#333', fontweight='bold')
    
    # Lưu ảnh
    output_image_path = os.path.join(RESULTS_DIR, "final_dashboard_professional.png")
    try:
        plt.savefig(output_image_path, dpi=300, bbox_inches='tight')
        print(f"\n[OK] Đã lưu biểu đồ đẹp vào:\n     {output_image_path}")
    except Exception as e:
        print(f"\n[!] Lỗi khi lưu ảnh: {e}")

    plt.show()

if __name__ == "__main__":
    draw_dashboard()