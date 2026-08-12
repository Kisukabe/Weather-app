# PHASES.md - Theo dõi Các Giai đoạn Phát triển (Phases Roadmap)

Tệp này dùng để quản lý tiến độ thực hiện từng giai đoạn (Phase) của dự án Weather MLOps.

---

## BẢNG TIẾN ĐỘ TỔNG QUAN

| Phase | Tên giai đoạn | Trạng thái | Đầu ra chính (Key Outputs) |
| :--- | :--- | :---: | :--- |
| **Phase 0** | Khởi tạo Dự án & Môi trường | `COMPLETED` | `requirements.txt`, Cấu trúc thư mục, `ARCHITECTURE_EXPLANATION.md` |
| **Phase 1** | Cấu hình & Công cụ Nền tảng | `COMPLETED` | `config/*.yaml`, `src/utils/`, `src/entity/`, `src/config/` |
| **Phase 2** | Stage 01: Data Ingestion (TP.HCM) | `COMPLETED` | `src/components/data_ingestion.py`, `hcm_archive.csv` (1,319 dòng), `hcm_forecast.csv` (108 dòng) |

| **Phase 3** | Stage 02: Data Validation Pipeline | `COMPLETED` | `src/components/data_validation.py`, `status.txt` (Validation status: True) |

| **Phase 4** | Stage 03: PySpark Data Transformation | `COMPLETED` | `src/components/data_transformation.py` (PySpark Engine: 86 dòng train, 22 dòng test) |

| **Phase 5** | Stage 04: Bias Correction Model Trainer | `COMPLETED` | `src/components/model_trainer.py`, `bias_correction_model.joblib` |

| **Phase 6** | Stage 05: Model Evaluation Pipeline | `COMPLETED` | `src/components/model_evaluation.py`, `metrics.json` |

| **Phase 7** | Stage 06: Online Prediction Pipeline | `COMPLETED` | `src/components/prediction.py`, `forecast_corrected.json` |

| **Phase 8** | Chạy Pipeline Tự động (Airflow) & Web UI | `PENDING` | `dags/weather_pipeline_dag.py`, `app.py` (Streamlit Dashboard) |

---

## CHI TIẾT CÁC BƯỚC ĐÃ HOÀN THÀNH TRONG PHASE 1

- [x] Tạo 4 tệp YAML cấu hình (`config/config.yaml`, `config/params.yaml`, `config/schema.yaml`, `config/logging.yaml`)
- [x] Tạo bộ khung thư mục `src/`, `artifacts/`, `logs/`
- [x] Hoàn thiện `src/utils/logger.py` (Khởi tạo hệ thống logging)
- [x] Hoàn thiện `src/utils/common.py` (Hàm đọc YAML, tạo folder, lưu JSON/bin)
- [x] Hoàn thiện `src/entity/config_entity.py` (Định nghĩa dataclasses cho 6 stage)
- [x] Hoàn thiện `src/config/configuration.py` (Lớp `ConfigurationManager`)

