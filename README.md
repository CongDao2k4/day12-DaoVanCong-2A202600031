# StudentOps AI Agent - Production Ready 🚀

Dự án này là một hệ thống AI Agent hỗ trợ sinh viên (**StudentOps**) được xây dựng bằng **FastAPI**, **LangGraph** và **Gemini Pro**, được tối ưu hóa hoàn toàn cho môi trường production với Docker và triển khai lên đám mây (Railway).

---

## 🛠 Công nghệ sử dụng
- **Core**: FastAPI, Pydantic v2, Pydantic Settings.
- **AI/LLM**: LangGraph, Google Gemini Pro.
- **Infrastructure**: Docker (Multi-stage Build), Railway, PostgreSQL.
- **Security**: X-API-Key Middleware.
- **Observability**: Structured JSON Logging, Health/Readiness Probes.

---

## 📁 Cấu trúc thư mục chuẩn Production
```text
.
├── app/                     # Mã nguồn chính của ứng dụng
│   ├── api/                 # FastAPI routes, schemas và middleware
│   ├── graph/               # Luồng xử lý LangGraph (Agent logic)
│   ├── llm/                 # Cấu hình kết nối Gemini
│   ├── telemetry/           # Hệ thống Logging và Monitoring
│   ├── tools/               # Các công cụ hỗ trợ Agent (DB, Email, Export)
│   └── config.py            # Quản lý cấu hình 12-Factor
├── server.py                # Entry point khởi chạy ứng dụng
├── Dockerfile               # Build image tối ưu (Multi-stage)
├── railway.toml             # Cấu hình deployment đám mây
└── requirements.txt         # Danh sách thư viện phụ thuộc
```

---

## 🚀 Hướng dẫn khởi chạy nhanh

### 1. Chạy local bằng Docker
Đảm bảo bạn đã có file `.env` với các Key cần thiết, sau đó chạy:

```bash
docker build -t studentops:prod .
docker run -p 8000:8000 --env-file .env studentops:prod
```

### 2. Triển khai lên Railway
Dự án được cấu hình sẵn để tự động deploy khi bạn push code lên GitHub. Hãy đảm bảo đã cấu hình đầy đủ **Variables** trên Railway Dashboard.

---

## 🔐 Biến môi trường (Environment Variables)
Cần cấu hình các biến sau trong production:
- `AGENT_API_KEY`: Mã bảo mật để truy cập API.
- `GOOGLE_API_KEY`: Key từ Google AI Studio.
- `DATABASE_URL`: Đường dẫn kết nối Postgres.
- `ENVIRONMENT`: Set thành `production`.

---

## 📡 API Documentation
Khi ứng dụng đang chạy, bạn có thể truy cập bộ tài liệu API tự động tại:
- **Swagger UI**: `http://localhost:8000/docs` hoặc `https://your-app.up.railway.app/docs`
- **Health Check**: `/health`

---

## 🛡 Tính năng Production nổi bật
- **Bảo mật**: Chặn hoàn toàn các truy cập trái phép bằng Header xác thực.
- **Độ tin cậy**: Tích hợp Liveness/Readiness probes để hạ tầng tự động khôi phục khi có lỗi.
- **Hiệu năng**: Docker image được tối ưu từ ~1.6GB xuống còn **236MB** nhờ Multi-stage build.
- **Tắt an toàn (Graceful Shutdown)**: Xử lý tín hiệu SIGTERM để không mất dữ liệu khi restart.

---
**Học viên:** Đào Văn Công  
**Dự án Lab Day 12 - Advanced Agentic Coding**
