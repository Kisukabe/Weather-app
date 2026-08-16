import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

from src.utils.common import load_bin, save_json
from src.utils.logger import logger
from src.entity.config_entity import PredictionConfig


class PredictionPipeline:
    """Tạo dự báo thời tiết trực tuyến đa chỉ số (Nhiệt độ, Độ ẩm, Mây, Mưa, UV) kết hợp Multi-Model."""

    def __init__(self, config: PredictionConfig):
        self.config = config

    def predict_future_weather(self):
        """Nạp dữ liệu forecast mới nhất, áp dụng toàn bộ Model Registry để hiệu chỉnh sai số."""
        try:
            logger.info("Đang nạp dữ liệu dự báo mới nhất từ Open-Meteo...")

            forecast_path = "artifacts/data_ingestion/hcm_forecast.csv"
            if not os.path.exists(forecast_path):
                raise FileNotFoundError(f"Không tìm thấy file {forecast_path}")

            df_fcst = pd.read_csv(forecast_path)

            # 1. Bổ sung các đặc trưng thời gian (Seasonality)
            df_fcst["date_parsed"] = pd.to_datetime(df_fcst["date"])
            df_fcst["month"] = df_fcst["date_parsed"].dt.month
            df_fcst["dayofweek"] = df_fcst["date_parsed"].dt.dayofweek + 1
            df_fcst["dayofyear"] = df_fcst["date_parsed"].dt.dayofyear

            # 2. Chuẩn bị đặc trưng nhiệt độ và độ ẩm
            df_fcst["fcst_temp_max"] = df_fcst["temp_max"]
            df_fcst["fcst_temp_min"] = df_fcst.get("temp_min", df_fcst["temp_max"] - 5.0)
            df_fcst["fcst_temp_mean"] = df_fcst.get("temp_mean", df_fcst["temp_max"] - 2.5)
            df_fcst["fcst_humidity"] = df_fcst.get("humidity", 75.0)
            df_fcst["fcst_cloud_cover"] = df_fcst.get("cloud_cover", 50.0)
            df_fcst["fcst_rain_probability"] = df_fcst.get("rain_probability", 0.0)

            # 3. Tạo Lag & Rolling Features
            df_fcst["fcst_temp_max_lag1"] = df_fcst["fcst_temp_max"].shift(1)
            df_fcst["fcst_temp_max_lag2"] = df_fcst["fcst_temp_max"].shift(2)
            df_fcst["fcst_temp_max_lag3"] = df_fcst["fcst_temp_max"].shift(3)
            df_fcst["fcst_humidity_lag1"] = df_fcst["fcst_humidity"].shift(1)
            df_fcst["fcst_cloud_cover_lag1"] = df_fcst["fcst_cloud_cover"].shift(1)

            df_fcst["rolling_avg_fcst_temp_3d"] = df_fcst["fcst_temp_max"].rolling(3).mean()
            df_fcst["rolling_avg_fcst_temp_7d"] = df_fcst["fcst_temp_max"].rolling(7).mean()
            df_fcst["rolling_avg_fcst_humidity_3d"] = df_fcst["fcst_humidity"].rolling(3).mean()
            df_fcst["fcst_temp_range"] = df_fcst["fcst_temp_max"] - df_fcst["fcst_temp_min"]

            # Lọc bỏ các dòng Null đầu chuỗi (do shift)
            df_valid = df_fcst.dropna().copy()

            candidate_features = [
                "fcst_temp_max",
                "fcst_temp_max_lag1",
                "fcst_temp_max_lag2",
                "fcst_temp_max_lag3",
                "fcst_temp_range",
                "rolling_avg_fcst_temp_3d",
                "rolling_avg_fcst_temp_7d",
                "fcst_humidity_lag1",
                "rolling_avg_fcst_humidity_3d",
                "fcst_cloud_cover_lag1",
                "month",
                "dayofweek",
                "dayofyear",
            ]

            feature_cols = [c for c in candidate_features if c in df_valid.columns]
            X_pred = df_valid[feature_cols]

            # 4. Nạp các mô hình Hồi quy Bias Correction từ Model Registry
            models_dir = Path(self.config.model_path).parent
            model_keys = ["xgboost", "lightgbm", "random_forest", "linear_regression"]
            loaded_models = {}

            for m_name in model_keys:
                m_file = models_dir / f"{m_name}.joblib"
                if m_file.exists():
                    try:
                        loaded_models[m_name] = load_bin(m_file)
                    except Exception as e:
                        logger.warning(f"Không thể nạp mô hình {m_name}: {e}")

            # Fallback nếu chưa có file riêng
            if not loaded_models and Path(self.config.model_path).exists():
                loaded_models["xgboost"] = load_bin(self.config.model_path)

            # 5. Nạp Rain Classifier
            rain_clf = None
            rain_file = models_dir / "rain_classifier.joblib"
            if rain_file.exists():
                try:
                    rain_clf = load_bin(rain_file)
                except Exception as e:
                    logger.warning(f"Không thể nạp Rain Classifier: {e}")

            # 6. Dự đoán cho từng ngày trong tương lai
            rain_intensity_labels = {0: "Không mưa", 1: "Mưa nhỏ", 2: "Mưa vừa", 3: "Mưa to"}
            predictions_list = []

            for idx, (_, row) in enumerate(df_valid.iterrows()):
                x_row = X_pred.iloc[[idx]]
                row_date = str(row["date"])
                raw_temp_max = round(float(row["fcst_temp_max"]), 2)
                raw_temp_min = round(float(row.get("temp_min", raw_temp_max - 5.0)), 2)

                # Tính kết quả dự đoán của từng mô hình
                model_predictions = {}
                for m_name, m_obj in loaded_models.items():
                    bias_pred = float(m_obj.predict(x_row)[0])
                    corr_temp = raw_temp_max + bias_pred
                    model_predictions[m_name] = {
                        "predicted_bias": round(bias_pred, 2),
                        "corrected_temp_max": round(corr_temp, 2),
                    }

                # Mô hình mặc định (XGBoost hoặc mô hình đầu tiên)
                default_pred = model_predictions.get("xgboost", next(iter(model_predictions.values()), {}))
                default_bias = default_pred.get("predicted_bias", 0.0)
                default_corrected = default_pred.get("corrected_temp_max", raw_temp_max)

                # Dự báo mưa
                will_rain_pred = 0
                if rain_clf is not None:
                    try:
                        will_rain_pred = int(rain_clf.predict(x_row)[0])
                    except Exception:
                        will_rain_pred = 1 if float(row.get("rain_probability", 0)) >= 50 else 0
                else:
                    will_rain_pred = 1 if float(row.get("rain_probability", 0)) >= 50 else 0

                pred_item = {
                    "date": row_date,
                    "city": str(row.get("city", "Ho Chi Minh City")),
                    # Dự báo nhiệt độ chính
                    "raw_forecast_temp_max": raw_temp_max,
                    "raw_forecast_temp_min": raw_temp_min,
                    "predicted_bias": default_bias,
                    "corrected_temp_max": default_corrected,
                    # Dự báo chi tiết các chỉ số mở rộng
                    "humidity": round(float(row.get("humidity", 75.0)), 1),
                    "cloud_cover": round(float(row.get("cloud_cover", 50.0)), 1),
                    "rain_probability": round(float(row.get("rain_probability", 0.0)), 1),
                    "sunshine_duration_hours": round(float(row.get("sunshine_duration", 0.0)) / 3600, 1),
                    "uv_index": round(float(row.get("uv_index", 7.0)), 1),
                    # Dự báo mưa
                    "will_rain": bool(will_rain_pred),
                    "rain_status": "Có mưa" if will_rain_pred == 1 else "Không mưa",
                    # Dự đoán riêng của từng mô hình (Model Registry)
                    "models": model_predictions,
                }
                predictions_list.append(pred_item)

            # 7. Đóng gói file JSON
            output_data = {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "city": "Ho Chi Minh City",
                "total_forecast_days": len(predictions_list),
                "default_model": "xgboost",
                "available_models": list(loaded_models.keys()),
                "predictions": predictions_list,
            }

            save_json(path=self.config.output_path, data=output_data)
            logger.info(f"✅ Đã tạo kết quả dự báo 7 chỉ số cho {len(predictions_list)} ngày tại: {self.config.output_path}")

            # 8. Lưu vào SQLite Database History
            try:
                from backend.app.db.session import get_connection
                with get_connection() as conn:
                    cursor = conn.cursor()
                    for item in predictions_list:
                        cursor.execute(
                            """
                            INSERT INTO predictions_history 
                            (forecast_date, model_name, raw_temp_max, corrected_temp_max, predicted_bias, humidity, cloud_cover, will_rain, city)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                item["date"],
                                "xgboost",
                                item["raw_forecast_temp_max"],
                                item["corrected_temp_max"],
                                item["predicted_bias"],
                                item["humidity"],
                                item["cloud_cover"],
                                1 if item["will_rain"] else 0,
                                item["city"],
                            ),
                        )
                    conn.commit()
                    logger.info("Đã ghi vết lịch sử dự báo vào SQLite Database.")
            except Exception as e:
                logger.debug(f"Bỏ qua ghi SQLite nếu DB chưa sẵn sàng: {e}")

        except Exception as e:
            logger.error(f"Lỗi trong quá trình dự báo trực tuyến: {e}")
            raise e
