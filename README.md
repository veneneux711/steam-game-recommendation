Steam ML - Hệ Thống Gợi Ý Game Thông Minh
Steam Game Recommendation System là một đồ án nghiên cứu áp dụng các kỹ thuật Học máy (Machine Learning) để xây dựng hệ thống tư vấn game cá nhân hóa. Hệ thống kết hợp sức mạnh của việc phân tích nội dung game và hành vi cộng đồng người chơi để đưa ra những gợi ý chính xác nhất.

Tính Năng Nổi Bật
Đa Mô Hình: Tích hợp 3 thuật toán gợi ý riêng biệt:
Content-Based Filtering (CB): Phân tích nội dung (Tags, Genres) để tìm game tương tự game bạn thích. Sử dụng SVD để hiểu ngữ nghĩa.
Collaborative Filtering (KNN): Tìm kiếm người chơi có "gu" giống bạn để xem họ chơi gì.
Hybrid Model: Kết hợp 2 model, sử dụng cơ chế "Synergy Boost" để đẩy ranking các game phù hợp lên.
Xử Lý Dữ Liệu Thông Minh:
Tự động đồng bộ hóa dữ liệu giữa các nguồn khác nhau.
Fuzzy Name Matching: Khắc phục lỗi lệch ID game giữa các bộ dữ liệu.
Shovelware Filter: Tự động lọc bỏ các game rác, game kém chất lượng.
Giao Diện Trực Quan (GUI): Xây dựng bằng Tkinter, cho phép tìm kiếm, đánh giá (Rate), quản lý danh sách yêu thích và xem kết quả trực tiếp.

Cấu Trúc Dự Án
Steam ML/
├── CB_model/                  # Mô hình Content-Based
│   ├── CB_games.csv           # Dữ liệu game (đã được làm gọn)
│   ├── cb_model.pkl           # Model đã huấn luyện (Lưu trữ SVD & Vectorizer)
│   ├── cb_recommendations.csv # Kết quả gợi ý từ CB
│   ├── ContentBased_model.py  # Thuật toán chính (TF-IDF + SVD)
│   └── UI_ContentBased.py     # Giao diện CB
│
├── KNN_model/                 # Mô hình Collaborative Filtering
│   ├── final_games.csv        # Danh sách game chuẩn
│   ├── final_reviews.csv      # Dữ liệu reviews người dùng
│   ├── rcm_games.csv          # Kết quả gợi ý từ KNN
│   └── UI.py                  # Giao diện KNN
│
├── Hybrid_model/              # Mô hình Lai
│   ├── run_hybrid.py          # Script chạy chính
│   └── Hybrid_recommendations_reader.py # Logic kết hợp & Chuẩn hóa điểm
│
├── results/                   # Nơi lưu kết quả cuối cùng (hybrid_ranking.csv)
├── user_data/                 # Lưu lịch sử đánh giá của người dùng
├── reduce_data.py             # Script đồng bộ và nén dữ liệu CB theo KNN
├── setup.bat                  # Cài đặt thư viện
└── run_*.bat                  # Các file chạy nhanh (Shortcuts)

Cơ Chế Hoạt Động (Technical Details)

1. Content-Based Model (CB)
Kỹ thuật: TF-IDF (Term Frequency-Inverse Document Frequency) kết hợp với TruncatedSVD (LSA) để giảm chiều dữ liệu, giúp máy tính "hiểu" được ngữ cảnh và thể loại game thay vì chỉ so sánh từ khóa đơn thuần.
Trọng số: Áp dụng Positional Weighting (Ưu tiên Genre và các Tag đầu tiên).
Điểm số: 
ScoreCB = (Similarity * 0.85) + (Popularity * 0.15)

2. KNN Model (Collaborative Filtering)
Kỹ thuật: User-Based Collaborative Filtering sử dụng khoảng cách Cosine trên ma trận thưa (Sparse Matrix).
Logic: Tìm tập hợp những người dùng (Neighbors) có lịch sử chơi game trùng khớp khoảng 70-80% với bạn, từ đó gợi ý những game mà họ đánh giá cao.

3. Hybrid Model
Kỹ thuật: Weighted Ensemble & Geometric Mean Boost.
Logic:
Chuẩn hóa điểm số từ KNN và CB về thang [0, 1].
Ghép nối dữ liệu bằng cách chuẩn hóa tên game (xóa ký tự đặc biệt, viết thường).
Synergy Boost: Nếu một game được cả 2 mô hình đề xuất, điểm số sẽ được cộng hưởng tăng mạnh.

2. KNN Model (Collaborative Filtering)
Kỹ thuật: User-Based Collaborative Filtering sử dụng khoảng cách Cosine trên ma trận thưa (Sparse Matrix).
Logic: Tìm tập hợp những người dùng (Neighbors) có lịch sử chơi game trùng khớp khoảng 70-80% với bạn, từ đó gợi ý những game mà họ đánh giá cao.

3. Hybrid Model
Kỹ thuật: Weighted Ensemble & Geometric Mean Boost.
Logic:
Chuẩn hóa điểm số từ KNN và CB về thang [0, 1].
Ghép nối dữ liệu bằng cách chuẩn hóa tên game (xóa ký tự đặc biệt, viết thường).
Synergy Boost: Nếu một game được cả 2 mô hình đề xuất, điểm số sẽ được cộng hưởng tăng mạnh.

Cài Đặt & Chuẩn Bị Dữ Liệu

Bước 1: Cài đặt Môi trường
Chạy file setup.bat để cài đặt các thư viện Python cần thiết:
setup.bat
(Yêu cầu: Python 3.x, pandas, numpy, scikit-learn, scipy, tkinter)

Bước 2: Tải Dữ Liệu (Quan Trọng)
Dự án sử dụng 2 bộ dữ liệu từ Kaggle. Bạn cần tải về và đặt đúng vị trí:
Dữ liệu cho KNN:
Nguồn: Steam Game Recommendations (Anton Kozyriev)
Giải nén vào thư mục KNN_model/.
Chạy Notebook KNN_model/data_preprocessing_1.ipynb để tạo ra file final_games.csv và final_reviews.csv.

Dữ liệu cho Content-Based:
Nguồn: Steam Games Dataset (Fronkon Games)
Giải nén vào thư mục CB_model/.
Đổi tên file thành CB_games.csv.
Đồng bộ dữ liệu:
Chạy script sau để cắt giảm dữ liệu CB cho khớp với KNN (giúp train nhanh hơn):
python reduce_data.py

Hướng Dẫn Sử Dụng
Để có kết quả tốt nhất, hãy thực hiện theo đúng trình tự:

1. Chạy Content-Based (CB)
Mở file: run_CB.bat
Thao tác:
Tìm kiếm và đánh giá (Rate) các game bạn thích (Ví dụ: Witcher 3, Cyberpunk...).
Bấm Save Ratings.
Bấm Train Model (Chỉ cần làm lần đầu hoặc khi cập nhật data).
Bấm Get Recommendations (Bắt buộc để tạo file dữ liệu cho Hybrid).

2. Chạy KNN
Mở file: run_KNN.bat
Thao tác:
Nhập tên game vào ô tìm kiếm -> Thêm vào danh sách "Played" -> Chấm điểm (Like/Dislike).
Bấm Confirm để lưu dữ liệu.
Bấm Get Recommendations (Bắt buộc).

3. Chạy Hybrid (Kết quả cuối cùng)
Mở file: run_Hybrid.bat
Hệ thống sẽ tự động đọc kết quả từ 2 bước trên, tính toán và hiển thị Bảng xếp hạng tối ưu nhất.
Xanh lá: Game được cả 2 mô hình đề xuất (Rất nên chơi).
Trắng: Game do một trong hai mô hình đề xuất.
