# StudentOps Production Deployment Guide

Tài liệu này hướng dẫn chi tiết các bước triển khai dự án **StudentOps API** (LangGraph + Gemini) lên môi trường Production (Railway) theo tiêu chuẩn Day 12.

## 1. Cấu trúc thư mục mới
Dự án đã được tái cấu trúc để tối ưu cho Production:
- `app/`: Thư mục chứa toàn bộ logic xử lý chính (API, Graph, Tools, LLM).
- `server.py`: Điểm khởi chạy ASGI cho Uvicorn.
- `Dockerfile`: Multi-stage build (giảm kích thước image, bảo mật cao).
- `requirements.txt`: Chứa toàn bộ thư viện cần thiết (FastAPI, LangGraph, Google GenAI, v.v.).

## 2. Các tính năng Production đã tích hợp
Dự án đã được refactor để đạt 20/20 tiêu chuẩn:
- **Xác thực API Key**: Header `X-API-Key` là bắt buộc cho mọi request tới `/chat`, `/meta`, `/history`.
- **Structured Logging**: Mọi request và sự kiện hệ thống được ghi log dạng JSON (Industry Standard).
- **Health & Readiness**: 
  - `/health`: Liveness probe.
  - `/ready`: Kiểm tra kết nối tới các Database (PostgreSQL).
- **Graceful Shutdown**: Xử lý tín hiệu SIGTERM để đóng kết nối PostgreSQL an toàn.
- **Environment Management**: Sử dụng `pydantic-settings` để quản lý biến môi trường chặt chẽ.

## 3. Các biến môi trường cần thiết (Railway Variables)

| Biến | Giá trị ví dụ | Ý nghĩa |
|---|---|---|
| `PORT` | `8000` | Cổng Railway sẽ cấp (tự động) |
| `ENVIRONMENT` | `production` | Bật các chế độ kiểm tra bảo mật |
| `AGENT_API_KEY` | `dao-van-cong-secret-123` | Key để bạn gọi API từ Postman/UI |
| `GOOGLE_API_KEY` | `your-gemini-key` | Key để chạy Gemini Pro |
| `DATABASE_URL` | `postgresql://...` | DB để lưu History (LangGraph) |
| `CTSV_DATABASE_URL` | `postgresql://...` | DB để Agent truy vấn dữ liệu sinh viên |

## 4. Kiểm tra trước khi nộp bài
1. Chạy thử Docker local:
   ```bash
   docker build -t studentops:prod .
   docker run -p 8000:8000 --env-file .env studentops:prod
   ```
2. Kiểm tra Health check: [http://localhost:8000/health](http://localhost:8000/health)
3. Chạy script chấm điểm:
   ```bash
   python check_production_ready.py
   ```

## 5. Nộp bài
- Chụp ảnh Dashboard Railway (Active).
- Chụp ảnh kết quả `python check_production_ready.py`.
- Lưu ảnh vào thư mục `screenshots/`.
- `git add .`, `git commit -m "docs: finalize StudentOps production readiness"`, `git push origin main`.
