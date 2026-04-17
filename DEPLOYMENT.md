# Deployment Information — StudentOps AI Agent

> **Student Name:** Đào Văn Công  
> **Student ID:** 2A202600031  
> **Date:** 17/04/2026

---

## 🌐 Public URL

**[https://just-solace-production-1642.up.railway.app/](https://just-solace-production-1642.up.railway.app/)**

---

## 🏗 Platform & Infrastructure

**Railway (Cloud PaaS)** — Hệ thống được triển khai dưới dạng container hóa (Docker) trên nền tảng Railway. Toàn bộ quy trình từ Build đến Deploy đều được tự động hóa qua luồng CI/CD từ GitHub.

### Architecture

```text
Internet
    │
    ▼ (HTTPS / Port 443)
┌─────────────────────────────────────────┐
│  Railway Edge Proxy (SSL Termination)   │
│  Tự động quản lý SSL và cân bằng tải     │
└──────────────────┬──────────────────────┘
                   │
                   ▼ (HTTP / Dynamic $PORT)
┌─────────────────────────────────────────┐
│  StudentOps API Container (FastAPI)     │
│  ├─ Security Middleware (X-API-Key/JWT) │
│  ├─ Rate Limiter (10 req/min)           │
│  └─ LangGraph Agent Logic               │
└──────┬──────────────────────┬───────────┘
       │                      │
       ▼ (gRPC)               ▼ (SQL)
┌──────────────┐    ┌──────────────────────┐
│  Google AI   │    │  PostgreSQL          │
│  (Gemini Pro │    │  (Persistent         │
│   Model)     │    │   Thread History)    │
└──────────────┘    └──────────────────────┘
```

### Service Components

| Service | Type | Provider | Description |
|---------|------|----------|-------------|
| **FastAPI App** | Container | Railway | Xử lý API, Auth, Rate limit và Agent logic. |
| **PostgreSQL** | Database | Railway | Lưu trữ bền vững lịch sử hội thoại (Checkpoint). |
| **Gemini Pro** | LLM API | Google | Bộ não xử lý ngôn ngữ tự nhiên của Agent. |

---

## 📡 Test Commands & Results

### 1. Health & Readiness Check

```bash
curl https://just-solace-production-1642.up.railway.app/health
# Expected Output:
# {"status": "ok", "timestamp": 1713364800.0}
```

### 2. Authentication Verification (Should fail)

```bash
curl -i https://just-solace-production-1642.up.railway.app/chat
# Expected Output: 
# HTTP/1.1 401 Unauthorized
# {"detail": "Mã API không hợp lệ hoặc đã hết hạn."}
```

### 3. API Test (With X-API-Key)

```bash
# Sử dụng Key: cong-vjp-pro-2024
curl -X POST https://just-solace-production-1642.up.railway.app/chat \
  -H "X-API-Key: cong-vjp-pro-2024" \
  -H "Content-Type: application/json" \
  -d '{"message": "Chào bạn, tôi là sinh viên K67", "thread_id": "test-123"}'

# Expected Output:
# {"thread_id": "test-123", "graph_mode": "agent", "state": {...}}
```

### 4. Rate Limiting Test (Limit: 10 req/min)

```bash
# Gửi 12 request liên tiếp
for i in {1..12}; do
  curl -s -o /dev/null -w "Req $i: HTTP %{http_code}\n" \
    -X POST https://just-solace-production-1642.up.railway.app/chat \
    -H "X-API-Key: cong-vjp-pro-2024" \
    -d '{"message": "test"}'
done

# Expected Output:
# Req 1-10: HTTP 200
# Req 11-12: HTTP 429 (Too Many Requests)
```

---

## 🛠 Configuration (.env.example)

Hệ thống quản lý cấu hình theo nguyên tắc **12-Factor App**, toàn bộ secrets được nạp qua biến môi trường trên Railway.

| Variable | Value (Example) | Purpose |
|----------|-----------------|---------|
| `PORT` | `8000` | Port lắng nghe (Railway cấp phát động). |
| `ENVIRONMENT` | `production` | Kích hoạt các chế độ kiểm tra bảo mật nghiêm ngặt. |
| `AGENT_API_KEY` | `cong-vjp-pro-2024` | Mã xác thực chính cho các yêu cầu API. |
| `GOOGLE_API_KEY` | `AIzaSy...` | Key kết nối tới Gemini Pro Model. |
| `DATABASE_URL` | `postgresql://...` | Đường dẫn kết nối Postgres bền vững. |
| `JWT_SECRET` | `dao-van-cong-jwt...` | Khóa bí mật dùng để mã hóa JWT Token. |

---

## 🚀 Deployment Steps (Railway)

### Step 1: Chuẩn bị mã nguồn
Đảm bảo project đã có `Dockerfile` đa tầng và `railway.toml`.

### Step 2: Kết nối GitHub
Kết nối repository `day12-DaoVanCong-2A202600031` với Railway Project.

### Step 3: Cấu hình Biến môi trường
Nạp đầy đủ các biến trong bảng trên vào tab **Variables** của Railway Dashboard.

### Step 4: Deploy & Verify
Railway sẽ tự động thực hiện:
1. `docker build` (Sử dụng Build Cache để tối ưu thời gian).
2. Kiểm tra Health Check tại `/health`.
3. Nếu PASS, sẽ định tuyến lưu lượng vào container mới.

---

## 📸 Screenshots Checklist
- [x] **Railway Dashboard**: Trạng thái `Active` xanh mướt.
- [x] **Health Check**: Kết quả JSON trả về `status: ok`.
- [x] **API Docs**: Giao diện Swagger UI chuyên nghiệp.
- [x] **Test Results**: Ảnh chụp terminal chạy `python test_features.py` đạt 100%.

---

## 🛡 Security & Operations Notes
- [x] Không commit file `.env` chứa bí mật.
- [x] Chế độ `production` thực thi kiểm tra Key nghiêm ngặt.
- [x] Giới hạn tốc độ (Rate Limit) bảo vệ tài nguyên LLM.
- [x] Xử lý tắt ứng dụng êm ái (Graceful Shutdown) bảo vệ kết nối Database.

---
**Deployment Status:** 🟢 Live & Healthy
