"""Swing Stock Analysis Streamlit Page (3-8 Day Swing Trading)."""

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
    label="🔎 Search Stock by Name or Symbol (Groww-Style Autocomplete):",
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
        st.metric("Live Daily Close", f"₹{cp:,.2f}")
    with mcol2:
        st.markdown(
            f"""
            <div style="background-color: {badge_color}22; border: 2px solid {badge_color}; border-radius: 8px; padding: 6px 12px; text-align: center;">
                <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">SWING ACTION BADGE</span><br/>
                <strong style="font-size: 16px; color: {badge_color};">{act} ({conf}%)</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mcol3:
        st.markdown(
            f"""
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 6px 12px; text-align: center;">
                <span style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">SETUP IDENTIFIED</span><br/>
                <strong style="font-size: 14px; color: #58a6ff;">{setup}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mcol4:
        st.caption(f"⏱️ Daily Analysis Time:\n`{ts}`")

    st.markdown("---")

    # 2. Daily Swing Chart (Plotly)
    candles = data.get("candles", [])
    if candles:
        fig_chart = swing_analyzer_chart(candles, symbol)
        st.plotly_chart(fig_chart, use_container_width=True)

    st.markdown("---")

    # 3. Trade Plan & 5-Point Checklist Side-by-Side
    col_plan, col_check = st.columns([1, 1])

    with col_plan:
        st.subheader("🎯 3-8 Day Swing Trade Execution Plan")
        if plan:
            st.markdown(
                f"""
                <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px;">
                    <p style="margin-bottom: 8px;"><b>📥 Buy Entry Range:</b> <span style="color: #58a6ff; font-size: 16px; font-weight: bold;">₹{plan.get('entry_low', 0):,.2f} – ₹{plan.get('entry_high', 0):,.2f}</span></p>
                    <p style="margin-bottom: 8px;"><b>🛡️ Stop Loss (Exit):</b> <span style="color: #ef4444; font-size: 16px; font-weight: bold;">₹{plan.get('stop_loss', 0):,.2f}</span> ({plan.get('stop_loss_pct', -2.5):+.1f}%)</p>
                    <p style="margin-bottom: 8px;"><b>🎯 Target 1 (50% Quantity):</b> <span style="color: #26a641; font-size: 16px; font-weight: bold;">₹{plan.get('target_1', 0):,.2f}</span> ({plan.get('target_1_pct', 5.0):+.1f}%)</p>
                    <p style="margin-bottom: 8px;"><b>🚀 Target 2 (Runner):</b> <span style="color: #26a641; font-size: 16px; font-weight: bold;">₹{plan.get('target_2', 0):,.2f}</span> ({plan.get('target_2_pct', 8.0):+.1f}%)</p>
                    <hr style="border-color: #30363d;"/>
                    <p style="margin-bottom: 0;"><b>⚖️ Risk-to-Reward Ratio:</b> <span style="color: #a7f3d0; font-weight: bold;">1 : {plan.get('risk_reward', 2.0):.1f}</span></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No active buy trade plan — criteria not met.")

    with col_check:
        st.subheader("📋 5-Point Swing Criteria Checklist")
        chk = data.get("checklist", {})
        score = data.get("checklist_score", 0)

        st.markdown(f"**Overall Score:** `{score} / 5 Criteria Passed` — **{verdict}**")
        st.markdown("")

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
