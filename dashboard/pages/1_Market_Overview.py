import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import requests
import streamlit as st

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Market Overview | AI Trading Analyst", layout="wide")
st.title("📊 Market Overview")

try:
    resp = requests.get(f"{API_BASE}/market/overview", timeout=5)
    data = resp.json() if resp.status_code == 200 else {}
except Exception:
    data = {}

st.subheader("Key Benchmark Indices")
indices = data.get("indices", [])
if indices:
    cols = st.columns(len(indices))
    for col, idx in zip(cols, indices):
        with col:
            st.metric(idx["name"], f"{idx['value']:,.2f}", f"{idx['change_pct']:+.2f}%")
else:
    st.info("Market data loading...")

st.markdown("---")
st.subheader("Sectors Covered")
sectors = data.get("sectors", ["IT", "Banking", "Auto", "Pharma", "Energy", "FMCG", "Steel"])
st.write(", ".join(sectors))
