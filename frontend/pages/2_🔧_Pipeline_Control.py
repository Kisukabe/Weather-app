import time
import streamlit as st
import pandas as pd
from frontend.components.sidebar import render_sidebar
from frontend.components.api_client import (
    trigger_pipeline_run,
    fetch_pipeline_status,
    fetch_pipeline_history,
)

st.set_page_config(
    page_title="Weather MLOps | Điều Khiển Pipeline",
    page_icon="🔧",
    layout="wide",
)

render_sidebar()

st.title("🔧 Quản Lý & Kích Hoạt MLOps Pipeline")
st.caption("Kích hoạt 6 Stage Pipeline (Ingestion ➔ Validation ➔ PySpark Transform ➔ Train Registry ➔ Evaluation ➔ Prediction)")

st.divider()

col_action, col_status = st.columns([1, 2])

with col_action:
    st.markdown("#### 🚀 Kích Hoạt Pipeline Thủ Công")
    st.write("Bấm nút bên dưới để khởi chạy toàn bộ 6 Stage của hệ thống.")

    if st.button("▶️ Kích Hoạt Run Full Pipeline", type="primary", use_container_width=True):
        res = trigger_pipeline_run()
        if res.get("status_code") in [200, 202]:
            st.success("✅ Đã gửi yêu cầu thành công! Pipeline đang chạy trong nền...")

            # Polling theo dõi trạng thái
            with st.spinner("Đang thực thi các Stage..."):
                completed = False
                for _ in range(60):  # Chờ tối đa 120s
                    time.sleep(2)
                    status_info = fetch_pipeline_status()
                    if status_info:
                        curr_status = status_info.get("status")
                        if curr_status == "SUCCESS":
                            st.balloons()
                            st.success(f"🎉 {status_info.get('message')}")
                            completed = True
                            time.sleep(1)
                            st.rerun()
                            break
                        elif curr_status == "FAILED":
                            st.error(f"❌ {status_info.get('message')}")
                            completed = True
                            break
        else:
            st.error(f"Lỗi khi gửi yêu cầu: {res.get('error', res.get('status_code'))}")

with col_status:
    st.markdown("#### 📡 Trạng Thái Hệ Thống Thời Gian Thực")
    status_info = fetch_pipeline_status()
    if status_info:
        status_badge = {
            "IDLE": "⚪ Sẵn sàng",
            "RUNNING": "🟡 Đang thực thi",
            "SUCCESS": "🟢 Thành công",
            "FAILED": "🔴 Thất bại",
        }.get(status_info.get("status", "IDLE"), "⚪ Chưa rõ")

        st.info(f"**Trạng thái:** {status_badge}")
        st.write(f"**Thông điệp:** {status_info.get('message', 'N/A')}")
        st.write(f"**Thời gian bắt đầu:** `{status_info.get('started_at', 'Chưa chạy')}`")
        st.write(f"**Thời gian chạy:** `{status_info.get('duration_seconds', 0.0)} giây`")
    else:
        st.warning("Chưa lấy được trạng thái từ Backend API.")

st.divider()

# Bảng lịch sử các lượt chạy từ SQLite
st.markdown("#### 📜 Lịch Sử Các Lượt Chạy Pipeline (SQLite History DB)")

history_data = fetch_pipeline_history(limit=15)
if history_data and "history" in history_data and history_data["history"]:
    df_hist = pd.DataFrame(history_data["history"])
    st.dataframe(df_hist, use_container_width=True)
else:
    st.caption("Chưa có lịch sử các lượt chạy được ghi nhận.")
