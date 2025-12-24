import pandas as pd
import os
import sys
import time

# --- 1. THIẾT LẬP ĐƯỜNG DẪN & IMPORT (Fix lỗi ModuleNotFoundError) ---
current_dir = os.path.dirname(os.path.abspath(__file__))   # .../test_scripts
project_root = os.path.dirname(current_dir)                # .../STEAM ML - SỬA LẠI CB
hybrid_model_path = os.path.join(project_root, "Hybrid_model")

# Thêm đường dẫn Hybrid_model vào hệ thống để import được
sys.path.append(hybrid_model_path)

try:
    from Hybrid_recommendations_reader import calculate_hybrid_ranking
except ImportError as e:
    print(f"Lỗi Import: {e}")
    print(f"Đường dẫn đã thử: {hybrid_model_path}")
    sys.exit(1)

# --- 2. CẤU HÌNH ---
KNN_DIR = os.path.join(project_root, "KNN_model")
CB_DIR = os.path.join(project_root, "CB_model")
RESULTS_DIR = os.path.join(project_root, "test_results")

# Biến lưu nội dung báo cáo
report_content = []

def log(text=""):
    """Hàm vừa in ra màn hình, vừa lưu vào biến report"""
    print(text)
    report_content.append(str(text))

def analyze_overlap(knn_dir, cb_dir):
    """Phân tích độ trùng lặp giữa 2 model con"""
    try:
        knn_path = os.path.join(knn_dir, "rcm_games.csv")
        cb_path = os.path.join(cb_dir, "cb_recommendations.csv")
        
        # Load dữ liệu thô
        if not os.path.exists(knn_path) or not os.path.exists(cb_path):
            log("Lỗi: Không tìm thấy file kết quả từ KNN hoặc CB.")
            return set()

        df_knn = pd.read_csv(knn_path)
        df_cb = pd.read_csv(cb_path)
        
        # Chuẩn hóa tên để so sánh (bỏ ký tự đặc biệt, lowercase)
        # Kiểm tra cột tồn tại trước khi xử lý
        knn_col = 'title' if 'title' in df_knn.columns else df_knn.columns[0]
        cb_col = 'Name' if 'Name' in df_cb.columns else df_cb.columns[0]

        knn_titles = set(df_knn[knn_col].astype(str).str.lower().str.replace(r'[^a-z0-9]', '', regex=True))
        cb_titles = set(df_cb[cb_col].astype(str).str.lower().str.replace(r'[^a-z0-9]', '', regex=True))
        
        overlap = knn_titles.intersection(cb_titles)
        
        log("\n" + "="*50)
        log("1. PHÂN TÍCH ĐỘ TRÙNG LẶP (OVERLAP ANALYSIS)")
        log("="*50)
        log(f"Số lượng gợi ý từ KNN: {len(knn_titles)}")
        log(f"Số lượng gợi ý từ Content-Based: {len(cb_titles)}")
        log(f"Số lượng game trùng nhau (Consensus): {len(overlap)}")
        
        if len(knn_titles) > 0:
            overlap_rate = (len(overlap) / len(knn_titles)) * 100
            log(f"Tỷ lệ trùng lặp: {overlap_rate:.2f}%")
            log("(Tỷ lệ này thấp là bình thường, cho thấy 2 thuật toán gợi ý các khía cạnh khác nhau)")
        
        return overlap
    except Exception as e:
        log(f"Lỗi khi phân tích overlap: {e}")
        return set()

def test_weight_sensitivity(knn_dir, cb_dir):
    """Chạy thử nghiệm với các trọng số khác nhau"""
    log("\n" + "="*50)
    log("2. THỬ NGHIM TRỌNG SỐ (WEIGHT SENSITIVITY TEST)")
    log("="*50)
    
    scenarios = [
        {'name': 'Thiên về Cộng đồng (KNN)', 'w_knn': 0.8, 'w_cb': 0.2},
        {'name': 'Cân bằng (Balanced)',      'w_knn': 0.5, 'w_cb': 0.5},
        {'name': 'Thiên về Nội dung (CB)',   'w_knn': 0.2, 'w_cb': 0.8}
    ]
    
    results = {}
    
    # Tắt output của hàm calculate_hybrid_ranking để báo cáo sạch đẹp
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    
    try:
        for sc in scenarios:
            df_hybrid = calculate_hybrid_ranking(
                knn_dir, cb_dir, top_n=10, 
                knn_weight=sc['w_knn'], cb_weight=sc['w_cb']
            )
            results[sc['name']] = df_hybrid
    except Exception:
        pass
    finally:
        sys.stdout = original_stdout # Khôi phục in ra màn hình

    # In kết quả sau khi đã tính xong
    for sc in scenarios:
        name = sc['name']
        log(f"\n--- Scenario: {name} (KNN={sc['w_knn']}, CB={sc['w_cb']}) ---")
        if name in results and not results[name].empty:
            df = results[name]
            top_3 = df['Title'].head(3).tolist()
            log(f"   Top 3 Games: {top_3}")
            
            # Đếm overlap trong top 10
            overlap_count = len(df[ (df['Knn Score'] > 0) & (df['Cb Score'] > 0) ])
            log(f"   Số game đồng thuận trong Top 10: {overlap_count}")
        else:
            log("   Không tạo được danh sách.")

    return results

def main():
    log("BẮT ĐẦU KIỂM THỬ HỆ THỐNG HYBRID...")
    log(f"Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Kiểm tra file đầu vào
    if not os.path.exists(KNN_DIR) or not os.path.exists(CB_DIR):
        log(f"Lỗi: Không tìm thấy thư mục KNN_model hoặc CB_model tại {project_root}")
        return

    # 2. Phân tích Overlap
    overlap_set = analyze_overlap(KNN_DIR, CB_DIR)
    
    # 3. Test các kịch bản trọng số
    test_weight_sensitivity(KNN_DIR, CB_DIR)
    
    # 4. Gợi ý kết luận
    log("\n" + "="*50)
    log("GỢI Ý VIẾT BÁO CÁO (CONCLUSIONS)")
    log("="*50)
    log("1. Về sự bổ trợ (Complementarity):")
    log("   Hệ thống Hybrid kết hợp danh sách từ KNN (thường là game phổ biến) và CB (game có nội dung tương đồng).")
    log(f"   Việc có {len(overlap_set)} game trùng nhau cho thấy sự đồng thuận nhất định giữa hành vi người dùng và nội dung game.")
    
    log("\n2. Về chiến lược Ranking:")
    log("   Cơ chế 'Synergy Boost' giúp đẩy các game xuất hiện ở cả 2 thuật toán lên Top đầu.")
    log("   Điều này giúp tăng độ tin cậy (Confidence) của gợi ý: Game vừa hay (được cộng đồng thích) vừa đúng gu (giống game đã chơi).")

    # --- LƯU FILE ---
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        
    output_path = os.path.join(RESULTS_DIR, "hybrid_evaluation_report.txt")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_content))
        print(f"\n[OK] Đã lưu báo cáo chi tiết vào file:\n     {output_path}")
    except Exception as e:
        print(f"\n[!] Lỗi không lưu được file: {e}")

if __name__ == "__main__":
    main()