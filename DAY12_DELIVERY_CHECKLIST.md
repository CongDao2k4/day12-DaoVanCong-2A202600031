#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Đào Văn Công  
> **Student ID:** 2A202600031  
> **Date:** 17/4/2026
> **Project URL:** https://just-solace-production-1642.up.railway.app/

---

##  Submission Requirements

### 1. Mission Answers (40 points)

# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
    1. **Lộ bí mật (Hardcoded Secrets)**: API Key của project và biến DB được ghi trực tiếp trong mã nguồn thay vì dùng biến môi trường.
    2. **Thiếu xác thực (No Authentication)**: Bất kỳ ai cũng có thể gọi API mà không cần mã bảo vệ.
    3. **Thiếu giám sát (No Health Checks)**: Hệ thống không có endpoint để tự động kiểm tra trạng thái sống/chết.
    4. **Log dạng văn bản thô**: Khó phân tích tự động bằng các công cụ hiện đại.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Cố định (Port 8000) | Linh hoạt | Để tương thích với Railway/Cloud. |
| Auth    | Không có | X-API-Key Header | đề phòng truy cập trái phép và bảo vệ tài nguyên LLM vì dùng API_KEY gọi model. |
| State   | Trong bộ nhớ (Memory) | Cơ sở dữ liệu (Postgres) | Đảm bảo không mất lịch sử chat khi hệ thống khởi động lại. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: `python:3.11-slim`
2. Working directory: `/app`.
3. Tại sao COPY requirements.txt trước?: Để tận dụng bộ nhớ đệm (Layer Caching) của Docker giúp build nhanh hơn nếu code thay đổi mà thư viện giữ nguyên.
4. CMD vs ENTRYPOINT: ENTRYPOINT: Là lệnh cố định (python)và CMD: Là tham số mặc định cho lệnh đó (các file .py), có thể ghi đè CMD khi chạy lệnh `docker run`.

### Exercise 2.3: Image size comparison
    - Develop: 1660 MB
    - Production: 236 MB
- Difference: 85.8%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://just-solace-production-1642.up.railway.app/
- Screenshot: 
![Deployment Dashboard](screenshots/dashboard.png)

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- Không có Key: Trả về mã lỗi 401 Unauthorized.
- Có Key sai: Trả về mã lỗi 401 Unauthorized.
- Có Key đúng: Trả về mã 200 OK cùng nội dung từ AI.

### Exercise 4.4: Cost guard implementation
- Sử dụng hàm `post_model_hook` trong LangGraph để theo dõi `usage_metadata`, tính toán số lượng token đã dùng trong mỗi lượt gọi và giới hạn nếu vượt mức ngân sách hàng tháng.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- Tích hợp endpoint `/health` và `/ready` để hạ tầng đám mây tự động phát hiện lỗi.
- Xử lý tín hiệu `SIGTERM` để đảm bảo đóng kết nối Database an toàn trước khi container bị tắt.
- Thiết kế Stateless (không lưu trạng thái trong app) để có thể chạy nhiều bản sao cùng lúc.

---

### 2. Full Source Code - StudentOps Complete (60 points)
Ứng dụng đã được refactor sang cấu trúc phân lớp chuyên nghiệp trong thư mục `app/`:
- `app/api/`: Xử lý API, Auth và Middleware.
- `app/telemetry/`: Hệ thống Logging JSON chuẩn công nghiệp.
- `app/graph/`: Logic AI Agent dựa trên LangGraph.
- `Dockerfile`: Multi-stage build (Builder stage & Runtime stage).

---

### 3. Service Domain Link

# Deployment Information

## Public URL
`https://just-solace-production-1642.up.railway.app/`

## Platform
Railway

## Environment Variables Set
- AGENT_API_KEY
- ENVIRONMENT
- GOOGLE_API_KEY
- JWT_SECRET

##  Pre-Submission Checklist
- [x] Repository is public
- [x] MISSION_ANSWERS.md completed
- [x] DEPLOYMENT.md has working public URL
- [x] All source code in app/ directory
- [x] No .env file committed
- [x] No hardcoded secrets in code
- [x] Public URL is accessible and working
