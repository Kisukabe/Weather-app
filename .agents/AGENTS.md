# AGENTS.md - Quy tắc và Chuẩn mực Dự án Weather MLOps

File này chứa toàn bộ các quy tắc (Rules) và tiêu chuẩn kỹ thuật áp dụng cho toàn bộ dự án Weather. Các AI agent và lập trình viên làm việc trên dự án này phải tuân thủ nghiêm ngặt các quy tắc dưới đây.

---

## 1. TIÊU CHUẨN KIẾN TRÚC (MLOps Pipeline Rules)
- **Tách biệt hoàn toàn Cấu hình và Code (Configuration-Driven):**
  - Không được "viết cứng" (hardcode) bất kỳ đường dẫn tệp tin, URL API, tham số mô hình nào vào trong code Python.
  - Mọi cấu hình đường dẫn phải nằm ở `config/config.yaml`.
  - Mọi siêu tham số mô hình phải nằm ở `config/params.yaml`.
  - Mọi định nghĩa cột/kiểu dữ liệu phải nằm ở `config/schema.yaml`.
- **Quản lý Sản phẩm Trung gian (Artifacts Isolation):**
  - Mỗi giai đoạn (Stage) chỉ được phép đọc và ghi dữ liệu trong thư mục con tương ứng của nó trong `artifacts/`.
  - Không sửa đổi hoặc ghi đè trực tiếp dữ liệu thô đầu vào.
- **Tính Độc lập của Stage:**
  - Mỗi Stage trong `src/pipeline/` phải có phương thức `main()` độc lập, có thể chạy riêng lẻ từ dòng lệnh mà không phụ thuộc vào trạng thái bộ nhớ của các Stage khác.

---

## 2. QUY TẮC MÃ NGUỒN (Coding Standards)
- **Định dạng và Đóng gói (Packaging):**
  - Tất cả các thư mục trong `src/` đều phải có tệp `__init__.py` (dấu gạch dưới kép).
  - Tên biến, hàm và class tuân theo chuẩn PEP 8 (snake_case cho biến/hàm, PascalCase cho Class).
- **Ghi nhật ký (Logging Required):**
  - Không sử dụng câu lệnh `print()` trong mã nguồn sản phẩm (`src/components/`, `src/pipeline/`).
  - Phải dùng `from src.utils.logger import logger` và ghi vết với các mức độ phù hợp (`logger.info`, `logger.warning`, `logger.error`).
- **Ép kiểu và Ràng buộc (Type Hinting & Validation):**
  - Sử dụng `@ensure_annotations` cho các hàm tiện ích trong `src/utils/common.py`.
  - Sử dụng `dataclass` trong `src/entity/config_entity.py` để định nghĩa rõ ràng kiểu dữ liệu cấu hình.

---

## 3. QUY TRÌNH PHÁT TRIỂN (Workflow Rules)
1. **Kiểm tra trước khi Commit/Run:**
   - Đảm bảo tất cả các file cấu hình YAML hợp lệ trước khi kích hoạt pipeline.
   - Kiểm tra `logs/app.log` khi xảy ra bất kỳ ngoại lệ (Exception) nào để truy vết lỗi.
2. **Bảo tồn tài liệu (Documentation Integrity):**
   - Giữ nguyên các comment giải thích và docstrings trong code.
   - Cập nhật file `.agents/PHASES.md` mỗi khi hoàn thành 1 giai đoạn của dự án.
