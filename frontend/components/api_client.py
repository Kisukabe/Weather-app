import os
import requests
from typing import Dict, Any, Optional
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "weather-mlops-dev-secret-key")


def get_headers() -> Dict[str, str]:
    """Tạo Header kèm API Key."""
    return {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }


@st.cache_data(ttl=15, show_spinner=False)
def fetch_health() -> Optional[Dict[str, Any]]:
    """Kiểm tra sức khỏe Backend API."""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_metrics() -> Optional[Dict[str, Any]]:
    """Lấy kết quả đánh giá mô hình (MAE, RMSE, R²)."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/v1/metrics", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_predictions() -> Optional[Dict[str, Any]]:
    """Lấy danh sách dự báo thời tiết 7 chỉ số mở rộng."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/v1/predictions", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_models() -> Optional[Dict[str, Any]]:
    """Lấy danh mục Model Registry."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/v1/models", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=10, show_spinner=False)
def fetch_pipeline_status() -> Optional[Dict[str, Any]]:
    """Lấy trạng thái thực thi Pipeline và APScheduler."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/v1/pipeline/status", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=10, show_spinner=False)
def fetch_pipeline_history(limit: int = 10) -> Optional[Dict[str, Any]]:
    """Lấy lịch sử các lần chạy Pipeline."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/v1/pipeline/history?limit={limit}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=5, show_spinner=False)
def fetch_logs(lines: int = 100) -> Optional[Dict[str, Any]]:
    """Lấy các dòng log mới nhất từ Backend."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/v1/logs?lines={lines}", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def trigger_pipeline_run() -> Dict[str, Any]:
    """Kích hoạt Pipeline qua API kèm Header API Key."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/v1/pipeline/run",
            headers=get_headers(),
            timeout=5,
        )
        return {"status_code": resp.status_code, "data": resp.json()}
    except Exception as e:
        return {"status_code": 500, "error": str(e)}
