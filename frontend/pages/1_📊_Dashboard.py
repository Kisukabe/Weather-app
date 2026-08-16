import streamlit as st
import pandas as pd
from frontend.components.sidebar import render_sidebar
from frontend.components.api_client import fetch_predictions, fetch_metrics, fetch_models
from frontend.components.charts import (
    plot_temperature_comparison,
    plot_weather_indicators,
    plot_models_comparison_bar,
)

st.set_page_config(
    page_title="Weather MLOps | Dashboard Dự Báo",
    page_icon="📊",
    layout="wide",
)

render_sidebar()

st.title("📊 Dashboard Dự Báo Thời Tiết & Model Registry")
st.caption("Hiệu chỉnh sai số vật lý và so sánh hiệu quả giữa các thuật toán Machine Learning.")

# 1. Hộp chọn mô hình ML (Model Selector)
st.markdown("#### 🤖 Chọn Mô Hình Hiệu Chỉnh (Model Registry)")

model_options = {
    "xgboost": "XGBoost Regressor (Độ chính xác cao nhất)",
    "lightgbm": "LightGBM Regressor (Tốc độ nhanh nhất)",
    "random_forest": "Random Forest Regressor (Ensemble ổn định)",
    "linear_regression": "Ridge Regression (Mô hình Baseline)",
}

col_select, col_info = st.columns([1, 2])
with col_select:
    selected_model_key = st.selectbox(
        "Mô hình đang áp dụng:",
        options=list(model_options.keys()),
        format_func=lambda k: model_options[k],
        index=0,
    )

metrics_data = fetch_metrics()
models_comp = metrics_data.get("models_comparison", {}) if metrics_data else {}
current_model_metric = models_comp.get(selected_model_key, {})

with col_info:
    if current_model_metric:
        m1, m2, m3 = st.columns(3)
        m1.metric("MAE của mô hình", f"{current_model_metric.get('mae', 0.0):.2f} °C")
        m2.metric("RMSE của mô hình", f"{current_model_metric.get('rmse', 0.0):.2f} °C")
        m3.metric("Mức giảm sai số", f"{current_model_metric.get('mae_reduction_percentage', 0.0):+.1f}%")

st.divider()

# 2. Lấy dữ liệu dự báo và vẽ biểu đồ
pred_data = fetch_predictions()

if pred_data and "predictions" in pred_data:
    df_pred = pd.DataFrame(pred_data["predictions"])

    # Biểu đồ so sánh nhiệt độ theo model được chọn
    st.plotly_chart(
        plot_temperature_comparison(df_pred, model_name=selected_model_key),
        use_container_width=True,
    )

    # 2 Biểu đồ hàng dưới: Chỉ số khí tượng mở rộng & So sánh 4 mô hình
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.plotly_chart(plot_weather_indicators(df_pred), use_container_width=True)
    with col_chart2:
        if models_comp:
            st.plotly_chart(plot_models_comparison_bar(models_comp), use_container_width=True)
        else:
            st.info("Chưa có dữ liệu so sánh các mô hình.")

    st.divider()

    # 3. Bảng dữ liệu chi tiết 7 chỉ số
    st.markdown("#### 📋 Bảng Chi Tiết Dự Báo Thời Tiết 16 Ngày Tới (TP.HCM)")

    # Định dạng bảng hiển thị đẹp mắt
    display_cols = [
        "date",
        "raw_forecast_temp_max",
        "corrected_temp_max",
        "humidity",
        "cloud_cover",
        "rain_probability",
        "rain_status",
        "sunshine_duration_hours",
        "uv_index",
    ]
    available_cols = [c for c in display_cols if c in df_pred.columns]
    table_df = df_pred[available_cols].copy()

    table_df.columns = [
        "Ngày",
        "Nhiệt độ thô (°C)",
        "Nhiệt độ hiệu chỉnh (°C)",
        "Độ ẩm (%)",
        "Mây phủ (%)",
        "Xác suất mưa (%)",
        "Trạng thái mưa",
        "Số giờ nắng (h)",
        "Chỉ số UV",
    ][:len(available_cols)]

    st.dataframe(table_df, use_container_width=True, height=400)

else:
    st.warning("⚠️ Chưa có dữ liệu dự báo. Vui lòng vào trang **🔧 Pipeline Control** để kích hoạt chạy pipeline!")
