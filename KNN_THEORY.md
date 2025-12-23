# Cơ Sở Lý Thuyết và Công Thức của KNN Model

## 1. Tổng Quan
**K-Nearest Neighbors (KNN)** trong hệ thống này là thuật toán **User-Based Collaborative Filtering (Lọc cộng tác dựa trên người dùng)**. Hệ thống không quan tâm game đó là thể loại gì, nó chỉ quan tâm: *"Những người chơi có gu giống bạn (Hàng xóm) đang chơi game gì khác? Nếu họ thích, khả năng cao bạn cũng sẽ thích."*

---

## 2. Quy Trình Xử Lý & Công Thức

### A. Ma trận Người dùng - Sản phẩm (User-Item Matrix)
Dữ liệu được biểu diễn dưới dạng **Sparse Matrix (Ma trận thưa)** để tiết kiệm bộ nhớ, vì một người dùng chỉ chơi một phần rất nhỏ trong tổng số game trên Steam.

Vector đánh giá của người dùng $u$ được định nghĩa:
$$ \vec{v}_u = [r_{u,1}, r_{u,2}, ..., r_{u,n}] $$

**Trong đó:**
*   $r_{u,i} = 1$: Người dùng thích (Like/Interested).
*   $r_{u,i} = -1$: Người dùng không thích (Dislike).
*   $r_{u,i} = 0$: Chưa tương tác.

### B. Bộ Lọc Hàng Xóm (Neighbor Selection Threshold)
Trước khi tính toán, hệ thống lọc bớt những người dùng không liên quan để giảm nhiễu.

$$ \text{Threshold} = \max(1, \lfloor N_{games} \times 0.7 \rfloor) $$

*   $N_{games}$: Tổng số game bạn đã chơi.
*   **Điều kiện:** Chỉ những user đã chơi trùng ít nhất 70% số game trong danh sách của bạn mới được đưa vào tập tính toán.

### C. Đo độ tương đồng (Cosine Distance)
Sử dụng khoảng cách Cosine để xác định ai là người có "gu" giống bạn nhất.

$$ \text{Dist}(u, v) = 1 - \cos(\vec{u}, \vec{v}) = 1 - \frac{\vec{u} \cdot \vec{v}}{||\vec{u}|| \times ||\vec{v}||} $$

*   $\text{Dist} \approx 0$: Hai người cực kỳ giống nhau (Soulmate).
*   $\text{Dist} \approx 1$: Không có điểm chung.
*   $\text{Dist} \approx 2$: Sở thích đối lập hoàn toàn.

### D. Trọng số Nâng cao (Advanced Weighting)
Ngoài khoảng cách, hệ thống áp dụng cơ chế thưởng điểm cho những người dùng thích các **Game Yêu Thích (Fav Games)** của bạn.

Trọng số cơ bản cho người dùng $v$:
$$ W_v = \frac{1}{10^{\sqrt{|\text{Fav}|}}} $$

**Cập nhật trọng số:**
Với mỗi game $g$ trong danh sách `Fav_Games` của bạn:
*   Nếu người dùng $v$ cũng thích $g$: $W_v = W_v \times 4$
*   Nếu người dùng $v$ ghét $g$: $W_v = W_v \times 0.5$ (hoặc loại bỏ).

### E. Tổng hợp ý kiến (Aggregation)
Dự đoán điểm số cho một game mới ($g$) dựa trên ý kiến của $K$ hàng xóm gần nhất.

$$ \text{Score}(g) = \sum_{v \in \text{Neighbors}} \left( \vec{v}_g \times \frac{W_v}{\text{Dist}(u, v) + \epsilon} \right) $$

**Trong đó:**
*   $\vec{v}_g$: Đánh giá của hàng xóm $v$ về game $g$ (1 hoặc -1).
*   $W_v$: Trọng số tin cậy của hàng xóm đó (từ bước D).
*   $\epsilon = 1e^{-9}$: Hằng số nhỏ để tránh lỗi chia cho 0 khi khoảng cách bằng 0.

---

## 3. Ứng Dụng Thực Tiễn trong Code (Data Flow)

Đây là cách các công thức trên tác động trực tiếp đến dữ liệu khi chạy `UI.py` hoặc `run_KNN.bat`:

### Bước 1: Sàng lọc ứng viên (The Filter)
*   **Input:** 1 triệu người dùng trên Steam. Bạn nhập vào 5 game (Witcher 3, Cyberpunk, ...).
*   **Code xử lý:** `user_review_counts >= threshold`.
*   **Tác động:** Loại bỏ 990,000 người chưa bao giờ chơi game nào trong danh sách của bạn. Chỉ giữ lại 10,000 người đã chơi ít nhất 3/5 game bạn nhập.
*   **Ý nghĩa:** Đảm bảo "hàng xóm" là những người thực sự hiểu gu của bạn, không phải người chơi ngẫu nhiên.

### Bước 2: Tìm người "cùng tần số" (Distance Calculation)
*   **Code xử lý:** `cosine_distances(user_vector_sparse, my_vector)`.
*   **Tác động:**
    *   Người A chơi Witcher 3 (Like), Cyberpunk (Like) giống hệt bạn $\rightarrow$ Dist = 0.1.
    *   Người B chơi Witcher 3 (Dislike) $\rightarrow$ Dist = 1.5.
*   **Kết quả:** Người A sẽ có tiếng nói trọng lượng gấp 15 lần người B trong việc gợi ý game mới.

### Bước 3: Boost Fan cứng (Fav Weighting)
*   **Tình huống:** Bạn đánh dấu **Thronebreaker** là "Favourite".
*   **Code xử lý:** `if game in fav_games_set: weights *= 4`.
*   **Tác động:** Những ai cũng thích *Thronebreaker* giống bạn sẽ được nhân 4 lần trọng số. Ý kiến của họ về các game khác sẽ trở thành "mệnh lệnh" cho hệ thống gợi ý.

### Bước 4: Bỏ phiếu và Gợi ý (Voting)
*   **Code xử lý:** Cộng dồn điểm số (Weighted Sum).
*   **Tình huống:**
    *   100 ông hàng xóm (Fan Witcher) đều Vote +1 cho game **"God of War"**.
    *   Khoảng cách Dist rất nhỏ, Weight rất lớn.
    *   $\rightarrow$ Điểm số của *God of War* tăng vọt lên 15.0.
*   **Kết quả:** *God of War* xuất hiện ở Rank 1 trong bảng kết quả KNN, dù bạn chưa hề nhắc đến tên game này. Đây chính là tính năng **"Khám phá" (Serendipity)**.

---

## 4. Đánh Giá Mô Hình

### Ưu Điểm
1.  **Tính Khám Phá (Serendipity):** Có khả năng gợi ý các game hoàn toàn khác thể loại nhưng hợp gu (Ví dụ: Fan RPG có thể được gợi ý game Đua xe nếu cộng đồng fan RPG cũng thích đua xe).
2.  **Không cần dữ liệu nội dung:** Không quan tâm game có tag gì, chỉ quan tâm nó có hay hay không.
3.  **Học theo xu hướng:** Nếu cộng đồng bắt đầu chơi một game mới, hệ thống sẽ tự động cập nhật gợi ý đó cho bạn.

### Nhược Điểm
1.  **Cold-start (Khởi đầu lạnh):** Không thể gợi ý game mới ra mắt chưa có ai chơi/review.
2.  **Popularity Bias:** Dễ bị thiên kiến về các game quá nổi tiếng (như CS:GO, PUBG) nếu không lọc kỹ.
3.  **Sparsity:** Nếu gu của bạn quá dị (game indie ít người chơi), sẽ khó tìm được hàng xóm.