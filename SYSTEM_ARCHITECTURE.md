# SYSTEM_ARCHITECTURE.md
# Tài liệu Kiến trúc Hệ thống - Automated Weather Forecast Bias Correction Pipeline

> **⚠️ ĐÂY LÀ TÀI LIỆU KIẾN TRÚC DUY NHẤT (Single Source of Truth)**
> Mọi thay đổi về hệ thống phải được cập nhật vào tệp này ngay lập tức.
> Phiên bản cuối cùng: **2026-08-12**

---

## 1. TỔNG QUAN DỰ ÁN (Project Overview)

| Mục | Nội dung |
| :--- | :--- |
| **Tên dự án** | Automated Weather Forecast Bias Correction Pipeline |
| **Khu vực** | TP. Hồ Chí Minh (Lat: `10.8231`, Lon: `106.6297`) |
| **Mục tiêu** | Xây dựng Data Pipeline tự động thu thập dữ liệu thời tiết từ API, xử lý bằng PySpark và ứng dụng Machine Learning để **hiệu chỉnh sai số dự báo (Bias Correction)** giữa dữ liệu dự báo vật lý và thời tiết thực tế |
| **Môi trường** | Python 3.10 / PySpark 4.x / macOS / Miniforge (`weather_env`) |
| **Interpreter** | `/Users/giabao/miniforge3/envs/weather_env/bin/python` |

---

## 2. TECH STACK

| Thành phần | Công nghệ | Phiên bản |
| :--- | :--- | :--- |
| **Data Collection** | Open-Meteo API (Archive + Forecast) | Miễn phí, không cần API Key |
| **Big Data Processing** | PySpark (`pyspark.sql`, Window Functions) | 4.2.0 |
| **Data Manipulation** | Pandas, NumPy | 2.3.3 / 2.2.6 |
| **Machine Learning** | Scikit-Learn (`RandomForestRegressor`) | 1.7.2 |
| **Model Serialization** | Joblib | 1.5.3 |
| **Data Format** | CSV (ingestion) → Parquet (transformation) | - |
| **Config Management** | PyYAML, python-box (`ConfigBox`) | 6.0.3 / 7.4.1 |
| **Type Enforcement** | ensure (`@ensure_annotations`) | 1.0.4 |
| **Orchestration** | Apache Airflow (Phase 8) | Chưa cài đặt |
| **Frontend** | Streamlit, Plotly | 1.61.1 / 6.9.0 |
| **Logging** | Python `logging` module + YAML config | Built-in |

---

## 3. BÀI TOÁN KHOA HỌC (Scientific Problem)

### 3.1 Bias Correction - Hiệu chỉnh sai số dự báo

Các mô hình vật lý khí tượng toàn cầu (GFS/ECMWF) đưa ra dự báo thô $F_t$ cho ngày $t$. Do đặc thù đô thị hóa, hiệu ứng đảo nhiệt, khí hậu nhiệt đới của TP.HCM, dữ liệu dự báo vật lý thường lệch so với thực tế đo đạc $O_t$.

**Công thức sai số:**
```
E_t = O_t - F_t
```

**Giải pháp Machine Learning:**
- Mô hình ML học hàm dự đoán sai số từ các features lịch sử
- Dự báo sau hiệu chỉnh: `O_corrected = F_t + E_predicted`
- Kết quả: Giảm đáng kể MAE/RMSE so với dự báo vật lý thô

### 3.2 Features Engineering (PySpark Window Functions)

| Nhóm Feature | Cách tính | Mục đích |
| :--- | :--- | :--- |
| **Lag Features** | Nhiệt độ/Mưa của t-1, t-2, t-3, t-7 ngày | Nhớ xu hướng ngắn hạn |
| **Rolling Mean** | Trung bình cuộn 3 ngày, 7 ngày | Làm mượt biến động nhiễu |
| **Rolling Std** | Độ lệch chuẩn cuộn 3 ngày, 7 ngày | Đo mức độ biến thiên |
| **Seasonality** | `sin(2π × day/365)`, `cos(2π × day/365)` | Nhận biết chu kỳ mùa |

---

## 4. KIẾN TRÚC HỆ THỐNG (System Architecture)

### 4.1 Triết lý thiết kế: Configuration-Driven MLOps Pipeline

Toàn bộ hệ thống được chia thành **5 tầng độc lập**, không tầng nào phụ thuộc trực tiếp vào tầng không liền kề:

```
┌─────────────────────────────────────────┐
│  TẦNG 5: Vận hành & Giao diện          │
│  main.py / app.py / dags/*.py           │
├─────────────────────────────────────────┤
│  TẦNG 4: Pipeline Orchestration         │
│  src/pipeline/stage_0X_*.py             │
├─────────────────────────────────────────┤
│  TẦNG 3: Core Business Logic            │
│  src/components/*.py (PySpark + ML)     │
├─────────────────────────────────────────┤
│  TẦNG 2: Quản lý Cấu hình & Entity     │
│  src/config/ + src/entity/              │
├─────────────────────────────────────────┤
│  TẦNG 1: Cấu hình Tĩnh (YAML)          │
│  config/*.yaml                          │
└─────────────────────────────────────────┘
```

### 4.2 Cấu trúc thư mục đầy đủ

```text
Weather/
│
├── config/                            # [TẦNG 1: CẤU HÌNH TĨNH]
│   ├── config.yaml                    # Đường dẫn artifacts cho từng stage
│   ├── params.yaml                    # Siêu tham số Random Forest + PySpark config
│   ├── schema.yaml                    # Định nghĩa tên cột và kiểu dữ liệu chuẩn
│   └── logging.yaml                   # Cấu hình hệ thống ghi nhật ký (log)
│
├── artifacts/                         # [KẾT QUẢ TRUNG GIAN - TỰ ĐỘNG SINH RA]
│   ├── data_ingestion/                # hcm_archive.csv, hcm_forecast.csv
│   ├── data_validation/               # status.txt
│   ├── data_transformation/           # train_transformed.parquet, test.parquet
│   ├── model_trainer/                 # bias_correction_model.joblib
│   ├── model_evaluation/              # metrics.json (MAE thô vs MAE sau hiệu chỉnh)
│   └── prediction/                    # forecast_corrected.json
│
├── logs/                              # [NHẬT KÝ - TỰ ĐỘNG SINH RA]
│   └── app.log
│
├── src/                               # [TẦNG 2-4: MÃ NGUỒN CHÍNH]
│   ├── __init__.py
│   │
│   ├── utils/                         # Công cụ dùng chung
│   │   ├── __init__.py
│   │   ├── logger.py                  # Khởi tạo logger "weather_predictor"
│   │   └── common.py                  # read_yaml, create_directories, save_json, save_bin, load_bin
│   │
│   ├── entity/                        # Định nghĩa cấu trúc dữ liệu cấu hình
│   │   ├── __init__.py
│   │   └── config_entity.py           # @dataclass cho 6 stage (frozen=True)
│   │
│   ├── config/                        # Quản lý cấu hình
│   │   ├── __init__.py
│   │   └── configuration.py           # ConfigurationManager: đọc YAML → trả về Entity
│   │
│   ├── components/                    # Logic nghiệp vụ chính (mỗi file = 1 nhiệm vụ)
│   │   ├── __init__.py
│   │   ├── data_ingestion.py          # Gọi Open-Meteo API, lưu CSV vào artifacts
│   │   ├── data_validation.py         # Kiểm tra schema, ghi status.txt
│   │   ├── data_transformation.py     # PySpark: tính Lag/Rolling/Bias features → Parquet
│   │   ├── model_trainer.py           # Train RandomForestRegressor, lưu .joblib
│   │   ├── model_evaluation.py        # Đánh giá MAE/RMSE/R2, lưu metrics.json
│   │   └── prediction.py              # Gọi Forecast API → tạo features → dự báo hiệu chỉnh
│   │
│   └── pipeline/                      # Điều phối (mỗi file gọi ConfigMgr + Component)
│       ├── __init__.py
│       ├── stage_01_data_ingestion.py
│       ├── stage_02_data_validation.py
│       ├── stage_03_data_transformation.py
│       ├── stage_04_model_trainer.py
│       ├── stage_05_model_evaluation.py
│       └── stage_06_prediction.py
│
├── dags/                              # [AIRFLOW - PHASE 8]
│   └── weather_pipeline_dag.py        # DAG: chạy 6 stage tự động hàng ngày (@daily)
│
├── .agents/                           # [BỘ NHỚ DỰ ÁN]
│   ├── AGENTS.md                      # Quy tắc coding cho AI agents
│   ├── PROJECT_MEMORY.md              # Ngân hàng ký ức và quyết định kiến trúc
│   ├── PHASES.md                      # Bảng theo dõi tiến độ các Phase
│   └── skills/weather-mlops/SKILL.md  # Skill hướng dẫn phát triển dự án
│
├── requirements.txt                   # Danh sách thư viện (pyspark, pandas, sklearn...)
├── main.py                            # Điểm khởi chạy toàn bộ pipeline (Stage 01→06)
├── app.py                             # Giao diện Web Streamlit Dashboard
├── SYSTEM_ARCHITECTURE.md             # ← FILE NÀY (tài liệu kiến trúc duy nhất)
└── implementation_plan.md             # Kế hoạch triển khai chi tiết
```

---

## 5. LUỒNG DỮ LIỆU (Data Flow)

### 5.1 Luồng Huấn luyện (Training Flow)

```
Open-Meteo Archive API (2020 → nay)
         │
         ▼
[Stage 01] data_ingestion.py
  → Thu thập: nhiệt độ max/min/mean, lượng mưa, tốc độ gió
  → Lưu: artifacts/data_ingestion/hcm_archive.csv
         │
         ▼
[Stage 02] data_validation.py
  → Kiểm tra: schema.yaml (tên cột, kiểu dữ liệu)
  → Lưu: artifacts/data_validation/status.txt
         │
         ▼
[Stage 03] data_transformation.py  ← PySpark Engine
  → Tính Lag(1,2,3,7), Rolling Mean/Std(3,7), Sin/Cos Seasonality
  → Tính Bias = temp_observed - temp_forecast (Target variable)
  → Chia Train/Test theo thời gian (không random split!)
  → Lưu: artifacts/data_transformation/train_transformed.parquet
         │
         ▼
[Stage 04] model_trainer.py
  → Train RandomForestRegressor (params từ params.yaml)
  → Lưu: artifacts/model_trainer/bias_correction_model.joblib
         │
         ▼
[Stage 05] model_evaluation.py
  → Tính MAE, RMSE, R2 (dự báo thô vs dự báo sau hiệu chỉnh)
  → Lưu: artifacts/model_evaluation/metrics.json
```

### 5.2 Luồng Dự báo Trực tuyến (Prediction Flow)

```
Open-Meteo Forecast API (past_days=10 + hôm nay)
         │
         ▼
[Stage 06] prediction.py
  → Tạo features cho ngày hôm nay (lag, rolling, seasonality)
  → Load: artifacts/model_trainer/bias_correction_model.joblib
  → Tính: forecast_corrected = F_tomorrow + model.predict(features_today)
  → Lưu: artifacts/prediction/forecast_corrected.json
         │
         ▼
app.py (Streamlit Dashboard)
  → Hiển thị: Dự báo đã hiệu chỉnh + So sánh với dự báo gốc + Biểu đồ
```

---

## 6. CẤU HÌNH HỆ THỐNG (System Configuration)

### 6.1 `config/config.yaml` - Đường dẫn Artifacts
```yaml
artifacts_root: artifacts

data_ingestion:
  root_dir: artifacts/data_ingestion
  archive_data_file: artifacts/data_ingestion/hcm_archive.csv
  forecast_data_file: artifacts/data_ingestion/hcm_forecast.csv
  latitude: 10.8231
  longitude: 106.6297
  city_name: "Ho Chi Minh City"

data_transformation:
  train_data_path: artifacts/data_transformation/train_transformed.parquet
  test_data_path: artifacts/data_transformation/test.parquet

model_trainer:
  model_path: artifacts/model_trainer/bias_correction_model.joblib

model_evaluation:
  metric_file_name: artifacts/model_evaluation/metrics.json

prediction:
  output_path: artifacts/prediction/forecast_corrected.json
```

### 6.2 `config/params.yaml` - Siêu tham số
```yaml
RandomForestRegressor:
  n_estimators: 100
  random_state: 42
  max_depth: 12
  n_jobs: -1

PySpark:
  app_name: "Weather_Bias_Correction_HCMC"
  master: "local[*]"
```

### 6.3 `config/schema.yaml` - Schema Dữ liệu
```yaml
COLUMNS:
  date: string
  temp_max: double
  temp_min: double
  temp_mean: double
  precipitation: double
  wind_speed: double
  city: string
```

---

## 7. QUY TẮC PHÁT TRIỂN (Development Rules)

1. **KHÔNG hardcode** bất kỳ đường dẫn, tọa độ, tham số nào trong code Python → phải để trong `config/*.yaml`
2. **KHÔNG dùng `print()`** trong `src/` → phải dùng `logger.info()`, `logger.error()`
3. **KHÔNG random split** dữ liệu time-series → phải cắt theo mốc thời gian
4. **Mỗi Stage Pipeline** phải có hàm `main()` độc lập, chạy được riêng lẻ
5. **Artifacts** của Stage trước là Input của Stage sau → không được bỏ qua Stage
6. Khi thêm đường dẫn artifact mới phải cập nhật đồng bộ: `config.yaml` → `config_entity.py` → `configuration.py`

---

## 8. TIẾN ĐỘ PHÁT TRIỂN (Progress Tracker)

| Phase | Nội dung | Trạng thái |
| :--- | :--- | :---: |
| Phase 0 | Khởi tạo dự án, cấu trúc thư mục | `✅ HOÀN THÀNH` |
| Phase 1 | Config YAML + Utils (logger, common) + Entity + ConfigManager | `🔄 ĐANG LÀM` |
| Phase 2 | Stage 01: Data Ingestion (Open-Meteo API → CSV) | `⏳ CHỜ` |
| Phase 3 | Stage 02: Data Validation (Schema Check) | `⏳ CHỜ` |
| Phase 4 | Stage 03: PySpark Data Transformation (Features + Bias) | `⏳ CHỜ` |
| Phase 5 | Stage 04: Bias Correction Model Trainer | `⏳ CHỜ` |
| Phase 6 | Stage 05: Model Evaluation (MAE so sánh) | `⏳ CHỜ` |
| Phase 7 | Stage 06: Online Prediction Pipeline | `⏳ CHỜ` |
| Phase 8 | Airflow DAG + Streamlit Dashboard | `⏳ CHỜ` |

---

## 9. LỊCH SỬ THAY ĐỔI KIẾN TRÚC (Change Log)

| Ngày | Thay đổi |
| :--- | :--- |
| 2026-06-28 | Khởi tạo ý tưởng: Mô hình dự báo thời tiết đơn giản (Pandas + Scikit-Learn) |
| 2026-06-28 | Quyết định dùng **Open-Meteo API** thay vì Weatherstack (gói free không có historical data) |
| 2026-07-04 | Nâng cấp kiến trúc lên **MLOps Pipeline 6 Stage** chuẩn (tham khảo customer_churn_prediction) |
| 2026-07-04 | Tạo bộ khung `.agents/` (AGENTS.md, PROJECT_MEMORY.md, PHASES.md, Skills) |
| 2026-08-10 | Thảo luận tích hợp **Apache Airflow** để tự động hóa pipeline (dự kiến Phase 8) |
| 2026-08-12 | **Thay đổi trọng tâm**: Khu vực TP.HCM, tích hợp **PySpark** cho Stage 03, bài toán **Bias Correction** |
| 2026-08-12 | Cài đặt môi trường: Miniforge `weather_env` (Python 3.10), PySpark 4.2.0 đã cài thành công |
