import time
from datetime import datetime
from typing import Any, Dict, Optional
from main import run_pipeline
from src.utils.logger import logger
from backend.app.db.session import record_pipeline_run, cleanup_old_records


class PipelineService:
    """Service điều phối và quản lý vòng đời thực thi của MLOps Pipeline."""

    def __init__(self):
        self.state: Dict[str, Any] = {
            "status": "IDLE",  # IDLE, RUNNING, SUCCESS, FAILED
            "message": "Pipeline sẵn sàng.",
            "started_at": None,
            "finished_at": None,
            "duration_seconds": 0.0,
            "last_error": None,
        }

    def is_running(self) -> bool:
        """Kiểm tra xem pipeline có đang chạy hay không."""
        return self.state["status"] == "RUNNING"

    def get_status(self) -> Dict[str, Any]:
        """Lấy trạng thái chi tiết của pipeline."""
        return dict(self.state)

    def execute_pipeline(self, triggered_by: str = "MANUAL") -> Dict[str, Any]:
        """Thực thi toàn bộ 6 Stage MLOps Pipeline và cập nhật trạng thái + lưu DB."""
        if self.is_running():
            logger.warning("PipelineService: Pipeline đang chạy, bỏ qua yêu cầu trùng.")
            return {
                "status": "REJECTED",
                "message": "Pipeline đang chạy, vui lòng chờ hoàn tất.",
            }

        start_time = time.time()
        start_iso = datetime.now().isoformat()

        self.state["status"] = "RUNNING"
        self.state["message"] = f"Đang thực thi MLOps Pipeline (kích hoạt bởi: {triggered_by})..."
        self.state["started_at"] = start_iso
        self.state["finished_at"] = None
        self.state["duration_seconds"] = 0.0
        self.state["last_error"] = None

        logger.info(f"PipelineService: Bắt đầu kích hoạt Pipeline [{triggered_by}] lúc {start_iso}")

        try:
            # Chạy 6 stage pipeline từ core engine
            run_pipeline()

            duration = round(time.time() - start_time, 2)
            finish_iso = datetime.now().isoformat()

            self.state["status"] = "SUCCESS"
            self.state["message"] = f"Pipeline đã hoàn tất thành công trong {duration}s."
            self.state["finished_at"] = finish_iso
            self.state["duration_seconds"] = duration

            # Ghi nhận vào SQLite Database
            record_pipeline_run(
                status="SUCCESS",
                duration_seconds=duration,
                triggered_by=triggered_by,
            )

            # Thực thi dọn dẹp dữ liệu cũ theo Retention Policy
            cleanup_old_records()

            logger.info(f"PipelineService: Pipeline hoàn tất thành công trong {duration}s.")
            return self.get_status()

        except Exception as e:
            duration = round(time.time() - start_time, 2)
            finish_iso = datetime.now().isoformat()
            error_msg = str(e)

            self.state["status"] = "FAILED"
            self.state["message"] = f"Lỗi thực thi Pipeline: {error_msg}"
            self.state["finished_at"] = finish_iso
            self.state["duration_seconds"] = duration
            self.state["last_error"] = error_msg

            # Ghi log thất bại vào SQLite Database
            record_pipeline_run(
                status="FAILED",
                duration_seconds=duration,
                triggered_by=triggered_by,
                error_message=error_msg,
            )

            logger.error(f"PipelineService: Pipeline thất bại sau {duration}s. Lỗi: {error_msg}")
            return self.get_status()


# Singleton instance
pipeline_service = PipelineService()
