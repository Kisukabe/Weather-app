from fastapi.testclient import TestClient
from backend.app.main_api import app

client = TestClient(app)


def test_health_check():
    """Kiểm tra endpoint /health."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "weather-mlops-backend"


def test_get_pipeline_status():
    """Kiểm tra endpoint /api/v1/pipeline/status."""
    response = client.get("/api/v1/pipeline/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "message" in data


def test_get_metrics():
    """Kiểm tra endpoint /api/v1/metrics."""
    response = client.get("/api/v1/metrics")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "raw_forecast_metrics" in data
        assert "corrected_forecast_metrics" in data


def test_get_predictions():
    """Kiểm tra endpoint /api/v1/predictions."""
    response = client.get("/api/v1/predictions")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "predictions" in data
