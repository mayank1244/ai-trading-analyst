import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dashboard.backend_starter import ensure_backend_running
ensure_backend_running()

import requests
import pandas as pd
import streamlit as st
from dashboard.components.cards import recommendation_card

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Intraday Scanner | AI Trading Analyst", layout="wide")
st.title("⚡ Intraday Scanner")
st.caption("Real-time Intraday Bullish Setups & High-Potential Penny Stocks (₹5 – ₹100) Expected to Rise in Next 1 Hour")

if st.button("⚡ Run Intraday Market Scan", use_container_width=True):
    with st.spinner("Scanning NSE universe for intraday momentum & penny stock surges..."):
        try:
            resp = requests.get(f"{API_BASE}/scanner/run", timeout=45)
            if resp.status_code == 200:
                st.session_state["scan_data"] = resp.json()
                st.success("Intraday Scan completed!")
            else:
                st.error("Scanner failed.")
        except Exception as exc:
            st.error(f"Error running scan: {exc}")

scan_data = st.session_state.get("scan_data", {})
intraday_stocks = scan_data.get("intraday_stocks", [])
intraday_penny_stocks = scan_data.get("intraday_penny_stocks", [])

def add_stock_to_watchlist(symbol: str, holding_period: str = "Intraday"):
    """Helper to add stock to watchlist via API."""
    try:
        resp = requests.post(
            f"{API_BASE}/watchlist",
            json={"symbol": symbol, "holding_period": holding_period, "notes": "Added from Intraday Scanner"},
        )
        if resp.status_code == 200:
            st.toast(f"✅ {symbol} added to Watchlist!", icon="⭐")
        else:
            st.warning(f"Could not add {symbol}: {resp.json().get('detail', 'Already in watchlist')}")
    except Exception as exc:
        st.error(f"Error adding {symbol}: {exc}")

tab1, tab2 = st.tabs([
    "🔥 Top 20 Intraday Bullish Stocks",
    "🚀 Top Intraday Penny Stocks (₹5 – ₹100 | Next 1-Hour Rise Potential)",
])

with tab1:
    st.subheader("🔥 Top 20 Intraday Bullish Stocks")
    st.caption("Criteria: Bullish momentum, high volume, tight intraday Stop Loss (~0.8%) & Target (~1.2%–2.5%)")

    if not intraday_stocks:
        st.info("Click '⚡ Run Intraday Market Scan' above to populate this list.")
    else:
        # Bulk Addition Bar
        symbols = [s.get("symbol") for s in intraday_stocks if s.get("symbol")]
        col_sel, col_act = st.columns([4, 1])
        with col_sel:
            selected_bulk = st.multiselect("Select stocks to bulk add to Watchlist:", options=symbols, key="bulk_sel_intraday", placeholder="Choose intraday stocks...")
        with col_act:
            st.write("")
            st.write("")
            if st.button("⭐ Add Selected", key="bulk_btn_intraday"):
                if selected_bulk:
                    for sym in selected_bulk:
                        add_stock_to_watchlist(sym)
                else:
                    st.info("Select at least one stock first.")

        st.markdown("---")

        for stock in intraday_stocks:
            sym = stock.get("symbol", "")
            c1, c2 = st.columns([5, 1])
            with c1:
                recommendation_card(stock)
            with c2:
                st.write("")
                st.write("")
                if st.button("➕ Watchlist", key=f"add_btn_intraday_{sym}"):
                    add_stock_to_watchlist(sym)

with tab2:
    st.subheader("🚀 Potential Penny Stocks (Price ₹5 – ₹100)")
    st.caption("Criteria: Stocks priced between ₹5 and ₹100 showing high volume surge & price raise momentum for the next 1 hour.")

    if not intraday_penny_stocks:
        st.info("Click '⚡ Run Intraday Market Scan' above to scan for potential 1-hour penny stock setups.")
    else:
        penny_symbols = [s.get("symbol") for s in intraday_penny_stocks if s.get("symbol")]
        col_sel, col_act = st.columns([4, 1])
        with col_sel:
            selected_bulk_penny = st.multiselect("Select penny stocks to bulk add to Watchlist:", options=penny_symbols, key="bulk_sel_penny", placeholder="Choose penny stocks...")
        with col_act:
            st.write("")
            st.write("")
            if st.button("⭐ Add Selected", key="bulk_btn_penny"):
                if selected_bulk_penny:
                    for sym in selected_bulk_penny:
                        add_stock_to_watchlist(sym, holding_period="Intraday (1 Hour Move)")
                else:
                    st.info("Select at least one penny stock first.")

        st.markdown("---")

        for stock in intraday_penny_stocks:
            sym = stock.get("symbol", "")
            c1, c2 = st.columns([5, 1])
            with c1:
                recommendation_card(stock)
            with c2:
                st.write("")
                st.write("")
                if st.button("➕ Watchlist", key=f"add_btn_penny_{sym}"):
                    add_stock_to_watchlist(sym, holding_period="Intraday (1 Hour Move)")
