import os
import json
import joblib
import yaml
from pathlib import Path
from typing import Any
from box import ConfigBox
from box.exceptions import BoxValueError
from ensure import ensure_annotations
from src.utils.logger import logger


@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """Đọc tệp YAML và trả về đối tượng ConfigBox.

    Args:
        path_to_yaml (Path): Đường dẫn tới file YAML

    Raises:
        ValueError: Nếu tệp rỗng
        e: Các lỗi đọc file khác

    Returns:
        ConfigBox: Dữ liệu cấu hình cho phép truy cập dạng attribute
    """
    try:
        with open(path_to_yaml, "r", encoding="utf-8") as yaml_file:
            content = yaml.safe_load(yaml_file)
            logger.info(f"Đã nạp thành công file yaml từ: {path_to_yaml}")
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError(f"File yaml bị rỗng: {path_to_yaml}")
    except Exception as e:
        raise e


@ensure_annotations
def create_directories(path_to_directories: list, verbose: bool = True):
    """Tạo danh sách các thư mục nếu chưa tồn tại.

    Args:
        path_to_directories (list): Danh sách đường dẫn thư mục
        verbose (bool, optional): In log thông báo. Mặc định là True.
    """
    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)
        if verbose:
            logger.info(f"Đã tạo thư mục tại: {path}")


@ensure_annotations
def save_json(path: Path, data: dict):
    """Lưu dữ liệu dạng dict vào tệp JSON.

    Args:
        path (Path): Đường dẫn lưu tệp JSON
        data (dict): Dữ liệu cần lưu
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f"Đã lưu tệp JSON thành công tại: {path}")


@ensure_annotations
def load_json(path: Path) -> ConfigBox:
    """Đọc tệp JSON và trả về ConfigBox.

    Args:
        path (Path): Đường dẫn tới tệp JSON

    Returns:
        ConfigBox: Dữ liệu dưới dạng ConfigBox
    """
    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)
    logger.info(f"Đã nạp tệp JSON thành công từ: {path}")
    return ConfigBox(content)


@ensure_annotations
def save_bin(data: Any, path: Path):
    """Lưu dữ liệu nhị phân (ví dụ: mô hình trained) bằng joblib.

    Args:
        data (Any): Dữ liệu cần lưu
        path (Path): Đường dẫn lưu tệp nhị phân
    """
    joblib.dump(value=data, filename=path)
    logger.info(f"Đã lưu tệp nhị phân tại: {path}")


@ensure_annotations
def load_bin(path: Path) -> Any:
    """Nạp dữ liệu nhị phân bằng joblib.

    Args:
        path (Path): Đường dẫn tới tệp nhị phân

    Returns:
        Any: Dữ liệu đã được khôi phục
    """
    data = joblib.load(filename=path)
    logger.info(f"Đã nạp tệp nhị phân từ: {path}")
    return data


@ensure_annotations
def get_size(path: Path) -> str:
    """Lấy kích thước tệp tính theo KB.

    Args:
        path (Path): Đường dẫn tới tệp

    Returns:
        str: Kích thước tính theo KB
    """
    size_in_kb = round(os.path.getsize(path) / 1024)
    return f"~ {size_in_kb} KB"
