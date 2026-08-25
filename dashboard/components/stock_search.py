"""Groww-Style Intelligent Stock Search & Suggestion Component for Streamlit Dashboard."""

from typing import Dict, List, Optional, Tuple
import streamlit as st
from app.market.nse_universe import NSE_UNIVERSE, StockInfo


def get_search_options() -> Tuple[List[str], Dict[str, str]]:
    """Generate list of formatted Groww-style display strings mapped to stock symbols.
    
    Format: 'SYMBOL — Company Name (Sector)'
    """
    options = [""]  # Index 0 is empty per no_default_search_stock rule
    mapping = {"": ""}
    
    # Sort universe alphabetically by symbol
    sorted_stocks = sorted(NSE_UNIVERSE.values(), key=lambda s: s.symbol)
    
    for s in sorted_stocks:
        display_str = f"{s.symbol} — {s.name} ({s.sector})"
        options.append(display_str)
        mapping[display_str] = s.symbol
        
    return options, mapping


def resolve_stock_query(query: str) -> Optional[str]:
    """Resolve free-text user query (any case, symbol, or company name) to valid NSE symbol.
    
    Examples:
    'motherson' -> 'MOTHERSON'
    'airtel' -> 'BHARTIARTL'
    'tata motors' -> 'TATAMOTORS'
    'hdfc' -> 'HDFCBANK'
    """
    if not query:
        return None
        
    q_clean = query.upper().strip()
    
    # 1. Exact Symbol Match
    if q_clean in NSE_UNIVERSE:
        return q_clean
        
    # Alias / Common Name Overrides
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
    }
    
    for key, sym in alias_map.items():
        if key in q_clean:
            return sym
            
    # 2. Company Name Contains Search
    for s in NSE_UNIVERSE.values():
        if q_clean in s.name.upper():
            return s.symbol
            
    return q_clean


def render_groww_stock_search(
    label: str = "🔎 Search Stock by Name or Symbol (Groww-Style Autocomplete):",
    session_key: str = "selected_symbol",
    box_key: str = "groww_stock_select_box"
) -> Tuple[str, bool]:
    """Renders Groww-style autocomplete search box in Streamlit.
    
    Supports typing uppercase, lowercase, company name, or selecting from suggestions.
    Returns: (resolved_symbol: str, submitted: bool)
    """
    options, mapping = get_search_options()
    
    current_sym = st.session_state.get(session_key, "")
    
    # Find current selected index
    current_index = 0
    if current_sym:
        for idx, opt in enumerate(options):
            if mapping.get(opt) == current_sym:
                current_index = idx
                break
                
    col_input, col_btn = st.columns([3, 1])
    
    with col_input:
        selected_display = st.selectbox(
            label,
            options=options,
            index=current_index,
            placeholder="Type company name or symbol (e.g. Motherson, Airtel, HDFC, Tatamotors)...",
            key=box_key
        )
        
    with col_btn:
        st.write("")
        st.write("")
        submitted = st.button("🔍 Search", key=f"btn_{box_key}", type="primary", use_container_width=True)
        
    selected_symbol = mapping.get(selected_display, "")
    
    if submitted or selected_symbol:
        if selected_symbol:
            st.session_state[session_key] = selected_symbol
            
    active_symbol = st.session_state.get(session_key, "")
    return active_symbol, submitted
