"""Macro & Lifetime Stock Analysis Streamlit Page (Day Trading vs 3-5 Day Swing Trading)."""

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

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Lifetime & Macro Analysis | AI Trading Analyst", layout="wide")

st.title("🏛️ Lifetime Inception & Macro Market Analyzer")
st.caption("Deep analysis of lifetime historical patterns (since IPO listing), 1000-Day EMA super-trend, national & international news drivers, and Day Trading vs. 3–5 Day Swing Trading strategy preferences.")

# Search Bar & Preset Symbols
col_search, col_space = st.columns([3, 1])

with col_search:
    symbol_input = st.text_input(
        "🔎 Enter NSE/BSE Stock Symbol for Lifetime & Macro Analysis:",
        value=st.session_state.get("selected_macro_symbol", ""),
        placeholder="e.g. BHARTIARTL, MOTHERSON, BEL, TATASTEEL, TATAMOTORS",
        key="macro_symbol_input_box",
    ).upper().strip()

# Quick Presets
st.write("Featured Multi-Decade Stocks & Boom Sectors:")
preset_cols = st.columns(5)
presets = ["BHARTIARTL", "MOTHERSON", "BEL", "TATASTEEL", "TATAMOTORS"]

for idx, p in enumerate(presets):
    if preset_cols[idx].button(p, key=f"macro_preset_{p}", use_container_width=True):
        st.session_state["selected_macro_symbol"] = p
        st.rerun()

symbol = symbol_input if symbol_input else ""

if not symbol:
    st.info("🔎 Enter a stock symbol above (e.g., BHARTIARTL, MOTHERSON, BEL) or click a featured stock button to run deep lifetime & macro analysis.")
    st.stop()

# Fetch Data from Macro Analyzer API
data = None
with st.spinner(f"Fetching full lifetime inception data (since IPO) & macro news drivers for {symbol}..."):
    try:
        resp = requests.get(f"{API_BASE}/macro_analyzer/analyze/{symbol}", timeout=35)
        if resp.status_code == 200:
            data = resp.json()
        else:
            st.error(f"Could not load macro lifetime data for '{symbol}'. Detail: {resp.json().get('detail', 'API Error')}")
    except Exception as exc:
        st.error(f"Connection error to macro analyzer backend: {exc}")

if data:
    name = data.get("name", symbol)
    sector = data.get("sector", "General")
    cp = data.get("current_price", 0.0)
    life = data.get("lifetime", {})
    tech = data.get("technical", {})
    macro = data.get("macro_news", {})
    day = data.get("day_trading", {})
    swing = data.get("swing_trading", {})

    st.markdown("---")
    st.subheader(f"📊 {name} ({symbol}) — {sector}")
    st.metric("Live Market Price", f"₹{cp:,.2f}")

    # 1. Lifetime Inception Matrix (Since IPO)
    st.markdown("### 📜 Lifetime Inception Profile (Since IPO Listing)")
    lcol1, lcol2, lcol3, lcol4, lcol5 = st.columns(5)

    with lcol1:
        st.metric("Listed Inception Date", life.get("inception_date", "N/A"), f"{life.get('total_years', 0)} Years")
    with lcol2:
        st.metric("IPO / Earliest Price", f"₹{life.get('ipo_price', 0):,.2f}")
    with lcol3:
        st.metric("Lifetime Return", f"+{life.get('lifetime_return_pct', 0):,.1f}%", f"{life.get('multibagger_x', 0):.1f}x Multibagger")
    with lcol4:
        st.metric("Annualized CAGR", f"{life.get('cagr_pct', 0):.1f}% p.a.")
    with lcol5:
        st.metric("All-Time High (ATH)", f"₹{life.get('ath', 0):,.2f}", f"{life.get('dist_ath_pct', 0):+.1f}% from ATH")

    st.markdown(
        f"""
        <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px 18px; margin-top: 10px;">
            <span>📉 <b>Historical Max Crisis Drawdown:</b> <span style="color: #ef4444; font-weight: bold;">{life.get('max_drawdown_pct', 0):.1f}%</span> &nbsp;|&nbsp; 
            📊 <b>1000-Day EMA Super-trend Level:</b> <span style="color: #58a6ff; font-weight: bold;">₹{life.get('ema_1000', 0):,.2f}</span> &nbsp;|&nbsp; 
            📈 <b>All-Time Low (ATL):</b> ₹{life.get('atl', 0):,.2f} ({life.get('atl_date', '')})</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 2. National & International News / Macro Drivers
    st.markdown("### 🌐 National & International Market News & Macro Impact")
    mcol1, mcol2 = st.columns(2)

    with mcol1:
        st.markdown(
            f"""
            <div style="background-color: #161b22; border-left: 4px solid #58a6ff; border-radius: 6px; padding: 14px; margin-bottom: 10px;">
                <h5 style="color: #58a6ff; margin-bottom: 6px;">🌍 Global Macro Sentiment</h5>
                <p style="margin-bottom: 0;">{macro.get('global_sentiment')}</p>
            </div>
            <div style="background-color: #161b22; border-left: 4px solid #26a641; border-radius: 6px; padding: 14px;">
                <h5 style="color: #26a641; margin-bottom: 6px;">🇮🇳 National Economy & Sector Tailwinds</h5>
                <p style="margin-bottom: 0;">{macro.get('national_sentiment')} {macro.get('sector_driver')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with mcol2:
        st.markdown(
            f"""
            <div style="background-color: #161b22; border-left: 4px solid #eab308; border-radius: 6px; padding: 14px; margin-bottom: 10px;">
                <h5 style="color: #eab308; margin-bottom: 6px;">⚡ Current Technical Indicators Summary</h5>
                <p style="margin-bottom: 4px;">• <b>Daily RSI (14):</b> <code>{tech.get('rsi_14', 50)}</code> ({'Overbought' if tech.get('rsi_14',50) >= 70 else 'Oversold' if tech.get('rsi_14',50) <= 30 else 'Active Momentum'})</p>
                <p style="margin-bottom: 4px;">• <b>Volume Ratio:</b> <code>{tech.get('vol_ratio', 1.0)}x</code> 20-Day Average</p>
                <p style="margin-bottom: 4px;">• <b>EMA 20 Support:</b> <code>₹{tech.get('ema_20', 0):,.2f}</code> (Distance: <code>{tech.get('dist_ema20_pct', 0):+.2f}%</code>)</p>
                <p style="margin-bottom: 0;">• <b>EMA 50 / 200:</b> <code>₹{tech.get('ema_50', 0):,.2f} / ₹{tech.get('ema_200', 0):,.2f}</code></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 3. Strategy Preferences: Day Trading vs 3-5 Day Swing Trading
    st.markdown("### ⚖️ Strategy Preference Comparison (Day Trading vs. 3–5 Day Swing Trading)")
    scol1, scol2 = st.columns(2)

    with scol1:
        st.subheader("⚡ 1-DAY INTRADAY TRADING PLAN")
        d_verdict = day.get("verdict", "")
        d_color = "#26a641" if "RECOMMENDED" in d_verdict else "#eab308"
        d_plan = day.get("plan", {})

        st.markdown(
            f"""
            <div style="background-color: {d_color}15; border: 2px solid {d_color}; border-radius: 8px; padding: 14px; text-align: center; margin-bottom: 12px;">
                <strong style="color: {d_color}; font-size: 15px;">{d_verdict}</strong>
            </div>
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px;">
                <p style="margin-bottom: 8px;"><b>📥 Intraday Entry Price:</b> <span style="color: #58a6ff; font-weight: bold;">₹{d_plan.get('entry', 0):,.2f}</span></p>
                <p style="margin-bottom: 8px;"><b>🛡️ Tight Stop Loss (-0.8%):</b> <span style="color: #ef4444; font-weight: bold;">₹{d_plan.get('stop_loss', 0):,.2f}</span></p>
                <p style="margin-bottom: 8px;"><b>🎯 Target 1 (+1.2% Scalp):</b> <span style="color: #26a641; font-weight: bold;">₹{d_plan.get('target_1', 0):,.2f}</span></p>
                <p style="margin-bottom: 0;"><b>🚀 Target 2 (+2.5% Momentum):</b> <span style="color: #26a641; font-weight: bold;">₹{d_plan.get('target_2', 0):,.2f}</span></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with scol2:
        st.subheader("🏹 3–5 DAY SWING TRADING PLAN")
        s_verdict = swing.get("verdict", "")
        s_color = "#26a641" if "PREFERRED" in s_verdict else "#eab308" if "WATCHLIST" in s_verdict else "#ef4444"
        s_plan = swing.get("plan", {})

        st.markdown(
            f"""
            <div style="background-color: {s_color}15; border: 2px solid {s_color}; border-radius: 8px; padding: 14px; text-align: center; margin-bottom: 12px;">
                <strong style="color: {s_color}; font-size: 15px;">{s_verdict}</strong>
            </div>
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px;">
                <p style="margin-bottom: 8px;"><b>📥 Swing Entry Range:</b> <span style="color: #58a6ff; font-weight: bold;">{s_plan.get('entry_range', '')}</span></p>
                <p style="margin-bottom: 8px;"><b>🛡️ Swing Stop Loss (-2.5%):</b> <span style="color: #ef4444; font-weight: bold;">₹{s_plan.get('stop_loss', 0):,.2f}</span></p>
                <p style="margin-bottom: 8px;"><b>🎯 Target 1 (50% Qty +5%):</b> <span style="color: #26a641; font-weight: bold;">₹{s_plan.get('target_1', 0):,.2f}</span></p>
                <p style="margin-bottom: 8px;"><b>🚀 Target 2 (Runner +8%):</b> <span style="color: #26a641; font-weight: bold;">₹{s_plan.get('target_2', 0):,.2f}</span></p>
                <hr style="border-color: #30363d; margin: 8px 0;"/>
                <p style="margin-bottom: 0;"><b>⚖️ Risk-to-Reward Ratio:</b> <span style="color: #a7f3d0; font-weight: bold;">1 : {s_plan.get('risk_reward', 2.0):.1f}</span></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
