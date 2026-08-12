import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from src.utils.common import save_bin
from src.utils.logger import logger
from src.entity.config_entity import ModelTrainerConfig


class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def train(self):
        """Huấn luyện mô hình Bias Correction (RandomForestRegressor)."""
        try:
            logger.info("Đang đọc tập dữ liệu Train Parquet...")
            train_df = pd.read_parquet(self.config.train_data_path)

            # Danh sách các đặc trưng (Features)
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
            target_col = "temp_max_bias"

            X_train = train_df[feature_cols]
            y_train = train_df[target_col]

            logger.info(f"Kích thước tập Train: {X_train.shape[0]} dòng, {X_train.shape[1]} đặc trưng.")
            logger.info(
                f"Huấn luyện mô hình RandomForestRegressor với "
                f"n_estimators={self.config.n_estimators}, max_depth={self.config.max_depth}..."
            )

            # Khởi tạo và huấn luyện mô hình
            rf_model = RandomForestRegressor(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                random_state=self.config.random_state,
                n_jobs=-1,
            )
            rf_model.fit(X_train, y_train)

            # Lưu mô hình huấn luyện được ra file .joblib
            save_bin(data=rf_model, path=self.config.model_path)
            logger.info(f"Đã huấn luyện và lưu mô hình Bias Correction tại: {self.config.model_path}")

        except Exception as e:
            logger.error(f"Lỗi trong quá trình huấn luyện mô hình: {e}")
            raise e
