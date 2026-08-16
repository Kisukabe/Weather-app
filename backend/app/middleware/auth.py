from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from backend.app.config import settings
from src.utils.logger import logger

# Header tên "X-API-Key"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Dependency kiểm tra tính hợp lệ của API Key từ Header `X-API-Key`.
    Dùng để bảo vệ các endpoints nhạy cảm (như trigger pipeline).
    """
    # Nếu không cấu hình api_key hoặc đang ở chế độ debug mà không truyền key
    if not settings.api_key:
        return "bypass"

    if not api_key:
        logger.warning("Truy cập bị từ chối: Thiếu header X-API-Key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu cần có Header 'X-API-Key' hợp lệ để thực thi.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if api_key != settings.api_key:
        logger.warning(f"Truy cập bị từ chối: API Key không chính xác ({api_key[:6]}***)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key không chính xác. Quyền truy cập bị từ chối.",
        )

    return api_key
