"""Live Auto-Refresh Component for Streamlit Dashboard."""

import time
import streamlit as st


def render_autorefresh_sidebar():
    """Render live auto-refresh toggle in sidebar and execute interval rerun."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⏱️ Live Data Auto-Refresh")
        enable_auto = st.toggle("🔄 Enable Auto-Refresh", value=False, key="auto_refresh_toggle")

        if enable_auto:
            refresh_interval = st.selectbox(
                "Refresh Interval:",
                options=[15, 30, 60],
                format_func=lambda x: f"Every {x} seconds",
                index=0,
                key="auto_refresh_interval_select",
            )
            st.caption(f"⚡ Live data updates automatically every {refresh_interval}s.")

            # Initialize last refresh timestamp
            last_refresh = st.session_state.get("last_auto_refresh_time", 0)
            now = time.time()

            if now - last_refresh >= refresh_interval:
                st.session_state["last_auto_refresh_time"] = now
                time.sleep(0.1)
                st.rerun()
