from src.config.configuration import ConfigurationManager
from src.components.data_ingestion import DataIngestion
from src.utils.logger import logger

STAGE_NAME = "Data Ingestion Stage"


class DataIngestionTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        data_ingestion_config = config.get_data_ingestion_config()
        data_ingestion = DataIngestion(config=data_ingestion_config)
        data_ingestion.download_archive_data()
        data_ingestion.download_forecast_data()


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> Stage {STAGE_NAME} bắt đầu <<<<<<")
        obj = DataIngestionTrainingPipeline()
        obj.main()
        logger.info(f">>>>>> Stage {STAGE_NAME} hoàn thành thành công <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
