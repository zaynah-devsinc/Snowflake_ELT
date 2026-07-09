from __future__ import annotations

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
RED     = "#ef4444"
BLUE    = "#3b82f6"
PURPLE  = "#8b5cf6"
AMBER   = "#f59e0b"


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


def render(filters: dict) -> None:
    st.markdown("### Product Analytics")
    st.caption("Product performance, stock levels, pricing, and category breakdown.")

    top_products_df    = utils.run_query(queries.get_top_products_query(filters, limit=20))
    category_dist_df   = utils.run_query(queries.get_category_distribution_query(filters))
    stock_df           = utils.run_query(queries.get_stock_levels_query(filters))
    revenue_product_df = utils.run_query(queries.get_revenue_by_product_query(filters))
    average_price_df   = utils.run_query(queries.get_average_selling_price_query(filters))

    kpi_df = utils.run_query(queries.get_kpi_query(filters))
    if not kpi_df.empty:
        kpi = kpi_df.iloc[0]
        low_stock = len(stock_df[stock_df["STOCK"] <= 20]) if not stock_df.empty else 0
        top_product_rev = top_products_df.iloc[0]["NET_REVENUE"] if not top_products_df.empty else 0
        kpis = [
            ("Total Products", utils.format_integer(kpi["TOTAL_PRODUCTS"]), "inventory_2", "#fff5f2"),
            ("Categories",       str(len(category_dist_df)),                  "category", "#eff6ff"),
            ("Low Stock Items",  str(low_stock),                             "warning", "#fffbeb"),
            ("Top Product Rev",  f"${top_product_rev:,.0f}",                 "emoji_events", "#f0fdf4"),
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

    tab1, tab2, tab3 = st.tabs([
        "Top Products",
        "Category Breakdown",
        "Stock & Pricing",
    ])

    with tab1:
        page_ui.section_header("Top 20 Products by Revenue")
        if not top_products_df.empty:
            fig = go.Figure(go.Bar(
                y=top_products_df["PRODUCT_NAME"],
                x=top_products_df["NET_REVENUE"],
                orientation="h",
                marker=dict(
                    color=top_products_df["NET_REVENUE"],
                    colorscale=[[0, "#fff5f2"], [1, ORANGE]],
                    showscale=False,
                    line_width=0,
                ),
                text=top_products_df["NET_REVENUE"].apply(lambda v: f"${v:,.0f}"),
                textposition="outside",
                textfont=dict(size=9, color=MUTED),
            ))
            _chart_layout(fig, height=480)
            fig.update_layout(showlegend=False, xaxis=dict(tickformat="~s", tickprefix="$"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="prod_top")
            page_ui.section_title("Product Detail")
            st.dataframe(
                top_products_df.rename(columns={
                    "PRODUCT_NAME": "Product", "CATEGORY": "Category",
                    "BRAND": "Brand", "ITEMS_SOLD": "Units Sold", "NET_REVENUE": "Revenue",
                }),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No product data for the selected filters.")

    with tab2:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            page_ui.section_header("Category Distribution (by product count)")
            if not category_dist_df.empty:
                palette = [ORANGE, DARK, BLUE, GREEN, PURPLE, AMBER]
                fig = go.Figure(go.Pie(
                    labels=category_dist_df["CATEGORY"],
                    values=category_dist_df["PRODUCT_COUNT"],
                    hole=0.52,
                    marker_colors=palette[:len(category_dist_df)],
                    textinfo="label+percent",
                    textfont_size=11,
                ))
                _chart_layout(fig, 340)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="prod_cat_pie")
            else:
                st.info("No category data.")
        with c2:
            page_ui.section_header("Revenue by Product (Top 20)")
            if not revenue_product_df.empty:
                top20 = revenue_product_df.head(20)
                colors = [ORANGE if i % 2 == 0 else DARK for i in range(len(top20))]
                fig = go.Figure(go.Bar(
                    x=top20["PRODUCT_NAME"],
                    y=top20["NET_REVENUE"],
                    marker_color=colors,
                    marker_line_width=0,
                ))
                _chart_layout(fig, 340)
                fig.update_layout(showlegend=False,
                                  xaxis=dict(tickangle=-35, tickfont=dict(size=8)),
                                  yaxis=dict(tickformat="~s", tickprefix="$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="prod_rev_bar")
            else:
                st.info("No revenue data.")

    with tab3:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            page_ui.section_header("Stock Levels", "Sorted from lowest to highest")
            if not stock_df.empty:
                st.dataframe(
                    stock_df.rename(columns={
                        "PRODUCT_NAME": "Product", "CATEGORY": "Category",
                        "BRAND": "Brand", "STOCK": "Stock",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No stock data.")
        with c2:
            page_ui.section_header("Average Selling Price", "Revenue per unit sold")
            if not average_price_df.empty:
                top_price = average_price_df.head(15)
                fig = go.Figure(go.Bar(
                    y=top_price["PRODUCT_NAME"],
                    x=top_price["AVERAGE_SELLING_PRICE"],
                    orientation="h",
                    marker=dict(
                        color=top_price["AVERAGE_SELLING_PRICE"],
                        colorscale=[[0, "#fff5f2"], [1, ORANGE]],
                        showscale=False,
                        line_width=0,
                    ),
                    text=top_price["AVERAGE_SELLING_PRICE"].apply(lambda v: f"${v:,.2f}"),
                    textposition="outside",
                    textfont=dict(size=9, color=MUTED),
                ))
                _chart_layout(fig, 380)
                fig.update_layout(showlegend=False, xaxis=dict(tickformat="~s", tickprefix="$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="prod_avg_price")
            else:
                st.info("No pricing data.")

        if not top_products_df.empty:
            search = st.text_input("Search products", placeholder="Product name or category…", key="product_search")
            if search:
                q = search.strip().lower()
                filtered = top_products_df[
                    top_products_df["PRODUCT_NAME"].str.lower().str.contains(q, na=False) |
                    top_products_df["CATEGORY"].str.lower().str.contains(q, na=False)
                ]
                if not filtered.empty:
                    page_ui.section_title(f"Search Results ({len(filtered)})")
                    st.dataframe(
                        filtered.rename(columns={
                            "PRODUCT_NAME": "Product", "CATEGORY": "Category",
                            "BRAND": "Brand", "ITEMS_SOLD": "Units Sold", "NET_REVENUE": "Revenue",
                        }),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info(f"No products match '{search}'.")
