import os
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from src.utils.common import load_bin, save_json
from src.utils.logger import logger
from src.entity.config_entity import ModelEvaluationConfig


class ModelEvaluation:
    """Đánh giá toàn diện Model Registry và so sánh ma trận metrics trên tập Test."""

    def __init__(self, config: ModelEvaluationConfig):
        self.config = config

    def eval_metrics(self, actual, pred):
        mae = mean_absolute_error(actual, pred)
        rmse = np.sqrt(mean_squared_error(actual, pred))
        r2 = r2_score(actual, pred) if len(actual) > 1 else 0.0
        return float(mae), float(rmse), float(r2)

    def evaluate_model(self):
        """Đánh giá tất cả các mô hình trong Model Registry và lưu bảng so sánh chi tiết."""
        try:
            logger.info("Đang đọc tập dữ liệu Test Parquet...")
            test_df = pd.read_parquet(self.config.test_data_path)

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

            feature_cols = [col for col in candidate_features if col in test_df.columns]
            X_test = test_df[feature_cols]
            y_obs_actual = test_df["obs_temp_max"]
            fcst_raw = test_df["fcst_temp_max"]

            # 1. Tính toán chỉ số cho Dự báo thô vật lý (Raw Forecast)
            raw_mae, raw_rmse, raw_r2 = self.eval_metrics(y_obs_actual, fcst_raw)
            logger.info(f"📊 Dự báo thô (Raw Forecast) - MAE: {raw_mae:.4f}°C | RMSE: {raw_rmse:.4f}°C")

            models_dir = Path(self.config.model_path).parent
            model_names = ["xgboost", "lightgbm", "random_forest", "linear_regression"]
            models_comparison = {}
            best_model_name = None
            lowest_mae = float("inf")

            # 2. Đánh giá từng mô hình Hồi quy Bias Correction
            for name in model_names:
                model_file = models_dir / f"{name}.joblib"
                if not model_file.exists():
                    # Fallback sang model mặc định nếu file riêng chưa có
                    model_file = self.config.model_path

                try:
                    model = load_bin(model_file)
                    predicted_bias = model.predict(X_test)
                    corrected_forecast = fcst_raw + predicted_bias

                    corr_mae, corr_rmse, corr_r2 = self.eval_metrics(y_obs_actual, corrected_forecast)
                    mae_reduction = float(((raw_mae - corr_mae) / raw_mae) * 100) if raw_mae != 0 else 0.0

                    models_comparison[name] = {
                        "mae": corr_mae,
                        "rmse": corr_rmse,
                        "r2": corr_r2,
                        "mae_reduction_percentage": mae_reduction,
                    }

                    logger.info(
                        f"🤖 Model [{name.upper():<16}] - MAE: {corr_mae:.4f}°C | Cải thiện: {mae_reduction:+.2f}%"
                    )

                    if corr_mae < lowest_mae:
                        lowest_mae = corr_mae
                        best_model_name = name

                except Exception as e:
                    logger.warning(f"Không thể đánh giá mô hình {name}: {e}")

            # Lấy metrics của mô hình tốt nhất hoặc mặc định
            default_metrics = models_comparison.get(
                best_model_name,
                {"mae": raw_mae, "rmse": raw_rmse, "r2": raw_r2, "mae_reduction_percentage": 0.0},
            )

            # 3. Đánh giá Rain Classifier nếu có
            rain_metrics = {}
            rain_model_file = models_dir / "rain_classifier.joblib"
            if rain_model_file.exists() and "will_rain" in test_df.columns:
                try:
                    rain_clf = load_bin(rain_model_file)
                    y_rain_true = test_df["will_rain"]
                    y_rain_pred = rain_clf.predict(X_test)

                    acc = accuracy_score(y_rain_true, y_rain_pred)
                    prec = precision_score(y_rain_true, y_rain_pred, zero_division=0)
                    rec = recall_score(y_rain_true, y_rain_pred, zero_division=0)
                    f1 = f1_score(y_rain_true, y_rain_pred, zero_division=0)

                    rain_metrics = {
                        "accuracy": float(acc),
                        "precision": float(prec),
                        "recall": float(rec),
                        "f1_score": float(f1),
                    }
                    logger.info(f"🌧️ Rain Classifier - Accuracy: {acc*100:.1f}% | F1-Score: {f1:.3f}")
                except Exception as e:
                    logger.warning(f"Lỗi khi đánh giá Rain Classifier: {e}")

            # 4. Đóng gói kết quả toàn diện vào metrics.json
            scores = {
                "best_model": best_model_name or "xgboost",
                "raw_forecast_metrics": {
                    "mae": raw_mae,
                    "rmse": raw_rmse,
                    "r2": raw_r2,
                },
                "corrected_forecast_metrics": default_metrics,
                "improvement": {
                    "mae_reduction_percentage": default_metrics.get("mae_reduction_percentage", 0.0),
                },
                "models_comparison": models_comparison,
                "rain_classification_metrics": rain_metrics,
            }

            save_json(path=self.config.metric_file_name, data=scores)
            logger.info(f"✅ Đã lưu ma trận đánh giá chi tiết tại: {self.config.metric_file_name}")

            # 5. Lưu vào SQLite Database nếu có session
            try:
                from backend.app.db.session import get_connection
                with get_connection() as conn:
                    cursor = conn.cursor()
                    for m_name, m_data in models_comparison.items():
                        cursor.execute(
                            """
                            INSERT INTO model_metrics_history 
                            (model_name, target_name, mae, rmse, r2, mae_reduction_percentage)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                m_name,
                                "temp_max_bias",
                                m_data["mae"],
                                m_data["rmse"],
                                m_data["r2"],
                                m_data["mae_reduction_percentage"],
                            ),
                        )
                    conn.commit()
                    logger.info("Đã ghi vết lịch sử đánh giá mô hình vào SQLite Database.")
            except Exception as e:
                logger.debug(f"Bỏ qua ghi SQLite nếu DB chưa sẵn sàng: {e}")

        except Exception as e:
            logger.error(f"Lỗi trong quá trình đánh giá mô hình: {e}")
            raise e
