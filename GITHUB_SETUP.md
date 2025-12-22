# Hướng Dẫn Đưa Project Lên GitHub

## Bước 1: Cài đặt Git (nếu chưa có)

Nếu bạn chưa cài Git, tải về từ: https://git-scm.com/download/win

Kiểm tra Git đã cài chưa:
```bash
git --version
```

## Bước 2: Tạo Repository trên GitHub

1. Đăng nhập vào GitHub: https://github.com
2. Nhấn nút "+" ở góc trên bên phải → "New repository"
3. Đặt tên repository (ví dụ: `Steam-ML`)
4. Chọn **Public** hoặc **Private**
5. **KHÔNG** tích vào "Initialize with README" (vì bạn đã có code)
6. Nhấn "Create repository"

## Bước 3: Khởi tạo Git trong Project

Mở PowerShell hoặc Command Prompt trong thư mục project và chạy các lệnh sau:

### 3.1. Khởi tạo Git repository
```bash
git init
```

### 3.2. Cấu hình Git user (CHỈ CẦN LÀM 1 LẦN)

**Thay thế bằng thông tin của bạn:**
```bash
git config --global user.name "veneneux711"
git config --global user.email "theartifactones@gmail.com"
```

**Lưu ý:** 
- `--global` sẽ áp dụng cho tất cả repositories
- Nếu chỉ muốn áp dụng cho repository này, bỏ `--global`
- Email nên dùng email đã đăng ký GitHub

### 3.3. Thêm tất cả files vào staging area
```bash
git add .
```

### 3.4. Commit lần đầu
```bash
git commit -m "Initial commit: Steam Game Recommendation System with KNN and Decision Tree models"
```

## Bước 4: Kết nối với GitHub Repository

Thay `YOUR_USERNAME` và `YOUR_REPOSITORY_NAME` bằng thông tin của bạn:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
```

Ví dụ:
```bash
git remote add origin https://github.com/yourusername/Steam-ML.git
```

## Bước 5: Push code lên GitHub

### Lần đầu tiên (nếu branch chính là main):
```bash
git branch -M main
git push -u origin main
```

### Nếu branch chính là master:
```bash
git branch -M master
git push -u origin master
```

## Bước 6: Xác thực (Authentication)

GitHub có thể yêu cầu bạn đăng nhập:
- Sử dụng **Personal Access Token** (khuyến nghị)
- Hoặc sử dụng GitHub CLI

### Tạo Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Chọn quyền: `repo` (full control)
4. Copy token và dùng làm password khi Git hỏi

## Các Lệnh Hữu Ích Khác

### Xem trạng thái files:
```bash
git status
```

### Xem các thay đổi:
```bash
git diff
```

### Push sau khi đã có remote:
```bash
git add .
git commit -m "Mô tả thay đổi"
git push
```

### Xem remote đã kết nối:
```bash
git remote -v
```

### Thay đổi remote URL:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
```

## Troubleshooting

### Lỗi "remote origin already exists":
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
```

### Lỗi "failed to push some refs":
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Xóa file khỏi Git nhưng giữ trong máy:
```bash
git rm --cached filename
```

## Lưu Ý

- File `.gitignore` đã được tạo để loại trừ các file không cần thiết (__pycache__, .pyc, etc.)
- Các file CSV và JSON vẫn được commit (bạn có thể chỉnh trong .gitignore nếu muốn)
- Nhớ commit và push thường xuyên để backup code

