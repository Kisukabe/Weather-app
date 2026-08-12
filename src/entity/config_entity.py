from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataIngestionConfig:
    root_dir: Path
    archive_data_file: Path
    forecast_data_file: Path
    latitude: float
    longitude: float
    city_name: str


@dataclass(frozen=True)
class DataValidationConfig:
    root_dir: Path
    input_data_dir: Path
    STATUS_FILE: str
    all_schema: dict


@dataclass(frozen=True)
class DataTransformationConfig:
    root_dir: Path
    input_archive_path: Path
    input_forecast_path: Path
    train_data_path: Path
    test_data_path: Path


@dataclass(frozen=True)
class ModelTrainerConfig:
    root_dir: Path
    train_data_path: Path
    test_data_path: Path
    model_path: Path
    n_estimators: int
    max_depth: int
    random_state: int


@dataclass(frozen=True)
class ModelEvaluationConfig:
    root_dir: Path
    test_data_path: Path
    model_path: Path
    metric_file_name: Path


@dataclass(frozen=True)
class PredictionConfig:
    root_dir: Path
    model_path: Path
    output_path: Path
