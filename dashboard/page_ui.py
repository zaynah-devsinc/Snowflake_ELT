"""Shared Streamlit UI helpers (no raw HTML wrappers — avoids stray </div> text)."""

from __future__ import annotations

import streamlit as st


def icon(name: str, size: int = 20, color: str | None = None) -> str:
    style = f"font-size:{size}px;line-height:1;"
    if color:
        style += f"color:{color};"
    return f'<span class="material-symbols-outlined" style="{style}">{name}</span>'


def icon_in_box(name: str, bg: str = "#f5f6fa", size: int = 18, color: str | None = None) -> str:
    return (
        f"<div style='background:{bg};border-radius:8px;width:28px;height:28px;"
        f"display:flex;align-items:center;justify-content:center;'>"
        f"{icon(name, size, color)}</div>"
    )


def section_header(title: str, subtitle: str = "") -> None:
    st.subheader(title, anchor=False, divider=False)
    if subtitle:
        st.caption(subtitle)


def section_title(title: str) -> None:
    st.markdown(f"**{title}**")


def render_dashboard_guide() -> None:
    with st.expander("About this dashboard — metrics, charts, and why they matter", expanded=False):
        st.markdown(
            """
This dashboard reads from the **ELT warehouse marts** built in this project:
`FACT_ORDERS` (order line items), `DIM_CUSTOMERS`, and `DIM_PRODUCTS`. Every number and chart
is computed from those tables — there are no placeholder or synthetic metrics.

---

#### Overview page

| Metric / view | Source | Why it is shown |
|---|---|---|
| **Total Revenue** | `SUM(net_sales)` on `FACT_ORDERS` | Headline business outcome after discounts |
| **Total Orders** | `COUNT(DISTINCT order_id)` | Volume of transactions, separate from line-item count |
| **Total Customers** | `COUNT(DISTINCT customer_id)` | Size of the active buyer base |
| **Total Products** | `COUNT(DISTINCT product_id)` | Breadth of catalogue sold |
| **Avg Order Value** | Revenue ÷ distinct orders | Typical transaction size |
| **Monthly Revenue & Orders** (line chart) | Monthly `net_sales` + order count | Spot seasonality and link revenue growth to order volume |
| **Revenue by Category** (bar chart) | `net_sales` grouped by `DIM_PRODUCTS.category` | Shows which product lines drive sales |
| **Order Status Distribution** (donut) | Line counts by `status` | Operational health — completed vs pending vs cancelled |
| **Recent / All Orders** (table) | Latest rows from `FACT_ORDERS` with customer & product joins | Drill-down into individual transactions |

---

#### Sales page

| Chart | Source | Why a graph |
|---|---|---|
| Revenue by Category | Category-level `net_sales` | Bar chart compares discrete categories side-by-side |
| Revenue by Brand | Brand-level `net_sales` | Identifies top-performing brands |
| Top Products | Product revenue & units sold | Horizontal bar ranks many SKUs legibly |
| Payment Method (pie) | Revenue share by `payment_method` | Part-to-whole view suits payment mix |
| Discount by Category | `AVG(discount_percent)` per category | Highlights where discounting erodes margin |
| Monthly / Daily trends | Time-series `net_sales` | Line charts show direction and volatility over time |

---

#### Customers page

| Metric / chart | Source | Why it is shown |
|---|---|---|
| Total Customers | Distinct buyers in `FACT_ORDERS` | Ground-truth customer count from orders |
| Repeat Buyers | Customers with >1 distinct order | Loyalty / retention signal |
| Top Customers (LTV) | `SUM(net_sales)` per customer | Ranked bar + table for highest-value accounts |
| Customers by Country / City | Distinct customers by geography | Bar charts compare regions |
| New Customers per Month | `signup_date` on `DIM_CUSTOMERS` | Signup velocity over time |
| Repeat & Avg Spend tables | Per-customer order stats from `FACT_ORDERS` | Behaviour detail for retention analysis |

---

#### Products page

| Metric / chart | Source | Why it is shown |
|---|---|---|
| Total Products / Categories | Distinct products & category count | Catalogue scope |
| Low Stock Items | `stock` from `DIM_PRODUCTS` where ≤ 20 | Inventory risk flag |
| Top Products by Revenue | Product-level `net_sales` | Best sellers |
| Category Distribution (pie) | Product count per category | Catalogue composition |
| Stock Levels (table) | `DIM_PRODUCTS.stock` sorted ascending | Surfaces items needing replenishment first |
| Average Selling Price | `net_sales ÷ quantity` per product | Effective price after discounts |
            """
        )
