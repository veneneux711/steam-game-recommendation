import pandas as pd
import os
import re
import shutil

# --- CẤU HÌNH ---
knn_path = os.path.join("KNN_model", "final_games.csv")
cb_path = os.path.join("CB_model", "CB_games.csv")

def normalize_name(title):
    if not isinstance(title, str): return ""
    # Chuyển về chữ thường, chỉ giữ lại chữ và số
    return re.sub(r'[^a-z0-9]', '', title.lower())

def reduce_dataset_fixed():
    print("="*50)
    print("DATA REDUCTION TOOL (FIXED COLUMN MISMATCH)")
    print("="*50)

    # 1. Load KNN (File chuẩn)
    print("1. Đang đọc KNN data...")
    try:
        df_knn = pd.read_csv(knn_path)
        # Tạo danh sách các tên game hợp lệ (Whitelist)
        # Chuẩn hóa tên để so sánh chính xác hơn
        valid_titles = set(df_knn['title'].apply(normalize_name))
        print(f"-> Đã load {len(df_knn)} game từ KNN làm chuẩn.")
    except Exception as e:
        print(f"Lỗi đọc KNN: {e}")
        return

    # 2. Load CB (File bị lệch cột)
    print("2. Đang đọc CB data...")
    try:
        df_cb = pd.read_csv(cb_path)
        original_count = len(df_cb)
        print(f"-> CB data gốc: {original_count} dòng.")
        
        # --- QUAN TRỌNG: XỬ LÝ LỆCH CỘT ---
        # Trong file CB của bạn: Header 'AppID' chứa Tên Game.
        # Chúng ta sẽ dùng cột này để so sánh.
        print("-> Đang xử lý đối chiếu tên game (Mapping)...")
        
        # Tạo cột tạm chứa tên đã chuẩn hóa từ cột 'AppID' (thực chất là Tên)
        # Chuyển sang string trước khi normalize để tránh lỗi nếu có số
        df_cb['temp_norm_name'] = df_cb['AppID'].astype(str).apply(normalize_name)
        
        # LOGIC LỌC: Giữ lại những dòng mà tên game (cột AppID) có trong danh sách KNN
        mask = df_cb['temp_norm_name'].isin(valid_titles)
        
        df_cb_reduced = df_cb[mask].copy()
        
        # Xóa cột tạm
        df_cb_reduced.drop(columns=['temp_norm_name'], inplace=True)
        
        new_count = len(df_cb_reduced)
        print(f"-> Kết quả lọc: Giữ lại {new_count} game (trùng khớp với KNN).")
        print(f"-> Đã loại bỏ: {original_count - new_count} game thừa.")

    except Exception as e:
        print(f"Lỗi xử lý CB: {e}")
        return

    # 3. Lưu file
    if new_count > 0:
        # Backup
        backup_path = cb_path + ".bak_v2"
        shutil.copy2(cb_path, backup_path)
        print(f"3. Đã backup file gốc sang: {backup_path}")
        
        # Lưu đè file CB_games.csv
        # Quan trọng: Giữ nguyên cấu trúc lệch cột để không làm hỏng code load data hiện tại của bạn
        df_cb_reduced.to_csv(cb_path, index=False)
        print(f"✅ THÀNH CÔNG! File {cb_path} đã được làm gọn.")
        print("-" * 50)
        print("HƯỚNG DẪN TIẾP THEO:")
        print("1. Mở App 'Game Recommendation'.")
        print("2. Vào tab Content-Based -> Bấm nút màu đỏ 'Clear Data'.")
        print("3. Bấm 'Train Model' (Bây giờ sẽ chạy rất nhanh).")
        print("4. Sau đó thử chức năng Hybrid lại.")
    else:
        print("❌ LỖI: Kết quả lọc bằng 0. Có thể tên game giữa 2 file quá khác biệt.")

if __name__ == "__main__":
    reduce_dataset_fixed()