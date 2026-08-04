import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dashboard.backend_starter import ensure_backend_running
ensure_backend_running()

import requests
import streamlit as st

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="AI Chat Assistant | AI Trading Analyst", layout="wide")
st.title("💬 AI Chat Assistant")
st.caption("Ask natural language questions about Indian stocks, technical signals, or market outlook.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Namaste! I am your AI Trading Assistant for the Indian Stock Market. Ask me about any stock, indicator, or market setup."}
    ]

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask a question (e.g. Should I buy Reliance? What is RSI?)...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Detect symbol
    detected_sym = None
    for word in user_input.upper().replace("?", "").replace(",", "").split():
        if len(word) >= 3 and word.isalnum():
            if word in ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "TATAMOTORS", "ITC", "WIPRO"]:
                detected_sym = word
                break

    with st.spinner("Analyzing..."):
        try:
            resp = requests.post(f"{API_BASE}/chat", json={"message": user_input, "symbol": detected_sym}, timeout=15)
            if resp.status_code == 200:
                reply = resp.json().get("message", "No response.")
            else:
                reply = "Unable to process chat request at the moment."
        except Exception as exc:
            reply = f"Error communicating with AI server: {exc}"

    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
