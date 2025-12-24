# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ QUY TRÌNH CONTENT-BASED FILTERING

## 2.1. Tổng Quan Phương Pháp
Hệ thống sử dụng phương pháp **Content-Based Filtering (Lọc dựa trên nội dung)** kết hợp với kỹ thuật **Latent Semantic Analysis (LSA)**. Thay vì chỉ so khớp từ khóa đơn thuần, hệ thống sử dụng thuật toán SVD để hiểu ngữ nghĩa tiềm ẩn của Game Tags và Genres, giúp đưa ra gợi ý chính xác ngay cả khi dữ liệu thưa thớt.

## 2.2. Các Bước Xử Lý Thuật Toán (Model Logic)

Dựa trên code `ContentBased_model.py`, quy trình xử lý bao gồm 4 giai đoạn chính:

### Giai đoạn 1: Feature Engineering (Tạo đặc trưng có trọng số)
Hệ thống không coi tất cả thông tin là ngang hàng. Trong hàm `prepare_content_features`, một kỹ thuật **Frequency Weighting** được áp dụng:
*   **Genres (Thể loại):** Được nhân bản **4 lần**.
*   **Tags (Nhãn):** Giữ nguyên (1 lần).
*   **Mục đích:** Ép thuật toán coi trọng Thể loại chính (RPG, Action...) hơn là các tag phụ (Indie, 2D...), đảm bảo game được gợi ý luôn đúng thể loại người dùng muốn.

### Giai đoạn 2: Vectorization & Dimensionality Reduction
Chuyển đổi văn bản thành không gian số học:

1.  **TF-IDF (Term Frequency - Inverse Document Frequency):**
    *   Chuyển văn bản thành vector với kích thước 5,000 đặc trưng.
    *   Loại bỏ các từ quá phổ biến (Stop words, max_df=0.7) để lọc nhiễu.

2.  **Truncated SVD (Singular Value Decomposition):**
    *   Giảm chiều dữ liệu từ **5,000 chiều** xuống **100 chiều**.
    *   **Tại sao dùng SVD?**
        *   Tăng tốc độ tính toán (Dense Matrix nhanh hơn Sparse Matrix).
        *   Khử nhiễu (Noise Reduction).
        *   Bắt được ngữ nghĩa ẩn (Latent Meaning): Ví dụ, máy sẽ hiểu "Shooter" và "FPS" có vector gần nhau trong không gian 100 chiều.

### Giai đoạn 3: Xây Dựng Hồ Sơ Người Dùng (User Profiling)
Hồ sơ người dùng ($V_{user}$) không phải là trung bình cộng đơn giản, mà là **Trung bình cộng có trọng số (Weighted Average)** dựa trên Rating:
*   Rating 5 sao $\rightarrow$ Trọng số $w=3$.
*   Rating 4 sao $\rightarrow$ Trọng số $w=2$.
*   Rating 3 sao $\rightarrow$ Trọng số $w=1$.

Công thức:
$$ V_{user} = \frac{\sum (V_{game\_i} \times w_i)}{\sum w_i} $$
*(Code: `np.average(..., weights=weights)`) - Điều này giúp game người dùng "thích nhất" sẽ kéo vector sở thích về phía nó mạnh nhất.*

### Giai đoạn 4: Tính Điểm & Bộ Lọc "Shovelware" (Recommendation & Filtering)
Đây là phần tinh túy nhất trong code của bạn để loại bỏ game rác.

1.  **Similarity Score ($S_{sim}$):** Tính Cosine Similarity giữa $V_{user}$ và $V_{game}$.
2.  **Popularity Score ($S_{pop}$):**
    $$ S_{pop} = \frac{\log_{10}(\text{Total Reviews} + 1)}{10.0} $$
    *(Dùng Logarit để tránh việc game bom tấn áp đảo hoàn toàn game nhỏ).*
3.  **Shovelware Filter (Bộ lọc game rác):**
    Hệ thống trừng phạt nặng các game có dấu hiệu là "Shovelware" (Game chất lượng kém làm ra để kiếm tiền nhanh):
    *   **Điều kiện:** Tổng Review < 100.
    *   **Xử lý:**
        *   Nếu Giá < $9.99 (Rẻ + Ít review): **Phạt 75% điểm số** ($Score \times 0.25$).
        *   Nếu Giá $\ge$ $9.99 (Đắt + Ít review): **Phạt 10% điểm số** ($Score \times 0.9$).

4.  **Final Score:**
    $$ Final = (S_{sim} \times 0.85) + (S_{pop} \times 0.15) \times \text{Penalty} $$

---

## 2.3. Quy Trình Xử Lý Dữ Liệu (Data Pipeline)

Dựa trên code `ContentBased_data_handler.py`, quy trình ETL (Extract - Transform - Load) xử lý các vấn đề thực tế của dữ liệu Steam:

### A. Làm sạch dữ liệu (Data Cleaning)
1.  **Sửa lỗi lệch cột (Column Misalignment Fix):**
    *   Phát hiện file CSV gốc bị lỗi header (Cột `AppID` chứa Tên game, cột `Name` chứa Ngày tháng).
    *   Code tự động đổi tên (`rename`) để đưa dữ liệu về đúng cột.
2.  **Chuẩn hóa kiểu dữ liệu (Type Casting):**
    *   **Price:** Xử lý các chuỗi phức tạp như "Free to Play", "$19.99", "Free" $\rightarrow$ Chuyển về số thực `0.0` hoặc `19.99`.
    *   **Reviews:** Loại bỏ dấu phẩy (1,234 $\rightarrow$ 1234) để tính toán toán học.

### B. Lưu trữ phản hồi (Feedback Loop)
*   Dữ liệu đánh giá của người dùng (User Ratings) được lưu trữ dưới dạng **JSON** (`cb_user_ratings.json`).
*   Cấu trúc JSON lưu `AppID` chuẩn xác, giúp hệ thống tái sử dụng dữ liệu cho các lần chạy sau mà không cần người dùng nhập lại.

---

## 2.4. Tổng Kết
Mô hình Content-Based được xây dựng không chỉ dựa trên lý thuyết TF-IDF cơ bản mà còn được tối ưu hóa cho bài toán thực tế của Steam thông qua:
1.  **SVD:** Giúp hiểu ngữ nghĩa sâu hơn.
2.  **Weighted Profile:** Tôn trọng mức độ yêu thích khác nhau của người dùng.
3.  **Shovelware Filter:** Kỹ thuật lọc nhiễu dựa trên tri thức miền (Domain Knowledge) về thị trường game (Giá rẻ + Ít review thường là game kém chất lượng).