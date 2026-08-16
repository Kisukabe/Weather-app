import os
import pandas as pd
import numpy as np
from pathlib import Path
from src.utils.logger import logger
from src.entity.config_entity import DataTransformationConfig


class DataTransformation:
    """
    Tiền xử lý dữ liệu và tạo đặc trưng Multi-Target.
    Hỗ trợ Apache PySpark Engine với cơ chế tự động Fallback sang Pandas
    nếu môi trường thiếu Java 17+.
    """

    def __init__(self, config: DataTransformationConfig):
        self.config = config

    def _transform_with_pandas(self, archive_path: str, forecast_path: str):
        """Xử lý dữ liệu bằng Pandas (Fallback engine khi Java/PySpark không khả dụng)."""
        logger.info("⚡ Đang thực thi Data Transformation bằng Pandas Engine...")

        df_arch = pd.read_csv(archive_path)
        df_fcst = pd.read_csv(forecast_path)

        # 1. Đổi tên cột
        arch_renames = {c: f"obs_{c}" for c in df_arch.columns if c not in ["date", "city"]}
        fcst_renames = {c: f"fcst_{c}" for c in df_fcst.columns if c not in ["date", "city"]}
        df_arch = df_arch.rename(columns=arch_renames).drop(columns=["city"], errors="ignore")
        df_fcst = df_fcst.rename(columns=fcst_renames).drop(columns=["city"], errors="ignore")

        # 2. Join dữ liệu theo date
        merged_df = pd.merge(df_arch, df_fcst, on="date", how="inner").sort_values("date").reset_index(drop=True)

        # 3. Đảm bảo tồn tại các cột cần thiết (phòng trường hợp file CSV cũ)
        if "obs_humidity" not in merged_df.columns:
            merged_df["obs_humidity"] = 75.0
        if "fcst_humidity" not in merged_df.columns:
            merged_df["fcst_humidity"] = 75.0
        if "obs_cloud_cover" not in merged_df.columns:
            merged_df["obs_cloud_cover"] = 50.0
        if "fcst_cloud_cover" not in merged_df.columns:
            merged_df["fcst_cloud_cover"] = 50.0
        if "obs_precipitation" not in merged_df.columns:
            merged_df["obs_precipitation"] = 0.0

        # 4. Tính các Target Variables
        merged_df["temp_max_bias"] = merged_df["obs_temp_max"] - merged_df["fcst_temp_max"]
        merged_df["temp_min_bias"] = merged_df["obs_temp_min"] - merged_df["fcst_temp_min"]
        merged_df["temp_mean_bias"] = merged_df["obs_temp_mean"] - merged_df["fcst_temp_mean"]
        merged_df["humidity_bias"] = merged_df["obs_humidity"] - merged_df["fcst_humidity"]
        merged_df["cloud_cover_bias"] = merged_df["obs_cloud_cover"] - merged_df["fcst_cloud_cover"]

        # Classification targets
        merged_df["will_rain"] = (merged_df["obs_precipitation"] > 0.5).astype(int)
        merged_df["rain_intensity"] = pd.cut(
            merged_df["obs_precipitation"],
            bins=[-float("inf"), 0.5, 5.0, 20.0, float("inf")],
            labels=[0, 1, 2, 3],
        ).fillna(0).astype(int)

        # 5. Tạo đặc trưng trễ (Lags) & Trung bình trượt (Rolling)
        merged_df["fcst_temp_max_lag1"] = merged_df["fcst_temp_max"].shift(1)
        merged_df["fcst_temp_max_lag2"] = merged_df["fcst_temp_max"].shift(2)
        merged_df["fcst_temp_max_lag3"] = merged_df["fcst_temp_max"].shift(3)
        merged_df["fcst_humidity_lag1"] = merged_df["fcst_humidity"].shift(1)
        merged_df["fcst_cloud_cover_lag1"] = merged_df["fcst_cloud_cover"].shift(1)

        merged_df["rolling_avg_fcst_temp_3d"] = merged_df["fcst_temp_max"].rolling(3).mean()
        merged_df["rolling_avg_fcst_temp_7d"] = merged_df["fcst_temp_max"].rolling(7).mean()
        merged_df["rolling_avg_fcst_humidity_3d"] = merged_df["fcst_humidity"].rolling(3).mean()
        merged_df["fcst_temp_range"] = merged_df["fcst_temp_max"] - merged_df["fcst_temp_min"]

        # 6. Seasonality
        dates = pd.to_datetime(merged_df["date"])
        merged_df["month"] = dates.dt.month
        merged_df["dayofweek"] = dates.dt.dayofweek + 1
        merged_df["dayofyear"] = dates.dt.dayofyear

        # 7. Loại bỏ Null
        valid_df = merged_df.dropna().copy()

        # 8. Split Train / Test
        total_count = len(valid_df)
        train_count = int(total_count * 0.8)
        train_df = valid_df.iloc[:train_count]
        test_df = valid_df.iloc[train_count:]

        # 9. Lưu Parquet
        Path(self.config.train_data_path).parent.mkdir(parents=True, exist_ok=True)
        train_df.to_parquet(self.config.train_data_path, index=False)
        test_df.to_parquet(self.config.test_data_path, index=False)

        logger.info(
            f"✅ [Pandas Engine] Hoàn tất Data Transformation! Tổng: {total_count} dòng. "
            f"Train: {len(train_df)} dòng, Test: {len(test_df)} dòng."
        )

    def transform_and_feature_engineering(self):
        """Tiền xử lý dữ liệu với PySpark, tự động fallback sang Pandas nếu lỗi Java."""
        try:
            from pyspark.sql import SparkSession
            from pyspark.sql import functions as F
            from pyspark.sql.window import Window

            logger.info("Đang khởi tạo PySpark Session...")
            spark = (
                SparkSession.builder.appName("Weather_MultiTarget_Transformation")
                .master("local[*]")
                .config("spark.sql.shuffle.partitions", "2")
                .config("spark.driver.memory", "1g")
                .getOrCreate()
            )

            archive_df = spark.read.csv(str(self.config.input_archive_path), header=True, inferSchema=True)
            forecast_df = spark.read.csv(str(self.config.input_forecast_path), header=True, inferSchema=True)

            for col in archive_df.columns:
                if col not in ["date", "city"]:
                    archive_df = archive_df.withColumnRenamed(col, f"obs_{col}")
            archive_df = archive_df.drop("city")

            for col in forecast_df.columns:
                if col not in ["date", "city"]:
                    forecast_df = forecast_df.withColumnRenamed(col, f"fcst_{col}")
            forecast_df = forecast_df.drop("city")

            merged_df = archive_df.join(forecast_df, on="date", how="inner")

            merged_df = (
                merged_df.withColumn("temp_max_bias", F.col("obs_temp_max") - F.col("fcst_temp_max"))
                .withColumn("temp_min_bias", F.col("obs_temp_min") - F.col("fcst_temp_min"))
                .withColumn("temp_mean_bias", F.col("obs_temp_mean") - F.col("fcst_temp_mean"))
                .withColumn("humidity_bias", F.col("obs_humidity") - F.col("fcst_humidity"))
                .withColumn("cloud_cover_bias", F.col("obs_cloud_cover") - F.col("fcst_cloud_cover"))
            )

            merged_df = merged_df.withColumn(
                "will_rain",
                F.when(F.col("obs_precipitation") > 0.5, 1).otherwise(0),
            ).withColumn(
                "rain_intensity",
                F.when(F.col("obs_precipitation") <= 0.5, 0)
                .when(F.col("obs_precipitation") <= 5.0, 1)
                .when(F.col("obs_precipitation") <= 20.0, 2)
                .otherwise(3),
            )

            window_spec = Window.orderBy("date")
            transformed_df = (
                merged_df
                .withColumn("fcst_temp_max_lag1", F.lag("fcst_temp_max", 1).over(window_spec))
                .withColumn("fcst_temp_max_lag2", F.lag("fcst_temp_max", 2).over(window_spec))
                .withColumn("fcst_temp_max_lag3", F.lag("fcst_temp_max", 3).over(window_spec))
                .withColumn("fcst_humidity_lag1", F.lag("fcst_humidity", 1).over(window_spec))
                .withColumn("fcst_cloud_cover_lag1", F.lag("fcst_cloud_cover", 1).over(window_spec))
                .withColumn("rolling_avg_fcst_temp_3d", F.avg("fcst_temp_max").over(window_spec.rowsBetween(-2, 0)))
                .withColumn("rolling_avg_fcst_temp_7d", F.avg("fcst_temp_max").over(window_spec.rowsBetween(-6, 0)))
                .withColumn("rolling_avg_fcst_humidity_3d", F.avg("fcst_humidity").over(window_spec.rowsBetween(-2, 0)))
                .withColumn("fcst_temp_range", F.col("fcst_temp_max") - F.col("fcst_temp_min"))
                .withColumn("date_parsed", F.to_date("date"))
                .withColumn("month", F.month("date_parsed"))
                .withColumn("dayofweek", F.dayofweek("date_parsed"))
                .withColumn("dayofyear", F.dayofyear("date_parsed"))
                .drop("date_parsed")
                .na.drop()
            )

            ordered_df = transformed_df.orderBy("date")
            total_count = ordered_df.count()
            train_count = int(total_count * 0.8)

            pd_df = ordered_df.toPandas()
            train_pd = pd_df.iloc[:train_count]
            test_pd = pd_df.iloc[train_count:]

            Path(self.config.train_data_path).parent.mkdir(parents=True, exist_ok=True)
            train_pd.to_parquet(self.config.train_data_path, index=False)
            test_pd.to_parquet(self.config.test_data_path, index=False)

            logger.info(
                f"✅ [PySpark Engine] Hoàn tất Data Transformation! Tổng: {total_count} dòng. "
                f"Train: {len(train_pd)} dòng, Test: {len(test_pd)} dòng."
            )
            spark.stop()

        except Exception as e:
            logger.warning(
                f"PySpark không thể khởi chạy trên môi trường local (Lỗi: {e}). "
                "Tự động chuyển sang Pandas Fallback Engine để hoàn tất quá trình..."
            )
            self._transform_with_pandas(
                archive_path=str(self.config.input_archive_path),
                forecast_path=str(self.config.input_forecast_path),
            )
