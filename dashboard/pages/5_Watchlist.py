"""Watchlist Page with custom timetable table."""

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pandas as pd
import requests
import streamlit as st

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Watchlist | AI Trading Analyst", layout="wide")
st.title("⭐ Watchlist")
st.caption("Track your saved stocks with snapshot entry prices and live market signals.")

col_input, col_btn = st.columns([3, 1])
with col_input:
    new_symbol = st.text_input("Enter Stock Symbol to Add (e.g. RELIANCE, HINDALCO):", value="").upper().strip()
with col_btn:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    add_clicked = st.button("➕ Add to Watchlist", use_container_width=True)

if add_clicked and new_symbol:
    try:
        resp = requests.post(f"{API_BASE}/watchlist", json={"symbol": new_symbol, "notes": "Added from UI"}, timeout=10)
        if resp.status_code == 200:
            st.success(f"Added {new_symbol} to watchlist!")
            st.rerun()
        else:
            st.warning(resp.json().get("detail", "Error adding stock"))
    except Exception as exc:
        st.error(f"Error: {exc}")

st.markdown("---")
st.subheader("📋 Saved Watchlist Portfolio")

try:
    resp = requests.get(f"{API_BASE}/watchlist", timeout=30)
    watchlist_items = resp.json() if resp.status_code == 200 else []
except Exception as exc:
    st.error(f"Failed to fetch watchlist: {exc}")
    watchlist_items = []

def format_holding_compact(period: str) -> str:
    if not period:
        return "3D-5D"
    p = str(period).lower().strip()
    if "intraday" in p:
        return "Intraday"
    if "3-5" in p or "3-5d" in p:
        return "3D-5D"
    if "1-2" in p or "1-2w" in p:
        return "1W-2W"
    if "1-3" in p or "1-3m" in p:
        return "1M-3M"
    return period.replace("days", "D").replace("day", "D").replace("weeks", "W").replace("week", "W").replace("months", "M").replace("month", "M").replace(" ", "")

if watchlist_items:
    table_data = []
    for item in watchlist_items:
        sym = item.get("symbol", "")
        w_val = item.get("watchlist_price")
        c_val = item.get("current_price")
        b_val = item.get("bullish_pct")
        t_val = item.get("target_price")
        s_val = item.get("stop_loss")

        w_price = float(w_val) if w_val is not None else 0.0
        c_price = float(c_val) if c_val is not None else 0.0
        bull_pct = float(b_val) if b_val is not None else 50.0
        holding = item.get("holding_period") or "3-5 days"
        target = float(t_val) if t_val is not None else 0.0
        sl = float(s_val) if s_val is not None else 0.0

        date_str = item.get("added_at_date") or ""
        if not date_str and item.get("added_at"):
            try:
                dt = pd.to_datetime(item.get("added_at"))
                date_str = dt.strftime("%d/%m/%Y")
            except Exception:
                date_str = ""

        compact_holding = format_holding_compact(holding)
        price_meta = f" ({date_str} {compact_holding})" if date_str else f" ({compact_holding})"
        watchlist_price_str = f"₹{w_price:,.2f}{price_meta}"

        table_data.append(
            {
                "Stocks": sym,
                "Watchlist Price": watchlist_price_str,
                "Current Price": f"₹{c_price:,.2f}",
                "Bullies percentage": f"{bull_pct:.0f}%",
                "holding period": holding,
                "target Price": f"₹{target:,.2f}",
                "Stop Loss": f"₹{sl:,.2f}",
            }
        )

    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**Manage Items**")
    remove_cols = st.columns(min(len(watchlist_items), 5))
    for idx, item in enumerate(watchlist_items):
        sym = item.get("symbol")
        col = remove_cols[idx % 5]
        with col:
            if st.button(f"🗑️ Remove {sym}", key=f"del_{sym}"):
                requests.delete(f"{API_BASE}/watchlist/{sym}", timeout=5)
                st.rerun()
else:
    st.info("Watchlist is empty. Add a stock symbol above to start tracking.")
