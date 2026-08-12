from src.utils.logger import logger
from src.pipeline.stage_01_data_ingestion import DataIngestionTrainingPipeline
from src.pipeline.stage_02_data_validation import DataValidationTrainingPipeline
from src.pipeline.stage_03_data_transformation import DataTransformationTrainingPipeline
from src.pipeline.stage_04_model_trainer import ModelTrainerTrainingPipeline
from src.pipeline.stage_05_model_evaluation import ModelEvaluationTrainingPipeline
from src.pipeline.stage_06_prediction import PredictionTrainingPipeline


def run_pipeline():
    # Stage 01: Data Ingestion
    STAGE_01 = "Data Ingestion"
    try:
        logger.info(f"\n>>>>>>> Stage {STAGE_01} Bắt đầu <<<<<<<")
        stage1 = DataIngestionTrainingPipeline()
        stage1.main()
        logger.info(f">>>>>>> Stage {STAGE_01} Hoàn tất <<<<<<<\n")
    except Exception as e:
        logger.exception(e)
        raise e

    # Stage 02: Data Validation
    STAGE_02 = "Data Validation"
    try:
        logger.info(f"\n>>>>>>> Stage {STAGE_02} Bắt đầu <<<<<<<")
        stage2 = DataValidationTrainingPipeline()
        stage2.main()
        logger.info(f">>>>>>> Stage {STAGE_02} Hoàn tất <<<<<<<\n")
    except Exception as e:
        logger.exception(e)
        raise e

    # Stage 03: Data Transformation
    STAGE_03 = "Data Transformation (PySpark)"
    try:
        logger.info(f"\n>>>>>>> Stage {STAGE_03} Bắt đầu <<<<<<<")
        stage3 = DataTransformationTrainingPipeline()
        stage3.main()
        logger.info(f">>>>>>> Stage {STAGE_03} Hoàn tất <<<<<<<\n")
    except Exception as e:
        logger.exception(e)
        raise e

    # Stage 04: Model Trainer
    STAGE_04 = "Model Trainer"
    try:
        logger.info(f"\n>>>>>>> Stage {STAGE_04} Bắt đầu <<<<<<<")
        stage4 = ModelTrainerTrainingPipeline()
        stage4.main()
        logger.info(f">>>>>>> Stage {STAGE_04} Hoàn tất <<<<<<<\n")
    except Exception as e:
        logger.exception(e)
        raise e

    # Stage 05: Model Evaluation
    STAGE_05 = "Model Evaluation"
    try:
        logger.info(f"\n>>>>>>> Stage {STAGE_05} Bắt đầu <<<<<<<")
        stage5 = ModelEvaluationTrainingPipeline()
        stage5.main()
        logger.info(f">>>>>>> Stage {STAGE_05} Hoàn tất <<<<<<<\n")
    except Exception as e:
        logger.exception(e)
        raise e

    # Stage 06: Online Prediction
    STAGE_06 = "Online Prediction"
    try:
        logger.info(f"\n>>>>>>> Stage {STAGE_06} Bắt đầu <<<<<<<")
        stage6 = PredictionTrainingPipeline()
        stage6.main()
        logger.info(f">>>>>>> Stage {STAGE_06} Hoàn tất <<<<<<<\n")
    except Exception as e:
        logger.exception(e)
        raise e


if __name__ == "__main__":
    logger.info("==========================================")
    logger.info("  KÍCH HOẠT WEATHER MLOPS PIPELINE (TP.HCM)  ")
    logger.info("==========================================")
    run_pipeline()
    logger.info("==========================================")
    logger.info("   PIPELINE ĐÃ CHẠY THÀNH CÔNG 100%!       ")
    logger.info("==========================================")
