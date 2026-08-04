import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dashboard.backend_starter import ensure_backend_running
ensure_backend_running()

import requests
import streamlit as st
from dashboard.components.cards import recommendation_card
from dashboard.components.charts import score_radar_chart

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Stock Analysis | AI Trading Analyst", layout="wide")
st.title("📈 Stock Analysis")

symbol = st.text_input("Enter NSE Stock Symbol (e.g. RELIANCE, TCS, INFY):", value="RELIANCE").upper().strip()

col_btn, col_chk = st.columns([1, 3])
with col_btn:
    analyze_btn = st.button("🔍 Analyze Stock", use_container_width=True)
with col_chk:
    skip_ai = st.checkbox("Quick Mode (Skip AI reasoning for faster result)", value=False)

if analyze_btn or symbol:
    with st.spinner(f"Analyzing {symbol}..."):
        try:
            resp = requests.get(f"{API_BASE}/analysis/{symbol}?skip_ai={skip_ai}", timeout=25)
            if resp.status_code == 200:
                rec = resp.json()
                st.session_state[f"rec_{symbol}"] = rec
            else:
                st.error(f"Analysis failed for {symbol}.")
        except Exception as exc:
            st.error(f"Error fetching analysis: {exc}")

rec = st.session_state.get(f"rec_{symbol}")

if rec:
    col_card, col_wl = st.columns([5, 1])
    with col_card:
        recommendation_card(rec)
    with col_wl:
        st.write("")
        st.write("")
        if st.button("➕ Add to Watchlist", key=f"wl_analysis_{symbol}"):
            try:
                resp = requests.post(f"{API_BASE}/watchlist", json={"symbol": symbol, "notes": "Added from Analysis"})
                if resp.status_code == 200:
                    st.toast(f"✅ {symbol} added to Watchlist!", icon="⭐")
                else:
                    st.warning(f"Could not add {symbol}: {resp.json().get('detail', 'Already in watchlist')}")
            except Exception as exc:
                st.error(f"Error adding {symbol}: {exc}")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Radar Component Breakdown")
        scores = {
            "Trend": rec.get("trend_score", 50),
            "Momentum": rec.get("momentum_score", 50),
            "Volume": rec.get("volume_score", 50),
            "S/R": rec.get("sr_score", 50),
            "Pattern": rec.get("pattern_score", 50),
            "Sector": rec.get("sector_score", 50),
            "Market": rec.get("market_score", 50),
            "Volatility": rec.get("volatility_score", 50),
        }
        fig_radar = score_radar_chart(scores)
        st.plotly_chart(fig_radar, use_container_width=True)

    with col2:
        st.subheader("Signals Detected")
        st.write("🟢 **Bullish Signals:**")
        for s in rec.get("bullish_signals", []):
            st.markdown(f"- {s}")

        st.write("🔴 **Bearish Signals:**")
        for s in rec.get("bearish_signals", []):
            st.markdown(f"- {s}")

    st.markdown("---")
    st.subheader("Detailed Technical & AI Explanation")
    st.markdown(rec.get("detailed_explanation", "No explanation available."))
