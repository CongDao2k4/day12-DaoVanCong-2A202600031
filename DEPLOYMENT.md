# Deployment Information - StudentOps AI Agent

## 🌐 Public URL
`https://just-solace-production-1642.up.railway.app/`

## 🏗 Platform
Railway

## 📡 Test Commands

### 1. Kiểm tra Liveness (Sức khỏe app)
```bash
curl https://just-solace-production-1642.up.railway.app/health
# Mong đợi: {"status": "ok", ...}
```

### 2. Kiểm tra Readiness (Kết nối Database)
```bash
curl https://just-solace-production-1642.up.railway.app/ready
# Mong đợi: {"status": "ok", "databases": {...}}
```

### 3. API Test (Yêu cầu xác thực)
```bash
# Sử dụng mã API: cong-vjp-pro-2024
curl -X POST https://just-solace-production-1642.up.railway.app/chat \
  -H "X-API-Key: cong-vjp-pro-2024" \
  -H "Content-Type: application/json" \
  -d '{"message": "Chào bạn, hãy liệt kê sinh viên K67", "thread_id": "test-123"}'
```

---

## 🛠 Biến môi trường đã cấu hình (Railway Variables)
- `AGENT_API_KEY`
- `ENVIRONMENT`
- `GOOGLE_API_KEY`
- `JWT_SECRET`

## 📸 Screenshots
![Deployment dashboard](screenshots/dashboard.png)
![Service running](screenshots/health.png)
![Service running with docs](screenshots/docs.png)
![Test results](screenshots/test.png)
