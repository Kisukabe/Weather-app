import os
import sys
from datetime import datetime
from fastapi import APIRouter
from backend.app.config import settings
from backend.app.services.scheduler_service import scheduler_service
from backend.app.db.session import get_connection

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """
    Endpoint kiểm tra trạng thái hoạt động toàn diện của hệ thống:
    - Backend Service
    - APScheduler
    - SQLite Database
    - Server Time & Environment
    """
    # 1. Kiểm tra kết nối Database
    db_status = "connected"
    try:
        with get_connection() as conn:
            conn.cursor().execute("SELECT 1")
    except Exception as e:
        db_status = f"error: {str(e)}"

    # 2. Lấy thông tin Scheduler
    scheduler_info = scheduler_service.get_info()

    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env,
        "database": db_status,
        "scheduler": scheduler_info,
        "python_version": sys.version.split()[0],
        "timestamp": datetime.now().isoformat(),
    }
