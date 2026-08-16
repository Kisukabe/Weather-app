import os
import time
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# Cấu hình đường dẫn Backend URL từ biến môi trường
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Weather Bias Correction | TP. Hồ Chí Minh",
    page_icon="🌤️",
    layout="wide",
)

st.title("🌤️ Automated Weather Forecast Bias Correction System")
st.markdown("### 📍 Trọng tâm: Thành phố Hồ Chí Minh (TP.HCM)")
st.caption(
    "Kiến trúc Web Decoupled: Streamlit Frontend ↔ FastAPI Backend ↔ PySpark MLOps Pipeline."
)

# Sidebar - Quản lý và theo dõi Pipeline qua REST API
st.sidebar.header("⚙️ Pipeline Controls")

# Kiểm tra trạng thái kết nối tới Backend
try:
    health_resp = requests.get(f"{BACKEND_URL}/health", timeout=3)
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        st.sidebar.success("🟢 Backend Connected (FastAPI)")
        if "scheduler" in health_data:
            sched = health_data["scheduler"]
            st.sidebar.caption(f"⏰ Lịch chạy tự động: **{sched.get('schedule')}**")
    else:
        st.sidebar.warning("🟡 Backend Status Warning")
except Exception:
    st.sidebar.error("🔴 Không thể kết nối tới Backend API server")

# Nút kích hoạt Pipeline qua REST API
if st.sidebar.button("🚀 Run Full Pipeline", use_container_width=True):
    try:
        trigger_resp = requests.post(f"{BACKEND_URL}/api/v1/pipeline/run", timeout=5)
        if trigger_resp.status_code in [200, 202]:
            st.sidebar.info("Đã gửi yêu cầu chạy Pipeline...")

            # Polling trạng thái Pipeline từ Backend
            with st.spinner("Pipeline đang thực thi 6 Stage trên Backend..."):
                completed = False
                while not completed:
                    time.sleep(2)
                    status_resp = requests.get(
                        f"{BACKEND_URL}/api/v1/pipeline/status", timeout=5
                    )
                    if status_resp.status_code == 200:
                        status_data = status_resp.json()
                        curr_status = status_data.get("status")
                        if curr_status == "SUCCESS":
                            st.sidebar.success("Pipeline đã chạy thành công 100%!")
                            completed = True
                            st.rerun()
                        elif curr_status == "FAILED":
                            st.sidebar.error(
                                f"Pipeline thất bại: {status_data.get('message')}"
                            )
                            completed = True
        else:
            st.sidebar.error(f"Lỗi gửi yêu cầu: {trigger_resp.status_code}")
    except Exception as e:
        st.sidebar.error(f"Lỗi kết nối API: {e}")


# 1. Hiển thị chỉ số đánh giá (Metrics) từ Backend REST API
st.subheader("📊 Chỉ số Đánh giá Mô hình (Evaluation Metrics)")
try:
    metrics_resp = requests.get(f"{BACKEND_URL}/api/v1/metrics", timeout=5)
    if metrics_resp.status_code == 200:
        metrics = metrics_resp.json()
        raw_mae = metrics["raw_forecast_metrics"]["mae"]
        corr_mae = metrics["corrected_forecast_metrics"]["mae"]
        improvement = metrics["improvement"]["mae_reduction_percentage"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("MAE Dự báo thô", f"{raw_mae:.2f} °C")
        with col2:
            st.metric(
                "MAE Sau hiệu chỉnh ML",
                f"{corr_mae:.2f} °C",
                delta=f"-{improvement:.1f}% MAE",
            )
        with col3:
            st.metric("Độ cải thiện độ chính xác", f"{improvement:.1f}%")
    else:
        st.info("Chưa có dữ liệu đánh giá. Vui lòng nhấn 'Run Full Pipeline'!")
except Exception:
    st.warning("Chưa tìm thấy dữ liệu đánh giá từ Backend API.")

st.divider()

# 2. Hiển thị biểu đồ so sánh dự báo từ Backend REST API
try:
    pred_resp = requests.get(f"{BACKEND_URL}/api/v1/predictions", timeout=5)
    if pred_resp.status_code == 200:
        pred_data = pred_resp.json()
        df_pred = pd.DataFrame(pred_data["predictions"])

        st.subheader("📈 Biểu đồ so sánh nhiệt độ dự báo thô vs Sau hiệu chỉnh")

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_pred["date"],
                y=df_pred["raw_forecast_temp_max"],
                mode="lines+markers",
                name="Dự báo thô (Open-Meteo)",
                line=dict(color="#FF4B4B", width=2, dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_pred["date"],
                y=df_pred["corrected_temp_max"],
                mode="lines+markers",
                name="Sau hiệu chỉnh (Bias Corrected ML)",
                line=dict(color="#00CC96", width=3),
            )
        )

        fig.update_layout(
            xaxis_title="Ngày",
            yaxis_title="Nhiệt độ cao nhất (°C)",
            template="plotly_dark",
            hovermode="x unified",
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)

        # 3. Bảng dữ liệu chi tiết
        st.subheader("📋 Bảng chi tiết dự báo thời tiết")
        st.dataframe(df_pred, use_container_width=True)
    else:
        st.info(
            "Chưa có dữ liệu dự báo. Vui lòng nhấn 'Run Full Pipeline' ở thanh bên trái!"
        )
except Exception:
    st.warning("Không thể lấy dữ liệu dự báo từ Backend API.")
