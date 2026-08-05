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
from dashboard.components.cards import recommendation_card

try:
    from dashboard.components.charts import score_radar_chart, why_up_down_chart
except Exception:
    import plotly.graph_objects as go
    from dashboard.components.charts import score_radar_chart

    def why_up_down_chart(bullish_signals, bearish_signals, quant_score=50.0):
        up_pct = round(quant_score, 1)
        down_pct = round(max(0.0, 100.0 - up_pct), 1)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=["🟢 Upside Driver (UP)", "🔴 Downside Risk (DOWN)"],
                x=[up_pct, down_pct],
                orientation="h",
                marker=dict(color=["#26a641", "#da3633"]),
                text=[f"🟢 UP: {up_pct}%", f"🔴 DOWN: {down_pct}%"],
                textposition="auto",
            )
        )
        fig.update_layout(
            title="<b>Why It Might Go UP vs. Why It Might Go DOWN</b>",
            paper_bgcolor="#0d1117",
            plot_bgcolor="#0d1117",
            font=dict(color="#c9d1d9"),
            height=260,
            xaxis=dict(range=[0, 100]),
            margin=dict(l=40, r=40, t=50, b=40),
        )
        return fig

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Stock Analysis | AI Trading Analyst", layout="wide")
st.title("📈 Stock Analysis & Movement Predictor")

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

    st.markdown("---")
    st.subheader("📊 Why It Might Go UP vs. Why It Might Go DOWN")
    
    # 1. UP vs DOWN Visual Graph
    bullish_signals = rec.get("bullish_signals", [])
    bearish_signals = rec.get("bearish_signals", [])
    quant_score = float(rec.get("quant_score", 50.0))

    fig_up_down = why_up_down_chart(bullish_signals, bearish_signals, quant_score)
    st.plotly_chart(fig_up_down, use_container_width=True)

    # 2. Detailed Drivers Comparison Side-by-Side
    col_up, col_down = st.columns(2)

    with col_up:
        st.markdown(
            """
            <div style="background-color: #0d2612; border: 1px solid #26a641; border-radius: 8px; padding: 14px;">
                <h4 style="color: #4ac26b; margin: 0 0 10px 0;">🚀 Why It Might Go UP (Bullish Drivers)</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if bullish_signals:
            for s in bullish_signals:
                st.markdown(f"🟢 **{s}**")
        else:
            st.info("No strong bullish momentum driver detected currently.")

    with col_down:
        st.markdown(
            """
            <div style="background-color: #2b0b0b; border: 1px solid #ef4444; border-radius: 8px; padding: 14px;">
                <h4 style="color: #f87171; margin: 0 0 10px 0;">🔻 Why It Might Go DOWN (Bearish Risks)</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if bearish_signals:
            for s in bearish_signals:
                st.markdown(f"🔴 **{s}**")
        else:
            st.info("No significant bearish downside risk detected currently.")

    st.markdown("---")

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
        st.subheader("Detailed Technical & AI Analysis Summary")
        st.markdown(rec.get("detailed_explanation", "No explanation available."))
