import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dashboard.backend_starter import ensure_backend_running
ensure_backend_running()

from dashboard.components.autorefresh import render_autorefresh_sidebar
render_autorefresh_sidebar()

import requests
import pandas as pd
import streamlit as st
from dashboard.components.cards import recommendation_card

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Market Scanner | AI Trading Analyst", layout="wide")
st.title("🔍 Market Scanner")
st.caption("Scan entire NSE universe for high-probability setups & add directly to your Watchlist.")

if st.button("⚡ Run Full Market Scan", use_container_width=True):
    with st.spinner("Scanning NSE stocks with 18+ indicators..."):
        try:
            resp = requests.get(f"{API_BASE}/scanner/run", timeout=30)
            if resp.status_code == 200:
                st.session_state["scan_data"] = resp.json()
                st.success("Scan completed!")
            else:
                st.error("Scanner failed.")
        except Exception as exc:
            st.error(f"Error running scan: {exc}")

scan_data = st.session_state.get("scan_data", {})

tab1, tab_risk, tab2, tab3, tab4 = st.tabs(
    ["Top 20 Buy", "🔥 Top 20 Risk Buy (₹100–₹5000 | >60% Bullish | 3-5 Days)", "Top 20 Sell", "Breakouts", "Momentum"]
)

def add_stock_to_watchlist(symbol: str, holding_period: str = "3-5 days"):
    """Helper to add stock to watchlist via API."""
    try:
        resp = requests.post(
            f"{API_BASE}/watchlist",
            json={"symbol": symbol, "holding_period": holding_period, "notes": "Added from Scanner"},
        )
        if resp.status_code == 200:
            st.toast(f"✅ {symbol} added to Watchlist!", icon="⭐")
        else:
            st.warning(f"Could not add {symbol}: {resp.json().get('detail', 'Already in watchlist')}")
    except Exception as exc:
        st.error(f"Error adding {symbol}: {exc}")

def render_stock_list(stocks: list, category_id: str):
    """Renders stocks list with individual and bulk Watchlist action buttons."""
    if not stocks:
        st.info("Click 'Run Full Market Scan' to populate this scanner list.")
        return

    # Bulk addition bar
    symbols = [s.get("symbol") for s in stocks if s.get("symbol")]
    col_sel, col_act = st.columns([4, 1])
    with col_sel:
        selected_bulk = st.multiselect("Select stocks to bulk add:", options=symbols, key=f"bulk_sel_{category_id}", placeholder="Choose stocks to add...")
    with col_act:
        st.write("") # layout padding
        st.write("")
        if st.button("⭐ Add Selected", key=f"bulk_btn_{category_id}"):
            if selected_bulk:
                for sym in selected_bulk:
                    add_stock_to_watchlist(sym)
            else:
                st.info("Select at least one stock first.")

    st.markdown("---")

    # Individual Stock Cards with "+ Add to Watchlist" button
    for stock in stocks:
        sym = stock.get("symbol", "")
        c1, c2 = st.columns([5, 1])
        with c1:
            recommendation_card(stock)
        with c2:
            st.write("")
            st.write("")
            if st.button("➕ Watchlist", key=f"add_btn_{category_id}_{sym}"):
                add_stock_to_watchlist(sym)

with tab1:
    top_buys = scan_data.get("top_buy", [])
    render_stock_list(top_buys, "top_buy")

with tab_risk:
    top_risk = scan_data.get("top_risk_buy", [])
    if top_risk:
        st.caption("Filtered: Price ₹100–₹5,000 | Bullish Chance > 60% | Holding Period: 3–5 Days")
    render_stock_list(top_risk, "top_risk_buy")

with tab2:
    top_sells = scan_data.get("top_sell", [])
    render_stock_list(top_sells, "top_sell")

with tab3:
    breakouts = scan_data.get("breakout_stocks", [])
    render_stock_list(breakouts, "breakout")

with tab4:
    mom = scan_data.get("momentum_stocks", [])
    render_stock_list(mom, "momentum")

