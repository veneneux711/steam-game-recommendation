# Steam Recommendation System - Hệ Thống Gợi Ý Game Đa Tầng

**Đồ án Máy Học & Khoa Học Dữ Liệu**  
Xây dựng hệ thống tư vấn game cá nhân hóa sử dụng kỹ thuật Hybrid (Kết hợp Content-Based và Collaborative Filtering).

---

## Giới Thiệu
Dự án giải quyết bài toán "Information Overload" (Quá tải thông tin) trên nền tảng Steam bằng cách cung cấp 3 lớp mô hình gợi ý:

1.  **Content-Based Filtering (CB):** Phân tích đặc trưng nội dung (Genres, Tags) sử dụng **TF-IDF** và **SVD** để tìm các game tương tự về mặt ngữ nghĩa.
2.  **Collaborative Filtering (KNN):** Phân tích hành vi người dùng bằng thuật toán **K-Nearest Neighbors** để tìm các game phổ biến trong cộng đồng người chơi có sở thích tương đồng.
3.  **Hybrid Model (Mô hình Lai):** Kết hợp kết quả từ hai mô hình trên, sử dụng cơ chế **"Synergy Boost"** (Cộng hưởng) để tối ưu hóa thứ hạng gợi ý.

---

## Cấu Trúc Dự Án

```text
STEAM ML/
├── CB_model/                  # [Module 1] Content-Based
│   ├── CB_games.csv           # Dữ liệu Metadata game
│   ├── cb_model.pkl           # Model đã huấn luyện (Vectorized)
│   ├── cb_recommendations.csv # Kết quả trung gian từ CB
│   └── ContentBased_model.py  # Thuật toán chính (TF-IDF + SVD)
│
├── KNN_model/                 # [Module 2] Collaborative Filtering
│   ├── final_reviews.csv      # Dữ liệu tương tác người dùng
│   ├── rcm_games.csv          # Kết quả trung gian từ KNN
│   ├── KNN_Core.py            # Thuật toán User-Based KNN
│   └── UI.py                  # Giao diện nhập liệu KNN
│
├── Hybrid_model/              # [Module 3] Hybrid Logic
│   ├── run_hybrid.py          # Script điều phối chính
│   └── Hybrid_recommendations_reader.py # Xử lý hợp nhất & Xếp hạng
│
├── test_scripts/              # [Module 4] Kiểm thử & Đánh giá
│   ├── test_cb_model.py       # Kiểm thử Content-Based (Genre Match)
│   ├── test_knn_model.py      # Kiểm thử KNN (Precision/Recall)
│   ├── test_hybrid_model.py   # Phân tích độ nhạy Hybrid
│   └── visualize_final_report.py # Tạo biểu đồ báo cáo
│
├── results/                   # Nơi lưu kết quả cuối cùng (CSV)
├── test_results/              # Nơi lưu báo cáo text & hình ảnh biểu đồ
├── user_data/                 # Dữ liệu người dùng cá nhân
└── run_*.bat                  # Các file chạy nhanh (Shortcuts)
```

---

## Cài Đặt & Khởi Chạy

### 1. Yêu cầu hệ thống
*   Python 3.8 trở lên.
*   Các thư viện: `pandas`, `numpy`, `scikit-learn`, `scipy`, `matplotlib`, `tkinter`.

### 2. Cài đặt thư viện
Chạy file `setup.bat` hoặc cài thủ công qua terminal:
```bash
pip install pandas numpy scikit-learn scipy matplotlib
```

### 3. Hướng Dẫn Sử Dụng

Để hệ thống hoạt động chính xác, vui lòng thực hiện theo quy trình **3 Bước** dưới đây:

**Bước 1: Chạy Mô hình KNN**
*   File chạy: `run_KNN.bat`
*   Thao tác:
    1.  Nhập tên game vào ô tìm kiếm -> Thêm vào danh sách "Played".
    2.  Bấm "Confirm" để lưu dữ liệu.
    3.  Bấm "Get Recommendations" (Bắt buộc).

**Bước 2: Chạy Mô hình Content-Based**
*   File chạy: `run_CB.bat`
*   Thao tác:
    1.  Tìm kiếm và Rate 5-10 game bạn thích.
    2.  Bấm "Save Ratings".
    3.  Bấm "Train Model".
    4.  Bấm "Get Recommendations" (Bắt buộc để sinh file dữ liệu cho bước sau).

**Bước 3: Chạy Mô hình Hybrid (Kết quả cuối cùng)**
*   File chạy: `run_Hybrid.bat`
*   Kết quả: Hệ thống sẽ tự động đọc kết quả từ Bước 1 & 2, tính toán điểm số cộng hưởng và hiển thị bảng xếp hạng tối ưu nhất.

---

## Kiểm Thử & Đánh Giá (Benchmarking)

Dự án đi kèm bộ công cụ kiểm thử tự động để đánh giá hiệu năng mô hình.

**Cách chạy kiểm thử:**
Mở terminal tại thư mục `test_scripts/` và chạy lần lượt các lệnh sau:

1.  **Test Content-Based (Đánh giá nội dung):**
    ```bash
    python test_cb_model.py
    ```
    *   *Chỉ số:* Genre Match Score (~93%), Tag Consistency.

2.  **Test KNN (Đánh giá hành vi):**
    ```bash
    python test_knn_model.py
    ```
    *   *Chỉ số:* Precision@10 (~15%), Recall@10 (~10%).

3.  **Tạo Báo cáo Tổng hợp (Dashboard):**
    ```bash
    python visualize_final_report.py
    ```
    *   *Kết quả:* File ảnh `test_results/final_dashboard_professional.png` dùng để chèn vào báo cáo đồ án.

---

## Công Nghệ & Thuật Toán Áp Dụng

### 1. Xử lý Dữ liệu (Data Engineering)
*   **Positional Weighting:** Tăng trọng số cho Genre và Top Tags để mô hình tập trung vào các đặc trưng quan trọng.
*   **Shovelware Filter:** Bộ lọc tự động loại bỏ game rác (Giá rẻ + Ít review) để đảm bảo chất lượng gợi ý.
*   **ID Recovery:** Cơ chế tự động khôi phục AppID khi dữ liệu nguồn bị lỗi hoặc thiếu sót.

### 2. Chiến lược Hybrid (Synergy Boost)
Sử dụng công thức tính điểm thưởng cho sự đồng thuận giữa hai mô hình:

$$ FinalScore = (W_{KNN} \cdot S_{KNN}) + (W_{CB} \cdot S_{CB}) + \sqrt{S_{KNN} \cdot S_{CB}} \cdot 0.5 $$

Cơ chế này giúp đẩy các game **"Vừa hay (KNN), vừa đúng gu (CB)"** lên vị trí cao nhất trên bảng xếp hạng.

---
