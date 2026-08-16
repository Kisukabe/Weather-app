import streamlit as st
from frontend.components.sidebar import render_sidebar
from frontend.components.api_client import fetch_logs

st.set_page_config(
    page_title="Weather MLOps | System Logs",
    page_icon="📋",
    layout="wide",
)

render_sidebar()

st.title("📋 Giám Sát Log Hệ Thống Thời Gian Thực")
st.caption("Xem logs ứng dụng trực tiếp từ server (Hỗ trợ Log Rotation tối đa 50MB).")

st.divider()

col_lines, col_search, col_btn = st.columns([1, 2, 1])

with col_lines:
    num_lines = st.slider("Số dòng log hiển thị:", min_value=20, max_value=300, value=100, step=20)

with col_search:
    search_keyword = st.text_input("🔍 Lọc log theo từ khóa (vd: ERROR, PySpark, Train):", value="")

with col_btn:
    st.write("")
    st.write("")
    if st.button("🔄 Làm mới Logs", use_container_width=True):
        st.rerun()

logs_data = fetch_logs(lines=num_lines)

if logs_data and "logs" in logs_data:
    raw_logs = logs_data["logs"]
    if search_keyword:
        filtered_logs = [line for line in raw_logs if search_keyword.lower() in line.lower()]
    else:
        filtered_logs = raw_logs

    st.markdown(f"**Tổng số dòng:** `{len(filtered_logs)}` / `{len(raw_logs)}`")
    st.code("\n".join(filtered_logs) if filtered_logs else "Không tìm thấy log phù hợp với từ khóa.", language="log")
else:
    st.info("Chưa thể tải dữ liệu log từ Backend.")
