# Cơ Sở Lý Thuyết và Công Thức của Content-Based Model

## 1. Tổng Quan
**Content-Based Filtering (Lọc dựa trên nội dung)** là phương pháp gợi ý dựa trên sự tương đồng giữa hồ sơ người dùng và đặc điểm của vật phẩm. Trong dự án Steam ML, chúng ta xây dựng vector đặc trưng cho mỗi game từ **Genres (Thể loại)** và **Tags (Nhãn)**, sau đó so sánh với vector sở thích của người dùng.

---

## 2. Quy Trình Xử Lý & Công Thức

### A. Xử lý Trọng số Vị trí (Positional Weighting)
Trước khi vector hóa, văn bản được xử lý để tăng cường tầm quan trọng của các từ khóa chính. Hệ thống mô phỏng cách Steam xếp hạng Tag (Tag đầu tiên quan trọng nhất).

*   **Genres:** Nhân bản **4 lần** (Vì thể loại là yếu tố cốt lõi).
*   **Top 3 Tags:** Nhân bản **3 lần**.
*   **Top 4-10 Tags:** Nhân bản **2 lần**.
*   **Các Tags còn lại:** Giữ nguyên (1 lần).

**Tác dụng:** Giúp thuật toán ưu tiên tìm kiếm các game cùng thể loại chính (VD: RPG) trước khi xét đến các yếu tố phụ (VD: Singleplayer).

### B. TF-IDF (Term Frequency - Inverse Document Frequency)
Chuyển đổi văn bản thành vector số học.

$$ \text{TF-IDF}(t, d) = \text{TF}(t, d) \times \text{IDF}(t) $$

*   **$\text{TF}(t, d)$**: Tần suất từ $t$ xuất hiện trong mô tả game $d$ (đã được nhân bản ở bước A).
*   **$\text{IDF}(t) = \log(\frac{N}{df_t})$**: Đánh giá độ hiếm của từ. Từ xuất hiện ở quá nhiều game (như "Indie", "Action") sẽ có trọng số thấp, từ đặc trưng (như "Cyberpunk", "Souls-like") sẽ có trọng số cao.

### C. Giảm chiều dữ liệu (SVD / LSA)
Sử dụng **Truncated SVD** để giảm số chiều của ma trận TF-IDF xuống còn **100 chiều**.

$$ A \approx U \times \Sigma \times V^T $$

**Tác dụng:**
*   **Latent Semantic Analysis (LSA):** Giúp máy tính hiểu "ngữ nghĩa" thay vì chỉ bắt từ khóa. Ví dụ: Máy sẽ hiểu *FPS* và *Shooter* có liên quan đến nhau.
*   **Xử lý ma trận thưa:** Giúp tính toán nhanh hơn và loại bỏ nhiễu.

### D. Vector Hồ sơ Người dùng ($V_{user}$)
Được tính bằng trung bình cộng có trọng số (Weighted Average) của các game người dùng đã đánh giá.

$$ V_{user} = \frac{\sum (V_{game_i} \times w_i)}{\sum w_i} $$

**Trong đó:**
*   $V_{game_i}$: Vector đặc trưng của game thứ $i$.
*   $w_i$: Trọng số dựa trên Rating của người dùng.
    *   Rating 5 sao $\rightarrow w = 3$
    *   Rating 4 sao $\rightarrow w = 2$
    *   Rating 3 sao $\rightarrow w = 1$

### E. Tính Điểm Tương Đồng ($S_{sim}$)
Sử dụng **Cosine Similarity** để đo góc giữa vector người dùng và vector game.

$$ S_{sim}(u, g) = \cos(V_{user}, V_{game}) = \frac{V_{user} \cdot V_{game}}{||V_{user}|| \times ||V_{game}||} $$

Kết quả $S_{sim}$ nằm trong khoảng $[-1, 1]$, càng gần 1 thì game càng phù hợp với sở thích người dùng.

### F. Điểm Phổ biến ($S_{pop}$)
Sử dụng Logarithm để chuẩn hóa số lượng Review, tránh việc game bom tấn lấn át hoàn toàn game Indie.

$$ S_{pop} = \frac{\log_{10}(\text{Total Reviews} + 1)}{10.0} $$

### G. Điểm Số Cuối Cùng & Bộ Lọc
Điểm cuối cùng ($Final\_Score$) là sự kết hợp giữa độ tương đồng và độ phổ biến, áp dụng thêm các hình phạt (Penalty) để lọc rác.

$$ \text{Base Score} = (S_{sim} \times 0.85) + (S_{pop} \times 0.15) $$

**Bộ lọc Shovelware (Shovelware Filter):**
Nếu game có ít hơn 100 review (hoặc dữ liệu lỗi):
1.  **Nếu giá < $9.99:**
    *   $Final\_Score = \text{Base Score} \times 0.25$ (Phạt nặng 75% - Nghi ngờ game rác).
    *   *Ngoại lệ:* Nếu $S_{sim} > 0.8$ (Rất giống) thì chỉ phạt nhẹ ($\times 0.6$).
2.  **Nếu giá $\ge$ $9.99:**
    *   $Final\_Score = \text{Base Score} \times 0.9$ (Phạt nhẹ 10% do thiếu dữ liệu tin cậy).

---

Dưới đây là cách các công thức toán học trên tác động trực tiếp đến dữ liệu trong quá trình chạy `ContentBased_model.py`:

### Bước 1: Tiền xử lý dữ liệu (Positional Weighting)
*   **Dữ liệu đầu vào:** Một dòng trong CSV: `Genres: "RPG", Tags: "Open World, Story Rich"`.
*   **Xử lý trong Code:** Hàm `prepare_content_features` thực hiện nhân bản chuỗi (String Multiplication).
*   **Dữ liệu đầu ra:** Chuỗi văn bản mới: `"RPG RPG RPG RPG Open World Open World Open World Story Rich Story Rich Story Rich"`.
*   **Tác dụng thực tế:** Khi đưa vào TF-IDF, từ "RPG" sẽ có tần suất xuất hiện (Term Frequency) cao gấp 4 lần bình thường. Điều này ép máy tính phải tìm các game có chữ "RPG" trước tiên.

### Bước 2: Ma trận hóa & Giảm chiều (TF-IDF + SVD)
*   **Code:** `vectorizer.fit_transform()` sau đó là `svd.fit_transform()`.
*   **Biến đổi dữ liệu:**
    1.  Từ 110,000 dòng văn bản game.
    2.  $\rightarrow$ Ma trận thưa (Sparse Matrix) khổng lồ: `(110000 dòng x 5000 cột từ khóa)`. Hầu hết là số 0.
    3.  $\rightarrow$ **Ma trận đặc (Dense Matrix):** `(110000 dòng x 100 cột)`.
*   **Tác dụng thực tế:** Thay vì lưu trữ hàng ngàn số 0 vô nghĩa, mỗi game giờ đây được đại diện bởi **100 con số thực** (Ví dụ: `[0.12, -0.5, 0.88, ...]`). 100 con số này là "tọa độ" của game trong không gian ngữ nghĩa.

### Bước 3: Tạo "Tâm điểm" sở thích (Weighted User Profile)
*   **Tình huống:** Bạn thích *Witcher 3* (5 sao) và thấy *Among Us* bình thường (3 sao).
*   **Xử lý trong Code:**
    *   Trọng số: *Witcher 3* ($w=3$), *Among Us* ($w=1$).
    *   Công thức `np.average`:
        $$ \frac{(Vector_{Witcher} \times 3) + (Vector_{AmongUs} \times 1)}{4} $$
*   **Tác dụng thực tế:** Vector kết quả ($V_{user}$) sẽ nằm rất gần tọa độ của *Witcher 3* và bị kéo lệch một chút về phía *Among Us*. Khi tìm kiếm, hệ thống sẽ quét xung quanh tọa độ này.

### Bước 4: Quét và Lọc (Similarity & Filtering)
*   **Code:** `cosine_similarity(user_profile, all_games)`.
*   **Tác động:** Tạo ra một danh sách 110,000 con số (từ -1 đến 1).
    *   Game *Skyrim*: 0.85 (Góc rất nhỏ $\rightarrow$ Rất giống).
    *   Game *FIFA 23*: 0.05 (Góc vuông $\rightarrow$ Không liên quan).
*   **Logic Lọc (Shovelware Filter):**
    *   Máy tính tìm thấy một game clone rẻ tiền có tag y hệt *Witcher 3*. Độ giống lên tới **0.9**.
    *   Code kiểm tra: `Price < 9.99` và `Review < 100`.
    *   **Hành động:** Nhân điểm 0.9 với 0.25 $\rightarrow$ Còn **0.225**.
    *   **Kết quả:** Game rác bị đá văng khỏi Top 20, nhường chỗ cho game xịn.
---
## 4. Ưu và Nhược Điểm

### Ưu Điểm
1.  **Cá nhân hóa cao:** Không phụ thuộc vào người dùng khác, chỉ tập trung vào sở thích riêng biệt của người dùng.
2.  **Giải thích được:** Có thể giải thích lý do gợi ý (VD: "Gợi ý game này vì bạn thích game A, B").
3.  **Khả năng "Cold-start" cho Item mới:** Có thể gợi ý các game vừa mới ra mắt (chưa có rating) miễn là có thông tin Tags/Genres.

### Nhược Điểm
1.  **Over-specialization:** Chỉ gợi ý các game "na ná" những gì đã chơi, khó khám phá ra các thể loại mới lạ.
2.  **Phụ thuộc vào Metadata:** Nếu Tags/Genres của game bị gắn sai, kết quả sẽ không chính xác.
## 3. Ứng Dụng Thực Tiễn trong Code (Data Flow)