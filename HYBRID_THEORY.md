# CHƯƠNG 3: CƠ SỞ LÝ THUYẾT MÔ HÌNH HYBRID (HYBRID RECOMMENDATION MODEL)

## 3.1. Tổng Quan Phương Pháp
Hệ thống sử dụng kiến trúc **Weighted Hybrid (Lai ghép có trọng số)** kết hợp với chiến lược **Synergy Re-ranking (Tái xếp hạng dựa trên sự cộng hưởng)**.

Thay vì chỉ gộp kết quả một cách đơn thuần, hệ thống hoạt động như một "bộ lọc thông minh" (Smart Filter) nhằm giải quyết hai vấn đề cốt lõi của các hệ thống gợi ý đơn lẻ:
1.  **Vấn đề của Content-Based:** Sự lặp lại nhàm chán (Over-specialization) và thiếu tính khám phá.
2.  **Vấn đề của Collaborative Filtering (KNN):** Thiên kiến phổ biến (Popularity Bias) và nhiễu dữ liệu.

Mô hình Hybrid sẽ tìm kiếm sự **"Đồng thuận" (Consensus)** giữa nội dung game và hành vi cộng đồng để đưa ra những gợi ý có độ tin cậy cao nhất.

---

## 3.2. Quy Trình Xử Lý Toán Học

Quá trình tính toán điểm số Hybrid trải qua 3 bước xử lý chính:

### Bước 1: Đồng bộ và Chuẩn hóa Dữ liệu (Normalization)

Do dữ liệu đầu vào đến từ hai không gian vector khác nhau (KNN dùng ma trận thưa User-Item, CB dùng ma trận đặc Metadata), hệ thống cần thực hiện hai phép chuẩn hóa:

**a. Chuẩn hóa Định danh (Identity Normalization):**
Sử dụng kỹ thuật **Fuzzy Name Matching** để khớp nối các game khi ID không đồng nhất hoặc bị thiếu.
$$ f(\text{name}) = \text{lowercase}(\text{regex\_remove\_special\_chars}(\text{name})) $$
*(Ví dụ: "The Witcher® 3: Wild Hunt" và "the witcher 3" sẽ được xử lý thành cùng một key: `thewitcher3wildhunt`).*

**b. Chuẩn hóa Điểm số (Score Scaling):**
Đưa điểm số của KNN (Distance-based score) và CB (Cosine Similarity) về cùng một hệ quy chiếu $[0, 1]$ để thực hiện phép cộng đại số.

$$ S'_{KNN} = \frac{S_{KNN}}{\max(S_{KNN\_all})} $$
$$ S'_{CB} = \frac{S_{CB}}{\max(S_{CB\_all})} $$

---

### Bước 2: Tính Điểm Nền Tảng (Base Score Calculation)

Điểm nền tảng được tính bằng tổ hợp tuyến tính (Linear Combination) giữa hai thành phần, cho phép điều chỉnh trọng số ($W$) linh hoạt tùy theo kịch bản kiểm thử.

$$ \text{Base Score} = (W_{KNN} \times S'_{KNN}) + (W_{CB} \times S'_{CB}) $$

*Trong đó:* $W_{KNN} + W_{CB} = 1$.

---

### Bước 3: Cơ Chế Cộng Hưởng (Synergy Boost Strategy) - *Trọng tâm*

Đây là đóng góp chính của thuật toán Hybrid trong đồ án này. Thay vì chỉ cộng điểm, hệ thống áp dụng cơ chế thưởng/phạt dựa trên sự **Giao thoa (Overlap)** của tập dữ liệu.

**Trường hợp A: Sự Đồng thuận (Consensus Case)**
Khi một tựa game xuất hiện trong danh sách gợi ý của **cả hai thuật toán** ($S'_{KNN} > 0$ và $S'_{CB} > 0$):
*   Hệ thống xác định đây là một "Strong Recommendation" (Gợi ý mạnh).
*   Áp dụng điểm thưởng **Synergy Boost** dựa trên trung bình nhân (Geometric Mean approximation):

$$ \text{Boost} = \sqrt{S'_{KNN} \times S'_{CB}} \times 0.5 $$
$$ \text{Final Score} = \text{Base Score} + \text{Boost} $$

*Ý nghĩa:* Cơ chế này đảm bảo những game vừa có nội dung phù hợp, vừa được cộng đồng đánh giá cao sẽ luôn được đẩy lên vị trí Top đầu (như kết quả thực nghiệm với *Thronebreaker* hay *God of War*).

**Trường hợp B: Gợi ý Đơn lẻ (Isolated Case)**
Khi một tựa game chỉ được gợi ý bởi một phía (chỉ KNN hoặc chỉ CB):
*   Hệ thống áp dụng **Hình phạt (Penalty)** để giảm độ ưu tiên.

$$ \text{Final Score} = \text{Base Score} \times 0.8 $$

*Ý nghĩa:* Giúp lọc bớt các game "rác" (KNN gợi ý bừa do game quá phổ biến) hoặc các game quá "ngách" (CB gợi ý nhưng cộng đồng không chơi).

---

## 3.3. Thiết Kế Luồng Dữ Liệu (Data Flow Design)

Hệ thống được thiết kế với kiến trúc **"Deep Scan & Merge"** (Quét sâu và Hợp nhất):

1.  **Deep Scan Input (Quét sâu đầu vào):**
    *   Thay vì chỉ lấy Top 10 game từ mỗi mô hình con (dễ dẫn đến việc không có game nào trùng nhau), hệ thống đọc **Top 200** ứng viên tiềm năng nhất từ KNN và CB.
    *   Điều này mở rộng không gian tìm kiếm, tăng xác suất tìm thấy các điểm giao thoa (Overlap).

2.  **Cơ chế Chịu lỗi (Fault Tolerance - ID Recovery):**
    *   Trong quá trình vận hành thực tế, dữ liệu từ Collaborative Filtering thường gặp lỗi thiếu Metadata (ví dụ: chỉ có tên game, mất AppID).
    *   Module Hybrid tích hợp cơ chế **ID Recovery**: Tự động tra cứu ngược vào cơ sở dữ liệu gốc (`final_games.csv`) để khôi phục AppID dựa trên tên game đã chuẩn hóa, đảm bảo tính toàn vẹn của dữ liệu đầu ra.

3.  **Ranking & Output:**
    *   Danh sách sau khi tính điểm `Final Score` sẽ được sắp xếp giảm dần.
    *   Chỉ lấy **Top N** (ví dụ: Top 50 hoặc Top 100) kết quả tốt nhất để hiển thị cho người dùng, đảm bảo hiệu năng và trải nghiệm người dùng tối ưu.