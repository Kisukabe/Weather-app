import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from main import run_pipeline
from src.utils.logger import logger

# Khởi tạo APScheduler toàn cục
scheduler = BackgroundScheduler(daemon=True)

# Lấy cấu hình lịch tự động từ biến môi trường (mặc định: 6:00 sáng mỗi ngày)
CRON_HOUR = int(os.getenv("SCHEDULE_CRON_HOUR", "6"))
CRON_MINUTE = int(os.getenv("SCHEDULE_CRON_MINUTE", "0"))

# Quản lý trạng thái Pipeline toàn cục
pipeline_state: Dict[str, Any] = {
    "status": "IDLE",  # IDLE, RUNNING, SUCCESS, FAILED
    "message": "Pipeline chưa được kích hoạt.",
    "started_at": None,
    "finished_at": None,
}


def _execute_pipeline_task():
    """Hàm chạy 6 Stage Pipeline trong Background Task hoặc qua APScheduler."""
    global pipeline_state
    if pipeline_state["status"] == "RUNNING":
        logger.warning("FastAPI Backend: Pipeline đang chạy, bỏ qua lượt kích hoạt trùng.")
        return

    pipeline_state["status"] = "RUNNING"
    pipeline_state["message"] = "Đang chạy 6 Stage MLOps Pipeline..."
    pipeline_state["started_at"] = datetime.now().isoformat()
    pipeline_state["finished_at"] = None

    try:
        logger.info("FastAPI Backend: Bắt đầu kích hoạt MLOps Pipeline...")
        run_pipeline()
        pipeline_state["status"] = "SUCCESS"
        pipeline_state["message"] = "Pipeline đã chạy thành công 100%!"
        logger.info("FastAPI Backend: Pipeline đã hoàn tất thành công.")
    except Exception as e:
        logger.error(f"FastAPI Backend: Lỗi khi chạy Pipeline: {e}")
        pipeline_state["status"] = "FAILED"
        pipeline_state["message"] = f"Lỗi thực thi Pipeline: {str(e)}"
    finally:
        pipeline_state["finished_at"] = datetime.now().isoformat()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý khởi động và dừng APScheduler ngầm cùng FastAPI server."""
    logger.info(f"Khởi động APScheduler ngầm: Lịch chạy tự động mỗi ngày lúc {CRON_HOUR:02d}:{CRON_MINUTE:02d} AM.")
    scheduler.add_job(
        _execute_pipeline_task,
        trigger=CronTrigger(hour=CRON_HOUR, minute=CRON_MINUTE),
        id="daily_weather_pipeline",
        name="Daily Weather Forecast Bias Correction Pipeline",
        replace_existing=True,
    )
    scheduler.start()
    yield
    logger.info("Tắt APScheduler ngầm...")
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="Weather MLOps Backend API",
    description="REST API cho Hệ thống Hiệu chỉnh Sai số Dự báo Thời tiết TP.HCM (Tích hợp APScheduler ngầm)",
    version="1.1.0",
    lifespan=lifespan,
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint kiểm tra sức khỏe dịch vụ Backend & APScheduler."""
    job = scheduler.get_job("daily_weather_pipeline")
    next_run = job.next_run_time.isoformat() if job and job.next_run_time else None
    return {
        "status": "healthy",
        "service": "weather-mlops-backend",
        "scheduler": {
            "enabled": scheduler.running,
            "schedule": f"Daily at {CRON_HOUR:02d}:{CRON_MINUTE:02d}",
            "next_run": next_run,
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/v1/metrics", tags=["Data"])
def get_metrics():
    """Lấy kết quả đánh giá mô hình (MAE, RMSE, R²) từ metrics.json."""
    metrics_file = Path("artifacts/model_evaluation/metrics.json")
    if not metrics_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Chưa có dữ liệu đánh giá. Vui lòng kích hoạt Pipeline trước!",
        )

    try:
        with open(metrics_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Lỗi khi đọc file metrics.json: {e}")
        raise HTTPException(status_code=500, detail="Không thể đọc file metrics.json")


@app.get("/api/v1/predictions", tags=["Data"])
def get_predictions():
    """Lấy danh sách dự báo nhiệt độ đã được hiệu chỉnh sai số từ forecast_corrected.json."""
    pred_file = Path("artifacts/prediction/forecast_corrected.json")
    if not pred_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Chưa có dữ liệu dự báo. Vui lòng kích hoạt Pipeline trước!",
        )

    try:
        with open(pred_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Lỗi khi đọc file forecast_corrected.json: {e}")
        raise HTTPException(
            status_code=500, detail="Không thể đọc file forecast_corrected.json"
        )


@app.post("/api/v1/pipeline/run", tags=["Pipeline"])
def trigger_pipeline(background_tasks: BackgroundTasks):
    """Kích hoạt chạy 6 Stage MLOps Pipeline thủ công qua API."""
    global pipeline_state
    if pipeline_state["status"] == "RUNNING":
        return {
            "status": "RUNNING",
            "message": "Pipeline đang trong quá trình thực thi, vui lòng chờ...",
        }

    background_tasks.add_task(_execute_pipeline_task)
    return {
        "status": "ACCEPTED",
        "message": "Đã tiếp nhận yêu cầu. Pipeline đang được khởi chạy trong nền.",
    }


@app.get("/api/v1/pipeline/status", tags=["Pipeline"])
def get_pipeline_status():
    """Lấy trạng thái thực thi hiện tại của Pipeline và lịch chạy APScheduler."""
    job = scheduler.get_job("daily_weather_pipeline")
    next_run = job.next_run_time.isoformat() if job and job.next_run_time else None

    return {
        **pipeline_state,
        "scheduler": {
            "enabled": scheduler.running,
            "schedule": f"Daily at {CRON_HOUR:02d}:{CRON_MINUTE:02d}",
            "next_run": next_run,
        },
    }
