import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.utils.logger import logger
from backend.app.config import settings


def get_db_path() -> Path:
    """Lấy đường dẫn file SQLite từ cấu hình và đảm bảo thư mục cha tồn tại."""
    db_path = Path(settings.sqlite_db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_connection() -> sqlite3.Connection:
    """Tạo kết nối SQLite với row_factory cho phép truy xuất dạng Dict."""
    conn = sqlite3.connect(get_db_path(), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Khởi tạo cấu trúc các bảng trong SQLite Database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # 1. Bảng lưu vết các lượt chạy Pipeline
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL,
                    duration_seconds REAL DEFAULT 0.0,
                    triggered_by TEXT DEFAULT 'MANUAL',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # 2. Bảng lưu lịch sử dự báo
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    forecast_date TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    raw_temp_max REAL,
                    corrected_temp_max REAL,
                    predicted_bias REAL,
                    humidity REAL,
                    cloud_cover REAL,
                    will_rain INTEGER DEFAULT 0,
                    city TEXT DEFAULT 'Ho Chi Minh City',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # 3. Bảng lưu lịch sử đánh giá độ chính xác mô hình
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS model_metrics_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    target_name TEXT NOT NULL,
                    mae REAL,
                    rmse REAL,
                    r2 REAL,
                    mae_reduction_percentage REAL,
                    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.commit()
            logger.info("Đã khởi tạo thành công cấu trúc SQLite Database.")
    except Exception as e:
        logger.error(f"Lỗi khởi tạo SQLite Database: {e}")
        raise e


def record_pipeline_run(
    status: str,
    duration_seconds: float = 0.0,
    triggered_by: str = "MANUAL",
    error_message: Optional[str] = None,
) -> int:
    """Ghi nhận một lượt chạy pipeline vào DB."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO pipeline_runs (status, duration_seconds, triggered_by, error_message)
                VALUES (?, ?, ?, ?)
                """,
                (status, duration_seconds, triggered_by, error_message),
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Lỗi ghi log pipeline run vào DB: {e}")
        return -1


def cleanup_old_records(retention_days: Optional[int] = None) -> int:
    """
    Cơ chế Retention: Tự động dọn dẹp các bản ghi cũ hơn retention_days.
    Mặc định lấy từ settings.db_retention_days (30 ngày).
    """
    if retention_days is None:
        retention_days = settings.db_retention_days

    cutoff_date = (datetime.now() - timedelta(days=retention_days)).strftime("%Y-%m-%d %H:%M:%S")
    deleted_total = 0

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM pipeline_runs WHERE created_at < ?", (cutoff_date,))
            deleted_total += cursor.rowcount

            cursor.execute("DELETE FROM predictions_history WHERE created_at < ?", (cutoff_date,))
            deleted_total += cursor.rowcount

            cursor.execute("DELETE FROM model_metrics_history WHERE evaluated_at < ?", (cutoff_date,))
            deleted_total += cursor.rowcount

            conn.commit()
            if deleted_total > 0:
                logger.info(
                    f"Retention Policy: Đã dọn dẹp {deleted_total} bản ghi cũ hơn {retention_days} ngày trong SQLite."
                )
        return deleted_total
    except Exception as e:
        logger.error(f"Lỗi khi thực thi Retention Cleanup trong SQLite: {e}")
        return 0


def get_recent_runs(limit: int = 10) -> List[Dict[str, Any]]:
    """Lấy danh sách các lượt chạy pipeline gần nhất."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM pipeline_runs ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Lỗi truy vấn pipeline runs: {e}")
        return []
