import os
import sys
import logging
import logging.config
from pathlib import Path
import yaml

# Tự động khắc phục lỗi encoding trên terminal
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_FILE_CONFIG = PROJECT_ROOT / "config" / "logging.yaml"
LOG_DIR = PROJECT_ROOT / "logs"


def setup_logging(config_path: Path = LOG_FILE_CONFIG):
    """Khởi tạo logging từ tệp config/logging.yaml."""
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            logging.config.dictConfig(config)
        except Exception as e:
            logging.basicConfig(
                level=logging.INFO,
                format="[%(asctime)s]: %(levelname)s: %(module)s: %(message)s",
                handlers=[
                    logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
                    logging.StreamHandler(sys.stdout),
                ],
            )
            logging.warning(
                f"Không thể nạp {config_path}. Đã dùng cấu hình mặc định. Lỗi: {e}"
            )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s]: %(levelname)s: %(module)s: %(message)s",
            handlers=[
                logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )


# Kích hoạt logging khi import module
setup_logging()

# Export logger instance chính cho dự án
logger = logging.getLogger("weather_predictor")
