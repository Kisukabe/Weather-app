import streamlit as st
from frontend.components.sidebar import render_sidebar
from frontend.components.api_client import fetch_metrics, fetch_health

st.set_page_config(
    page_title="Weather MLOps | Trang chủ",
    page_icon="🌤️",
    layout="wide",
)

render_sidebar()

st.title("🌤️ Automated Weather Forecast Bias Correction System")
st.markdown("### 📍 Dự Báo Khí Tượng & Hiệu Chỉnh Sai Số Thời Tiết TP. Hồ Chí Minh")
st.caption("Kiến trúc MLOps Decoupled: Streamlit UI ↔ FastAPI Backend ↔ Apache PySpark Engine ↔ Model Registry")

st.divider()

col1, col2, col3, col4 = st.columns(4)

metrics_data = fetch_metrics()
if metrics_data:
    raw_mae = metrics_data.get("raw_forecast_metrics", {}).get("mae", 0.0)
    corr_mae = metrics_data.get("corrected_forecast_metrics", {}).get("mae", 0.0)
    improvement = metrics_data.get("improvement", {}).get("mae_reduction_percentage", 0.0)
    best_model = metrics_data.get("best_model", "XGBoost").upper()

    with col1:
        st.metric("🏆 Mô hình tốt nhất", best_model)
    with col2:
        st.metric("🌡️ MAE Dự báo thô", f"{raw_mae:.2f} °C")
    with col3:
        st.metric("🎯 MAE Sau hiệu chỉnh", f"{corr_mae:.2f} °C")
    with col4:
        st.metric("📈 Mức độ cải thiện", f"{improvement:+.1f}%", delta=f"{improvement:+.1f}%")
else:
    st.info("💡 Chưa có dữ liệu đánh giá mô hình. Vui lòng vào trang **🔧 Pipeline Control** để kích hoạt pipeline.")

st.divider()

st.markdown("""
### 🚀 Các Tính Năng Chính Của Hệ Thống:

1. **📊 Dashboard Dự Báo Đa Chỉ Số & Model Selector**:
   - Tự do chuyển đổi giữa **4 mô hình ML** (`XGBoost`, `LightGBM`, `Random Forest`, `Ridge Regression`) để so sánh kết quả.
   - Dự báo đầy đủ **7 chỉ số**: Nhiệt độ Max/Min, Độ ẩm, Mây mù, Xác suất mưa, Phân loại mưa, Nắng, Tia UV.

2. **🔧 Điều Khiển & Theo Dõi Pipeline (Pipeline Control)**:
   - Kích hoạt toàn bộ 6 Stage MLOps Pipeline với 1 cú click.
   - Theo dõi trạng thái tiến độ thời gian thực và tra cứu lịch sử các lượt chạy từ SQLite Database.

3. **📋 Giám Sát Log Hệ Thống (System Logs)**:
   - Theo dõi logs ứng dụng trực tiếp với cơ chế **Log Rotation (tối đa 50MB)** đảm bảo an toàn bộ nhớ.

---
👉 **Hãy chọn một trang từ menu bên trái để bắt đầu khám phá!**
""")
