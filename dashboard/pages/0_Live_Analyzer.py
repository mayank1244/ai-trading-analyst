"""Live Stock Auto-Analyzer Streamlit Page."""

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dashboard.backend_starter import ensure_backend_running
ensure_backend_running()

import requests
import streamlit as st
import plotly.graph_objects as go

from dashboard.components.charts import live_analyzer_chart

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Live Stock Auto-Analyzer | AI Trading Analyst", layout="wide")

# Header & Live Streaming Badge
col_title, col_live = st.columns([3, 1])
with col_title:
    st.title("⚡ Live Stock Auto-Analyzer")
    st.caption("Live TradingView-style candlestick chart, automatic indicators (EMA 20/50, RSI, MACD, BB), pattern detection, & AI signal badge.")
with col_live:
    st.write("")
    st.markdown(
        """
        <div style="background-color: #064e3b; border: 1px solid #10b981; border-radius: 6px; padding: 8px 14px; text-align: center; margin-top: 10px;">
            <span style="height: 10px; width: 10px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 6px;"></span>
            <strong style="color: #a7f3d0; font-size: 13px; letter-spacing: 0.5px;">🟢 LIVE REAL-TIME FEED</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Search Bar & Timeframe Switcher
col_search, col_time = st.columns([3, 2])

with col_search:
    symbol_input = st.text_input(
        "🔎 Enter NSE/BSE Stock Symbol:",
        value=st.session_state.get("selected_symbol", "HDFCBANK"),
        placeholder="e.g. HDFCBANK, RELIANCE, RBA, INFY, TATAMOTORS",
        key="symbol_input_box",
    ).upper().strip()

with col_time:
    st.write("**Timeframe:**")
    tf_cols = st.columns(5)
    timeframes = ["1m", "5m", "15m", "1h", "1d"]
    selected_tf = st.session_state.get("selected_tf", "15m")

    for idx, tf in enumerate(timeframes):
        if tf_cols[idx].button(
            tf.upper(),
            key=f"tf_btn_{tf}",
            type="primary" if tf == selected_tf else "secondary",
            use_container_width=True,
        ):
            st.session_state["selected_tf"] = tf
            st.rerun()

timeframe = st.session_state.get("selected_tf", "15m")

# Quick Preset Buttons
st.write("Popular Stocks:")
preset_cols = st.columns(7)
presets = ["HDFCBANK", "RELIANCE", "INFY", "TATAMOTORS", "RBA", "SUZLON", "JPPOWER"]

for idx, p in enumerate(presets):
    if preset_cols[idx].button(p, key=f"preset_{p}", use_container_width=True):
        st.session_state["selected_symbol"] = p
        st.rerun()

symbol = symbol_input if symbol_input else "HDFCBANK"

# Continuous Real-Time Live Streaming Trigger (No timing selectors shown)
import time
last_stream = st.session_state.get("live_analyzer_stream_time", 0)
now = time.time()
if now - last_stream >= 5:
    st.session_state["live_analyzer_stream_time"] = now

# Fetch Data from Live Analyzer API
data = None
with st.spinner(f"Fetching live real-time {timeframe} OHLCV data & running indicators for {symbol}..."):
    try:
        resp = requests.get(f"{API_BASE}/live_analyzer/analyze/{symbol}?timeframe={timeframe}", timeout=30)
        if resp.status_code == 200:
            data = resp.json()
        else:
            st.error(f"Could not load live data for '{symbol}'. Detail: {resp.json().get('detail', 'API Error')}")
    except Exception as exc:
        st.error(f"Connection error to live analyzer backend: {exc}")

if data:
    # 1. Header Metrics & Signal Badge Bar
    cp = data.get("current_price", 0.0)
    chg = data.get("change_pct", 0.0)
    act = data.get("action", "HOLD")
    conf = data.get("confidence", 50.0)
    ts = data.get("timestamp", "")
    risk = data.get("risk_level", "MEDIUM")
    trend = data.get("trend_direction", "SIDEWAYS")

    badge_color = "#26a641" if "BUY" in act else "#ef4444" if "SELL" in act else "#eab308"
    trend_icon = "📈 Bullish" if "UP" in trend or "BULL" in trend else "📉 Bearish" if "DOWN" in trend or "BEAR" in trend else "➡️ Sideways"
    risk_color = "#26a641" if risk == "LOW" else "#eab308" if risk == "MEDIUM" else "#ef4444"

    mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)

    with mcol1:
        st.metric("Live Market Price", f"₹{cp:,.2f}", f"{chg:+.2f}%")
    with mcol2:
        st.markdown(
            f"""
            <div style="background-color: {badge_color}22; border: 2px solid {badge_color}; border-radius: 8px; padding: 6px 12px; text-align: center;">
                <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">LIVE SIGNAL BADGE</span><br/>
                <strong style="font-size: 18px; color: {badge_color};">{act.replace('_', ' ')} ({conf}%)</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mcol3:
        st.metric("Trend Direction", trend_icon)
    with mcol4:
        st.markdown(
            f"""
            <div style="background-color: {risk_color}22; border: 1px solid {risk_color}; border-radius: 8px; padding: 6px 12px; text-align: center;">
                <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">RISK LEVEL</span><br/>
                <strong style="font-size: 16px; color: {risk_color};">{risk} RISK</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mcol5:
        st.caption(f"⏱️ Live Updated:\n`{ts}`")

    st.markdown("---")

    # 2. Interactive Plotly Candlestick Chart (4 Panels)
    candles = data.get("candles", [])
    fig_chart = live_analyzer_chart(candles, symbol, timeframe)
    st.plotly_chart(fig_chart, use_container_width=True)

    st.markdown("---")

    # 3. AI Analysis Panel Below Chart
    st.subheader("🤖 AI Technical Analysis & Short-Term Prediction")

    pcol1, pcol2 = st.columns(2)

    with pcol1:
        st.markdown(
            """
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px;">
                <h4 style="color: #58a6ff; margin-top: 0;">📈 Indicator & Pattern Drivers</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.write(f"**EMA 20:** ₹{data.get('ema_20', 0):,.2f} | **EMA 50:** ₹{data.get('ema_50', 0):,.2f}")
        st.write(f"**RSI (14):** {data.get('rsi', 50)} | **VWAP:** ₹{data.get('vwap', 0):,.2f}")
        st.write(f"**Volume Surge:** {data.get('volume_surge_ratio', 1.0)}x 20-candle average")

        st.markdown("##### Key Signal Reasons:")
        for r in data.get("reasons", []):
            st.markdown(f"- {r}")

        patterns = data.get("detected_patterns", [])
        if patterns:
            st.markdown(f"🕯️ **Candlestick Patterns Detected:** {', '.join(patterns)}")

    with pcol2:
        st.markdown(
            """
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px;">
                <h4 style="color: #79c0ff; margin-top: 0;">🎯 Short-Term Target & Support/Resistance</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(f"**Short-Term Prediction:** {data.get('prediction', 'Consolidating')}")
        st.write(f"🎯 **Target Price:** ₹{data.get('target_price', cp):,.2f}")
        st.write(f"🛡️ **Stop Loss:** ₹{data.get('stop_loss', cp):,.2f}")

        st.markdown("##### Key Support & Resistance Levels:")
        supports = data.get("support_levels", [])
        resistances = data.get("resistance_levels", [])

        st.write(f"🟢 **Support Levels:** {', '.join([f'₹{s:.2f}' for s in supports])}")
        st.write(f"🔴 **Resistance Levels:** {', '.join([f'₹{r:.2f}' for r in resistances])}")
