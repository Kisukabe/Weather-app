import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any


def plot_temperature_comparison(df: pd.DataFrame, model_name: str = "xgboost") -> go.Figure:
    """Biểu đồ so sánh nhiệt độ dự báo thô và sau hiệu chỉnh bằng mô hình được chọn."""
    fig = go.Figure()

    # Dữ liệu dự báo thô
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["raw_forecast_temp_max"],
            mode="lines+markers",
            name="Dự báo thô (Open-Meteo)",
            line=dict(color="#FF4B4B", width=2, dash="dash"),
            marker=dict(size=6),
            hovertemplate="Ngày: %{x}<br>Dự báo thô: %{y:.1f}°C<extra></extra>",
        )
    )

    # Dữ liệu sau hiệu chỉnh theo mô hình được chọn
    y_corrected = df["corrected_temp_max"]
    if "models" in df.columns and len(df) > 0 and isinstance(df["models"].iloc[0], dict):
        try:
            model_values = [row.get(model_name, {}).get("corrected_temp_max", row.get("corrected_temp_max")) for row in df["models"]]
            if any(v is not None for v in model_values):
                y_corrected = model_values
        except Exception:
            pass

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=y_corrected,
            mode="lines+markers",
            name=f"Hiệu chỉnh ML ({model_name.upper()})",
            line=dict(color="#00CC96", width=3.5),
            marker=dict(size=8, color="#00CC96"),
            hovertemplate="Ngày: %{x}<br>Hiệu chỉnh: %{y:.1f}°C<extra></extra>",
        )
    )

    fig.update_layout(
        title=f"📈 So sánh Nhiệt Độ Cao Nhất Dự Báo Thô vs Sau Hiệu Chỉnh ({model_name.upper()})",
        xaxis_title="Thời gian (Ngày)",
        yaxis_title="Nhiệt độ (°C)",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def plot_weather_indicators(df: pd.DataFrame) -> go.Figure:
    """Biểu đồ đa trục hiển thị Độ ẩm, Độ che phủ mây và Xác suất mưa."""
    fig = go.Figure()

    if "humidity" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["humidity"],
                mode="lines",
                name="Độ ẩm (%)",
                line=dict(color="#636EFA", width=2),
                hovertemplate="Độ ẩm: %{y:.0f}%<extra></extra>",
            )
        )

    if "cloud_cover" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["cloud_cover"],
                mode="lines",
                name="Độ phủ mây (%)",
                line=dict(color="#AB63FA", width=2, dash="dot"),
                hovertemplate="Độ phủ mây: %{y:.0f}%<extra></extra>",
            )
        )

    if "rain_probability" in df.columns:
        fig.add_trace(
            go.Bar(
                x=df["date"],
                y=df["rain_probability"],
                name="Xác suất mưa (%)",
                marker_color="rgba(0, 180, 255, 0.4)",
                hovertemplate="Xác suất mưa: %{y:.0f}%<extra></extra>",
            )
        )

    fig.update_layout(
        title="💧 Các Chỉ Số Khí Tượng Mở Rộng (Độ Ẩm, Mây, Xác Suất Mưa)",
        xaxis_title="Thời gian (Ngày)",
        yaxis_title="Tỷ lệ phần trăm (%)",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def plot_models_comparison_bar(models_comparison: Dict[str, Any]) -> go.Figure:
    """Biểu đồ cột so sánh mức độ giảm sai số MAE của 4 mô hình trong Model Registry."""
    model_names = list(models_comparison.keys())
    mae_reductions = [
        models_comparison[m].get("mae_reduction_percentage", 0.0) for m in model_names
    ]

    colors = ["#00CC96" if val >= 0 else "#FF4B4B" for val in mae_reductions]

    fig = go.Figure(
        go.Bar(
            x=[m.upper() for m in model_names],
            y=mae_reductions,
            marker_color=colors,
            text=[f"{v:+.1f}%" for v in mae_reductions],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="🏆 So sánh Mức độ Cải thiện Sai số MAE (%) giữa các Mô hình",
        xaxis_title="Mô hình ML trong Registry",
        yaxis_title="% Giảm sai số MAE (Càng cao càng tốt)",
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig
