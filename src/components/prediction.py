import os
import pandas as pd
import requests
from datetime import datetime
from src.utils.common import load_bin, save_json
from src.utils.logger import logger
from src.entity.config_entity import PredictionConfig


class PredictionPipeline:
    def __init__(self, config: PredictionConfig):
        self.config = config

    def predict_future_weather(self):
        """Tải dự báo mới nhất từ API, hiệu chỉnh sai số bằng ML và lưu JSON."""
        try:
            logger.info("Đang nạp dữ liệu dự báo mới nhất từ Open-Meteo...")
            
            # 1. Đọc dữ liệu forecast thô đã chuẩn bị ở Stage 1
            forecast_path = "artifacts/data_ingestion/hcm_forecast.csv"
            if not os.path.exists(forecast_path):
                raise FileNotFoundError(f"Không tìm thấy file {forecast_path}")

            df_fcst = pd.read_csv(forecast_path)
            
            # Tính toán các đặc trưng (Features) cho dự báo
            df_fcst["date_parsed"] = pd.to_datetime(df_fcst["date"])
            df_fcst["month"] = df_fcst["date_parsed"].dt.month
            df_fcst["dayofweek"] = df_fcst["date_parsed"].dt.dayofweek + 1
            df_fcst["dayofyear"] = df_fcst["date_parsed"].dt.dayofyear

            df_fcst["fcst_temp_max"] = df_fcst["temp_max"]
            df_fcst["fcst_temp_max_lag1"] = df_fcst["fcst_temp_max"].shift(1)
            df_fcst["fcst_temp_max_lag2"] = df_fcst["fcst_temp_max"].shift(2)
            df_fcst["fcst_temp_max_lag3"] = df_fcst["fcst_temp_max"].shift(3)
            df_fcst["rolling_avg_fcst_temp_3d"] = df_fcst["fcst_temp_max"].rolling(3).mean()
            df_fcst["rolling_avg_fcst_temp_7d"] = df_fcst["fcst_temp_max"].rolling(7).mean()

            # Lấy các dòng hợp lệ (loại bỏ Null do shift/rolling)
            df_valid = df_fcst.dropna().copy()

            feature_cols = [
                "fcst_temp_max",
                "fcst_temp_max_lag1",
                "fcst_temp_max_lag2",
                "fcst_temp_max_lag3",
                "rolling_avg_fcst_temp_3d",
                "rolling_avg_fcst_temp_7d",
                "month",
                "dayofweek",
                "dayofyear",
            ]

            X_pred = df_valid[feature_cols]

            # Nạp mô hình ML Bias Correction
            model = load_bin(self.config.model_path)

            # Dự đoán sai số bias & tính nhiệt độ sau hiệu chỉnh
            predicted_bias = model.predict(X_pred)
            df_valid["predicted_bias"] = predicted_bias
            df_valid["corrected_temp_max"] = df_valid["fcst_temp_max"] + predicted_bias

            # Đóng gói kết quả dạng danh sách dict
            results = []
            for _, row in df_valid.iterrows():
                results.append({
                    "date": str(row["date"]),
                    "raw_forecast_temp_max": round(float(row["fcst_temp_max"]), 2),
                    "predicted_bias": round(float(row["predicted_bias"]), 2),
                    "corrected_temp_max": round(float(row["corrected_temp_max"]), 2),
                    "city": str(row["city"]),
                })

            # Lưu ra file output_path (JSON)
            output_data = {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "city": "Ho Chi Minh City",
                "predictions": results,
            }

            save_json(path=self.config.output_path, data=output_data)
            logger.info(f"Đã tạo kết quả dự báo hiệu chỉnh cho {len(results)} ngày tại: {self.config.output_path}")

        except Exception as e:
            logger.error(f"Lỗi trong quá trình dự báo trực tuyến: {e}")
            raise e
