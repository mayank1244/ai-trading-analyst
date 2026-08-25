"""Swing Stock Analysis Streamlit Page (3 - 8 Days Swing Trading Plan)."""

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

from dashboard.components.charts import swing_analyzer_chart
from dashboard.components.stock_search import render_groww_stock_search

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Swing Stock Analysis | AI Trading Analyst", layout="wide")

st.title("🎯 Swing Stock Analysis (3 – 8 Days)")
st.caption("Daily chart analysis using Daily EMA 20/50/200, Daily RSI 14, Volume Surge, 5-Point Swing Checklist, & Calculated Risk-to-Reward Trade Plan.")

# Groww-Style Autocomplete Stock Search
symbol, _ = render_groww_stock_search(
    label="🔎 Search Stock by Name or Symbol (Groww-Style Freeform Search):",
    session_key="selected_swing_symbol",
    box_key="swing_stock_select_box",
)

# Quick Presets
st.write("Popular Swing Candidates:")
preset_cols = st.columns(7)
presets = ["BHARTIARTL", "MOTHERSON", "BEL", "DEEPAKFERT", "TATAMOTORS", "TITAN", "RELIANCE"]

for idx, p in enumerate(presets):
    if preset_cols[idx].button(p, key=f"swing_preset_{p}", use_container_width=True):
        st.session_state["selected_swing_symbol"] = p
        st.rerun()

if not symbol:
    st.info("🔎 Search company name or symbol above (e.g., Airtel, Motherson, Tatamotors, Reliance) or click a candidate button to view 3–8 day swing analysis.")
    st.stop()

# Fetch Data from Swing Analyzer API
data = None
with st.spinner(f"Running daily swing analysis for {symbol}..."):
    try:
        resp = requests.get(f"{API_BASE}/swing_analyzer/analyze/{symbol}", timeout=25)
        if resp.status_code == 200:
            data = resp.json()
        else:
            st.error(f"Could not load swing data for '{symbol}'. Detail: {resp.json().get('detail', 'API Error')}")
    except Exception as exc:
        st.error(f"Connection error to swing analyzer backend: {exc}")

if data:
    current_price = data.get("current_price", 0.0)
    verdict = data.get("verdict", "NEUTRAL")
    confidence = data.get("confidence", 50.0)
    setup_name = data.get("setup_name", "Swing Setup")
    ema20 = data.get("ema_20", 0.0)
    ema50 = data.get("ema_50", 0.0)
    ema200 = data.get("ema_200", 0.0)
    rsi = data.get("rsi", 50.0)
    vol_ratio = data.get("volume_surge_ratio", 1.0)
    high_20d = data.get("20d_high", 0.0)
    low_20d = data.get("20d_low", 0.0)
    plan = data.get("trade_plan", {})
    candles = data.get("candles", [])

    st.markdown("---")

    # Header Card: Verdict + Current Price
    col_sym, col_verdict, col_conf = st.columns([2, 3, 2])

    with col_sym:
        st.subheader(f"📊 {symbol}")
        st.metric("Current Market Price (Daily)", f"₹{current_price:,.2f}")

    with col_verdict:
        v_color = "#26a641" if "BUY" in verdict else "#eab308" if "WATCHLIST" in verdict else "#ef4444"
        st.markdown(
            f"""
            <div style="background-color: {v_color}15; border: 2px solid {v_color}; border-radius: 8px; padding: 14px; text-align: center; margin-top: 10px;">
                <h4 style="color: {v_color}; margin: 0;">{verdict}</h4>
                <small style="color: #8b949e;">Pattern Setup: {setup_name}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_conf:
        st.metric("Setup Confidence Score", f"{confidence:.1f}%")

    st.markdown("---")

    # Interactive Daily Chart
    if candles:
        st.subheader("📈 Daily Candlestick Chart with Moving Averages & Volume")
        fig = swing_analyzer_chart(candles=candles, symbol=symbol)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Two Columns: Calculated Trade Plan vs 5-Point Checklist
    col_plan, col_check = st.columns([1, 1])

    with col_plan:
        st.subheader("🏹 Calculated Swing Trade Plan")

        st.markdown(
            f"""
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px;">
                <p style="font-size: 15px; margin-bottom: 8px;"><b>📥 Ideal Entry Range:</b> <span style="color: #58a6ff; font-weight: bold;">{plan.get('entry_range', 'N/A')}</span></p>
                <p style="font-size: 15px; margin-bottom: 8px;"><b>🛡️ Stop Loss (Exit):</b> <span style="color: #ef4444; font-weight: bold;">₹{plan.get('stop_loss', 0):,.2f}</span> (-2.5%)</p>
                <p style="font-size: 15px; margin-bottom: 8px;"><b>🎯 Target 1 (50% Quantity):</b> <span style="color: #26a641; font-weight: bold;">₹{plan.get('target_1', 0):,.2f}</span> (+5.0%)</p>
                <p style="font-size: 15px; margin-bottom: 8px;"><b>🚀 Target 2 (Runner):</b> <span style="color: #26a641; font-weight: bold;">₹{plan.get('target_2', 0):,.2f}</span> (+8.0%)</p>
                <hr style="border-color: #30363d; margin: 10px 0;"/>
                <p style="font-size: 14px; margin-bottom: 4px;">⚖️ <b>Risk-to-Reward Ratio:</b> <span style="color: #a7f3d0; font-weight: bold;">{plan.get('risk_reward_ratio', '1 : 2.0')}</span></p>
                <p style="font-size: 13px; color: #8b949e; margin-bottom: 0;">⏱️ Estimated Holding Horizon: <b>{plan.get('holding_period', '3 – 8 Days')}</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_check:
        st.subheader("📋 Swing Criteria Checklist")
        chk = data.get("checklist", [])

        if isinstance(chk, list):
            passed_count = sum(1 for item in chk if item.get("passed", False))
            st.markdown(f"**Overall Score:** `{passed_count} / {len(chk)} Criteria Passed` — **{verdict}**")
            st.markdown("")

            for item in chk:
                name = item.get("name", "Criteria Check")
                passed = item.get("passed", False)
                detail = item.get("detail", "")
                icon = "✅ PASS" if passed else "❌ FAIL"
                color = "#26a641" if passed else "#ef4444"

                st.markdown(
                    f"""
                    <div style="background-color: #161b22; border-left: 4px solid {color}; border-radius: 4px; padding: 8px 12px; margin-bottom: 6px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span><b>{name}</b></span>
                            <span style="color: {color}; font-weight: bold;">{icon}</span>
                        </div>
                        <small style="color: #8b949e;">Detail: {detail}</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        elif isinstance(chk, dict):
            checks_def = [
                ("check_1_trend", "1. Trend Stack (Price > EMA 20 > 50 > 200)"),
                ("check_2_setup", "2. Swing Setup (EMA Pullback or Range Breakout)"),
                ("check_3_rsi", "3. RSI Momentum (Daily RSI 14 in 50–65 Zone)"),
                ("check_4_volume", "4. Volume Surge (>1.2x 20-Day Average)"),
                ("check_5_rr", "5. Risk-Reward Ratio (Target ÷ Risk >= 1:2)"),
            ]
            for key, label in checks_def:
                cdata = chk.get(key, {})
                passed = cdata.get("pass", False)
                val = cdata.get("val", "")
                icon = "✅ PASS" if passed else "❌ FAIL"
                color = "#26a641" if passed else "#ef4444"

                st.markdown(
                    f"""
                    <div style="background-color: #161b22; border-left: 4px solid {color}; border-radius: 4px; padding: 8px 12px; margin-bottom: 6px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span><b>{label}</b></span>
                            <span style="color: {color}; font-weight: bold;">{icon}</span>
                        </div>
                        <small style="color: #8b949e;">Detail: {val}</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
