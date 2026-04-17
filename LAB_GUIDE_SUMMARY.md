#  Tổng Hợp Toàn Bộ Quy Trình Lab: AI Agent Deployment

Tài liệu này tổng hợp chi tiết cách thực hiện từ Part 1 đến Part 6, giúp bạn nắm vững quy trình triển khai ứng dụng AI chuẩn Production.

---

## 🏗 Part 1: Localhost vs Production
**Mục tiêu:** Nhận diện và sửa các lỗi "Anti-patterns" thường gặp khi code trên máy cá nhân.

*   **Các bước chính:**
    1.  **Phát hiện Anti-patterns:** Tìm các lỗi như hardcoded secrets (API Key), port cố định, không có health check.
    2.  **Sử dụng Environment Variables:** Sử dụng thư viện `python-dotenv` hoặc `pydantic-settings` để đọc cấu hình từ file `.env`.
    3.  **Graceful Shutdown:** Thêm code xử lý tín hiệu `SIGTERM` để đảm bảo app tắt an toàn, không bị ngắt kết nối đột ngột.
    4.  **Health Check:** Tạo endpoint `GET /health` để hệ thống giám sát biết app còn sống.

---

## 🐳 Part 2: Docker Containerization
**Mục tiêu:** Đóng gói app vào Container để chạy ổn định trên mọi môi trường.

*   **Các bước chính:**
    1.  **Dockerfile Cơ Bản:** Viết Dockerfile Single-stage (dễ nhưng image nặng ~1GB+).
    2.  **Multi-stage Build (Nâng cao):**
        *   **Stage 1 (Builder):** Cài đặt dependencies, dùng image có đầy đủ build-tools.
        *   **Stage 2 (Runtime):** Chỉ copy các thư viện đã cài sang image `slim` sạch sẽ.
    3.  **Tối ưu hóa:** Sử dụng `.dockerignore` để loại bỏ `venv`, `node_modules`, `.git` giúp build nhanh và image nhẹ.
    4.  **Kết quả:** Giảm kích thước image từ >1.6GB xuống còn <250MB.

---

## ☁️ Part 3: Cloud Deployment
**Mục tiêu:** Đưa app lên mạng Internet bằng các nền tảng PaaS như Railway, Render.

*   **Các bước chính:**
    1.  **Kết nối GitHub:** Đẩy code lên GitHub để kích hoạt CI/CD tự động.
    2.  **Triển khai trên Railway:** Tạo dự án, kết nối Repo GitHub, chọn Dockerfile làm môi trường build.
    3.  **Quản lý Biến môi trường:** Cấu hình `PORT`, `AGENT_API_KEY` trực tiếp trên Dashboard của Cloud thay vì ghi vào code.
    4.  **Public URL:** Tạo domain `.up.railway.app` hoặc `.onrender.com` để truy cập từ bất cứ đâu.

---

## 🔐 Part 4: API Security
**Mục tiêu:** Bảo vệ API khỏi các truy cập trái phép và kiểm soát chi phí.

*   **Các bước chính:**
    1.  **Authentication:** Sử dụng `API Key Header` (X-API-Key) hoặc `JWT Token` để xác thực người dùng.
    2.  **Rate Limiting:** Sử dụng Redis hoặc bộ nhớ đệm để giới hạn số lượt gọi (vd: 10 req/min). Tránh bị spam làm cạn kiệt tài khoản OpenAI.
    3.  **Cost Guard:** Tính toán số token và chi phí ước tính, chặn người dùng nếu họ vượt quá ngân sách tháng (vd: $10/month).

---

## ⚖️ Part 5: Scaling & Reliability
**Mục tiêu:** Thiết kế hệ thống có khả năng mở rộng và độ tin cậy cao.

*   **Các bước chính:**
    1.  **Stateless Design:** Chuyển dữ liệu lịch sử hội thoại (Conversation History) từ bộ nhớ RAM sang **Redis**. Giúp bạn có thể chạy nhiều bản sao (Instance) của agent mà không làm mất dữ liệu người dùng.
    2.  **Load Balancing:** Sử dụng Nginx như một Reverse Proxy để phân phối tải đều cho nhiều instance của app.
    3.  **Readiness Probe:** Thêm endpoint `GET /ready` để Load Balancer biết khi nào app đã sẵn sàng nhận traffic.

---

## 🚀 Part 6: Final Project
**Mục tiêu:** Kết hợp tất cả kiến thức trên vào một dự án duy nhất.

*   **Cấu trúc hoàn chỉnh:**
    *   Thư mục `app/` chứa logic lõi sạch sẽ.
    *   `Dockerfile` tối ưu hóa đa tầng.
    *   `docker-compose.yml` để chạy cả Agent và Redis cùng lúc.
    *   Hỗ trợ đầy đủ Health check, Auth, Rate limit và Stateless.
*   **Kiểm tra:** Sử dụng script `check_production_ready.py` để đảm bảo 100% các tiêu chuẩn sản xuất đã được đáp ứng trước khi nộp bài.

---

**LƯU Ý:** Để nộp bài thành công, hãy đảm bảo link GitHub của bạn chứa đầy đủ các file đã được tối ưu hóa ở thư mục gốc và có ảnh chụp màn hình minh chứng trong thư mục `screenshots/`.
