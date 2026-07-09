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


def _customer_row(rank: int, name: str, country: str, orders: int, ltv: float) -> str:
    rank_label = f"#{rank}"
    rank_color = ORANGE if rank <= 3 else MUTED
    ltv_s  = f"${ltv:,.2f}"
    bar_w  = min(100, int(ltv / 500))
    return f"""
    <div style='display:flex;align-items:center;gap:12px;padding:10px 0;
                border-bottom:1px solid {BORDER};'>
        <div style='width:28px;text-align:center;font-size:12px;font-weight:700;color:{rank_color};'>{rank_label}</div>
        <div style='flex:1;'>
            <div style='font-size:13px;font-weight:600;color:{DARK};'>{name}</div>
            <div style='font-size:11px;color:{MUTED};'>{country} · {orders} orders</div>
        </div>
        <div style='text-align:right;'>
            <div style='font-size:14px;font-weight:800;color:{ORANGE};'>{ltv_s}</div>
            <div style='height:4px;background:#f0f2f8;border-radius:4px;margin-top:4px;width:80px;'>
                <div style='height:100%;width:{bar_w}%;background:{ORANGE};border-radius:4px;'></div>
            </div>
        </div>
    </div>"""


def render(filters: dict) -> None:
    st.markdown("### Customer Analytics")
    st.caption("Lifetime value, geography, and repeat purchase behaviour.")

    top_customers_df = utils.run_query(queries.get_top_customers_query(filters, limit=100))
    country_df       = utils.run_query(queries.get_customers_by_country_query(filters))
    city_df          = utils.run_query(queries.get_customers_by_city_query(filters))
    repeat_df        = utils.run_query(queries.get_repeat_customers_query(filters))
    spend_df         = utils.run_query(queries.get_average_spend_per_customer_query(filters))
    new_customers_df = utils.run_query(queries.get_new_customers_query(filters))

    kpi_df = utils.run_query(queries.get_kpi_query(filters))
    if not kpi_df.empty:
        kpi = kpi_df.iloc[0]
        top_country = country_df.iloc[0]["COUNTRY"] if not country_df.empty else "—"
        kpis = [
            ("Total Customers", utils.format_integer(kpi["TOTAL_CUSTOMERS"]), "groups", "#fff5f2"),
            ("Repeat Buyers",     str(len(repeat_df)),                        "repeat", "#f0fdf4"),
            ("Avg Order Value",   utils.format_currency(kpi["AVERAGE_ORDER_VALUE"]), "credit_card", "#eff6ff"),
            ("Top Country",       top_country,                              "public", "#fdf4ff"),
        ]
        pills_html = "<div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:24px;'>"
        for label, val, icon_name, bg in kpis:
            pills_html += f"""
            <div style='background:#fff;border-radius:16px;padding:16px 18px;
                        border:1.5px solid {BORDER};flex:1;min-width:130px;'>
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;'>
                    {page_ui.icon_in_box(icon_name, bg)}
                    <div style='font-size:11px;color:{MUTED};font-weight:600;text-transform:uppercase;
                                letter-spacing:0.06em;'>{label}</div>
                </div>
                <div style='font-size:22px;font-weight:800;color:{DARK};'>{val}</div>
            </div>"""
        pills_html += "</div>"
        st.markdown(pills_html, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Top Customers",
        "Geography",
        "Growth",
        "Repeat & Spend",
    ])

    with tab1:
        col_list, col_chart = st.columns([1, 1.4], gap="large")
        with col_list:
            page_ui.section_header("Customer Leaderboard", "Ranked by lifetime value")
            if not top_customers_df.empty:
                rows_html = f"<div style='background:#fff;border-radius:16px;padding:16px;border:1.5px solid {BORDER};'>"
                for rank, (_, row) in enumerate(top_customers_df.head(10).iterrows(), 1):
                    rows_html += _customer_row(
                        rank,
                        str(row.get("CUSTOMER_NAME", "—")),
                        str(row.get("COUNTRY", "—")),
                        int(row.get("ORDER_COUNT", 0)),
                        float(row.get("LIFETIME_VALUE", 0)),
                    )
                rows_html += "</div>"
                st.markdown(rows_html, unsafe_allow_html=True)
            else:
                st.info("No customer data.")
        with col_chart:
            page_ui.section_header("Lifetime Value Chart")
            if not top_customers_df.empty:
                top10 = top_customers_df.head(10)
                fig = go.Figure(go.Bar(
                    y=top10["CUSTOMER_NAME"],
                    x=top10["LIFETIME_VALUE"],
                    orientation="h",
                    marker=dict(
                        color=top10["LIFETIME_VALUE"],
                        colorscale=[[0, "#fff5f2"], [1, ORANGE]],
                        showscale=False,
                        line_width=0,
                    ),
                    text=top10["LIFETIME_VALUE"].apply(lambda v: f"${v:,.0f}"),
                    textposition="outside",
                    textfont=dict(size=10, color=MUTED),
                ))
                _chart_layout(fig, 380)
                fig.update_layout(showlegend=False, xaxis=dict(tickformat="~s", tickprefix="$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="cust_ltv")
        page_ui.section_title("Full Customer Table")
        if not top_customers_df.empty:
            st.dataframe(
                top_customers_df.rename(columns={
                    "CUSTOMER_NAME": "Customer", "EMAIL": "Email", "CITY": "City",
                    "COUNTRY": "Country", "ORDER_COUNT": "Orders",
                    "LIFETIME_VALUE": "Lifetime Value", "AVERAGE_ORDER_VALUE": "Avg Order Value",
                }),
                use_container_width=True,
                hide_index=True,
            )

    with tab2:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            page_ui.section_header("Customers by Country")
            if not country_df.empty:
                palette = [ORANGE if i == 0 else DARK if i == 1 else BLUE if i == 2 else MUTED
                           for i in range(len(country_df))]
                fig = go.Figure(go.Bar(
                    y=country_df["COUNTRY"],
                    x=country_df["CUSTOMER_COUNT"],
                    orientation="h",
                    marker_color=palette,
                    marker_line_width=0,
                ))
                _chart_layout(fig, 360)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="cust_country")
            else:
                st.info("No geography data.")
        with c2:
            page_ui.section_header("Top 20 Cities")
            if not city_df.empty:
                top_cities = city_df.head(15)
                fig = go.Figure(go.Bar(
                    y=top_cities["CITY"],
                    x=top_cities["CUSTOMER_COUNT"],
                    orientation="h",
                    marker=dict(
                        color=top_cities["CUSTOMER_COUNT"],
                        colorscale=[[0, "#fff5f2"], [1, ORANGE]],
                        showscale=False,
                        line_width=0,
                    ),
                ))
                _chart_layout(fig, 360)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="cust_city")
            else:
                st.info("No city data.")

    with tab3:
        page_ui.section_header("New Customers per Month", "Monthly signup velocity from DIM_CUSTOMERS")
        if not new_customers_df.empty:
            if not pd.api.types.is_datetime64_any_dtype(new_customers_df["MONTH"]):
                new_customers_df["MONTH"] = pd.to_datetime(new_customers_df["MONTH"], errors="coerce")
            new_customers_df["MONTH"] = new_customers_df["MONTH"].dt.to_period("M").dt.to_timestamp()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=new_customers_df["MONTH"],
                y=new_customers_df["NEW_CUSTOMERS"],
                mode="lines+markers",
                line=dict(color=ORANGE, width=3),
                marker=dict(size=7, color=ORANGE, line=dict(color="#fff", width=2)),
                fill="tozeroy",
                fillcolor="rgba(255,92,53,0.10)",
                name="New Customers",
            ))
            _chart_layout(fig, 340)
            fig.update_layout(yaxis=dict(title="New Customers"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="cust_growth")
        else:
            st.info("No signup data available.")

    with tab4:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            page_ui.section_header("Repeat Customers", "Customers with more than 1 order")
            if not repeat_df.empty:
                st.dataframe(
                    repeat_df.rename(columns={
                        "CUSTOMER_NAME": "Customer", "COUNTRY": "Country",
                        "ORDER_COUNT": "Orders", "LIFETIME_VALUE": "Lifetime Value",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No repeat customers found.")
        with c2:
            page_ui.section_header("Average Spend Per Customer")
            if not spend_df.empty:
                top_spend = spend_df.head(15)
                fig = go.Figure(go.Bar(
                    y=top_spend["CUSTOMER_NAME"],
                    x=top_spend["AVERAGE_SPEND"],
                    orientation="h",
                    marker_color=DARK,
                    marker_line_width=0,
                ))
                _chart_layout(fig, 340)
                fig.update_layout(showlegend=False, xaxis=dict(tickformat="~s", tickprefix="$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="cust_spend")
            else:
                st.info("No spend data.")

        if not top_customers_df.empty:
            search = st.text_input("Search customers", placeholder="Customer name or email…", key="cust_search")
            if search:
                q = search.strip()
                filtered = top_customers_df[
                    top_customers_df["CUSTOMER_NAME"].str.contains(q, case=False, na=False, regex=False) |
                    top_customers_df["EMAIL"].str.contains(q, case=False, na=False, regex=False)
                ]
                page_ui.section_title("Search Results")
                if filtered.empty:
                    st.info("No matching customers found. Try a broader name or email fragment.")
                else:
                    st.dataframe(filtered, use_container_width=True, hide_index=True)
