# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y gcc libpq-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --prefix=/install

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app

# Copy thư viện vào hệ thống
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/
COPY server.py .
COPY utils/ ./utils/
COPY app/templates/ ./app/templates/

# Thiết lập biến môi trường
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Khởi chạy thông qua server.py để xử lý Port an toàn bằng Python logic
CMD ["python", "server.py"]
