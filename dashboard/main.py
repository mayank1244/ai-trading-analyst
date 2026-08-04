"""Streamlit Main Dashboard Homepage."""

import requests
import streamlit as st
from dashboard.components.cards import index_card, recommendation_card
from dashboard.components.charts import sector_heatmap

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="AI Trading Analyst | NSE/BSE India",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d1117 !important;
    color: #c9d1d9;
}
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d;
}
h1, h2, h3 { color: #e6edf3 !important; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("📈 AI Trading Analyst — Indian Stock Market")
st.caption("Hybrid Decision Engine (70% Quant + 30% AI) | Non-Execution Research Platform")

# Index strip
col1, col2, col3, col4 = st.columns(4)

try:
    resp = requests.get(f"{API_BASE}/market/indices", timeout=5)
    indices = resp.json() if resp.status_code == 200 else []
except Exception:
    indices = []

default_indices = [
    {"name": "NIFTY50", "value": 24200.0, "change": 120.5, "change_pct": 0.5},
    {"name": "SENSEX", "value": 79500.0, "change": 350.0, "change_pct": 0.44},
    {"name": "BANKNIFTY", "value": 51800.0, "change": -150.0, "change_pct": -0.29},
    {"name": "VIX", "value": 15.2, "change": -0.4, "change_pct": -2.5},
]

display_indices = indices if indices else default_indices

for col, idx in zip([col1, col2, col3, col4], display_indices[:4]):
    with col:
        index_card(idx["name"], idx["value"], idx["change"], idx["change_pct"])

st.markdown("---")

# Main columns
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("💡 Top Recommended Opportunities")
    try:
        scan_resp = requests.get(f"{API_BASE}/scanner/run", timeout=20)
        scan_data = scan_resp.json() if scan_resp.status_code == 200 else {}
        top_buys = scan_data.get("top_buy", [])
    except Exception:
        top_buys = []

    if top_buys:
        for item in top_buys[:5]:
            recommendation_card(item)
    else:
        st.info("Run the Market Scanner to discover high-probability opportunities.")

with right_col:
    st.subheader("🗺️ Sector Performance")
    sector_data = {"IT": 75.0, "Banking": 60.0, "Auto": 80.0, "Pharma": 45.0, "Energy": 65.0, "FMCG": 55.0}
    fig = sector_heatmap(sector_data)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("⚠️ **SEBI Compliance Disclaimer**: All recommendations are generated for paper research and educational purposes only. No orders are placed.")
