# Hướng Dẫn Kiểm Thử & Đánh Giá Hệ Thống (Testing Guide)

Tài liệu này hướng dẫn quy trình **Benchmark** (Đánh giá hiệu năng) của hệ thống gợi ý game Steam. Thay vì kiểm tra thủ công từng người, chúng ta sử dụng tập dữ liệu **50 người dùng ảo (Synthetic Users)** với các hồ sơ sở thích khác nhau để đo lường độ chính xác và tính ổn định của thuật toán.

---

## 1. Cấu Trúc Kiểm Thử

Quy trình gồm 3 bước tự động hóa:
1.  **Generate Data:** Tạo ra 50 người dùng với các "Persona" (Kiểu người chơi) cụ thể (VD: Fan RPG, Fan FPS, Người chơi ngẫu nhiên...).
2.  **Run Benchmark:** Hệ thống tự động nạp dữ liệu của từng người dùng ảo vào KNN và Content-Based, sau đó chạy Hybrid Model để lấy kết quả.
3.  **Visualization:** Vẽ biểu đồ phân tích từ kết quả thu được.

---

## 2. Chuẩn Bị Môi Trường

Trước khi chạy test, đảm bảo bạn đã cài đặt đủ thư viện và Model đã được Train:

1.  Cài đặt thư viện vẽ biểu đồ:
    ```bash
    pip install matplotlib seaborn pandas
    ```
2.  Đảm bảo file `cb_model.pkl` đã tồn tại trong thư mục `CB_model` (Nếu chưa, hãy chạy `run_CB.bat` -> Train Model).

---

## 3. Quy Trình Thực Hiện

Mở Terminal (Command Prompt) và di chuyển vào thư mục chứa script test (ví dụ `test_scripts`):
```bash
cd test_scripts
```

### Bước 1: Tạo Dữ Liệu Giả Lập
Chạy script để sinh ra dữ liệu hành vi của 50 người dùng ảo.
```bash
python generate_synthetic_users.py
```
*   **Output:** Tạo thư mục `synthetic_data/` chứa 50 folder con (Mỗi folder là một user với file `your_games.csv` và `cb_user_ratings.json` tương ứng).
*   **Mục đích:** Giả lập các tình huống người dùng thực tế (Người thích hành động, người thích chiến thuật...).

### Bước 2: Chạy Benchmark (Tự động hóa)
Script này sẽ lần lượt đóng vai 50 user, nạp dữ liệu vào hệ thống và ghi lại game Top 1 được gợi ý.
```bash
python run_benchmark.py
```
*   **Thời gian chạy:** Khoảng 1-3 phút.
*   **Output:** File `benchmark_report.csv` chứa bảng kết quả chi tiết (User nào -> Gợi ý game gì -> Điểm số bao nhiêu).
*   **Lưu ý:** Script sẽ tự động import các model từ thư mục cha, bạn không cần copy file đi đâu cả.

### Bước 3: Trực Quan Hóa Kết Quả
Biến file CSV thành các biểu đồ đánh giá.
```bash
python visualize_results.py
```
*   **Output:**
    *   Hiển thị cửa sổ chứa 4 biểu đồ phân tích.
    *   Lưu ảnh biểu đồ vào file `benchmark_analysis.png`.

---

## 4. Cách Đọc Biểu Đồ & Phân Tích

Khi bảo vệ đồ án, bạn sử dụng các biểu đồ này để giải thích:

### A. Scatter Plot: KNN vs Content-Based
*   **Trục X:** Điểm số từ KNN (Cộng đồng).
*   **Trục Y:** Điểm số từ Content-Based (Nội dung).
*   **Phân tích:**
    *   Các điểm nằm ở **góc trên bên phải**: Game được cả 2 mô hình đánh giá cao $\rightarrow$ Gợi ý chất lượng nhất (Hybrid hiệu quả).
    *   Các điểm nằm sát trục: Game chỉ mạnh về một yếu tố (Trend hoặc Nội dung).

### B. Bar Chart: Điểm số trung bình theo nhóm (Persona)
*   Biểu đồ này cho biết hệ thống gợi ý tốt nhất cho đối tượng nào.
*   **Kỳ vọng:** Nhóm "RPG_Fan" hoặc "FPS_Fan" nên có điểm cao hơn nhóm "Random_Player" (vì người chơi ngẫu nhiên rất khó đoán).

### C. Top Games (Biểu đồ tần suất)
*   Thống kê những game nào xuất hiện nhiều nhất ở vị trí Top 1.
*   **Phân tích:**
    *   Nếu biểu đồ đa dạng (nhiều game khác nhau): Hệ thống có tính **Cá nhân hóa (Personalization)** tốt.
    *   Nếu chỉ có 1-2 cột cao vút (VD: Ai cũng được gợi ý *CS:GO*): Hệ thống bị lỗi **Thiên kiến phổ biến (Popularity Bias)**.

---

## 5. Dọn Dẹp Sau Khi Test
Sau khi chạy test xong, hệ thống của bạn đang lưu dữ liệu của user ảo cuối cùng (User 50). Để quay lại sử dụng bình thường:
1.  Chạy `run_KNN.bat` $\rightarrow$ Xóa các game trong danh sách "Played".
2.  Chạy `run_CB.bat` $\rightarrow$ Bấm "Clear All Ratings".
3.  Nhập lại dữ liệu thật của bạn.