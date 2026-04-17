# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y gcc libpq-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --prefix=/install

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app

# Copy packages từ builder
COPY --from=builder /install /usr/local

# Copy application
COPY app/ ./app/
COPY utils/ ./utils/

# Thiết lập biến môi trường
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Lệnh bắt đầu đơn giản nhất
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Sử dụng biến môi trường $PORT thay vì số 8000 cố định
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

