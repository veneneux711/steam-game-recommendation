# CHI TIẾT KỸ THUẬT VÀ XỬ LÝ DỮ LIỆU (TECHNICAL IMPLEMENTATION DETAILS)

Tài liệu này mô tả các kỹ thuật xử lý dữ liệu (Data Engineering), các thuật toán "hậu xử lý" (Post-processing) và kiến trúc mã nguồn giúp hệ thống vận hành ổn định.

---

## 1. Đồng Bộ Hóa Dữ Liệu (Data Synchronization)

### Vấn đề: Sự chênh lệch dữ liệu (Data Mismatch)
*   **KNN Dataset:** ~15,000 game (Dữ liệu hành vi người chơi - Interaction Data).
*   **Content-Based Dataset:** ~110,000 game (Dữ liệu Metadata từ Steam Store).
*   **Hậu quả:** CB Model gợi ý các game mà KNN không hề biết, dẫn đến việc không thể tính toán điểm số Hybrid (Synergy) cho các game này. Ngoài ra, tốc độ training CB bị chậm do dữ liệu rác.

### Giải pháp: Script `reduce_data.py`
Công cụ tiền xử lý (Preprocessing Tool) để đồng bộ không gian mẫu.
1.  **Whitelist:** Lấy danh sách `Game Name` từ dataset của KNN làm chuẩn.
2.  **Filtering:** Loại bỏ tất cả các dòng trong dataset CB nếu tên game không tồn tại trong Whitelist.
3.  **Kết quả:** Giảm dữ liệu CB xuống còn **~17,000 dòng**, đảm bảo tính nhất quán 100% giữa hai mô hình.

---

## 2. Kỹ Thuật Khớp Tên Mờ (Fuzzy Name Matching)

### Vấn đề: Xung đột Định danh (Identity Crisis)
ID của game trong dataset KNN (dạng số tự tăng) không khớp với Steam AppID chuẩn trong dataset CB. Do đó, không thể `JOIN` bảng dữ liệu bằng ID.

### Giải pháp: Hàm `normalize_name`
Hệ thống sử dụng kỹ thuật chuẩn hóa chuỗi để tạo khóa liên kết (Join Key).

**Quy tắc chuẩn hóa:**
```python
def normalize_name(title):
    # 1. Chuyển về chữ thường (Lowercase)
    # 2. Loại bỏ toàn bộ ký tự đặc biệt, khoảng trắng (Regex: [^a-z0-9])
    return re.sub(r'[^a-z0-9]', '', title.lower())
```

**Ví dụ thực tế:**
*   CB: `"The Witcher® 3: Wild Hunt"` $\rightarrow$ `thewitcher3wildhunt`
*   KNN: `"The Witcher 3: Wild Hunt"` $\rightarrow$ `thewitcher3wildhunt`
*   $\Rightarrow$ **MATCH (Trùng khớp)**.

---

## 3. Cơ Chế Tự Động Khôi Phục ID (Auto ID Recovery)

### Vấn đề: Mất mát dữ liệu trong luồng KNN
Trong một số trường hợp, file kết quả đầu ra của KNN (`rcm_games.csv`) chỉ chứa tên game và điểm số, bị thiếu cột `AppID` do quá trình xử lý vector. Điều này khiến module Hybrid không thể hiển thị hình ảnh hoặc link game.

### Giải pháp: Fallback Lookup
Module `Hybrid_recommendations_reader.py` được trang bị cơ chế "cứu hộ":
1.  Kiểm tra cột `app_id` trong file kết quả KNN.
2.  Nếu thiếu, hệ thống tự động load file gốc `final_games.csv`.
3.  Tạo từ điển ánh xạ (Mapping Dictionary): `{Title: AppID}`.
4.  Điền lại ID bị thiếu vào bảng kết quả trước khi gửi sang giao diện.

---

## 4. Bộ Lọc Chất Lượng & Chuẩn Hóa (Quality Control)

### 4.1. Shovelware Filtering (Lọc game rác)
Áp dụng tại lớp Content-Based để loại bỏ các game chất lượng thấp (giá rẻ, ít review) nhưng lại "spam" tags giống game bom tấn.
*   **Logic:** Nếu `Reviews < 100` VÀ `Price < 9.99$` $\rightarrow$ **Score *= 0.25**.

### 4.2. Score Normalization (Chuẩn hóa điểm số Hybrid)
Điểm số thô của KNN (Aggregate Distance) và CB (Cosine Similarity) có thang đo khác nhau. Hệ thống thực hiện chuẩn hóa Min-Max (phiên bản đơn giản hóa) để đưa về cùng trọng số:

```python
# Đưa về thang [0, 1]
knn_norm = knn_raw / max(knn_raw_list)
cb_norm = cb_raw / max(cb_raw_list)
```
Điều này ngăn chặn việc một mô hình có điểm số lớn (như KNN) lấn át hoàn toàn mô hình kia.

---

## 5. Kiến Trúc Kiểm Thử Tự Động (Automated Testing Architecture)

Hệ thống tách biệt hoàn toàn môi trường chạy (Production) và môi trường kiểm thử (Testing) để đảm bảo tính khách quan.

### 5.1. Test Scripts (`/test_scripts`)
*   Sử dụng cơ chế `sys.path.append` để dynamic import các module chính (`CB_model`, `KNN_model`) mà không cần copy code.
*   **Mocking:** Giả lập hành vi người dùng (Synthetic User Profiles) để test độ ổn định.

### 5.2. Visualization Engine
*   Sử dụng thư viện `matplotlib` với cấu hình `GridSpec` để vẽ Dashboard phức tạp.
*   Tự động phát hiện các trường hợp đặc biệt (ví dụ: `KNN Contribution = 0%`) để thêm chú thích (Footnote) giải thích vào biểu đồ, giúp báo cáo trực quan và dễ hiểu hơn.

---

## 6. Cấu Trúc Lưu Trữ (Storage Architecture)

Hệ thống tối ưu hóa I/O bằng cách chia nhỏ định dạng lưu trữ:

*   **Model States (`.pkl`):** Lưu trữ ma trận TF-IDF và SVD đã huấn luyện. Giúp khởi động Content-Based Model chỉ trong **< 1 giây** thay vì phải train lại từ đầu.
*   **User Data:**
    *   `cb_user_ratings.json`: Lưu trữ dạng JSON key-value, phù hợp cho việc tra cứu nhanh theo tên game.
    *   `your_games.csv`: Lưu trữ dạng bảng, tương thích với đầu vào của thuật toán KNN.
*   **Intermediate Results (`.csv`):** Các file `rcm_games.csv`, `cb_recommendations.csv` đóng vai trò là bộ đệm (Buffer) giao tiếp giữa các mô hình con và mô hình Hybrid.