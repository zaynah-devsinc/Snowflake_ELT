import streamlit as st
from datetime import datetime

import pages.customers as customers_page
import pages.forecast as forecast_page
import pages.overview as overview_page
import pages.products as products_page
import pages.sales as sales_page

PAGE_CONFIG = {
    "Overview":   {"module": overview_page},
    "Sales":      {"module": sales_page},
    "Customers":  {"module": customers_page},
    "Products":   {"module": products_page},
    "Forecast":   {"module": forecast_page},
}

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

html, body, .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #f5f6fa !important;
    color: #1a1d23 !important;
}

/* ── Hide sidebar entirely ── */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── Hide default chrome ── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── Main content full width ── */
.main .block-container {
    padding: 0 32px 32px 32px !important;
    max-width: none !important;
}

/* ── Top nav bar ── */
.top-nav {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 16px 0 20px 0;
}
.top-nav-logo {
    width: 36px; height: 36px;
    background: #FF5C35;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    color: #fff;
    margin-right: 16px;
}
.top-nav-logo .material-symbols-outlined {
    font-family: 'Material Symbols Outlined';
    font-size: 22px;
    line-height: 1;
}

.material-symbols-outlined {
    font-family: 'Material Symbols Outlined';
    font-weight: normal;
    font-style: normal;
    font-size: 20px;
    line-height: 1;
    display: inline-block;
    -webkit-font-smoothing: antialiased;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 1.5px solid #eef0f7 !important;
    border-radius: 0 !important;
    padding: 0 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 0 !important;
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 10px 18px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1.5px !important;
    height: auto !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #1a1d23 !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #FF5C35 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #FF5C35 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 20px !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1.5px solid #eef0f7 !important;
}

/* ── Info box ── */
.stAlert { border-radius: 12px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f0f2f8; border-radius: 3px; }
::-webkit-scrollbar-thumb { background: #d0d5e8; border-radius: 3px; }
</style>
"""


def main():
    st.set_page_config(
        page_title="Snowflake ELT Dashboard",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    if "last_refresh" not in st.session_state:
        st.session_state["last_refresh"] = datetime.utcnow()

    # ── Top nav ──
    pages = list(PAGE_CONFIG.keys())
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = pages[0]

    nav_cols = st.columns([0.08] + [0.23] * len(pages))
    with nav_cols[0]:
        st.markdown(
            '<div class="top-nav-logo" style="margin-top:4px;">'
            '<span class="material-symbols-outlined">ac_unit</span></div>',
            unsafe_allow_html=True,
        )
    for i, p in enumerate(pages):
        with nav_cols[i + 1]:
            if st.button(p, key=f"nav_{p}", use_container_width=True):
                st.session_state["active_page"] = p
                st.rerun()

    st.markdown("<hr style='border:none;border-top:1.5px solid #eef0f7;margin:0 0 20px 0;'>", unsafe_allow_html=True)

    page_module = PAGE_CONFIG[st.session_state["active_page"]]["module"]
    page_module.render({})


if __name__ == "__main__":
    main()
