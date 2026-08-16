import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from src.utils.logger import logger

router = APIRouter(prefix="/api/v1", tags=["Data"])


@router.get("/metrics")
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
            return json.load(f)
    except Exception as e:
        logger.error(f"Lỗi khi đọc file metrics.json: {e}")
        raise HTTPException(status_code=500, detail="Không thể đọc file metrics.json")


@router.get("/predictions")
def get_predictions(
    model: Optional[str] = Query(None, description="Tên mô hình (vd: xgboost, random_forest, lightgbm)"),
):
    """
    Lấy danh sách dự báo thời tiết đã được hiệu chỉnh sai số từ file forecast_corrected.json.
    Hỗ trợ lọc hoặc chọn mô hình.
    """
    pred_file = Path("artifacts/prediction/forecast_corrected.json")
    if not pred_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Chưa có dữ liệu dự báo. Vui lòng kích hoạt Pipeline trước!",
        )

    try:
        with open(pred_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if model:
            data["selected_model"] = model
        return data
    except Exception as e:
        logger.error(f"Lỗi khi đọc file forecast_corrected.json: {e}")
        raise HTTPException(status_code=500, detail="Không thể đọc file forecast_corrected.json")


@router.get("/logs")
def get_system_logs(lines: int = Query(50, ge=1, le=500, description="Số dòng log gần nhất cần lấy")):
    """Lấy các dòng log mới nhất từ logs/app.log để hiển thị trực tiếp trên Dashboard."""
    log_file = Path("logs/app.log")
    if not log_file.exists():
        return {"total_lines": 0, "logs": ["Chưa có dữ liệu log."]}

    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return {
                "total_lines": len(tail_lines),
                "logs": [line.rstrip() for line in tail_lines],
            }
    except Exception as e:
        logger.error(f"Lỗi khi đọc file log: {e}")
        raise HTTPException(status_code=500, detail="Không thể đọc file log hệ thống")
