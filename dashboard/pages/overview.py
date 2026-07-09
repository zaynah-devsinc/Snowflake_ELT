from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

import page_ui
import queries
import utils


# ── Color palette ──────────────────────────────────────────────────────────
ORANGE  = "#FF5C35"
DARK    = "#1a1d23"
CARD_BG = "#ffffff"
MUTED   = "#64748b"
BORDER  = "#eef0f7"
GREEN   = "#22c55e"
RED     = "#ef4444"
AMBER   = "#f59e0b"
PURPLE  = "#8b5cf6"
BLUE    = "#3b82f6"


# ── Helpers ─────────────────────────────────────────────────────────────────

def _chart_layout(fig: go.Figure, height: int = 260) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=16, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=MUTED, size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11)),
        showlegend=True,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickfont=dict(size=10))
    return fig


def _status_badge(status: str) -> str:
    colors = {
        "completed":   (GREEN,  "#f0fdf4"),
        "pending":     (AMBER,  "#fffbeb"),
        "in progress": (BLUE,   "#eff6ff"),
        "cancelled":   (RED,    "#fef2f2"),
        "refunded":    (PURPLE, "#f5f3ff"),
    }
    key = status.lower() if status else ""
    dot, bg = colors.get(key, ("#94a3b8", "#f8fafc"))
    label = status.title() if status else "—"
    return (
        f"<span style='display:inline-flex;align-items:center;gap:5px;"
        f"background:{bg};color:{dot};border-radius:20px;padding:3px 10px;"
        f"font-size:11px;font-weight:600;'>"
        f"<span style='width:6px;height:6px;border-radius:50%;background:{dot};display:inline-block;'></span>"
        f"{label}</span>"
    )


def _render_kpi_card(title: str, value: str, icon_name: str, highlight: bool = False) -> None:
    icon_html = page_ui.icon(icon_name, size=18, color="#fff" if highlight else None)
    icon_box_style = (
        "background:rgba(255,255,255,0.2);"
        if highlight
        else "background:#f5f6fa;"
    )
    if highlight:
        st.markdown(
            f"""
            <div style='background:linear-gradient(135deg,{ORANGE} 0%,#FF8C6B 100%);
                        border-radius:20px;padding:22px;color:#fff;height:100%;
                        box-shadow:0 8px 32px rgba(255,92,53,0.3);'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;'>
                    <div style='font-size:12px;font-weight:600;opacity:0.9;text-transform:uppercase;
                                letter-spacing:0.05em;'>{title}</div>
                    <div style='{icon_box_style}border-radius:10px;width:34px;height:34px;
                                display:flex;align-items:center;justify-content:center;'>{icon_html}</div>
                </div>
                <div style='font-size:28px;font-weight:800;line-height:1.1;'>{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style='background:{CARD_BG};border-radius:20px;padding:22px;
                        border:1.5px solid {BORDER};box-shadow:0 4px 20px rgba(0,0,0,0.04);height:100%;'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;'>
                    <div style='font-size:12px;color:{MUTED};font-weight:600;letter-spacing:0.05em;
                                text-transform:uppercase;'>{title}</div>
                    <div style='{icon_box_style}border-radius:10px;width:34px;height:34px;
                                display:flex;align-items:center;justify-content:center;'>{icon_html}</div>
                </div>
                <div style='font-size:28px;font-weight:800;color:{DARK};line-height:1.1;'>{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Chart helpers ────────────────────────────────────────────────────────────

def _revenue_area_chart(revenue_df) -> go.Figure:
    fig = go.Figure()
    if revenue_df.empty:
        return fig
    months   = revenue_df["MONTH"].dt.strftime("%b %Y").tolist()
    revenues = revenue_df["NET_REVENUE"].tolist()
    orders   = revenue_df["ORDER_COUNT"].tolist()

    fig.add_trace(go.Scatter(
        x=months, y=revenues, name="Revenue",
        mode="lines+markers",
        line=dict(color=ORANGE, width=3),
        marker=dict(size=6, color=ORANGE, line=dict(color="#fff", width=2)),
        fill="tozeroy",
        fillcolor="rgba(255,92,53,0.10)",
    ))
    fig.add_trace(go.Scatter(
        x=months, y=orders, name="Orders",
        mode="lines+markers",
        line=dict(color=DARK, width=2, dash="dot"),
        marker=dict(size=5, color=DARK),
        yaxis="y2",
    ))
    _chart_layout(fig, height=280)
    fig.update_layout(
        yaxis2=dict(overlaying="y", side="right", showgrid=False, tickfont=dict(size=9),
                    title="Orders"),
        yaxis=dict(title="Revenue ($)", tickformat="~s"),
    )
    return fig


def _category_bar_chart(category_df) -> go.Figure:
    fig = go.Figure()
    if category_df.empty:
        return fig
    cats = category_df["CATEGORY"].tolist()
    vals = category_df["NET_REVENUE"].tolist()
    colors = [ORANGE if i % 2 == 0 else DARK for i in range(len(cats))]
    fig.add_trace(go.Bar(
        x=cats, y=vals,
        marker_color=colors,
        marker_line_width=0,
    ))
    _chart_layout(fig, height=280)
    fig.update_layout(showlegend=False, yaxis=dict(tickformat="~s", tickprefix="$"))
    return fig


def _status_donut_chart(status_df) -> go.Figure:
    fig = go.Figure()
    if status_df.empty:
        return fig
    palette = [ORANGE, DARK, BLUE, GREEN, PURPLE]
    fig.add_trace(go.Pie(
        labels=status_df["STATUS"].tolist(),
        values=status_df["COUNT"].tolist(),
        hole=0.55,
        marker_colors=palette[:len(status_df)],
        textinfo="percent",
        textfont_size=11,
    ))
    _chart_layout(fig, height=260)
    fig.update_layout(
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
    )
    return fig


# ── Recent orders table ─────────────────────────────────────────────────────

def _render_orders_table(orders_df) -> None:
    if orders_df.empty:
        st.info("No recent orders found.")
        return

    cols_map = {
        "ORDER_ID": "Order ID", "ORDER_DATE": "Date",
        "CUSTOMER_NAME": "Customer", "PRODUCT_NAME": "Product",
        "CATEGORY": "Category", "NET_SALES": "Amount", "STATUS": "Status",
    }
    disp = orders_df[[c for c in cols_map if c in orders_df.columns]].copy()
    disp = disp.rename(columns=cols_map)

    header_html = """
    <div style='display:grid;grid-template-columns:130px 1fr 1fr 1fr 80px 100px;
                gap:8px;padding:10px 16px;background:#f8fafc;border-radius:12px 12px 0 0;
                font-size:11px;font-weight:700;color:#94a3b8;letter-spacing:0.08em;
                text-transform:uppercase;border:1.5px solid #eef0f7;border-bottom:none;'>
        <span>Order ID</span><span>Customer</span><span>Product</span>
        <span>Category</span><span>Amount</span><span>Status</span>
    </div>"""
    st.markdown(header_html, unsafe_allow_html=True)

    rows_html = "<div style='border:1.5px solid #eef0f7;border-top:none;border-radius:0 0 12px 12px;overflow:hidden;'>"
    for i, (_, row) in enumerate(disp.iterrows()):
        bg = "#ffffff" if i % 2 == 0 else "#fafbfd"
        oid      = row.get("Order ID", "—")
        customer = str(row.get("Customer", "—"))[:18]
        product  = str(row.get("Product", "—"))[:22]
        category = str(row.get("Category", "—"))[:14]
        amount   = f"${row.get('Amount', 0):,.2f}" if row.get("Amount") else "—"
        status   = _status_badge(str(row.get("Status", "")))

        rows_html += f"""
        <div style='display:grid;grid-template-columns:130px 1fr 1fr 1fr 80px 100px;
                    gap:8px;padding:12px 16px;background:{bg};
                    font-size:12px;color:#334155;align-items:center;
                    border-bottom:1px solid #f1f5f9;'>
            <span style='font-weight:600;color:{ORANGE};font-size:11px;'>{oid}</span>
            <span style='font-weight:500;'>{customer}</span>
            <span style='color:{MUTED};'>{product}</span>
            <span style='color:{MUTED};'>{category}</span>
            <span style='font-weight:700;color:{DARK};'>{amount}</span>
            <span>{status}</span>
        </div>"""

    rows_html += "</div>"
    st.markdown(rows_html, unsafe_allow_html=True)


# ── Main render ─────────────────────────────────────────────────────────────

def render(filters: dict) -> None:
    now_hour = datetime.now().hour
    greeting = "Good morning" if now_hour < 12 else ("Good afternoon" if now_hour < 17 else "Good evening")

    st.markdown(f"### {greeting}, Overview")
    st.caption("Orders, revenue, and customer metrics from FACT_ORDERS.")
    page_ui.render_dashboard_guide()

    kpi_df      = utils.run_query(queries.get_kpi_query(filters))
    revenue_df  = utils.run_query(queries.get_monthly_revenue_query(filters))
    category_df = utils.run_query(queries.get_category_revenue_query(filters))
    status_df   = utils.run_query(queries.get_status_distribution_query(filters))
    orders_df   = utils.run_query(queries.get_base_order_query(filters, limit=10))

    if kpi_df.empty:
        st.warning("No data available for the selected filters.")
        return

    kpi = kpi_df.iloc[0]
    total_revenue   = utils.format_currency(kpi["TOTAL_REVENUE"])
    total_orders    = utils.format_integer(kpi["TOTAL_ORDERS"])
    total_customers = utils.format_integer(kpi["TOTAL_CUSTOMERS"])
    total_products  = utils.format_integer(kpi["TOTAL_PRODUCTS"])
    avg_order_val   = utils.format_currency(kpi["AVERAGE_ORDER_VALUE"])

    if not revenue_df.empty:
        revenue_df = revenue_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(revenue_df["MONTH"]):
            revenue_df["MONTH"] = pd.to_datetime(revenue_df["MONTH"], errors="coerce")
        revenue_df["MONTH"] = revenue_df["MONTH"].dt.to_period("M").dt.to_timestamp()

    # Row 1 — KPI cards
    kpi_cols = st.columns(5, gap="medium")
    kpi_items = [
        ("Total Revenue", total_revenue, "payments", True),
        ("Total Orders", total_orders, "receipt_long", False),
        ("Total Customers", total_customers, "groups", False),
        ("Total Products", total_products, "inventory_2", False),
        ("Avg Order Value", avg_order_val, "paid", False),
    ]
    for col, (title, value, icon_name, highlight) in zip(kpi_cols, kpi_items):
        with col:
            _render_kpi_card(title, value, icon_name, highlight=highlight)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Row 2 — Charts
    chart_left, chart_right = st.columns(2, gap="large")
    with chart_left:
        page_ui.section_header("Monthly Revenue & Orders", "Line chart — seasonality and order volume from FACT_ORDERS")
        if not revenue_df.empty:
            st.plotly_chart(_revenue_area_chart(revenue_df), use_container_width=True,
                            config={"displayModeBar": False}, key="overview_revenue")
        else:
            st.info("No revenue data available.")
    with chart_right:
        page_ui.section_header("Revenue by Category", "Bar chart — which product categories drive net sales")
        if not category_df.empty:
            st.plotly_chart(_category_bar_chart(category_df), use_container_width=True,
                            config={"displayModeBar": False}, key="overview_category")
        else:
            st.info("No category data.")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Row 3 — Status donut + Recent orders
    status_col, orders_col = st.columns([1, 2], gap="large")
    with status_col:
        page_ui.section_header("Order Status Distribution", "Donut — share of completed, pending, and cancelled lines")
        if not status_df.empty:
            st.plotly_chart(_status_donut_chart(status_df), use_container_width=True,
                            config={"displayModeBar": False}, key="overview_status")
        else:
            st.info("No status data.")
    with orders_col:
        page_ui.section_header("Recent Orders", "Latest 10 line items with customer and product context")
        _render_orders_table(orders_df)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Row 4 — All orders
    page_ui.section_header("All Orders", "Searchable table — up to 50 most recent order lines")
    full_orders = utils.run_query(queries.get_base_order_query(filters, limit=50))
    if not full_orders.empty:
        display_df = full_orders.drop(columns=["PRODUCT_PRICE", "STOCK"], errors="ignore")
        display_df = display_df.rename(columns={
            "ORDER_ID": "Order ID", "ORDER_DATE": "Date",
            "CUSTOMER_NAME": "Customer", "PRODUCT_NAME": "Product",
            "CATEGORY": "Category", "NET_SALES": "Net Sales",
            "STATUS": "Status", "PAYMENT_METHOD": "Payment",
        })
        st.dataframe(display_df, use_container_width=True, height=420, hide_index=True)
    else:
        st.info("No orders found.")
