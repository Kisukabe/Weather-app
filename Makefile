.PHONY: install backend frontend pipeline docker-up docker-down test clean

# Cài đặt ứng dụng local
install:
	pip install -r requirements.txt
	pip install -e .

# Chạy Backend API (FastAPI) từ backend/app/main_api.py
backend:
	PYTHONPATH=. uvicorn backend.app.main_api:app --reload --port 8000

# Chạy Frontend Dashboard (Streamlit) từ frontend/app.py
frontend:
	PYTHONPATH=. BACKEND_URL=http://localhost:8000 streamlit run frontend/app.py --server.port 8501

# Chạy MLOps Pipeline trực tiếp qua CLI
pipeline:
	PYTHONPATH=. python main.py

# Khởi chạy Docker Compose (Backend + Frontend)
docker-up:
	docker compose up -d --build

# Dừng Docker Compose
docker-down:
	docker compose down

# Chạy kiểm thử tự động
test:
	PYTHONPATH=. pytest tests/ -v

# Dọn dẹp cache
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
