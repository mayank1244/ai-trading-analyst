"""Groww-Style Global Live Autocomplete Stock Search Component for Streamlit Dashboard."""

from typing import Dict, List, Optional, Tuple
import streamlit as st
import yfinance as yf
from app.market.nse_universe import NSE_UNIVERSE, StockInfo


def search_global_stocks(query: str, limit: int = 6) -> List[Dict[str, str]]:
    """Search global stocks across NSE, BSE, and international markets.
    
    Returns list of dicts: [{'symbol': 'MOTHERSON', 'name': 'Samvardhana Motherson Intl', 'exchange': 'NSE'}]
    """
    if not query or len(query.strip()) < 2:
        return []
        
    q_clean = query.strip()
    results = []
    seen_symbols = set()
    
    # 1. Search local NSE_UNIVERSE first (Instant match)
    q_upper = q_clean.upper()
    for s in NSE_UNIVERSE.values():
        if q_upper in s.symbol or q_upper in s.name.upper():
            clean_sym = s.symbol.replace(".NS", "").replace(".BO", "")
            if clean_sym not in seen_symbols:
                seen_symbols.add(clean_sym)
                results.append({
                    "symbol": clean_sym,
                    "name": s.name,
                    "exchange": "NSE"
                })
                
    # 2. Live yfinance global search for any other stock name (e.g. intellect, motherson sumi, etc.)
    try:
        yf_search = yf.Search(q_clean, max_results=10)
        for item in yf_search.quotes:
            raw_sym = item.get("symbol", "")
            exchange = item.get("exchDisp", item.get("exchange", ""))
            longname = item.get("longname", item.get("shortname", raw_sym))
            
            clean_sym = raw_sym.replace(".NS", "").replace(".BO", "")
            if clean_sym and clean_sym not in seen_symbols:
                seen_symbols.add(clean_sym)
                results.append({
                    "symbol": clean_sym,
                    "name": longname,
                    "exchange": exchange
                })
    except Exception:
        pass
        
    return results[:limit]


def resolve_stock_query(query: str) -> Optional[str]:
    """Resolve free-text user query to valid uppercase ticker symbol."""
    if not query:
        return None
        
    q_clean = query.upper().strip()
    
    # Common Aliases
    alias_map = {
        "AIRTEL": "BHARTIARTL",
        "BHARTI": "BHARTIARTL",
        "TATA MOTORS": "TATAMOTORS",
        "TATA MOTOR": "TATAMOTORS",
        "MOTHERSON": "MOTHERSON",
        "MOTHERSON SUMI": "MOTHERSON",
        "DEEPAK": "DEEPAKFERT",
        "DEEPAK FERTILIZERS": "DEEPAKFERT",
        "TATA STEEL": "TATASTEEL",
        "HDFC": "HDFCBANK",
        "HDFC BANK": "HDFCBANK",
        "ICICI": "ICICIBANK",
        "ICICI BANK": "ICICIBANK",
        "SBI": "SBIN",
        "STATE BANK": "SBIN",
        "RELIANCE": "RELIANCE",
        "INFY": "INFY",
        "INFOSYS": "INFY",
        "BEL": "BEL",
        "BHARAT ELECTRONICS": "BEL",
        "INTELLECT": "INTELLECT",
    }
    
    for key, sym in alias_map.items():
        if key in q_clean:
            return sym
            
    if q_clean in NSE_UNIVERSE:
        return q_clean
        
    for s in NSE_UNIVERSE.values():
        if q_clean in s.name.upper():
            return s.symbol
            
    return q_clean.replace(" ", "")


def render_groww_stock_search(
    label: str = "🔎 Search Stock by Name or Symbol (Groww Global Search):",
    session_key: str = "selected_symbol",
    box_key: str = "groww_stock_search_input"
) -> Tuple[str, bool]:
    """Renders Groww-style global freeform search input with live stock suggestions in Streamlit."""
    col_input, col_btn = st.columns([3, 1])
    
    with col_input:
        query_input = st.text_input(
            label,
            value=st.session_state.get(session_key, ""),
            placeholder="Type company name or symbol (e.g. motherson, intellect, airtel, tatamotors, suzlon)...",
            key=box_key
        ).strip()
        
    with col_btn:
        st.write("")
        st.write("")
        submitted = st.button("🔍 Search", key=f"btn_{box_key}", type="primary", use_container_width=True)
        
    # Live Global Suggestions Cards
    if query_input:
        matches = search_global_stocks(query_input, limit=4)
        if matches:
            st.markdown("**💡 Matching Stock Options:**")
            sug_cols = st.columns(min(len(matches), 4))
            for idx, item in enumerate(matches[:4]):
                sym = item["symbol"]
                name = item["name"][:22]
                exch = item["exchange"]
                btn_label = f"📌 {sym} — {name} [{exch}]"
                
                if sug_cols[idx].button(btn_label, key=f"sug_{box_key}_{sym}_{idx}", use_container_width=True):
                    st.session_state[session_key] = sym
                    st.rerun()
                    
    resolved_symbol = resolve_stock_query(query_input) if query_input else ""
    
    if submitted and resolved_symbol:
        st.session_state[session_key] = resolved_symbol
        
    active_symbol = st.session_state.get(session_key, "")
    return active_symbol, submitted
