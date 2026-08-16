import os
import pytest
from pathlib import Path
from src.config.configuration import ConfigurationManager
from backend.app.db.session import init_db, cleanup_old_records, get_connection


def test_configuration_manager_loading():
    """Kiểm tra ConfigurationManager nạp đúng toàn bộ các file YAML."""
    config_mgr = ConfigurationManager()
    
    # 1. Ingestion Config
    ingestion_cfg = config_mgr.get_data_ingestion_config()
    assert Path(ingestion_cfg.root_dir).exists() or Path("artifacts/data_ingestion").parent.exists()
    assert ingestion_cfg.city_name == "Ho Chi Minh City"
    assert ingestion_cfg.latitude > 0
    assert ingestion_cfg.longitude > 0

    # 2. Validation Config
    validation_cfg = config_mgr.get_data_validation_config()
    assert validation_cfg.status_file is not None

    # 3. Model Trainer Config
    trainer_cfg = config_mgr.get_model_trainer_config()
    assert trainer_cfg.target_column == "temp_max_bias"
    assert trainer_cfg.n_estimators > 0


def test_sqlite_db_and_cleanup():
    """Kiểm tra SQLite DB khởi tạo bảng và cơ chế dọn dẹp log sau 30 ngày."""
    init_db()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Kiểm tra bảng pipeline_runs tồn tại
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pipeline_runs'")
        assert cursor.fetchone() is not None

        # Kiểm tra bảng predictions_history tồn tại
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='predictions_history'")
        assert cursor.fetchone() is not None

        # Kiểm tra bảng model_metrics_history tồn tại
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_metrics_history'")
        assert cursor.fetchone() is not None

    # Kiểm tra hàm dọn dẹp không ném ngoại lệ
    deleted = cleanup_old_records(days=30)
    assert isinstance(deleted, int)
