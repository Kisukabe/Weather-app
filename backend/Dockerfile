# ============================================================
# 🌤️ Backend Multi-Stage Dockerfile: FastAPI + PySpark Engine
# ============================================================

# --- Stage 1: Builder Stage ---
FROM python:3.10-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: Final Minimal Runtime Stage ---
FROM python:3.10-slim AS runtime

# Cài đặt OpenJDK Java cho PySpark và curl cho Healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập Java Home
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="/root/.local/bin:$JAVA_HOME/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy các thư viện đã build từ builder stage
COPY --from=builder /root/.local /root/.local

# Copy toàn bộ mã nguồn backend và pipeline
COPY . .

# Cài đặt package nội bộ
RUN pip install --no-cache-dir -e .

# Tạo sẵn thư mục artifacts và logs
RUN mkdir -p artifacts logs

# Port 8000 (Local / Render) và 7860 (Hugging Face / Cloud Run)
EXPOSE 8000 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Khởi chạy FastAPI
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
