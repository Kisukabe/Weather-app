import streamlit as st
from frontend.components.api_client import fetch_health, BACKEND_URL


def render_sidebar():
    """Hiển thị Sidebar dùng chung cho toàn bộ các trang Streamlit."""
    st.sidebar.markdown("### 🌤️ Weather MLOps System")
    st.sidebar.caption("Hệ thống Hiệu chỉnh Sai số Dự báo Thời tiết TP.HCM")

    st.sidebar.divider()

    # Kiểm tra trạng thái Backend
    health = fetch_health()
    if health and health.get("status") == "healthy":
        st.sidebar.success("🟢 Backend Connected (FastAPI)")
        if "scheduler" in health:
            sched = health["scheduler"]
            st.sidebar.caption(f"⏰ Lịch chạy tự động: **{sched.get('schedule', 'N/A')}**")
            if sched.get("next_run"):
                next_time = sched["next_run"].split("T")[1][:5] if "T" in sched["next_run"] else sched["next_run"]
                st.sidebar.caption(f"⏳ Lần chạy kế tiếp: **{next_time}**")
        st.sidebar.caption(f"📦 DB: **{health.get('database', 'connected')}**")
    else:
        st.sidebar.error(f"🔴 Không thể kết nối tới Backend ({BACKEND_URL})")

    st.sidebar.divider()
    st.sidebar.caption("Phiên bản: **v2.0.0 (Multi-Model Registry)**")
