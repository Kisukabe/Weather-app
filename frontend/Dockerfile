# ============================================================
# 📊 Frontend Multi-Stage Dockerfile: Streamlit Web UI
# ============================================================

# --- Stage 1: Builder Stage ---
FROM python:3.10-slim AS builder

WORKDIR /build

COPY frontend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: Final Minimal Runtime Stage ---
FROM python:3.10-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY frontend/ ./frontend/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "frontend/app.py"]
