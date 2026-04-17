# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y gcc libpq-dev
COPY requirements.txt .
# SỬA TẠI ĐÂY: Dùng --prefix thay vì --user
RUN pip install --no-cache-dir -r requirements.txt --prefix=/install

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app

# Copy thư viện vào hệ thống (giúp nhận diện module ngay lập tức)
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/
COPY server.py .
COPY utils/ ./utils/
COPY app/templates/ ./app/templates/

# Thiết lập biến môi trường
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Lệnh bắt đầu dùng biến PORT linh hoạt
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
