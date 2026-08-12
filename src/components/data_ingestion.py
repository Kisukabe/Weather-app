import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from src.utils.logger import logger
from src.entity.config_entity import DataIngestionConfig


class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_archive_data(self) -> str:
        """Tải dữ liệu thời tiết thực tế lịch sử tại TP.HCM từ Open-Meteo Archive API."""
        try:
            logger.info("Bắt đầu tải dữ liệu thời tiết lịch sử (Archive Data)...")
            
            # Đặt khoảng thời gian lấy dữ liệu (Ví dụ: từ 2023-01-01 đến ngày hôm qua)
            end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            start_date = "2023-01-01"

            url = (
                f"https://archive-api.open-meteo.com/v1/archive?"
                f"latitude={self.config.latitude}&longitude={self.config.longitude}"
                f"&start_date={start_date}&end_date={end_date}"
                f"&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
                f"precipitation_sum,wind_speed_10m_max"
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
                "city": self.config.city_name,
            })

            # Lưu ra file CSV
            df.to_csv(self.config.archive_data_file, index=False)
            logger.info(f"Đã lưu dữ liệu Archive ({len(df)} dòng) tại: {self.config.archive_data_file}")
            return str(self.config.archive_data_file)

        except Exception as e:
            logger.error(f"Lỗi khi tải Archive Data: {e}")
            raise e

    def download_forecast_data(self) -> str:
        """Tải dữ liệu dự báo vật lý thô tại TP.HCM từ Open-Meteo Forecast API."""
        try:
            logger.info("Bắt đầu tải dữ liệu dự báo thời tiết (Forecast Data)...")

            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={self.config.latitude}&longitude={self.config.longitude}"
                f"&past_days=92&forecast_days=16"
                f"&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
                f"precipitation_sum,wind_speed_10m_max"
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
                "city": self.config.city_name,
            })

            # Lưu ra file CSV
            df.to_csv(self.config.forecast_data_file, index=False)
            logger.info(f"Đã lưu dữ liệu Forecast ({len(df)} dòng) tại: {self.config.forecast_data_file}")
            return str(self.config.forecast_data_file)

        except Exception as e:
            logger.error(f"Lỗi khi tải Forecast Data: {e}")
            raise e
