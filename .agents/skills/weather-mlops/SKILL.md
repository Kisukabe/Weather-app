]]]]]---
name: weather-mlops
description: Quy trình phát triển và tiêu chuẩn mã nguồn cho dự án Weather Forecasting MLOps Pipeline. Sử dụng skill này khi cần kiểm tra quy chuẩn thiết kế, luồng chạy pipeline, hoặc viết các component/pipeline mới cho bài toán thời tiết.
---

# Weather MLOps Skill Guidelines

Skill này cung cấp các hướng dẫn chuyên biệt cho việc phát triển và mở rộng hệ thống dự báo thời tiết bằng MLOps.

## 1. Nguyên tắc thiết kế Component trong `src/components/`

Mỗi Component là một lớp (class) Python chịu trách nhiệm thực thi một tác vụ duy nhất:
- **Đầu vào:** Luôn nhận một đối tượng Config (được định nghĩa từ `src/entity/config_entity.py`).
- **Thực thi:**
  - Không đọc trực tiếp từ tệp YAML trong Component.
  - Sử dụng `logger.info()` để ghi lại tiến trình.
  - Xử lý ngoại lệ với `try...except` và ghi vết lỗi bằng `logger.error()`.
- **Đầu ra:** Ghi tệp kết quả vào đường dẫn được chỉ định trong Config (`artifacts/...`).

## 2. Quy trình kiểm thử độc lập một Stage

Để test một Stage bất kỳ mà không cần chạy lại toàn bộ từ đầu:
```python
if __name__ == '__main__':
    from src.config.configuration import ConfigurationManager
    config = ConfigurationManager()
    # Ví dụ với Data Ingestion
    data_ingestion_config = config.get_data_ingestion_config()
    data_ingestion = DataIngestion(config=data_ingestion_config)
    data_ingestion.download_data()
```

## 3. Quản lý Thư mục và File Artifacts

- Tất cả các đường dẫn artifacts phải được quản lý tập trung trong `config/config.yaml`.
- Khi cần tạo đường dẫn artifacts mới, cập nhật theo 3 bước:
  1. Thêm key vào `config/config.yaml`.
  2. Thêm field vào `@dataclass` tương ứng trong `src/entity/config_entity.py`.
  3. Thêm getter method trong `src/config/configuration.py`.
