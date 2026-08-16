import time
from collections import defaultdict
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from src.utils.logger import logger
from backend.app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware giới hạn số lượng request theo IP (Rate Limiting).
    Tự động giải phóng bộ nhớ (cleanup) định kỳ mỗi 5 phút để tránh rò rỉ RAM.
    """

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests or settings.rate_limit_requests
        self.window_seconds = window_seconds or settings.rate_limit_window_seconds
        self.client_requests: Dict[str, List[float]] = defaultdict(list)
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 phút

    def _cleanup_expired_records(self, now: float):
        """Dọn dẹp các IP đã hết hạn lưu vết khỏi RAM."""
        if now - self.last_cleanup < self.cleanup_interval:
            return

        cutoff = now - self.window_seconds
        expired_ips = []

        for ip, timestamps in self.client_requests.items():
            valid_timestamps = [ts for ts in timestamps if ts > cutoff]
            if valid_timestamps:
                self.client_requests[ip] = valid_timestamps
            else:
                expired_ips.append(ip)

        for ip in expired_ips:
            del self.client_requests[ip]

        self.last_cleanup = now
        logger.debug(f"RateLimiter Cleanup: Đã giải phóng {len(expired_ips)} IP hết hạn.")

    async def dispatch(self, request: Request, call_next):
        # Bỏ qua Rate Limit cho các endpoint hệ thống
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json", "/metrics"]:
            return await call_next(request)

        # Lấy địa chỉ IP của client (hỗ trợ reverse proxy headers)
        client_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )

        now = time.time()
        self._cleanup_expired_records(now)

        # Lọc các timestamp trong cửa sổ thời gian (window)
        cutoff = now - self.window_seconds
        timestamps = [ts for ts in self.client_requests[client_ip] if ts > cutoff]
        self.client_requests[client_ip] = timestamps

        # Kiểm tra vượt ngưỡng
        if len(timestamps) >= self.max_requests:
            logger.warning(
                f"Rate Limit Exceeded: IP {client_ip} đã vượt {self.max_requests} req/{self.window_seconds}s"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "code": 429,
                    "message": "Quá nhiều yêu cầu. Vui lòng thử lại sau.",
                    "detail": f"Giới hạn {self.max_requests} requests mỗi {self.window_seconds} giây.",
                },
                headers={"Retry-After": str(self.window_seconds)},
            )

        # Ghi nhận request hợp lệ
        self.client_requests[client_ip].append(now)
        return await call_next(request)
