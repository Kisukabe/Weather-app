import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.utils.common import load_bin, save_json
from src.utils.logger import logger
from src.entity.config_entity import ModelEvaluationConfig


class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config

    def eval_metrics(self, actual, pred):
        mae = mean_absolute_error(actual, pred)
        rmse = np.sqrt(mean_squared_error(actual, pred))
        r2 = r2_score(actual, pred)
        return mae, rmse, r2

    def evaluate_model(self):
        """Đánh giá hiệu quả mô hình Bias Correction trên tập Test."""
        try:
            logger.info("Đang đọc tập dữ liệu Test Parquet...")
            test_df = pd.read_parquet(self.config.test_data_path)

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

            X_test = test_df[feature_cols]
            y_obs_actual = test_df["obs_temp_max"]
            fcst_raw = test_df["fcst_temp_max"]

            # Nạp mô hình đã huấn luyện
            model = load_bin(self.config.model_path)

            # 1. Dự đoán sai số bias bằng ML
            predicted_bias = model.predict(X_test)

            # 2. Nhiệt độ sau hiệu chỉnh: Corrected = Raw Forecast + Predicted Bias
            corrected_forecast = fcst_raw + predicted_bias

            # 3. Tính toán chỉ số cho Dự báo thô (Raw Forecast)
            raw_mae, raw_rmse, raw_r2 = self.eval_metrics(y_obs_actual, fcst_raw)

            # 4. Tính toán chỉ số cho Dự báo sau hiệu chỉnh (Corrected Forecast)
            corr_mae, corr_rmse, corr_r2 = self.eval_metrics(y_obs_actual, corrected_forecast)

            mae_reduction = (
                float(((raw_mae - corr_mae) / raw_mae) * 100)
                if raw_mae != 0
                else 0.0
            )

            scores = {
                "raw_forecast_metrics": {
                    "mae": float(raw_mae),
                    "rmse": float(raw_rmse),
                    "r2": float(raw_r2),
                },
                "corrected_forecast_metrics": {
                    "mae": float(corr_mae),
                    "rmse": float(corr_rmse),
                    "r2": float(corr_r2),
                },
                "improvement": {
                    "mae_reduction_percentage": mae_reduction
                },
            }


            # Lưu các thông số đánh giá vào metrics.json
            save_json(path=self.config.metric_file_name, data=scores)
            
            logger.info(f"MAE Dự báo thô: {raw_mae:.4f}°C | MAE Sau hiệu chỉnh: {corr_mae:.4f}°C")
            logger.info(
                f"Độ cải thiện MAE: {scores['improvement']['mae_reduction_percentage']:.2f}%"
            )
            logger.info(f"Đã lưu kết quả đánh giá tại: {self.config.metric_file_name}")

        except Exception as e:
            logger.error(f"Lỗi trong quá trình đánh giá mô hình: {e}")
            raise e
