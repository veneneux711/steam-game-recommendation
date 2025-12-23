# Chi Tiết Kỹ Thuật và Xử Lý Dữ Liệu (Technical Details)

Tài liệu này mô tả các kỹ thuật xử lý dữ liệu, các công cụ tiện ích và các bộ lọc logic được áp dụng trong dự án để đảm bảo hệ thống hoạt động trơn tru và chính xác.

## 1. Đồng Bộ Hóa Dữ Liệu (Data Synchronization)

### Vấn đề: Sự chênh lệch dữ liệu (Data Bloat & Mismatch)
Dự án sử dụng hai nguồn dữ liệu khác nhau:
1.  **KNN Dataset:** ~15,000 game (Có dữ liệu hành vi người chơi).
2.  **Content-Based Dataset:** ~110,000 game (Dữ liệu thô từ Steam Store).

**Hậu quả:**
*   CB Model gợi ý các game mà KNN không hề biết (không có dữ liệu user để kiểm chứng).
*   Tốc độ huấn luyện (Training) của CB Model rất chậm do phải xử lý hàng chục ngàn game rác/ít người chơi.

### Giải pháp: Script `reduce_data.py`
Chúng tôi phát triển một công cụ để "gọt giũa" dữ liệu CB dựa trên KNN.

**Nguyên lý hoạt động:**
1.  **Whitelist:** Lấy danh sách tên game từ KNN làm danh sách chuẩn.
2.  **Normalize:** Chuẩn hóa tên game của cả 2 bên (xóa ký tự đặc biệt, chuyển về chữ thường) để so sánh.
3.  **Filtering:** Loại bỏ tất cả các game trong file CB nếu tên game đó không tồn tại trong Whitelist của KNN.

**Kết quả:**
*   Giảm dữ liệu CB từ **111,452 dòng** xuống còn **~17,000 dòng**.
*   Đảm bảo 100% game được gợi ý đều có dữ liệu ở cả 2 mô hình, tối đa hóa khả năng giao thoa (Overlap) cho Hybrid Model.

---

## 2. Kỹ Thuật Khớp Tên Mờ (Fuzzy Name Matching)

### Vấn đề: Xung đột Định danh (Identity Crisis)
ID của game trong bộ dữ liệu KNN không phải là Steam AppID chuẩn (Ví dụ: Witcher 3 có ID là `53715` thay vì `292030`). Do đó, không thể ghép bảng (Merge) dựa trên cột `AppID`.

### Giải pháp: Hàm `normalize_name`
Hệ thống sử dụng kỹ thuật so sánh chuỗi đã qua xử lý để làm "Cầu nối" giữa hai mô hình.

**Quy tắc chuẩn hóa:**
```python
def normalize_name(title):
    # 1. Chuyển về chữ thường (Lowercase)
    # 2. Loại bỏ toàn bộ ký tự đặc biệt (chỉ giữ a-z, 0-9)
    return re.sub(r'[^a-z0-9]', '', title.lower())
```

**Ví dụ thực tế:**
*   Bên CB: `"The Witcher® 3: Wild Hunt"` $\rightarrow$ `thewitcher3wildhunt`
*   Bên KNN: `"The Witcher 3: Wild Hunt"` $\rightarrow$ `thewitcher3wildhunt`
*   $\Rightarrow$ **MATCH (Trùng khớp)**.

---

## 3. Bộ Lọc Chất Lượng (Shovelware Filtering)

### Vấn đề: Game rác (Shovelware)
Trên Steam có rất nhiều game chất lượng thấp, giá rẻ, nhưng lại copy thẻ tag của các game bom tấn.
*   *Ví dụ:* Một game 18+ giá $0.99 có tag "RPG", "Open World" giống hệt *The Witcher 3*.
*   Nếu chỉ so sánh Tag (TF-IDF), game rác này sẽ có điểm tương đồng rất cao.

### Giải pháp: Logic Phạt điểm (Penalty Logic)
Hệ thống áp dụng bộ lọc trong `ContentBased_model.py` dựa trên **Giá tiền** và **Số lượng Review**.

**Logic Code:**
```python
if total_reviews < 100:  # Nếu game ít người chơi/thiếu dữ liệu
    if price < 9.99:     # VÀ giá rẻ bèo (< $10)
        # -> Khả năng cao là game rác
        final_score *= 0.25  # Phạt nặng (Giảm 75% điểm)
    else:
        # -> Có thể là game Indie xịn hoặc game cũ
        final_score *= 0.9   # Phạt nhẹ (Giảm 10% điểm)
```

**Tác dụng:** Loại bỏ các game "ký sinh" khỏi bảng xếp hạng, giữ lại các game chất lượng cao.

---

## 4. Xử Lý Lỗi & An Toàn Dữ Liệu (Robustness)

### Vấn đề: Crash khi file rỗng
Khi người dùng chưa nhập dữ liệu (List yêu thích trống, List đã chơi trống), các hàm `pd.read_csv` thông thường sẽ gây crash chương trình (`EmptyDataError`).

### Giải pháp: Safe Data Loading
Trong `Data_handler.py`, hệ thống kiểm tra kích thước file trước khi đọc.

1.  **Kiểm tra tồn tại:** `if not os.path.exists(path)...`
2.  **Kiểm tra kích thước:** `if os.path.getsize(path) == 0...`
3.  **Tự động sửa:** Nếu file lỗi hoặc trống, hệ thống tự động tạo một `DataFrame` rỗng với đúng cấu trúc cột (`columns=['gameID', 'gameName', ...]`) để chương trình tiếp tục chạy mượt mà.

---

## 5. Cấu Trúc Lưu Trữ (Storage Architecture)

Hệ thống sử dụng cơ chế lưu trữ lai để tối ưu hóa việc đọc ghi:

*   **Dữ liệu tĩnh (Static Data):** Lưu dạng `.csv` (Dữ liệu game, Kết quả gợi ý). Dễ dàng kiểm tra bằng Excel.
*   **Dữ liệu mô hình (Model State):** Lưu dạng `.pkl` (Pickle). Lưu trữ ma trận SVD và Vectorizer đã huấn luyện để không phải tính toán lại mỗi lần mở app.
*   **Dữ liệu người dùng (User Data):**
    *   Content-Based: Lưu `.json` (Dễ đọc, cấu trúc linh hoạt).
    *   KNN: Lưu `.csv` (Tương thích với định dạng dataset gốc).