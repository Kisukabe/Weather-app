import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from src.utils.logger import logger
from src.entity.config_entity import DataIngestionConfig


class DataIngestion:
    """Tải và lưu trữ dữ liệu thời tiết thực tế và dự báo mở rộng từ Open-Meteo API."""

    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_archive_data(self) -> str:
        """Tải dữ liệu thời tiết thực tế lịch sử (nhiệt độ, lượng mưa, độ ẩm, mây, nắng) từ Archive API."""
        try:
            logger.info("Bắt đầu tải dữ liệu thời tiết lịch sử mở rộng (Archive Data)...")

            end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            start_date = "2023-01-01"

            # Danh sách biến thời tiết mở rộng
            daily_vars = [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "precipitation_sum",
                "wind_speed_10m_max",
                "relative_humidity_2m_mean",
                "cloud_cover_mean",
                "sunshine_duration",
            ]

            url = (
                f"https://archive-api.open-meteo.com/v1/archive?"
                f"latitude={self.config.latitude}&longitude={self.config.longitude}"
                f"&start_date={start_date}&end_date={end_date}"
                f"&daily={','.join(daily_vars)}"
                f"&timezone=Asia%2FBangkok"
            )

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            daily_data = data.get("daily", {})
            df = pd.DataFrame({
                "date": daily_data.get("time", []),
                "temp_max": daily_data.get("temperature_2m_max", []),
                "temp_min": daily_data.get("temperature_2m_min", []),
                "temp_mean": daily_data.get("temperature_2m_mean", []),
                "precipitation": daily_data.get("precipitation_sum", []),
                "wind_speed": daily_data.get("wind_speed_10m_max", []),
                "humidity": daily_data.get("relative_humidity_2m_mean", [75.0] * len(daily_data.get("time", []))),
                "cloud_cover": daily_data.get("cloud_cover_mean", [50.0] * len(daily_data.get("time", []))),
                "rain_probability": [
                    100.0 if (p or 0) > 0.5 else 0.0 for p in daily_data.get("precipitation_sum", [])
                ],
                "sunshine_duration": daily_data.get("sunshine_duration", [0.0] * len(daily_data.get("time", []))),
                "uv_index": [7.0] * len(daily_data.get("time", [])),  # Mặc định UV trung bình TP.HCM
                "city": self.config.city_name,
            })

            # Điền giá trị rỗng nếu có
            df["humidity"] = df["humidity"].fillna(75.0)
            df["cloud_cover"] = df["cloud_cover"].fillna(50.0)
            df["precipitation"] = df["precipitation"].fillna(0.0)

            # Lưu ra file CSV
            df.to_csv(self.config.archive_data_file, index=False)
            logger.info(f"Đã lưu dữ liệu Archive mở rộng ({len(df)} dòng) tại: {self.config.archive_data_file}")
            return str(self.config.archive_data_file)

        except Exception as e:
            logger.error(f"Lỗi khi tải Archive Data: {e}")
            raise e

    def download_forecast_data(self) -> str:
        """Tải dữ liệu dự báo vật lý thô mở rộng từ Open-Meteo Forecast API."""
        try:
            logger.info("Bắt đầu tải dữ liệu dự báo thời tiết mở rộng (Forecast Data)...")

            daily_vars = [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "precipitation_sum",
                "wind_speed_10m_max",
                "relative_humidity_2m_mean",
                "cloud_cover_mean",
                "precipitation_probability_max",
                "sunshine_duration",
                "uv_index_max",
            ]

            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={self.config.latitude}&longitude={self.config.longitude}"
                f"&past_days=92&forecast_days=16"
                f"&daily={','.join(daily_vars)}"
                f"&timezone=Asia%2FBangkok"
            )

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            daily_data = data.get("daily", {})
            times = daily_data.get("time", [])

            df = pd.DataFrame({
                "date": times,
                "temp_max": daily_data.get("temperature_2m_max", []),
                "temp_min": daily_data.get("temperature_2m_min", []),
                "temp_mean": daily_data.get("temperature_2m_mean", []),
                "precipitation": daily_data.get("precipitation_sum", []),
                "wind_speed": daily_data.get("wind_speed_10m_max", []),
                "humidity": daily_data.get("relative_humidity_2m_mean", [75.0] * len(times)),
                "cloud_cover": daily_data.get("cloud_cover_mean", [50.0] * len(times)),
                "rain_probability": daily_data.get("precipitation_probability_max", [0.0] * len(times)),
                "sunshine_duration": daily_data.get("sunshine_duration", [0.0] * len(times)),
                "uv_index": daily_data.get("uv_index_max", [7.0] * len(times)),
                "city": self.config.city_name,
            })

            # Điền giá trị rỗng nếu có
            df["humidity"] = df["humidity"].fillna(75.0)
            df["cloud_cover"] = df["cloud_cover"].fillna(50.0)
            df["rain_probability"] = df["rain_probability"].fillna(0.0)
            df["precipitation"] = df["precipitation"].fillna(0.0)
            df["uv_index"] = df["uv_index"].fillna(7.0)

            # Lưu ra file CSV
            df.to_csv(self.config.forecast_data_file, index=False)
            logger.info(f"Đã lưu dữ liệu Forecast mở rộng ({len(df)} dòng) tại: {self.config.forecast_data_file}")
            return str(self.config.forecast_data_file)

        except Exception as e:
            logger.error(f"Lỗi khi tải Forecast Data: {e}")
            raise e
