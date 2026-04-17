# Day 12 Lab - Mission Answers

**Student:** Dao Van Cong (2A202600031)  
**Date:** 17/04/2026

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **API Key Hardcoded**: Lộ thông tin bí mật trực tiếp trong mã nguồn (`OPENAI_API_KEY`).
2. **Fixed Port/Host**: Sử dụng `host="localhost"` và `port=8000` cố định, không linh hoạt khi deploy lên cloud.
3. **Debug Mode Enabled**: `reload=True` không nên dùng trong môi trường production vì tốn tài nguyên và tiềm ẩn rủi ro bảo mật.
4. **Lack of Health Check**: Không có endpoint `/health` để hệ thống giám sát biết container còn hoạt động hay không.
5. **Standard print() Logging**: Sử dụng `print()` thay vì thư viện logging chuyên nghiệp, không hỗ trợ cấu trúc JSON cho log management.
6. **No Graceful Shutdown**: Không xử lý tín hiệu (SIGTERM) để đóng các kết nối một cách an toàn trước khi dừng.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Hardcoded | Env Vars (.env) | Giúp bảo mật secret và linh hoạt thay đổi config mà không cần sửa code. |
| Health check | None | /health endpoint | Để platform (Railway, Docker) tự động phát hiện và restart khi app crash. |
| Logging | print() | Structured JSON | Dễ dàng parse log, theo dõi lỗi và giám sát hệ thống ở quy mô lớn. |
| Shutdown | Sudden | Graceful | Đảm bảo các request đang xử lý được hoàn tất và đóng database connection an toàn. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image**: `python:3.11-slim`
2. **Working directory**: `/app`
3. **Why COPY requirements.txt first?**: Để tận dụng cơ chế Docker Layer Caching. Nếu code thay đổi nhưng requirements không đổi, Docker sẽ dùng lại layer đã cài thư viện, giúp build nhanh hơn.
4. **CMD vs ENTRYPOINT**: `ENTRYPOINT` định nghĩa lệnh thực thi chính không thể ghi đè dễ dàng, còn `CMD` cung cấp các đối số mặc định có thể bị ghi đè khi chạy container.

### Exercise 2.3: Image size comparison
- Develop: 1660 MB
- Production: 236 MB
- Difference: 85.8% (Giảm đáng kể nhờ template slim và multi-stage build)

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://day12-lab-production.up.railway.app (Ví dụ)
- Screenshot: [screenshots/railway_deploy.png]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- **Auth Test**: 
  - No key: `401 Unauthorized`
  - Wrong key: `401 Unauthorized`
  - Correct key: `200 OK`
- **Rate Limit Test**: Sau 10 request/phút, nhận được `429 Too Many Requests`.

### Exercise 4.4: Cost guard implementation
Sử dụng Redis để lưu trữ tổng chi phí tích lũy của user trong tháng. Mỗi khi có request, hệ thống sẽ tính toán chi phí ước tính, cộng dồn vào Redis và kiểm tra xem có vượt quá limit ($10) hay không bằng lệnh `INCRBYFLOAT` của Redis.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Health Checks**: Đã thêm `/health` (liveness) và `/ready` (readiness).
- **Graceful Shutdown**: Sử dụng `signal` handler để bắt `SIGTERM` và chờ 5-10s cho các task hiện tại hoàn tất.
- **Stateless Design**: Di chuyển toàn bộ conversation history từ `dict` trong memory sang **Redis**, giúp scale-out nhiều instance mà không mất dữ liệu.
- **Load Balancing**: Sử dụng Nginx để phân phối traffic theo thuật toán Round Robin tới 3 agent instances.
