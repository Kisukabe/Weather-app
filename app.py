import os
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Weather Bias Correction | TP. Hồ Chí Minh",
    page_icon="🌤️",
    layout="wide",
)

st.title("🌤️ Automated Weather Forecast Bias Correction System")
st.markdown("### 📍 Trọng tâm: Thành phố Hồ Chí Minh (TP.HCM)")
st.caption("Hệ thống MLOps tự động thu thập dữ liệu thời tiết, trích xuất đặc trưng với PySpark & hiệu chỉnh sai số dự báo bằng Machine Learning.")

# Sidebar nút kích hoạt Pipeline
st.sidebar.header("⚙️ Pipeline Controls")
if st.sidebar.button("🚀 Run Full Pipeline", use_container_width=True):
    with st.spinner("Đang chạy toàn bộ 6 Stage MLOps Pipeline..."):
        ret = os.system("PYTHONPATH=. /Users/giabao/miniforge3/envs/weather_env/bin/python main.py")
        if ret == 0:
            st.sidebar.success("Pipeline đã chạy thành công 100%!")
        else:
            st.sidebar.error("Có lỗi xảy ra khi chạy Pipeline!")

# 1. Hiển thị chỉ số đánh giá (Metrics)
metrics_path = Path("artifacts/model_evaluation/metrics.json")
if metrics_path.exists():
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    raw_mae = metrics["raw_forecast_metrics"]["mae"]
    corr_mae = metrics["corrected_forecast_metrics"]["mae"]
    improvement = metrics["improvement"]["mae_reduction_percentage"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("MAE Dự báo thô", f"{raw_mae:.2f} °C")
    with col2:
        st.metric("MAE Sau hiệu chỉnh ML", f"{corr_mae:.2f} °C", delta=f"-{improvement:.1f}% MAE")
    with col3:
        st.metric("Độ cải thiện độ chính xác", f"{improvement:.1f}%")

st.divider()

# 2. Hiển thị biểu đồ so sánh dự báo
prediction_path = Path("artifacts/prediction/forecast_corrected.json")
if prediction_path.exists():
    with open(prediction_path, "r", encoding="utf-8") as f:
        pred_data = json.load(f)

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
    st.warning("Chưa tìm thấy dữ liệu dự báo. Vui lòng nhấn 'Run Full Pipeline' ở thanh bên trái!")
