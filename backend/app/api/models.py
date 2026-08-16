import json
from pathlib import Path
from fastapi import APIRouter
from src.utils.logger import logger

router = APIRouter(prefix="/api/v1/models", tags=["Models"])

# Danh mục các mô hình được hỗ trợ trong Model Registry
AVAILABLE_MODELS = [
    {
        "id": "xgboost",
        "name": "XGBoost Regressor",
        "type": "Gradient Boosting",
        "description": "Hiệu năng và độ chính xác cao nhất cho dữ liệu chuỗi thời gian.",
        "is_default": True,
    },
    {
        "id": "lightgbm",
        "name": "LightGBM Regressor",
        "type": "Leaf-wise Gradient Boosting",
        "description": "Tốc độ huấn luyện và suy luận nhanh nhất, tiết kiệm RAM.",
        "is_default": False,
    },
    {
        "id": "random_forest",
        "name": "Random Forest Regressor",
        "type": "Bagging Ensemble",
        "description": "Mô hình cổ điển, tính ổn định cao, chống quá khớp tốt.",
        "is_default": False,
    },
    {
        "id": "linear_regression",
        "name": "Ridge Regression",
        "type": "Linear Model (Baseline)",
        "description": "Mô hình tuyến tính cơ sở (Baseline) phục vụ so sánh hiệu quả.",
        "is_default": False,
    },
]


@router.get("")
def list_available_models():
    """Liệt kê danh sách tất cả các mô hình trong Model Registry và metrics so sánh."""
    models_dir = Path("artifacts/model_trainer")
    metrics_file = Path("artifacts/model_evaluation/metrics.json")

    metrics_data = {}
    if metrics_file.exists():
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
        except Exception as e:
            logger.warning(f"Không thể nạp metrics.json: {e}")

    result = []
    for model in AVAILABLE_MODELS:
        model_file = models_dir / f"{model['id']}.joblib"
        # Trường hợp model_trainer lưu file mặc định model.joblib
        is_trained = model_file.exists() or (models_dir / "model.joblib").exists()

        result.append({
            **model,
            "status": "trained" if is_trained else "not_trained",
            "metrics": metrics_data.get(model["id"], metrics_data.get("corrected_forecast_metrics", {})),
        })

    return {
        "total_models": len(result),
        "default_model": "xgboost",
        "models": result,
    }
