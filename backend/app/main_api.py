"""
[DEPRECATED] Module này đã được tái cấu trúc thành backend/app/main.py.
Giữ lại file này như một proxy tương thích ngược.
"""
import warnings
from backend.app.main import app, create_app

warnings.warn(
    "backend.app.main_api đã chuyển sang backend.app.main. Vui lòng cập nhật import.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["app", "create_app"]
