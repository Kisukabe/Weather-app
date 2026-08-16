from fastapi import APIRouter, BackgroundTasks, Depends, status
from backend.app.services.pipeline_service import pipeline_service
from backend.app.services.scheduler_service import scheduler_service
from backend.app.middleware.auth import verify_api_key
from backend.app.db.session import get_recent_runs

router = APIRouter(prefix="/api/v1/pipeline", tags=["Pipeline"])


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
def trigger_pipeline(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
):
    """
    Kích hoạt chạy 6 Stage MLOps Pipeline trong Background Task.
    Được bảo vệ bởi API Key (Header `X-API-Key`).
    """
    if pipeline_service.is_running():
        return {
            "status": "RUNNING",
            "message": "Pipeline đang trong quá trình thực thi, vui lòng không kích hoạt lặp lại.",
            "current_state": pipeline_service.get_status(),
        }

    # Thêm task chạy ngầm không block request
    background_tasks.add_task(pipeline_service.execute_pipeline, triggered_by="API_MANUAL")

    return {
        "status": "ACCEPTED",
        "message": "Đã tiếp nhận yêu cầu. MLOps Pipeline đang được thực thi trong nền.",
    }


@router.get("/status")
def get_pipeline_status():
    """Lấy trạng thái thực thi hiện tại của Pipeline và thông tin lịch chạy tự động."""
    return {
        **pipeline_service.get_status(),
        "scheduler": scheduler_service.get_info(),
    }


@router.get("/history")
def get_pipeline_history(limit: int = 10):
    """Lấy lịch sử các lần chạy Pipeline gần nhất từ SQLite Database."""
    runs = get_recent_runs(limit=limit)
    return {
        "total": len(runs),
        "history": runs,
    }
