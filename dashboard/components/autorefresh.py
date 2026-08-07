"""Live Seamless Auto-Refresh Component for Streamlit Dashboard."""

import time
import streamlit as st


def render_autorefresh_sidebar(interval_seconds: int = 10):
    """Silently execute live background auto-refresh across all pages without displaying sidebar toggles."""
    last_refresh = st.session_state.get("last_auto_refresh_time", 0)
    now = time.time()

    if now - last_refresh >= interval_seconds:
        st.session_state["last_auto_refresh_time"] = now
        time.sleep(0.1)
        st.rerun()
