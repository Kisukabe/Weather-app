import os
import pandas as pd
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from src.utils.logger import logger
from src.entity.config_entity import DataTransformationConfig


class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config

    def init_spark_session(self) -> SparkSession:
        """Khởi tạo PySpark Session."""
        spark = (
            SparkSession.builder.appName("Weather_Bias_Correction_HCMC")
            .master("local[*]")
            .config("spark.sql.shuffle.partitions", "4")
            .getOrCreate()
        )
        return spark

    def transform_and_feature_engineering(self):
        """Tiền xử lý và tạo đặc trưng bằng PySpark cho bài toán Bias Correction."""
        try:
            spark = self.init_spark_session()
            logger.info("Đã khởi tạo thành công PySpark Session.")

            # Đọc dữ liệu Archive và Forecast bằng PySpark DataFrame
            archive_df = spark.read.csv(
                str(self.config.input_archive_path), header=True, inferSchema=True
            )
            forecast_df = spark.read.csv(
                str(self.config.input_forecast_path), header=True, inferSchema=True
            )

            # Đổi tên cột để tránh trùng khớp khi JOIN
            archive_df = (
                archive_df.withColumnRenamed("temp_max", "obs_temp_max")
                .withColumnRenamed("temp_min", "obs_temp_min")
                .withColumnRenamed("temp_mean", "obs_temp_mean")
                .withColumnRenamed("precipitation", "obs_precipitation")
                .withColumnRenamed("wind_speed", "obs_wind_speed")
                .drop("city")
            )

            forecast_df = (
                forecast_df.withColumnRenamed("temp_max", "fcst_temp_max")
                .withColumnRenamed("temp_min", "fcst_temp_min")
                .withColumnRenamed("temp_mean", "fcst_temp_mean")
                .withColumnRenamed("precipitation", "fcst_precipitation")
                .withColumnRenamed("wind_speed", "fcst_wind_speed")
                .drop("city")
            )

            # Join 2 tập dữ liệu theo ngày (date)
            merged_df = archive_df.join(forecast_df, on="date", how="inner")

            # Tính Target variable: Bias (Sai số dự báo = Thực tế - Dự báo)
            merged_df = merged_df.withColumn(
                "temp_max_bias", F.col("obs_temp_max") - F.col("fcst_temp_max")
            )

            # Khai báo Window Spec phục vụ Window Functions
            window_spec = Window.orderBy("date")

            # Tạo các đặc trưng trễ (Lag) và trung bình trượt (Rolling)
            transformed_df = (
                merged_df.withColumn(
                    "fcst_temp_max_lag1", F.lag("fcst_temp_max", 1).over(window_spec)
                )
                .withColumn(
                    "fcst_temp_max_lag2", F.lag("fcst_temp_max", 2).over(window_spec)
                )
                .withColumn(
                    "fcst_temp_max_lag3", F.lag("fcst_temp_max", 3).over(window_spec)
                )
                .withColumn(
                    "rolling_avg_fcst_temp_3d",
                    F.avg("fcst_temp_max").over(
                        window_spec.rowsBetween(-2, 0)
                    ),
                )
                .withColumn(
                    "rolling_avg_fcst_temp_7d",
                    F.avg("fcst_temp_max").over(
                        window_spec.rowsBetween(-6, 0)
                    ),
                )
            )

            # Trích xuất đặc trưng thời gian (Seasonality)
            transformed_df = (
                transformed_df.withColumn("date_parsed", F.to_date("date"))
                .withColumn("month", F.month("date_parsed"))
                .withColumn("dayofweek", F.dayofweek("date_parsed"))
                .withColumn("dayofyear", F.dayofyear("date_parsed"))
                .drop("date_parsed")
            )

            # Loại bỏ các dòng bị Null do Lag
            transformed_df = transformed_df.na.drop()

            # Sắp xếp và chia tập Train (80%) / Test (20%)
            ordered_df = transformed_df.orderBy("date")
            total_count = ordered_df.count()
            train_count = int(total_count * 0.8)

            pd_df = ordered_df.toPandas()
            train_pd = pd_df.iloc[:train_count]
            test_pd = pd_df.iloc[train_count:]

            # Lưu file kết quả ra định dạng Parquet
            train_pd.to_parquet(self.config.train_data_path, index=False)
            test_pd.to_parquet(self.config.test_data_path, index=False)

            logger.info(
                f"Đã hoàn tất PySpark Transformation! Tổng: {total_count} dòng. "
                f"Train: {len(train_pd)} dòng, Test: {len(test_pd)} dòng."
            )
            logger.info(f"Train data lưu tại: {self.config.train_data_path}")
            logger.info(f"Test data lưu tại: {self.config.test_data_path}")

            spark.stop()

        except Exception as e:
            logger.error(f"Lỗi trong quá trình Data Transformation: {e}")
            raise e
