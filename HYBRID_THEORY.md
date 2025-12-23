# Cơ Sở Lý Thuyết và Công Thức của Hybrid Model

## 1. Tổng Quan
**Hybrid Recommendation System (Hệ thống Gợi ý Lai)** là phương pháp kết hợp sức mạnh của **Content-Based Filtering (CB)** và **Collaborative Filtering (KNN)**. Mục tiêu là tạo ra một danh sách gợi ý vừa đảm bảo tính **liên quan về nội dung** (đúng gu), vừa đảm bảo tính **hấp dẫn cộng đồng** (game hay, không phải game rác).

Trong dự án này, chúng ta sử dụng phương pháp **Weighted Ensemble** kết hợp với **Fuzzy Name Matching** để hợp nhất dữ liệu từ nhiều nguồn khác nhau.

---

## 2. Quy Trình Xử Lý & Công Thức

### A. Đồng bộ dữ liệu (Fuzzy Name Matching)
Do dữ liệu từ KNN và CB đến từ hai nguồn khác nhau, ID của game có thể không khớp. Hệ thống sử dụng kỹ thuật chuẩn hóa tên để ghép nối.

Hàm chuẩn hóa $f(name)$:
$$ f(\text{name}) = \text{lowercase}(\text{remove\_special\_chars}(\text{name})) $$

*   **Ví dụ:**
    *   CB: "The Witcher® 3: Wild Hunt" $\rightarrow$ `thewitcher3wildhunt`
    *   KNN: "The Witcher 3: Wild Hunt" $\rightarrow$ `thewitcher3wildhunt`
    *   $\Rightarrow$ **Khớp (Match)**.

### B. Chuẩn hóa Điểm số (Score Normalization)
Điểm số (Score) của KNN và CB có thang đo khác nhau (KNN có thể lên tới 200, CB chỉ max là 1). Cần đưa về khoảng $[0, 1]$.

$$ S'_{KNN} = \frac{S_{KNN}}{\max(S_{KNN\_all})} $$
$$ S'_{CB} = \frac{S_{CB}}{\max(S_{CB\_all})} $$

### C. Tổng hợp cơ bản (Weighted Combination)
Tính điểm trung bình cộng có trọng số giữa hai mô hình.

$$ \text{Base Score} = (S'_{KNN} \times W_{KNN}) + (S'_{CB} \times W_{CB}) $$

**Trong code:**
*   $W_{KNN} = 0.5$ (hoặc 0.6)
*   $W_{CB} = 0.5$ (hoặc 0.4)

### D. Cơ chế Cộng hưởng (Synergy Boost) - *Quan Trọng*
Đây là "bí thuật" giúp các siêu phẩm (Masterpiece) leo lên Top. Hệ thống thưởng điểm cho các game được **cả hai mô hình** cùng đề xuất.

**Trường hợp 1: Game có sự đồng thuận (Giao thoa)**
Nếu $S'_{KNN} > 0$ VÀ $S'_{CB} > 0$:
$$ \text{Boost} = \sqrt{S'_{KNN} \times S'_{CB}} \times 0.5 $$
$$ \text{Final Score} = \text{Base Score} + \text{Boost} $$

*   *Giải thích:* Sử dụng trung bình nhân (Geometric Mean) để tạo ra sự cộng hưởng. Game phải tốt ở cả 2 mặt mới có Boost cao.

**Trường hợp 2: Game đơn lẻ (Chỉ xuất hiện 1 bên)**
Nếu chỉ có $S'_{KNN} > 0$ HOẶC chỉ có $S'_{CB} > 0$:
$$ \text{Final Score} = \text{Base Score} \times 0.8 $$

*   *Giải thích:* Áp dụng hình phạt (Penalty) 20% để ưu tiên những game có sự đồng thuận cao hơn.

---

## 3. Ứng Dụng Thực Tiễn trong Code (Data Flow)

Dưới đây là quy trình xử lý dữ liệu thực tế khi bạn chạy file `run_hybrid.py`:

### Bước 1: Quét sâu (Deep Scan)
*   **Vấn đề:** Nếu chỉ lấy Top 20 mỗi bên, khả năng trùng nhau rất thấp (Game A đứng thứ 5 bên KNN nhưng đứng thứ 50 bên CB sẽ bị loại).
*   **Giải pháp:** Code đọc **Top 200** game từ mỗi file kết quả (`rcm_games.csv` và `cb_recommendations.csv`).
*   **Tác dụng:** Mở rộng "vùng phủ sóng" để tìm kiếm tối đa các điểm giao thoa.

### Bước 2: Ghép nối (Merging)
*   Hệ thống tạo một bảng chung, sử dụng `normalized_title` làm khóa chính (Key).
*   Nếu game bị thiếu AppID (do lỗi dữ liệu KNN), hệ thống tự động tra cứu lại trong `final_games.csv` để điền ID chuẩn vào.

### Bước 3: Tính điểm & Xếp hạng (Scoring & Ranking)
**Ví dụ thực tế:**
1.  **Game "God of War":**
    *   KNN (Cộng đồng): Rank 4 (Rất cao) $\rightarrow$ $S'_{KNN} \approx 0.9$.
    *   CB (Nội dung): Rank 35 (Khá) $\rightarrow$ $S'_{CB} \approx 0.4$.
    *   **Kết quả:** Có giao thoa $\rightarrow$ Được cộng thêm điểm Boost $\rightarrow$ Nhảy lên **Top 2 Hybrid**.
2.  **Game "Euro Truck Simulator 2":**
    *   KNN: Rank 9 (Cao - do game thủ chơi tạp) $\rightarrow$ $S'_{KNN} \approx 0.7$.
    *   CB: Rank N/A (Thấp - do khác thể loại RPG) $\rightarrow$ $S'_{CB} = 0$.
    *   **Kết quả:** Không có Boost, bị phạt 20% $\rightarrow$ Tụt xuống **Rank 20**.

### Bước 4: Xuất kết quả
*   Tạo file `hybrid_ranking.csv`.
*   Hiển thị giao diện UI với mã màu:
    *   **Xanh lá:** Game được cả 2 mô hình đề xuất (Highly Recommended).
    *   **Trắng:** Game chỉ do 1 mô hình đề xuất.

---

## 4. Đánh Giá Mô Hình

### Ưu Điểm
1.  **Độ chính xác vượt trội:** Khắc phục điểm yếu của từng mô hình đơn lẻ.
2.  **Giải quyết vấn đề "Lệch pha":** KNN có thể gợi ý game "lạc quẻ", CB có thể gợi ý game "rác". Hybrid dùng cái này để kiểm chứng cái kia.
3.  **Linh hoạt:** Có thể điều chỉnh trọng số ($W_{KNN}, W_{CB}$) để ưu tiên theo xu hướng cộng đồng hoặc theo nội dung thuần túy.
4.  **Robust (Bền vững):** Nhờ cơ chế Name Matching, hệ thống vẫn chạy tốt ngay cả khi ID game bị lỗi hoặc dữ liệu không đồng nhất.

### Nhược Điểm
1.  **Chi phí tính toán:** Phải chạy cả 2 mô hình con trước khi chạy Hybrid.
2.  **Độ phức tạp:** Code xử lý ghép nối dữ liệu (Merge) phức tạp hơn.
3.  **Phụ thuộc dữ liệu:** Cần cả dữ liệu Rating của người dùng và Metadata của game để hoạt động tối ưu.