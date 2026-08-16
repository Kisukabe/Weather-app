# PHASES.md - Theo dõi Các Giai đoạn Phát triển (Phases Roadmap v2.0)

Tệp này dùng để quản lý và theo dõi tiến độ thực hiện các giai đoạn kiến trúc nâng cao của dự án Weather MLOps.

---

## 📊 BẢNG TIẾN ĐỘ TỔNG QUAN HỆ THỐNG V2.0

| Giai đoạn | Tên Giai Đoạn | Trạng Thái | Chi Tiết Đầu Ra Cốt Lõi |
| :--- | :--- | :---: | :--- |
| **Phase 1** | **Backend Modularization & Security** | `COMPLETED 100%` | Pydantic Settings, Rate Limiter (60 req/min), API Key Auth, SQLite DB, Log Rotation 50MB, Router Layer |
| **Phase 2** | **ML Engine Optimization (Multi-Model)** | `COMPLETED 100%` | Ingestion đa chỉ số, PySpark Big Data Transform, Model Registry (XGBoost, LGBM, RF, Ridge, Rain Classifier) |
| **Phase 3** | **Docker & Packaging Optimization** | `COMPLETED 100%` | Multi-stage Dockerfiles, Docker Compose Dev/Prod, Cấu hình hiện đại `pyproject.toml` (PEP 517/518/621) |
| **Phase 4** | **CI/CD & GitHub Actions Automation** | `COMPLETED 100%` | Quality Gate CI, Daily PySpark Cron Pipeline (6:00 AM, 7GB RAM Runner), Render IaC `render.yaml` |
| **Phase 5** | **Frontend React + Vite + TailwindCSS** | `COMPLETED 100%` | SPA Dashboard, Model Selector, Recharts Visualizations, Pipeline Control, System Logs, Vercel Config |
| **Phase 6** | **Testing Suite & Documentation** | `COMPLETED 100%` | Pytest Unit Tests (API, Components, DB), Tài liệu toàn diện `README.md`, Cập nhật `.agents/PHASES.md` |

---

## 🎯 DANH SÁCH KIỂM TRA CHI TIẾT (TASK CHECKLIST)

### Phase 1: Backend Architecture & Security
- [x] Tạo cấu hình môi trường `.env.example` và `backend/app/config.py` (Pydantic Settings).
- [x] Cài đặt SQLite Database `weather_history.db` với cơ chế tự động dọn dẹp sau 30 ngày.
- [x] Xây dựng Middleware Rate Limiting (60 req/min/IP) và xác thực `X-API-Key`.
- [x] Tách tầng dịch vụ: `PipelineService` (quản lý trạng thái) và `SchedulerService` (APScheduler).
- [x] Tách router module hóa: `/health`, `/api/v1/pipeline`, `/api/v1/data`, `/api/v1/models`.
- [x] Cài đặt App Factory Pattern và Lifespan Management trong `backend/app/main.py`.

### Phase 2: Multi-Target ML Engine & Model Registry
- [x] Mở rộng `schema.yaml` và `data_ingestion.py` để thu thập Độ ẩm, Mây mù, Mưa, Nắng, Tia UV.
- [x] Tối ưu hóa `data_transformation.py` với Apache PySpark Engine và cơ chế Fallback mượt mà.
- [x] Xây dựng `model_trainer.py` huấn luyện Model Registry (4 thuật toán Hồi quy + Rain Classifier).
- [x] Nâng cấp `model_evaluation.py` so sánh ma trận metrics (MAE, RMSE, R²) và lưu vào SQLite DB.
- [x] Hoàn thiện `prediction.py` dự báo 7 chỉ số thời tiết 16 ngày và so sánh kết quả từng mô hình.

### Phase 3: Docker Multi-Stage & Packaging
- [x] Xây dựng `backend/Dockerfile` và `frontend/Dockerfile` tối ưu kích thước với Builder Stage.
- [x] Cấu hình `docker-compose.yml` (Production) và `docker-compose.dev.yml` (Hot-Reload).
- [x] Chuyển đổi đóng gói dự án sang tiêu chuẩn `pyproject.toml`.

### Phase 4: CI/CD & GitHub Actions Engine
- [x] Thiết lập `.github/workflows/ci.yml` kiểm tra chất lượng mã nguồn, linting và pytest.
- [x] Thiết lập `.github/workflows/daily-pipeline.yml` tự động chạy PySpark lúc 6:00 AM (7GB RAM Runner).
- [x] Viết file Infrastructure-as-Code `render.yaml` phục vụ 1-Click Deploy Backend lên Render.

### Phase 5: Frontend Single Page Application (React + Vite)
- [x] Khởi tạo dự án React 18, Vite 6, TailwindCSS và Lucide Icons.
- [x] Tạo Typed API Service Client và TypeScript data contracts trong `src/types/` và `src/services/`.
- [x] Xây dựng UI Components Glassmorphism (Navbar, MetricCard, ModelSelector, WeatherCard).
- [x] Tích hợp biểu đồ tương tác Recharts (Nhiệt độ, Khí tượng mở rộng, So sánh 4 Models).
- [x] Đóng gói 3 trang (Dashboard, Pipeline Control, System Logs) và cấu hình Vercel (`vercel.json`).

### Phase 6: Testing & Final Polish
- [x] Bổ sung Unit Tests kiểm tra Component và SQLite Database trong `tests/test_components.py`.
- [x] Nâng cấp toàn diện tài liệu `README.md` với sơ đồ kiến trúc, bảng REST API và hướng dẫn triển khai.
- [x] Đồng bộ tiến độ vào `.agents/PHASES.md`.
