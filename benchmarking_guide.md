# HƯỚNG DẪN KIỂM THỬ & ĐÁNH GIÁ HỆ THỐNG (BENCHMARKING GUIDE)

Tài liệu này hướng dẫn quy trình **Benchmark** (Đánh giá hiệu năng) của hệ thống gợi ý game Steam. Quy trình được chia thành 3 giai đoạn kiểm thử độc lập cho từng mô hình và tổng hợp kết quả bằng Dashboard trực quan.

---

## 1. Cấu Trúc Thư Mục Kiểm Thử

Đảm bảo các file script nằm trong thư mục `test_scripts/` và cấu trúc dự án như sau:

```
STEAM ML/
├── CB_model/               # Chứa dữ liệu & model Content-Based
├── KNN_model/              # Chứa dữ liệu & model Collaborative
├── Hybrid_model/           # Chứa logic kết hợp
├── results/                # Nơi chứa file kết quả chạy Hybrid (hybrid_ranking.csv)
├── test_results/           # (Tự động tạo) Nơi lưu báo cáo text và ảnh biểu đồ
└── test_scripts/
    ├── test_cb_model.py           # Test độ chính xác nội dung
    ├── test_knn_model.py          # Test độ chính xác hành vi
    ├── test_hybrid_model.py       # Phân tích độ nhạy Hybrid
    └── visualize_final_report.py  # Vẽ biểu đồ tổng hợp
```

---

## 2. Chuẩn Bị Môi Trường

Mở Terminal (Command Prompt) và cài đặt các thư viện cần thiết:
```bash
pip install pandas numpy matplotlib scipy scikit-learn
```

Di chuyển vào thư mục script trước khi chạy:
```bash
cd test_scripts
```

---

## 3. Quy Trình Thực Hiện (4 Bước)

### Bước 1: Đánh Giá Content-Based Model
Kiểm tra khả năng phân loại game dựa trên nội dung (Genre, Tags).
*   **Lệnh chạy:**
    ```bash
    python test_cb_model.py
    ```
*   **Dữ liệu:** Test trên 20% toàn bộ dataset (~3,400 games).
*   **Chỉ số quan trọng:**
    *   **Genre Match Score:** Tỷ lệ game gợi ý đúng thể loại chính (Kỳ vọng > 80%).
    *   **Tag Consistency:** Độ trùng khớp về thẻ (Kỳ vọng > 30-40%).

### Bước 2: Đánh Giá KNN Model (Collaborative Filtering)
Kiểm tra khả năng dự đoán hành vi người dùng dựa trên lịch sử chơi.
*   **Lệnh chạy:**
    ```bash
    python test_knn_model.py
    ```
*   **Cấu hình tối ưu:** Top-10 gợi ý, User có > 50 reviews.
*   **Chỉ số quan trọng:**
    *   **Precision@10:** Độ chính xác trong 10 gợi ý đầu (Kỳ vọng ~= 10%).
    *   **Recall@10:** Khả năng tìm lại các game yêu thích đã bị ẩn (Kỳ vọng > 10%).

###Phân Tích Hybrid Model
Do đặc thù 2 dataset khác nhau, và hệ thống knn chỉ thực sự toả sáng khi làm việc với lượng nhỏ data game từ người dùng nhập vào nên Hybrid model sẽ chỉ đánh giá trong các trường hợp cụ thể
*   2 file .bat của CB và KNN cần chạy trước nhằm nhập game vào, lưu data và lấy gợi ý
Kiểm tra cơ chế kết hợp và độ ổn định của hệ thống lai.
*   **Điều kiện:** Cần chạy `run_hybrid_system.py` ở thư mục gốc trước để tạo ra file `results/hybrid_ranking.csv` (nếu chưa có).
*   **Lệnh chạy:**
    ```bash
    python test_hybrid_model.py
    ```
*   **Mục tiêu:**
    *   **Sensitivity Analysis:** Kiểm tra xem Top 3 game thay đổi thế nào khi chỉnh trọng số.
    *   **Synergy Boost:** Xác nhận các game "Đồng thuận" (xuất hiện ở cả 2 model) có được đẩy lên đầu không.

### Bước 4: Tạo Báo Cáo Trực Quan (Dashboard)
Tổng hợp toàn bộ số liệu thành biểu đồ chuyên nghiệp.
*   **Lệnh chạy:**
    ```bash
    python visualize_final_report.py
    ```
*   **Output:** File ảnh chất lượng cao `test_results/final_dashboard_professional.png`.

---

## 4. Hướng Dẫn Đọc Biểu Đồ (Dashboard Analysis)

Sử dụng ảnh `final_dashboard_professional.png`.

### Biểu đồ A: Content-Based Performance (Cột Xanh)
*   Thể hiện độ an toàn của hệ thống.
*   **Genre Match cao (93%)** $\rightarrow$ Hệ thống không bao giờ gợi ý sai lệch thể loại (Ví dụ: Không gợi ý game thời trang cho người thích game bắn súng).

### Biểu đồ B: KNN Performance (Cột Cam/Vàng)
*   Thể hiện độ thông minh trong việc đoán ý người dùng.
*   **Precision (15.45%):** Trong 10 game gợi ý, có khoảng 1-2 game chắc chắn user sẽ thích.
*   **Recall (10.66%):** Tỷ lệ bao phủ, tìm lại được các game cũ.
*   *Lưu ý:* Precision thấp là bình thường với không gian dữ liệu lớn như Steam.

### Với việc chạy cá nhân cho file test_result_cd_rpg
### Biểu đồ C: Hybrid Composition (Biểu đồ Tròn)
*   Phân tích nguồn gốc của các game trong Top Ranking.
*   **Màu Tím (Đồng thuận - Consensus):** Đây là vùng quan trọng nhất. Nếu miếng này xuất hiện, chứng tỏ thuật toán Hybrid hoạt động hiệu quả, lọc ra được những "siêu phẩm" vừa đúng gu (Content) vừa hay (KNN).
*   **Màu Xanh/Cam:** Thể hiện sự đa dạng hóa nguồn gợi ý.

---
