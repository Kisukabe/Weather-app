# PROJECT_MEMORY.md - Ngân hàng Ký ức Dự án (Project Memory Bank)

Tệp này lưu trữ ngữ cảnh quan trọng, các quyết định kiến trúc đã thống nhất và thông tin trạng thái tích lũy của dự án Weather.

---

## 1. THÔNG TIN TỔNG QUAN DỰ ÁN
- **Tên dự án:** Automated Weather Forecast Bias Correction Pipeline (TP.HCM)
- **Mục tiêu chính:** Xây dựng hệ thống Data Pipeline tự động thu thập dữ liệu thời tiết, sử dụng **PySpark** để xử lý dữ liệu quy mô lớn và ứng dụng Machine Learning để **hiệu chỉnh sai số (Bias Correction)** giữa dữ liệu dự báo vật lý và thời tiết thực tế tại **TP. Hồ Chí Minh**.
- **Địa điểm trọng tâm:** TP. Hồ Chí Minh (Latitude: `10.8231`, Longitude: `106.6297`)
- **Môi trường:** Python 3.13 / PySpark 3.x (macOS / Miniforge)
- **Tech Stack:**
  - **Data Collection:** Open-Meteo Historical Weather API & Forecast API
  - **Data Processing & Feature Engineering:** **PySpark** (`pyspark.sql`, Window Functions, VectorAssembler)
  - **Machine Learning & Bias Correction:** Scikit-Learn / PySpark MLlib (`RandomForestRegressor`, `GradientBoostedTrees`)
  - **Pipeline Orchestration:** Apache Airflow / Modular 6-Stage MLOps Pipeline
  - **Utilities & Config:** `python-box` (`ConfigBox`), `ensure`, PyYAML, Logging
  - **Frontend / Visualization:** Streamlit, Plotly

---

## 2. CÁC QUYẾT ĐỊNH KIẾN TRÚC ĐÃ THỐNG NHẤT (Key Decisions)

1. **Lựa chọn API Thời tiết:**
   - **Open-Meteo API**: Thu thập cả dữ liệu thực tế lịch sử (Archive) và dữ liệu dự báo vật lý (Forecast) cho TP.HCM không cần API Key.

2. **Bài toán Hiệu chỉnh Sai số (Bias Correction Formulation):**
   - Gọi $F_t$ là dự báo thô của mô hình vật lý khí tượng cho ngày $t$.
   - Gọi $O_t$ là thời tiết đo đạc thực tế tại TP.HCM cho ngày $t$.
   - Sai số mô hình: $E_t = O_t - F_t$.
   - **Mô hình ML** sẽ học hàm dự đoán sai số: $\hat{E}_t = f(F_t, \text{Lags}, \text{Rolling Window}, \text{Seasonality})$.
   - **Dự báo sau hiệu chỉnh:** $\hat{O}_t = F_t + \hat{E}_t$ (giúp giảm đáng kể độ lệch MAE/RMSE so với dự báo thô).

3. **Công nghệ Tiền xử lý & Trích xuất Đặc trưng (PySpark Engine):**
   - Sử dụng **PySpark DataFrames** và **PySpark Window Functions** (`Window.orderBy()`, `lag()`, `avg().over()`) thay cho Pandas thuần để đảm bảo pipeline xử lý song song, sẵn sàng mở rộng quy mô (Big Data).

4. **Kiến trúc MLOps Pipeline:**
   - Xây dựng theo mô hình 6 Stage Pipeline chuẩn, cấu hình động qua YAML, lưu giữ Artifacts trung gian ở từng bước.

---

## 3. LỊCH SỬ THAY ĐỔI & TRẠNG THÁI HIỆN TẠI (State Tracker)
- **2026-06-28:** Khởi tạo ý tưởng và thiết lập kế hoạch `implementation_plan.md`.
- **2026-07-04:** Chuyển đổi toàn bộ cấu hình sang kiến trúc MLOps chuẩn 6 Stage. Tạo 4 file YAML cấu hình.
- **2026-08-12:** Cập nhật yêu cầu nâng cao: Tập trung khu vực **TP.HCM**, tích hợp **PySpark** cho bước Data Transformation và triển khai mô hình **Bias Correction (Hiệu chỉnh sai số dự báo)**.
- **Trạng thái hiện tại:** Đã hoàn thành **Phase 1** (Logger, Common Utils, Config Entities, ConfigurationManager). Chuẩn bị chuyển sang **Phase 2: Stage 01 Data Ingestion** (Thu thập dữ liệu thời tiết TP.HCM qua Open-Meteo API).


