# 🌤️ Automated Weather Forecast Bias Correction System (TP. Hồ Chí Minh)

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Apache PySpark](https://img.shields.io/badge/PySpark-3.5-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-7GB_RAM_Runner-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

<p align="center">
  <strong>Hệ thống MLOps Pipeline cấp độ Doanh nghiệp tự động thu thập dữ liệu thời tiết thực tế, trích xuất đặc trưng bằng Apache PySpark, huấn luyện Model Registry (XGBoost, LightGBM, Random Forest, Ridge) để hiệu chỉnh sai số dự báo khí tượng và phục vụ người dùng qua ứng dụng React + Vite + TailwindCSS tốc độ cao.</strong>
</p>

</div>

---

## 📌 1. Bối Cảnh & Mục Tiêu Dự Án

Dự báo thời tiết từ các mô hình khí tượng toàn cầu (như Open-Meteo GFS/ECMWF) thường gặp sai số địa phương (bias) do đặc thù vi khí hậu của **TP. Hồ Chí Minh** (khí hậu nhiệt đới gió mùa, hiệu ứng đảo nhiệt đô thị).

### 🎯 Điểm Nổi Bật Của Hệ Thống:
1. **Thu thập dữ liệu đa chiều**: Nhiệt độ Max/Min/Mean, Độ ẩm, Độ che phủ mây, Xác suất mưa, Thời lượng nắng, Chỉ số cực tím UV.
2. **Kỹ nghệ đặc trưng Big Data (PySpark Engine)**: Tự động tính toán Lag Features (1-3 ngày), Rolling Averages (3d, 7d), Seasonality và phân chia Train/Test định dạng Parquet.
3. **Model Registry Đa Thuật Toán**: Huấn luyện và đánh giá song song **4 mô hình Hồi quy** (`XGBoost`, `LightGBM`, `Random Forest`, `Ridge`) kết hợp **Rain Classifier** để phân loại xác suất mưa.
4. **Kiến trúc Web Decoupled Hiện Đại**:
   - **Frontend**: Single Page Application viết bằng **React 18 + Vite + TailwindCSS + Recharts** (Deploy 0đ trên **Vercel**).
   - **Backend**: **FastAPI REST API Server** với Rate Limiting (60 req/min), Xác thực API Key, Log Rotation tối đa 50MB, và SQLite Database 30-day retention (Deploy trên **Render**).
5. **Điện Toán Đám Mây 0đ**: Huấn luyện định kỳ mỗi ngày lúc **06:00 AM** thông qua **GitHub Actions Runner (7GB RAM, OpenJDK 17)** hoàn toàn miễn phí.

---

## 🏗️ 2. Kiến Trúc Hệ Thống (System Architecture)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        USER WEB CLIENT (Vercel)                        │
│                 React 18 + Vite + TailwindCSS + Recharts               │
│      [ Dashboard ]    [ Model Selector ]    [ Pipeline Control ]       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS REST API / JSON
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      BACKEND REST API (Render / Docker)                │
│                            FastAPI Web Server                          │
│  ├─ Middleware: Rate Limiter (60 req/min) & API Key Auth (X-API-Key)   │
│  ├─ Routers: /health, /api/v1/metrics, /predictions, /models, /logs    │
│  ├─ Storage: SQLite DB (artifacts/weather_history.db - 30-day cleanup) │
│  └─ Logs: Rotating File Handler (Max 50MB)                             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Triggers
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             DAILY MLOPS ENGINE (GitHub Actions Cloud - 7GB RAM)        │
│  ├─ Stage 01: Data Ingestion (Open-Meteo Multi-Target API)             │
│  ├─ Stage 02: Data Validation (Strict Schema Enforcement)              │
│  ├─ Stage 03: PySpark Data Transformation (Parquet Big Data Engine)    │
│  ├─ Stage 04: Model Trainer Registry (XGBoost, LGBM, RF, Ridge, Rain)  │
│  ├─ Stage 05: Multi-Model Evaluation & Scoring Matrix                  │
│  └─ Stage 06: Multi-Output 16-Day Online Prediction                    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 3. Cấu Trúc Thư Mục Chuẩn MLOps

```text
Weather/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Quality Gate CI (Linting, Pytest, Docker Build)
│       └── daily-pipeline.yml        # Daily PySpark Cron Pipeline (6 AM, 7GB RAM)
├── backend/                          # [FastAPI REST API Service]
│   ├── app/
│   │   ├── api/                      # Modular REST Routers (/health, /pipeline, /data, /models)
│   │   ├── middleware/               # Rate Limiter & API Key Auth
│   │   ├── services/                 # Pipeline Executor & APScheduler Service
│   │   ├── db/                       # SQLite Session & 30-day Retention Cleanup
│   │   ├── config.py                 # Pydantic Settings (.env configuration)
│   │   └── main.py                   # App Factory & Lifespan Management
│   ├── Dockerfile                    # Multi-Stage Backend Dockerfile
│   └── requirements.txt
├── frontend/                         # [React + Vite + TailwindCSS SPA]
│   ├── src/
│   │   ├── components/               # Navbar, MetricCards, ModelSelector, WeatherCards
│   │   │   └── charts/               # Recharts Temperature, Indicators, Model Comparison
│   │   ├── pages/                    # DashboardPage, PipelineControlPage, SystemLogsPage
│   │   ├── services/                 # Axios Typed API Service Client
│   │   ├── types/                    # TypeScript Data Contracts
│   │   ├── App.tsx                   # Main React App Coordinator
│   │   └── index.css                 # Glassmorphic Design System & Tailwinds
│   ├── Dockerfile                    # Multi-Stage Frontend Dockerfile
│   ├── package.json                  # React 18, Vite 6, TailwindCSS, Recharts
│   └── vercel.json                   # 1-Click Vercel Deployment Configuration
├── src/                              # [Core MLOps Pipeline Engine]
│   ├── components/                   # 6 Giai đoạn Pipeline
│   │   ├── data_ingestion.py         # Open-Meteo Ingestion (Nhiệt độ, Mây, Ẩm, Mưa, UV)
│   │   ├── data_validation.py        # Schema Quality Gate
│   │   ├── data_transformation.py    # Apache PySpark Feature Engineering Engine
│   │   ├── model_trainer.py          # Model Registry Trainer (4 Models + Classifier)
│   │   ├── model_evaluation.py       # Metrics Evaluation Matrix (MAE, RMSE, R²)
│   │   └── prediction.py             # 16-Day Multi-Target Online Prediction
│   ├── config/                       # ConfigurationManager (Zero Hardcoding)
│   ├── entity/                       # Strongly-typed Dataclasses
│   ├── pipeline/                     # Stage Wrappers (Stage 01 -> Stage 06)
│   └── utils/                        # Logger (Rotating 50MB) & Common Helpers
├── config/                           # YAML Configuration Files
│   ├── config.yaml                   # File Paths & Artifact Locations
│   ├── params.yaml                   # Hyperparameters for all 4 Models
│   ├── schema.yaml                   # Data Columns & Target Schema Definitions
│   └── logging.yaml                  # Log Rotation Policy
├── tests/                            # Automated Testing Suite (Pytest)
│   ├── test_api.py                   # API Endpoint Tests
│   └── test_components.py            # Component & Database Tests
├── artifacts/                        # Pipeline Outputs (Parquet, Models, Predictions, SQLite)
├── docker-compose.yml                # Production Docker Compose (Bridge Network & Healthchecks)
├── docker-compose.dev.yml            # Hot-Reload Development Compose
├── render.yaml                       # Infrastructure-as-Code for Render Cloud
├── vercel.json                       # Root Vercel Routing Configuration
├── pyproject.toml                    # Modern PEP 517/518/621 Packaging Configuration
├── Makefile                          # Shortcuts for Local Development
└── main.py                           # CLI Pipeline Runner
```

---

## 🌐 4. Danh Sách REST API Endpoints

Tất cả các endpoint phục vụ tại tiền tố `/api/v1` (Tài liệu tương tác Swagger xem tại `http://localhost:8000/docs`):

| Method | Endpoint | Bảo Mật | Mô tả |
| :--- | :--- | :---: | :--- |
| `GET` | `/health` | Public | Kiểm tra trạng thái Backend, SQLite DB và APScheduler |
| `GET` | `/api/v1/metrics` | Public | Lấy ma trận so sánh metrics (MAE, RMSE, R²) của 4 mô hình |
| `GET` | `/api/v1/predictions` | Public | Lấy dữ liệu dự báo 16 ngày (Hỗ trợ lọc theo `?model=xgboost`) |
| `GET` | `/api/v1/models` | Public | Lấy danh mục Model Registry và trạng thái huấn luyện |
| `POST` | `/api/v1/pipeline/run` | `X-API-Key` | Kích hoạt chạy 6 Stage Pipeline trong Background Task |
| `GET` | `/api/v1/pipeline/status`| Public | Lấy tiến độ thực thi hiện tại của Pipeline |
| `GET` | `/api/v1/pipeline/history`| Public | Tra cứu lịch sử các lượt chạy từ SQLite DB |
| `GET` | `/api/v1/logs` | Public | Đọc các dòng log mới nhất từ file xoay vòng `logs/app.log` |

---

## ⚡ 5. Hướng Dẫn Cài Đặt & Khởi Chạy Local

### Yêu Cầu Hệ Thống:
- **Python**: `>= 3.10`
- **Node.js**: `>= 18.0` & `npm`
- **Java**: `OpenJDK 17` (cho PySpark Engine)

---

### Khởi Chạy Từng Phần (Local Dev):

```bash
# 1. Cài đặt Backend dependencies
pip install -e ".[dev]"

# 2. Chạy Backend FastAPI (Port 8000)
uvicorn backend.app.main:app --reload --port 8000

# 3. Cài đặt và chạy React Frontend (Port 3000)
cd frontend
npm install
npm run dev
```

Mở trình duyệt tại: 👉 **`http://localhost:3000`**

---

### Khởi Chạy Bằng Docker Compose:

```bash
# Chạy toàn bộ hệ thống bằng Docker Compose
docker compose up -d --build

# Xem log thời gian thực
docker compose logs -f
```

---

## 🧪 6. Kiểm Thử Tự Động (Automated Testing)

Chạy toàn bộ bài kiểm thử với `pytest`:

```bash
pytest
```

---

## 🚀 7. Hướng Dẫn Triển Khai Lên Đám Mây (0đ Chi Phí)

1. **GitHub Actions (Training Engine 7GB RAM)**:
   - Pipeline tự động chạy lúc 06:00 AM mỗi ngày hoặc bấm "Run workflow" trong tab Actions trên GitHub.
2. **Render (Backend API)**:
   - Kết nối GitHub repo với Render và chọn **Blueprint Deploy** (file `render.yaml` sẽ tự động cấu hình toàn bộ).
3. **Vercel (React Frontend)**:
   - Import repository vào Vercel, chọn framework **Vite** và bấm **Deploy**.

---

## 📄 Bản Quyền & Giấy Phép
Dự án được phát hành theo giấy phép **MIT License**. Mọi đóng góp và mã nguồn mở đều được hoan nghênh!
