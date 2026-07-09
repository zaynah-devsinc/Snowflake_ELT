from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
from datetime import datetime

import page_ui


ROOT_DIR = Path(__file__).resolve().parents[2]
FORECAST_DIR = ROOT_DIR / "forecasts"

ORANGE = "#FF5C35"
DARK = "#1a1d23"
MUTED = "#64748b"
CARD_BG = "#ffffff"
BORDER = "#eef0f7"
GREEN = "#22c55e"
RED = "#ef4444"
BLUE = "#3b82f6"


def _load_csv(filename: str) -> pd.DataFrame:
    path = FORECAST_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=["MONTH"])
    return df


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def _build_forecast_figure(history_df: pd.DataFrame, forecast_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if not history_df.empty:
        fig.add_trace(go.Scatter(
            x=history_df["MONTH"], y=history_df["revenue"],
            name="Actual Revenue",
            mode="lines+markers",
            line=dict(color=DARK, width=3),
            marker=dict(size=6, color=DARK),
        ))
    if not forecast_df.empty:
        fig.add_trace(go.Scatter(
            x=forecast_df["MONTH"], y=forecast_df["predicted_revenue"],
            name="Forecast Revenue",
            mode="lines+markers",
            line=dict(color=ORANGE, width=3, dash="dash"),
            marker=dict(size=6, color=ORANGE),
        ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=MUTED, size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickfont=dict(size=10), tickprefix="$")
    return fig


def render(filters: dict) -> None:
    st.markdown("### Forecast")
    st.caption("Revenue forecasting with a simple linear regression model built on historical monthly sales.")

    history_df = _load_csv("monthly_revenue.csv")
    forecast_df = _load_csv("revenue_forecast.csv")

    if history_df.empty or forecast_df.empty:
        st.warning("Forecast data is not available. Run python/forecast_revenue.py to generate forecasts.")
        return

    last_actual = history_df.iloc[-1]["revenue"]
    next_month = forecast_df.iloc[0]["predicted_revenue"]
    growth = ((next_month - last_actual) / last_actual) * 100 if last_actual else 0

    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Last Month Revenue", _format_currency(last_actual))
    kpi_cols[0].caption(history_df.iloc[-1]["MONTH"].strftime("%b %Y"))
    kpi_cols[1].metric("Predicted Next Month", _format_currency(next_month))
    kpi_cols[1].caption(forecast_df.iloc[0]["MONTH"].strftime("%b %Y"))
    kpi_cols[2].metric("Expected Growth", f"{growth:.1f}%")
    kpi_cols[2].caption("Next month vs last actual month")

    st.subheader("Historical Revenue")
    fig_actual = go.Figure(go.Scatter(
        x=history_df["MONTH"], y=history_df["revenue"],
        mode="lines+markers",
        line=dict(color=DARK, width=3),
        marker=dict(size=6, color=DARK),
        name="Actual Revenue",
    ))
    fig_actual.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig_actual.update_xaxes(showgrid=False, zeroline=False)
    fig_actual.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickprefix="$")
    st.plotly_chart(fig_actual, use_container_width=True, config={"displayModeBar": False})

    st.subheader("Forecast")
    fig_forecast = _build_forecast_figure(history_df, forecast_df)
    st.plotly_chart(fig_forecast, use_container_width=True, config={"displayModeBar": False})

    st.subheader("Prediction Table")
    display_table = forecast_df.copy()
    if not pd.api.types.is_datetime64_any_dtype(display_table["MONTH"]):
        display_table["MONTH"] = pd.to_datetime(display_table["MONTH"], errors="coerce")
    display_table["MONTH"] = display_table["MONTH"].dt.strftime("%b %Y")
    display_table["predicted_revenue"] = display_table["predicted_revenue"].apply(_format_currency)
    st.dataframe(display_table.rename(columns={"MONTH": "Month", "predicted_revenue": "Predicted Revenue"}), use_container_width=True, hide_index=True)

    st.subheader("Forecast Metrics")
    metric_cols = st.columns(3)
    metric_cols[0].markdown("**Model Used**")
    metric_cols[0].markdown("Linear Regression")
    metric_cols[1].markdown("**Training Period**")
    metric_cols[1].markdown(f"{history_df.iloc[0]["MONTH"].strftime("%b %Y")} - {history_df.iloc[-1]["MONTH"].strftime("%b %Y")}")
    metric_cols[2].markdown("**Forecast Horizon**")
    metric_cols[2].markdown("3 Months")

    st.subheader("Insights")
    direction = "increase" if growth >= 0 else "decrease"
    insight_html = f"<div style='background:#ffffff;border-radius:20px;padding:22px;border:1.5px solid {BORDER};box-shadow:0 6px 24px rgba(0,0,0,0.05);'>"
    insight_html += f"<p style='margin:0 0 10px;font-size:14px;color:{DARK};'>Revenue is expected to {direction} by approximately <strong>{abs(growth):.1f}%</strong> over the next month.</p>"
    insight_html += "<p style='margin:0;font-size:14px;color:#475569;'>The historical trend shows steady growth across the training period, supporting a linear forecast for the next quarters.</p>"
    insight_html += "</div>"
    st.markdown(insight_html, unsafe_allow_html=True)
