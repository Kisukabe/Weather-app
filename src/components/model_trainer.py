import os
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import Ridge
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

from src.utils.common import save_bin
from src.utils.logger import logger
from src.entity.config_entity import ModelTrainerConfig


class ModelTrainer:
    """Huấn luyện và đóng gói Model Registry gồm 4 thuật toán Hồi quy và 1 Bộ phân loại Mưa."""

    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def train(self):
        """Huấn luyện tập hợp các mô hình trong Model Registry."""
        try:
            logger.info("Đang đọc tập dữ liệu Train Parquet...")
            train_df = pd.read_parquet(self.config.train_data_path)

            # 1. Tập hợp các đặc trưng đầu vào (Features)
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

            # Chỉ lấy các cột thực sự có trong train_df
            feature_cols = [col for col in candidate_features if col in train_df.columns]
            target_col = "temp_max_bias"

            X_train = train_df[feature_cols]
            y_train = train_df[target_col]

            logger.info(f"Kích thước tập Train: {X_train.shape[0]} dòng, {X_train.shape[1]} đặc trưng: {feature_cols}")

            # Thư mục lưu trữ models
            model_dir = Path(self.config.model_path).parent
            model_dir.mkdir(parents=True, exist_ok=True)

            # 2. Khởi tạo 4 mô hình Hồi quy Bias Correction
            models = {
                "random_forest": RandomForestRegressor(
                    n_estimators=self.config.n_estimators or 100,
                    max_depth=self.config.max_depth or 12,
                    random_state=self.config.random_state or 42,
                    n_jobs=-1,
                ),
                "xgboost": XGBRegressor(
                    n_estimators=200,
                    max_depth=6,
                    learning_rate=0.05,
                    random_state=42,
                    n_jobs=-1,
                ),
                "lightgbm": LGBMRegressor(
                    n_estimators=200,
                    learning_rate=0.05,
                    random_state=42,
                    verbose=-1,
                ),
                "linear_regression": Ridge(alpha=1.0),
            }

            # 3. Huấn luyện từng mô hình và lưu ra file riêng
            for name, model in models.items():
                logger.info(f"Đang huấn luyện mô hình: {name}...")
                model.fit(X_train, y_train)
                save_path = model_dir / f"{name}.joblib"
                save_bin(data=model, path=save_path)
                logger.info(f"Đã lưu mô hình {name} tại: {save_path}")

            # Lưu mô hình mặc định (XGBoost / RandomForest) vào model_path
            default_model = models["xgboost"]
            save_bin(data=default_model, path=self.config.model_path)
            logger.info(f"Đã lưu mô hình mặc định (XGBoost) tại: {self.config.model_path}")

            # 4. Huấn luyện Rain Classifier (Dự báo mưa) nếu có cột will_rain
            if "will_rain" in train_df.columns:
                logger.info("Đang huấn luyện mô hình Phân loại Mưa (Rain Classifier)...")
                y_rain = train_df["will_rain"]
                rain_clf = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=8,
                    random_state=42,
                    n_jobs=-1,
                )
                rain_clf.fit(X_train, y_rain)
                rain_path = model_dir / "rain_classifier.joblib"
                save_bin(data=rain_clf, path=rain_path)
                logger.info(f"Đã lưu Rain Classifier tại: {rain_path}")

            logger.info("🎉 Hoàn tất huấn luyện toàn bộ Model Registry thành công!")

        except Exception as e:
            logger.error(f"Lỗi trong quá trình huấn luyện mô hình: {e}")
            raise e
