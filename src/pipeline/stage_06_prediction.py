from src.config.configuration import ConfigurationManager
from src.components.prediction import PredictionPipeline
from src.utils.logger import logger

STAGE_NAME = "Online Prediction Stage"


class PredictionTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        prediction_config = config.get_prediction_config()
        prediction_pipeline = PredictionPipeline(config=prediction_config)
        prediction_pipeline.predict_future_weather()


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> Stage {STAGE_NAME} bắt đầu <<<<<<")
        obj = PredictionTrainingPipeline()
        obj.main()
        logger.info(f">>>>>> Stage {STAGE_NAME} hoàn thành thành công <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
