"""Streamlit card components."""

import streamlit as st


def index_card(name: str, value: float, change: float, change_pct: float) -> None:
    is_up = change >= 0
    color = "#3fb950" if is_up else "#f85149"
    arrow = "▲" if is_up else "▼"

    html = f"""
<div style="background:#161b22; border:1px solid #30363d; border-radius:8px; padding:12px; text-align:center;">
    <div style="font-size:12px; color:#8b949e;">{name}</div>
    <div style="font-size:18px; font-weight:700; color:#e6edf3;">{value:,.2f}</div>
    <div style="font-size:12px; color:{color};">{arrow} {abs(change):,.2f} ({abs(change_pct):.2f}%)</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def recommendation_card(rec: dict) -> None:
    action = str(rec.get("action", "HOLD")).upper()
    colors = {
        "STRONG_BUY": "#1a7f37",
        "BUY": "#26a641",
        "WATCHLIST": "#d29922",
        "HOLD": "#8b949e",
        "SELL": "#da3633",
        "STRONG_SELL": "#b91c1c",
    }
    badge_color = colors.get(action, "#7c6af7")

    symbol = rec.get("symbol", "")
    price = rec.get("current_price", 0.0)
    conf = rec.get("confidence", 0.0)
    entry = rec.get("entry_price", 0.0)
    sl = rec.get("stop_loss", 0.0)
    t1 = rec.get("target_1", 0.0)

    html = f"""
<div style="background:#161b22; border:1px solid #30363d; border-left:4px solid {badge_color}; border-radius:8px; padding:16px; margin-bottom:12px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="font-size:20px; font-weight:700; color:#e6edf3;">{symbol}</span>
            <span style="font-size:14px; color:#8b949e; margin-left:8px;">₹{price:,.2f}</span>
        </div>
        <span style="background:{badge_color}; color:#fff; padding:4px 12px; border-radius:12px; font-size:12px; font-weight:700;">{action} ({conf:.0f}%)</span>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-top:12px; font-size:12px; text-align:center;">
        <div style="background:#0d1117; padding:6px; border-radius:4px;">Entry: <strong style="color:#58a6ff;">₹{entry:,.2f}</strong></div>
        <div style="background:#0d1117; padding:6px; border-radius:4px;">Stop Loss: <strong style="color:#f85149;">₹{sl:,.2f}</strong></div>
        <div style="background:#0d1117; padding:6px; border-radius:4px;">Target 1: <strong style="color:#3fb950;">₹{t1:,.2f}</strong></div>
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)
