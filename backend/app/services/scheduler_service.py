from typing import Any, Dict, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.utils.logger import logger
from backend.app.config import settings
from backend.app.services.pipeline_service import pipeline_service


class SchedulerService:
    """Service quản lý lập lịch định kỳ tự động chạy Pipeline (APScheduler)."""

    def __init__(self):
        self.scheduler = BackgroundScheduler(daemon=True)
        self.job_id = "daily_weather_pipeline"

    def start(self):
        """Khởi động bộ lập lịch nếu được bật trong cấu hình."""
        if not settings.auto_train_enabled:
            logger.info("SchedulerService: Lịch tự động bị tắt trong cấu hình (AUTO_TRAIN_ENABLED=False).")
            return

        cron_hour = settings.schedule_cron_hour
        cron_minute = settings.schedule_cron_minute

        logger.info(
            f"SchedulerService: Cấu hình lịch chạy tự động mỗi ngày lúc {cron_hour:02d}:{cron_minute:02d}."
        )

        self.scheduler.add_job(
            func=self._scheduled_task,
            trigger=CronTrigger(hour=cron_hour, minute=cron_minute),
            id=self.job_id,
            name="Daily Weather Forecast Bias Correction Pipeline",
            replace_existing=True,
        )

        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("SchedulerService: APScheduler đã khởi động thành công.")

    def _scheduled_task(self):
        """Hàm callback được gọi khi đến giờ chạy theo lịch."""
        logger.info("SchedulerService: Bắt đầu kích hoạt Pipeline theo lịch định kỳ...")
        pipeline_service.execute_pipeline(triggered_by="CRON")

    def shutdown(self, wait: bool = False):
        """Dừng scheduler một cách an toàn."""
        if self.scheduler.running:
            logger.info("SchedulerService: Đang dừng APScheduler...")
            self.scheduler.shutdown(wait=wait)
            logger.info("SchedulerService: APScheduler đã dừng.")

    def get_next_run_time(self) -> Optional[str]:
        """Lấy thời gian của lần chạy tự động tiếp theo."""
        try:
            job = self.scheduler.get_job(self.job_id)
            if job and job.next_run_time:
                return job.next_run_time.isoformat()
        except Exception:
            pass
        return None

    def get_info(self) -> Dict[str, Any]:
        """Trả về thông tin trạng thái của scheduler."""
        return {
            "enabled": self.scheduler.running,
            "schedule": f"Daily at {settings.schedule_cron_hour:02d}:{settings.schedule_cron_minute:02d}",
            "next_run": self.get_next_run_time(),
        }


# Singleton instance
scheduler_service = SchedulerService()
