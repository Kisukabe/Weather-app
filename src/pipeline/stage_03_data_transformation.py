from src.config.configuration import ConfigurationManager
from src.components.data_transformation import DataTransformation
from src.utils.logger import logger

STAGE_NAME = "Data Transformation Stage (PySpark Engine)"


class DataTransformationTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        data_transformation_config = config.get_data_transformation_config()
        data_transformation = DataTransformation(config=data_transformation_config)
        data_transformation.transform_and_feature_engineering()


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> Stage {STAGE_NAME} bắt đầu <<<<<<")
        obj = DataTransformationTrainingPipeline()
        obj.main()
        logger.info(f">>>>>> Stage {STAGE_NAME} hoàn thành thành công <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
