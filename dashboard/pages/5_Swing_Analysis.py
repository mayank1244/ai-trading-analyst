"""Swing Stock Analysis Streamlit Page (3-8 Day Swing Trading)."""

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

from dashboard.components.charts import swing_analyzer_chart

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Swing Stock Analysis | AI Trading Analyst", layout="wide")

st.title("🎯 Swing Stock Analysis (3 – 8 Days)")
st.caption("Daily chart analysis using Daily EMA 20/50/200, Daily RSI 14, Volume Surge, 5-Point Swing Checklist, & Calculated Risk-to-Reward Trade Plan.")

# Search Bar & Preset Symbols
col_search, col_space = st.columns([3, 1])

with col_search:
    symbol_input = st.text_input(
        "🔎 Enter NSE/BSE Stock Symbol for Swing Analysis:",
        value=st.session_state.get("selected_swing_symbol", "DEEPAKFERT"),
        placeholder="e.g. DEEPAKFERT, TATAMOTORS, TITAN, RELIANCE, DIVISLAB",
        key="swing_symbol_input_box",
    ).upper().strip()

# Quick Presets
st.write("Popular Swing Candidates:")
preset_cols = st.columns(7)
presets = ["DEEPAKFERT", "TATAMOTORS", "TITAN", "DIVISLAB", "HCLTECH", "RELIANCE", "UPL"]

for idx, p in enumerate(presets):
    if preset_cols[idx].button(p, key=f"swing_preset_{p}", use_container_width=True):
        st.session_state["selected_swing_symbol"] = p
        st.rerun()

symbol = symbol_input if symbol_input else "DEEPAKFERT"

# Fetch Data from Swing Analyzer API
data = None
with st.spinner(f"Running 3-8 Day Swing Analysis for {symbol} on Daily Charts..."):
    try:
        resp = requests.get(f"{API_BASE}/swing_analyzer/analyze/{symbol}", timeout=30)
        if resp.status_code == 200:
            data = resp.json()
        else:
            st.error(f"Could not analyze swing data for '{symbol}'. Detail: {resp.json().get('detail', 'API Error')}")
    except Exception as exc:
        st.error(f"Connection error to swing analyzer backend: {exc}")

if data:
    # 1. Metric Header Bar
    cp = data.get("current_price", 0.0)
    act = data.get("action", "AVOID")
    verdict = data.get("verdict", "")
    conf = data.get("confidence", 50.0)
    setup = data.get("setup_name", "")
    ts = data.get("timestamp", "")
    plan = data.get("trade_plan", {})

    badge_color = "#26a641" if "BUY" in act else "#ef4444" if "AVOID" in act else "#eab308"

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)

    with mcol1:
        st.metric("Current Daily Price", f"₹{cp:,.2f}")
    with mcol2:
        st.markdown(
            f"""
            <div style="background-color: {badge_color}22; border: 2px solid {badge_color}; border-radius: 8px; padding: 6px 12px; text-align: center;">
                <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">SWING VERDICT</span><br/>
                <strong style="font-size: 16px; color: {badge_color};">{verdict} ({conf}%)</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mcol3:
        st.markdown(
            f"""
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 6px 12px; text-align: center;">
                <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">DETECTED SETUP</span><br/>
                <strong style="font-size: 14px; color: #58a6ff;">{setup}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mcol4:
        st.caption(f"📅 Daily Analysis Updated:\n`{ts}`")

    st.markdown("---")

    # 2. Swing Trade Execution Plan & 5-Point Checklist Cards
    pcol1, pcol2 = st.columns(2)

    with pcol1:
        st.markdown(
            """
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px;">
                <h4 style="color: #26a641; margin-top: 0;">🎯 3–8 Day Swing Trade Execution Plan</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(f"**Holding Period:** `{plan.get('holding_period', '3-8 Days')}`")
        st.markdown(f"📥 **Entry Range:** `{plan.get('entry_range', '')}`")
        st.markdown(f"🛡️ **Stop Loss:** `₹{plan.get('stop_loss', 0):,.2f}` (-2.5%)")
        st.markdown(f"🎯 **Target 1 (+5%):** `₹{plan.get('target_1', 0):,.2f}`")
        st.markdown(f"🚀 **Target 2 (+8%):** `₹{plan.get('target_2', 0):,.2f}`")
        st.markdown(f"⚖️ **Risk : Reward Ratio:** `{plan.get('risk_reward_ratio', '1 : 2.5')}`")

    with pcol2:
        st.markdown(
            """
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px;">
                <h4 style="color: #58a6ff; margin-top: 0;">📋 5-Point Swing Checklist Verification</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        checklist = data.get("checklist", [])
        for item in checklist:
            icon = "✅" if item.get("passed") else "❌"
            color = "#a7f3d0" if item.get("passed") else "#fca5a5"
            st.markdown(
                f"""
                <div style="margin-bottom: 8px;">
                    {icon} <strong style="color: {color};">{item.get('name')}</strong><br/>
                    <span style="font-size: 13px; color: #94a3b8; margin-left: 24px;">{item.get('detail')}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # 3. Interactive Daily Swing Candlestick Chart
    candles = data.get("candles", [])
    fig_chart = swing_analyzer_chart(candles, symbol)
    st.plotly_chart(fig_chart, use_container_width=True)

    st.markdown("---")

    # 4. Indicator Deep Dive Summary
    st.subheader("📊 Key Indicator Readings (Daily Chart)")
    icol1, icol2, icol3, icol4 = st.columns(4)

    with icol1:
        st.write(f"**Daily EMA 20:** ₹{data.get('ema_20', 0):,.2f}")
    with icol2:
        st.write(f"**Daily EMA 50:** ₹{data.get('ema_50', 0):,.2f}")
    with icol3:
        st.write(f"**Daily RSI (14):** {data.get('rsi', 50)}")
    with icol4:
        st.write(f"**Volume Ratio:** {data.get('volume_surge_ratio', 1.0)}x 20-day avg")
