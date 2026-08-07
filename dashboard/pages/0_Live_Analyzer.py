"""Live Stock Auto-Analyzer Streamlit Page."""

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
        value=st.session_state.get("selected_symbol", ""),
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

symbol = symbol_input if symbol_input else ""

if not symbol:
    st.info("🔎 Enter a stock symbol above (e.g., HDFCBANK, RELIANCE) or click a popular stock button to start live analysis.")
    st.stop()

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
                <strong style="font-size: 16px; color: {badge_color};">{act} ({conf}%)</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mcol3:
        st.markdown(
            f"""
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 6px 12px; text-align: center;">
                <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">TREND DIRECTION</span><br/>
                <strong style="font-size: 15px; color: #58a6ff;">{trend_icon}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mcol4:
        st.markdown(
            f"""
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 6px 12px; text-align: center;">
                <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">RISK LEVEL</span><br/>
                <strong style="font-size: 15px; color: {risk_color};">{risk} RISK</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mcol5:
        st.caption(f"⏱️ Live Updated:\n`{ts}`")

    st.markdown("---")

    # 2. Interactive Candlestick Chart
    candles = data.get("candles", [])
    sr_levels = data.get("sr_levels", {})
    patterns = data.get("detected_patterns", [])

    fig_chart = live_analyzer_chart(candles, symbol, timeframe, sr_levels, patterns)
    st.plotly_chart(fig_chart, use_container_width=True)

    st.markdown("---")

    # 3. Detected Patterns & Indicator Signals Breakdown
    pcol1, pcol2 = st.columns(2)

    with pcol1:
        st.subheader("🕯️ Detected Candlestick Patterns")
        if patterns:
            for p in patterns:
                ptype = p.get("type", "NEUTRAL")
                pcolor = "#26a641" if ptype == "BULLISH" else "#ef4444" if ptype == "BEARISH" else "#eab308"
                st.markdown(
                    f"""
                    <div style="background-color: #161b22; border-left: 4px solid {pcolor}; border-radius: 4px; padding: 10px; margin-bottom: 8px;">
                        <strong style="color: {pcolor};">{p.get('name')}</strong> ({ptype}) — <i>{p.get('desc')}</i>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No major single or multi-candle pattern detected on current timeframe.")

    with pcol2:
        st.subheader("📊 Indicator Signals Breakdown")
        ind = data.get("indicators", {})
        rsi_val = ind.get("rsi", 50)
        macd_sig = ind.get("macd_signal", "NEUTRAL")
        ema_sig = ind.get("ema_signal", "NEUTRAL")
        bb_sig = ind.get("bb_signal", "NEUTRAL")

        st.write(f"**RSI (14):** `{rsi_val:.1f}` ({'Overbought > 70' if rsi_val >= 70 else 'Oversold < 30' if rsi_val <= 30 else 'Neutral 30-70'})")
        st.write(f"**MACD Signal:** `{macd_sig}`")
        st.write(f"**EMA (20/50):** `{ema_sig}`")
        st.write(f"**Bollinger Bands:** `{bb_sig}`")

    # 4. Support & Resistance Summary
    st.markdown("---")
    st.subheader("🧱 Key Support & Resistance Levels")
    supports = sr_levels.get("supports", [])
    resistances = sr_levels.get("resistances", [])

    scol1, scol2 = st.columns(2)
    with scol1:
        st.markdown("**🟢 Support Levels (Buying Demand Zones):**")
        if supports:
            for s in supports:
                st.markdown(f"- `₹{s:,.2f}`")
        else:
            st.caption("No strong support detected nearby.")

    with scol2:
        st.markdown("**🔴 Resistance Levels (Selling Ceiling Zones):**")
        if resistances:
            for r in resistances:
                st.markdown(f"- `₹{r:,.2f}`")
        else:
            st.caption("No strong resistance detected nearby.")
