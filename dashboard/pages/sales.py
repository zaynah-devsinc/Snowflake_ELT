from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

import page_ui
import queries
import utils

ORANGE  = "#FF5C35"
DARK    = "#1a1d23"
MUTED   = "#64748b"
BORDER  = "#eef0f7"
GREEN   = "#22c55e"
BLUE    = "#3b82f6"
PURPLE  = "#8b5cf6"


def _chart_layout(fig: go.Figure, height: int = 300) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=MUTED, size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickfont=dict(size=10))
    return fig


def _kpi_pill(label: str, value: str, bg: str, icon_name: str) -> str:
    return f"""<div style='background:#fff;border-radius:16px;padding:16px 18px;
                           border:1.5px solid {BORDER};flex:1;min-width:130px;'>
                   <div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;'>
                       {page_ui.icon_in_box(icon_name, bg)}
                       <div style='font-size:11px;color:{MUTED};font-weight:600;
                                   text-transform:uppercase;letter-spacing:0.06em;'>{label}</div>
                   </div>
                   <div style='font-size:22px;font-weight:800;color:{DARK};'>{value}</div>
               </div>"""


def render(filters: dict) -> None:
    st.markdown("### Sales Analytics")
    st.caption("Deep dive into revenue, brands, products and payment performance.")

    category_df = utils.run_query(queries.get_category_revenue_query(filters))
    brand_df    = utils.run_query(queries.get_sales_by_brand_query(filters))
    product_df  = utils.run_query(queries.get_top_products_query(filters, limit=10))
    payment_df  = utils.run_query(queries.get_revenue_by_payment_method_query(filters))
    discount_df = utils.run_query(queries.get_discount_analysis_query(filters))
    monthly_df  = utils.run_query(queries.get_monthly_revenue_query(filters))
    daily_df    = utils.run_query(queries.get_daily_sales_query(filters))

    kpi_df = utils.run_query(queries.get_kpi_query(filters))
    if not kpi_df.empty:
        kpi = kpi_df.iloc[0]
        pills_html = f"""<div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:24px;'>
            {_kpi_pill("Revenue",   utils.format_currency(kpi["TOTAL_REVENUE"]),   "#fff5f2", "payments")}
            {_kpi_pill("Orders",    utils.format_integer(kpi["TOTAL_ORDERS"]),     "#f5f6fa", "receipt_long")}
            {_kpi_pill("Customers", utils.format_integer(kpi["TOTAL_CUSTOMERS"]), "#eff6ff", "groups")}
            {_kpi_pill("Avg Order", utils.format_currency(kpi["AVERAGE_ORDER_VALUE"]), "#f0fdf4", "paid")}
        </div>"""
        st.markdown(pills_html, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Category & Brand",
        "Top Products",
        "Payment & Discount",
        "Time Series",
    ])

    with tab1:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            page_ui.section_header("Revenue by Category", "Net sales split across product categories")
            if not category_df.empty:
                colors = [ORANGE if i % 2 == 0 else DARK for i in range(len(category_df))]
                fig = go.Figure(go.Bar(
                    x=category_df["CATEGORY"],
                    y=category_df["NET_REVENUE"],
                    marker_color=colors,
                    marker_line_width=0,
                ))
                _chart_layout(fig, 320)
                fig.update_layout(showlegend=False, yaxis=dict(tickformat="~s", tickprefix="$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="sales_category")
            else:
                st.info("No category data.")
        with c2:
            page_ui.section_header("Revenue by Brand", "Top performing brands by net sales")
            if not brand_df.empty:
                top_brands = brand_df.head(8)
                fig = go.Figure(go.Bar(
                    x=top_brands["BRAND"],
                    y=top_brands["NET_REVENUE"],
                    marker=dict(
                        color=top_brands["NET_REVENUE"],
                        colorscale=[[0, "#fff5f2"], [1, ORANGE]],
                        showscale=False,
                        line_width=0,
                    ),
                ))
                _chart_layout(fig, 320)
                fig.update_layout(showlegend=False, yaxis=dict(tickformat="~s", tickprefix="$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="sales_brand")
            else:
                st.info("No brand data.")

    with tab2:
        page_ui.section_header("Top 10 Products by Revenue")
        if not product_df.empty:
            fig = go.Figure(go.Bar(
                y=product_df["PRODUCT_NAME"],
                x=product_df["NET_REVENUE"],
                orientation="h",
                marker=dict(
                    color=product_df["NET_REVENUE"],
                    colorscale=[[0, "#fff5f2"], [1, ORANGE]],
                    showscale=False,
                    line_width=0,
                ),
                text=product_df["NET_REVENUE"].apply(lambda v: f"${v:,.0f}"),
                textposition="outside",
                textfont=dict(size=10, color=MUTED),
            ))
            _chart_layout(fig, height=380)
            fig.update_layout(showlegend=False, xaxis=dict(tickformat="~s", tickprefix="$"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="sales_top_products")
            page_ui.section_title("Product Detail Table")
            st.dataframe(
                product_df.rename(columns={
                    "PRODUCT_NAME": "Product", "CATEGORY": "Category",
                    "BRAND": "Brand", "ITEMS_SOLD": "Units Sold", "NET_REVENUE": "Revenue",
                }),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No product data available for the selected filters.")

    with tab3:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            page_ui.section_header("Revenue by Payment Method")
            if not payment_df.empty:
                palette = [ORANGE, DARK, BLUE, GREEN, PURPLE]
                fig = go.Figure(go.Pie(
                    labels=payment_df["PAYMENT_METHOD"],
                    values=payment_df["NET_REVENUE"],
                    hole=0.52,
                    marker_colors=palette[:len(payment_df)],
                    textinfo="label+percent",
                    textfont_size=11,
                ))
                _chart_layout(fig, 320)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="sales_payment")
            else:
                st.info("No payment data.")
        with c2:
            page_ui.section_header("Discount Analysis by Category")
            if not discount_df.empty:
                discount_df["AVERAGE_DISCOUNT"] = discount_df["AVERAGE_DISCOUNT"].round(2)
                fig = go.Figure(go.Bar(
                    y=discount_df["CATEGORY"],
                    x=discount_df["AVERAGE_DISCOUNT"],
                    orientation="h",
                    marker_color=ORANGE,
                    marker_line_width=0,
                    text=discount_df["AVERAGE_DISCOUNT"].apply(lambda v: f"{v:.1f}%"),
                    textposition="outside",
                    textfont=dict(size=10),
                ))
                _chart_layout(fig, 320)
                fig.update_layout(
                    showlegend=False,
                    xaxis=dict(ticksuffix="%", title="Average Discount"),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="sales_discount")
            else:
                st.info("No discount data.")

    with tab4:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            page_ui.section_header("Monthly Sales Trend")
            if not monthly_df.empty:
                if not pd.api.types.is_datetime64_any_dtype(monthly_df["MONTH"]):
                    monthly_df["MONTH"] = pd.to_datetime(monthly_df["MONTH"], errors="coerce")
                monthly_df["MONTH"] = monthly_df["MONTH"].dt.to_period("M").dt.to_timestamp()
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=monthly_df["MONTH"], y=monthly_df["NET_REVENUE"],
                    mode="lines+markers",
                    line=dict(color=ORANGE, width=3),
                    marker=dict(size=7, color=ORANGE, line=dict(color="#fff", width=2)),
                    fill="tozeroy",
                    fillcolor="rgba(255,92,53,0.10)",
                    name="Revenue",
                ))
                _chart_layout(fig, 300)
                fig.update_layout(yaxis=dict(tickformat="~s", tickprefix="$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="sales_monthly")
            else:
                st.info("No monthly data.")
        with c2:
            page_ui.section_header("Daily Sales Trend")
            if not daily_df.empty:
                if not pd.api.types.is_datetime64_any_dtype(daily_df["DAY"]):
                    daily_df["DAY"] = pd.to_datetime(daily_df["DAY"], errors="coerce")
                daily_df["DAY"] = daily_df["DAY"].dt.date
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=daily_df["DAY"], y=daily_df["NET_REVENUE"],
                    mode="lines",
                    line=dict(color=DARK, width=2),
                    fill="tozeroy",
                    fillcolor="rgba(26,29,35,0.06)",
                    name="Daily Revenue",
                ))
                _chart_layout(fig, 300)
                fig.update_layout(yaxis=dict(tickformat="~s", tickprefix="$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="sales_daily")
            else:
                st.info("No daily data.")
