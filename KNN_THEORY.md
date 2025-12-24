# CHƯƠNG 1: MÔ HÌNH COLLABORATIVE FILTERING (KNN)

## 1.1. Tổng Quan Phương Pháp
Mô hình sử dụng thuật toán **User-Based Collaborative Filtering** với hướng tiếp cận bộ nhớ (Memory-based). Thay vì học các tham số mô hình phức tạp (như Matrix Factorization), hệ thống tính toán trực tiếp sự tương đồng giữa người dùng hiện tại và cộng đồng người chơi (Neighbors) để đưa ra dự đoán.

Giả thuyết cốt lõi: *"Những người dùng có lịch sử đánh giá game tương tự trong quá khứ sẽ có xu hướng thích những game giống nhau trong tương lai."*

---

## 1.2. Quy Trình Xử Lý Toán Học

### Bước 1: Xây Dựng Ma Trận Tương Tác (Interaction Matrix Construction)
Dữ liệu được biểu diễn dưới dạng ma trận thưa (Sparse Matrix) để tối ưu hóa bộ nhớ:

*   Mỗi hàng là một User ($u$).
*   Mỗi cột là một Game ($i$).
*   Giá trị $r_{ui}$:
    *   $1$: Thích (Like/Interested).
    *   $-1$: Không thích (Dislike).
    *   $0$: Chưa tương tác.

Trong code, ma trận này được xây dựng bằng `scipy.sparse.csr_matrix` từ danh sách `(row_indices, col_indices, data)`.

### Bước 2: Sàng Lọc Hàng Xóm (Neighbor Filtering)
Để giảm nhiễu và tăng tốc độ, hệ thống không so sánh với toàn bộ 1 triệu người dùng, mà áp dụng bộ lọc sơ cấp:

$$ \text{Threshold} = \max(1, \lfloor N_{games} \times \alpha \rfloor) $$

*   $N_{games}$: Số lượng game người dùng hiện tại đã chơi.
*   $\alpha$: Hệ số lọc (Match Percentage). Trong thực nghiệm, $\alpha = 0.5$ (50%).
*   **Điều kiện:** Chỉ những user đã tương tác với ít nhất `Threshold` game trùng với người dùng hiện tại mới được đưa vào tập ứng viên hàng xóm ($U_{candidate}$).

### Bước 3: Đo Độ Tương Đồng (Similarity Measurement)
Sử dụng **Cosine Distance** để đo khoảng cách giữa vector người dùng hiện tại ($\vec{u}$) và vector hàng xóm ($\vec{v}$).

$$ \text{Distance}(u, v) = 1 - \text{Similarity}(u, v) = 1 - \frac{\vec{u} \cdot \vec{v}}{||\vec{u}|| \times ||\vec{v}||} $$

*   $\vec{u} \cdot \vec{v}$: Tích vô hướng (Dot Product).
*   Code sử dụng `sklearn.metrics.pairwise.cosine_distances`.

### Bước 4: Tính Trọng Số Đóng Góp (Weighting Scheme)
Hệ thống áp dụng cơ chế trọng số động (Dynamic Weighting) để ưu tiên những hàng xóm "chất lượng":

**a. Trọng số cơ bản (Base Weight):**
$$ W_{base} = \frac{1}{10^{\sqrt{|\text{Fav}|}}} $$
*(Giảm trọng số nếu người dùng có quá nhiều game yêu thích, tránh loãng).*

**b. Điều chỉnh theo Game Yêu Thích (Favorite Boosting):**
Với mỗi game $g$ mà người dùng đánh dấu là "Yêu thích" (Favourite):
*   Nếu hàng xóm cũng thích $g$: $W_v = W_v \times 4$ (Tăng độ tin cậy gấp 4 lần).
*   Nếu hàng xóm ghét $g$: $W_v = W_v / 2$ (Giảm độ tin cậy).

### Bước 5: Dự Đoán & Xếp Hạng (Prediction & Ranking)
Điểm số dự đoán cho game $i$ được tính bằng tổng trọng số của $K$ hàng xóm gần nhất (K-Nearest Neighbors).

$$ \text{Score}(i) = \sum_{v \in \text{KNN}} \left( r_{vi} \times \frac{W_v}{\text{Distance}(u, v) + \epsilon} \right) $$

*   $r_{vi}$: Đánh giá của hàng xóm $v$ cho game $i$.
*   $\epsilon = 1e^{-9}$: Hằng số làm mượt (Smoothing) để tránh lỗi chia cho 0.

---

## 1.3. Thiết Kế Luồng Dữ Liệu (Implementation Pipeline)

Dựa trên file `test_knn_model.py` và `Data_handler.py`, quy trình thực tế diễn ra như sau:

1.  **Input Processing:**
    *   Đọc file `your_games.csv` (Lịch sử chơi) và `fav_games.csv` (Danh sách yêu thích).
    *   Chuyển đổi review dạng chữ (Like, Interested) sang dạng số (1, 0.5, -1).

2.  **Vectorization:**
    *   Biến đổi `your_games` thành vector thưa `my_vector`.
    *   Lọc tập dữ liệu lớn `final_reviews.csv` để tạo `user_vector_sparse`.

3.  **KNN Execution:**
    *   Tính khoảng cách Cosine.
    *   Lấy Top $K$ hàng xóm gần nhất (Mặc định $K=1000$ hoặc $K=len(candidates)$).
    *   Nhân ma trận thưa với vector trọng số để ra điểm số tổng hợp.

4.  **Ranking & Filtering:**
    *   Sắp xếp danh sách game theo điểm số giảm dần.
    *   **Post-filtering:** Loại bỏ các game người dùng đã chơi (nằm trong `not_played_games_id`).
    *   Tách riêng danh sách **Wishlist Recommendations** (Gợi ý dựa trên game đang quan tâm).

---

## 1.4. Đánh Giá & Tối Ưu (Evaluation & Tuning)

Trong quá trình kiểm thử (Benchmarking), mô hình đã được tinh chỉnh tham số để đạt hiệu quả tối ưu:

*   **Vấn đề Cold-Start:** Với người dùng mới (ít game), ngưỡng lọc $\alpha$ được hạ xuống $0.3$ để đảm bảo tìm được đủ hàng xóm.
*   **Vấn đề Precision/Recall:**
    *   Thực nghiệm cho thấy Precision@10 đạt **15.45%** trên tập người dùng tích cực (>50 reviews).
    *   Recall@10 đạt **10.66%**, chứng tỏ khả năng khôi phục lại sở thích người dùng khá tốt trong không gian dữ liệu thưa.