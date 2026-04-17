# 🚀 Hướng Dẫn Chi Tiết Triển Khai (Deployment Guide)

Tài liệu này hướng dẫn chi tiết cách đưa AI Agent của bạn lên internet thông qua Railway bằng phương pháp kết nối GitHub (Phương pháp ổn định nhất).

---

## Bước 1: Chuẩn bị Repository trên GitHub
1.  **Tạo Repo:** Truy cập [github.com](https://github.com), nhấn **New**.
    *   Tên Repo: `day12-agent-deployment` (hoặc tên tùy ý).
    *   Chế độ: **Public**.
2.  **Đẩy code lên (Từ Terminal tại máy):**
    ```bash
    git add .
    git commit -m "feat: production ready"
    git push origin main
    ```

---

## Bước 2: Thiết lập trên Railway Dashboard
1.  **Đăng nhập:** Truy cập [railway.app](https://railway.app).
2.  **Tạo project mới:** Nhấn **New Project** -> **Deploy from GitHub repo**.
3.  **Cấp quyền:** Nếu là lần đầu, bạn cần nhấn **Configure GitHub App** để cấp quyền cho Railway truy cập Repo của bạn.
4.  **Chọn Repo:** Tìm và chọn đúng tên Repository bạn vừa push code ở Bước 1.
5.  **Chọn "Deploy Now":** Ngay lập tức Railway sẽ tạo một Service và bắt đầu build.

---

## Bước 3: Cấu hình Biến môi trường (Cực kỳ quan trọng)
*App sẽ bị báo lỗi "Crash" hoặc "Offline" nếu thiếu bước này.*

1.  Tại giao diện dự án, nhấn vào cái ô Service (hình chữ nhật) đang hiển thị.
2.  Chọn tab **Variables**.
3.  Nhấn **+ New Variable** và thêm chính xác 3 biến sau:
    *   `PORT`: `8000` (Để Railway biết mở cổng nào).
    *   `AGENT_API_KEY`: `your-secret-key` (Dùng để xác thực khi gọi API qua curl/postman).
    *   `ENVIRONMENT`: `production` (Để app chạy các cấu hình tối ưu).
4.  Nhấn **Deploy** (hoặc đợi Railway tự động redeploy khi bạn lưu biến).

---

## Bước 4: Cấp Domain (Lấy link nộp bài)
1.  Tại Dashboard của Service, chọn tab **Settings**.
2.  Kéo xuống mục **Networking**.
3.  Nhấn nút **Generate Domain**.
4.  Railway sẽ cấp cho bạn một link có dạng: `https://...up.railway.app`.

---

## Bước 5: Kiểm tra và Gỡ lỗi (Troubleshooting)
Nếu app không chạy (hiện màu đỏ), hãy kiểm tra 2 nơi:

*   **Tab Deployments -> View Logs:**
    *   **Build Logs:** Xem quá trình cài đặt Docker có lỗi không (vd: thiếu thư viện trong requirements.txt).
    *   **Deploy Logs:** Xem app có bị lỗi code khi khởi chạy không (vd: lỗi kết nối Redis, lỗi import).
*   **Lỗi thường gặp:**
    *   `401 Unauthorized`: Bạn quên chưa truyền header `X-API-Key` khi gọi API.
    *   `503 Service Unavailable`: App đang khởi động hoặc Health check bị fail.
    *   `Permission Denied`: Đảm bảo Dockerfile có dòng `USER appuser` (non-root).

---

## Bước 6: Test kết quả cuối cùng
Mở Terminal trên máy bạn và chạy thử:
```bash
# Thay <your-url> bằng link ở Bước 4
curl https://<your-url>/health
```
Nếu nhận được `{"status": "ok"}` -> **Chúc mừng! Bạn đã hoàn thành bài Lab!**
