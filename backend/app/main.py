from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utils.logger import logger
from backend.app.config import settings
from backend.app.db.session import init_db
from backend.app.services.scheduler_service import scheduler_service
from backend.app.middleware.rate_limiter import RateLimitMiddleware
from backend.app.api.health import router as health_router
from backend.app.api.pipeline import router as pipeline_router
from backend.app.api.data import router as data_router
from backend.app.api.models import router as models_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Quản lý vòng đời khởi động và kết thúc (Graceful Shutdown) của FastAPI.
    - Startup: Khởi tạo SQLite DB, khởi chạy APScheduler.
    - Shutdown: Tắt APScheduler và giải phóng tài nguyên an toàn.
    """
    logger.info(f"🚀 Khởi động {settings.app_name} [Env: {settings.app_env}]...")

    # 1. Khởi tạo cấu trúc Database
    init_db()

    # 2. Khởi động bộ lập lịch APScheduler
    scheduler_service.start()

    logger.info("✅ Hệ thống Backend đã sẵn sàng phục vụ requests.")
    yield

    # 3. Graceful Shutdown
    logger.info("🛑 Nhận tín hiệu dừng hệ thống. Đang thực hiện Graceful Shutdown...")
    scheduler_service.shutdown(wait=False)
    logger.info("👋 Backend đã dừng an toàn.")


def create_app() -> FastAPI:
    """App Factory pattern tạo và cấu hình ứng dụng FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        description="REST API cho Hệ thống Hiệu chỉnh Sai số Dự báo Thời tiết TP.HCM (Kiến trúc Module hóa & Model Registry)",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # --- Cấu hình Middlewares ---
    # 1. Rate Limiting Middleware (60 req/min/IP)
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )

    # 2. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Đăng ký các Routers ---
    app.include_router(health_router)
    app.include_router(pipeline_router)
    app.include_router(data_router)
    app.include_router(models_router)

    return app


# Khởi tạo instance ứng dụng chính
app = create_app()
