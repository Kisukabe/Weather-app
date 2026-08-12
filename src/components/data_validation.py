import os
import pandas as pd
from src.utils.logger import logger
from src.entity.config_entity import DataValidationConfig


class DataValidation:
    def __init__(self, config: DataValidationConfig):
        self.config = config

    def validate_all_columns(self) -> bool:
        """Kiểm tra sự tồn tại và tính hợp lệ của tất cả các cột dữ liệu theo Schema."""
        try:
            validation_status = True
            
            # Đọc cả 2 file CSV vừa tải về ở Stage 1
            archive_file = os.path.join(self.config.input_data_dir, "hcm_archive.csv")
            forecast_file = os.path.join(self.config.input_data_dir, "hcm_forecast.csv")

            df_archive = pd.read_csv(archive_file)
            df_forecast = pd.read_csv(forecast_file)

            all_schema_columns = list(self.config.all_schema.keys())

            # Kiểm tra cột cho Archive Data
            archive_cols = list(df_archive.columns)
            for col in all_schema_columns:
                if col not in archive_cols:
                    validation_status = False
                    logger.warning(f"Cột '{col}' không tồn tại trong Archive Data!")

            # Kiểm tra cột cho Forecast Data
            forecast_cols = list(df_forecast.columns)
            for col in all_schema_columns:
                if col not in forecast_cols:
                    validation_status = False
                    logger.warning(f"Cột '{col}' không tồn tại trong Forecast Data!")

            # Ghi trạng thái kiểm tra vào tệp status.txt
            with open(self.config.STATUS_FILE, "w", encoding="utf-8") as f:
                f.write(f"Validation status: {validation_status}")

            if validation_status:
                logger.info("Tất cả các cột dữ liệu đều HỢP LỆ theo Schema!")
            else:
                logger.error("Dữ liệu KHÔNG HỢP LỆ theo Schema!")

            return validation_status

        except Exception as e:
            logger.error(f"Lỗi trong quá trình Data Validation: {e}")
            raise e
