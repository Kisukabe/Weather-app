from pathlib import Path
from src.utils.common import read_yaml, create_directories
from src.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    ModelEvaluationConfig,
    PredictionConfig,
)

# Khai báo các đường dẫn hằng số
CONFIG_FILE_PATH = Path("config/config.yaml")
PARAMS_FILE_PATH = Path("config/params.yaml")
SCHEMA_FILE_PATH = Path("config/schema.yaml")


class ConfigurationManager:
    def __init__(
        self,
        config_filepath=CONFIG_FILE_PATH,
        params_filepath=PARAMS_FILE_PATH,
        schema_filepath=SCHEMA_FILE_PATH,
    ):
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)

        # Tạo thư mục gốc lưu trữ artifacts
        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=Path(config.root_dir),
            archive_data_file=Path(config.archive_data_file),
            forecast_data_file=Path(config.forecast_data_file),
            latitude=float(config.latitude),
            longitude=float(config.longitude),
            city_name=str(config.city_name),
        )

        return data_ingestion_config

    def get_data_validation_config(self) -> DataValidationConfig:
        config = self.config.data_validation
        schema = self.schema.COLUMNS

        create_directories([config.root_dir])

        data_validation_config = DataValidationConfig(
            root_dir=Path(config.root_dir),
            input_data_dir=Path(config.input_data_dir),
            STATUS_FILE=str(config.STATUS_FILE),
            all_schema=dict(schema),
        )

        return data_validation_config

    def get_data_transformation_config(self) -> DataTransformationConfig:
        config = self.config.data_transformation

        create_directories([config.root_dir])

        data_transformation_config = DataTransformationConfig(
            root_dir=Path(config.root_dir),
            input_archive_path=Path(config.input_archive_path),
            input_forecast_path=Path(config.input_forecast_path),
            train_data_path=Path(config.train_data_path),
            test_data_path=Path(config.test_data_path),
        )

        return data_transformation_config

    def get_model_trainer_config(self) -> ModelTrainerConfig:
        config = self.config.model_trainer
        params = self.params.RandomForestRegressor

        create_directories([config.root_dir])

        model_trainer_config = ModelTrainerConfig(
            root_dir=Path(config.root_dir),
            train_data_path=Path(config.train_data_path),
            test_data_path=Path(config.test_data_path),
            model_path=Path(config.model_path),
            n_estimators=int(params.n_estimators),
            max_depth=int(params.max_depth),
            random_state=int(params.random_state),
        )

        return model_trainer_config

    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        config = self.config.model_evaluation

        create_directories([config.root_dir])

        model_evaluation_config = ModelEvaluationConfig(
            root_dir=Path(config.root_dir),
            test_data_path=Path(config.test_data_path),
            model_path=Path(config.model_path),
            metric_file_name=Path(config.metric_file_name),
        )

        return model_evaluation_config

    def get_prediction_config(self) -> PredictionConfig:
        config = self.config.prediction

        create_directories([config.root_dir])

        prediction_config = PredictionConfig(
            root_dir=Path(config.root_dir),
            model_path=Path(config.model_path),
            output_path=Path(config.output_path),
        )

        return prediction_config
