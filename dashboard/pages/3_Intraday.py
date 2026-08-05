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

# Fallback: If API returned output without intraday_penny_stocks, run directly via scanner module
if not intraday_penny_stocks and intraday_stocks:
    try:
        import asyncio
        from app.scanner.market_scanner import market_scanner
        loop = asyncio.new_event_loop()
        res = loop.run_until_complete(market_scanner.scan_universe())
        intraday_penny_stocks = [
            {
                "symbol": r.symbol,
                "name": r.name,
                "sector": r.sector,
                "current_price": r.current_price,
                "change_pct": r.change_pct,
                "volume": r.volume,
                "quant_score": r.quant_score,
                "recommendation": r.recommendation,
                "confidence": r.confidence,
                "entry_price": r.entry_price,
                "stop_loss": r.stop_loss,
                "target_1": r.target_1,
                "target_2": r.target_2,
                "risk_reward": r.risk_reward,
                "holding_period": r.holding_period,
                "bullish_signals": r.bullish_signals,
                "bearish_signals": r.bearish_signals,
                "is_breakout": r.is_breakout,
                "is_near_support": r.is_near_support,
                "is_high_volume": r.is_high_volume,
                "pattern_name": r.pattern_name,
                "technical_summary": r.technical_summary,
            }
            for r in res.intraday_penny_stocks
        ]
    except Exception:
        pass

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
    st.markdown(
        """
        <div style="background-color: #2b0b0b; border: 2px solid #ef4444; border-radius: 8px; padding: 14px; margin-bottom: 20px;">
            <h3 style="color: #ef4444; margin: 0;">🔴 Day Potential Penny Stocks List (Price Range: ₹5 – ₹100)</h3>
            <p style="color: #fca5a5; margin: 6px 0 0 0; font-size: 14px; font-weight: 500;">
                High-potential intraday penny stocks priced between ₹5 and ₹100 showing volume surges & price raise momentum.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not intraday_penny_stocks:
        st.info("Click '⚡ Run Intraday Market Scan' above to scan for potential penny stock setups.")
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
