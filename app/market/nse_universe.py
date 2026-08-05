"""NSE Stock Universe — Curated list of key NSE stocks."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class StockInfo:
    symbol: str
    name: str
    sector: str
    market_cap_category: str
    index_membership: List[str]


NSE_UNIVERSE: Dict[str, StockInfo] = {
    "RELIANCE": StockInfo("RELIANCE", "Reliance Industries Ltd", "Energy", "large", ["NIFTY50"]),
    "TCS": StockInfo("TCS", "Tata Consultancy Services Ltd", "IT", "large", ["NIFTY50"]),
    "HDFCBANK": StockInfo("HDFCBANK", "HDFC Bank Ltd", "Banking", "large", ["NIFTY50"]),
    "ICICIBANK": StockInfo("ICICIBANK", "ICICI Bank Ltd", "Banking", "large", ["NIFTY50"]),
    "INFY": StockInfo("INFY", "Infosys Ltd", "IT", "large", ["NIFTY50"]),
    "HINDUNILVR": StockInfo("HINDUNILVR", "Hindustan Unilever Ltd", "FMCG", "large", ["NIFTY50"]),
    "ITC": StockInfo("ITC", "ITC Ltd", "FMCG", "large", ["NIFTY50"]),
    "BHARTIARTL": StockInfo("BHARTIARTL", "Bharti Airtel Ltd", "Telecom", "large", ["NIFTY50"]),
    "SBIN": StockInfo("SBIN", "State Bank of India", "Banking", "large", ["NIFTY50"]),
    "BAJFINANCE": StockInfo("BAJFINANCE", "Bajaj Finance Ltd", "NBFC", "large", ["NIFTY50"]),
    "KOTAKBANK": StockInfo("KOTAKBANK", "Kotak Mahindra Bank Ltd", "Banking", "large", ["NIFTY50"]),
    "LT": StockInfo("LT", "Larsen & Toubro Ltd", "Engineering", "large", ["NIFTY50"]),
    "AXISBANK": StockInfo("AXISBANK", "Axis Bank Ltd", "Banking", "large", ["NIFTY50"]),
    "ASIANPAINT": StockInfo("ASIANPAINT", "Asian Paints Ltd", "Paints", "large", ["NIFTY50"]),
    "MARUTI": StockInfo("MARUTI", "Maruti Suzuki India Ltd", "Auto", "large", ["NIFTY50"]),
    "WIPRO": StockInfo("WIPRO", "Wipro Ltd", "IT", "large", ["NIFTY50"]),
    "HCLTECH": StockInfo("HCLTECH", "HCL Technologies Ltd", "IT", "large", ["NIFTY50"]),
    "NTPC": StockInfo("NTPC", "NTPC Ltd", "Power", "large", ["NIFTY50"]),
    "SUNPHARMA": StockInfo("SUNPHARMA", "Sun Pharmaceutical Industries Ltd", "Pharma", "large", ["NIFTY50"]),
    "TATAMOTORS": StockInfo("TATAMOTORS", "Tata Motors Ltd", "Auto", "large", ["NIFTY50"]),
    "TATASTEEL": StockInfo("TATASTEEL", "Tata Steel Ltd", "Steel", "large", ["NIFTY50"]),
    "ADANIENT": StockInfo("ADANIENT", "Adani Enterprises Ltd", "Conglomerate", "large", ["NIFTY50"]),
    "ADANIPORTS": StockInfo("ADANIPORTS", "Adani Ports & SEZ Ltd", "Infrastructure", "large", ["NIFTY50"]),
    "JSWSTEEL": StockInfo("JSWSTEEL", "JSW Steel Ltd", "Steel", "large", ["NIFTY50"]),
    "POWERGRID": StockInfo("POWERGRID", "Power Grid Corporation of India Ltd", "Power", "large", ["NIFTY50"]),
    "TITAN": StockInfo("TITAN", "Titan Company Ltd", "Consumer", "large", ["NIFTY50"]),
    "ULTRACEMCO": StockInfo("ULTRACEMCO", "UltraTech Cement Ltd", "Cement", "large", ["NIFTY50"]),
    "BAJAJFINSV": StockInfo("BAJAJFINSV", "Bajaj Finserv Ltd", "NBFC", "large", ["NIFTY50"]),
    "NESTLEIND": StockInfo("NESTLEIND", "Nestle India Ltd", "FMCG", "large", ["NIFTY50"]),
    "ONGC": StockInfo("ONGC", "Oil & Natural Gas Corp Ltd", "Energy", "large", ["NIFTY50"]),
    "M&M": StockInfo("M&M", "Mahindra & Mahindra Ltd", "Auto", "large", ["NIFTY50"]),
    "TECHM": StockInfo("TECHM", "Tech Mahindra Ltd", "IT", "large", ["NIFTY50"]),
    "DIVISLAB": StockInfo("DIVISLAB", "Divi's Laboratories Ltd", "Pharma", "large", ["NIFTY50"]),
    "APOLLOHOSP": StockInfo("APOLLOHOSP", "Apollo Hospitals Enterprise Ltd", "Healthcare", "large", ["NIFTY50"]),
    "CIPLA": StockInfo("CIPLA", "Cipla Ltd", "Pharma", "large", ["NIFTY50"]),
    "COALINDIA": StockInfo("COALINDIA", "Coal India Ltd", "Mining", "large", ["NIFTY50"]),
    "DRREDDY": StockInfo("DRREDDY", "Dr. Reddy's Laboratories Ltd", "Pharma", "large", ["NIFTY50"]),
    "EICHERMOT": StockInfo("EICHERMOT", "Eicher Motors Ltd", "Auto", "large", ["NIFTY50"]),
    "GRASIM": StockInfo("GRASIM", "Grasim Industries Ltd", "Textiles", "large", ["NIFTY50"]),
    "HEROMOTOCO": StockInfo("HEROMOTOCO", "Hero MotoCorp Ltd", "Auto", "large", ["NIFTY50"]),
    "HINDALCO": StockInfo("HINDALCO", "Hindalco Industries Ltd", "Metals", "large", ["NIFTY50"]),
    "INDUSINDBK": StockInfo("INDUSINDBK", "IndusInd Bank Ltd", "Banking", "large", ["NIFTY50"]),
    "LTIM": StockInfo("LTIM", "LTIMindtree Ltd", "IT", "large", ["NIFTY50"]),
    "SBILIFE": StockInfo("SBILIFE", "SBI Life Insurance Co Ltd", "Insurance", "large", ["NIFTY50"]),
    "TATACONSUM": StockInfo("TATACONSUM", "Tata Consumer Products Ltd", "FMCG", "large", ["NIFTY50"]),
    "UPL": StockInfo("UPL", "UPL Ltd", "Chemicals", "large", ["NIFTY50"]),
    "BPCL": StockInfo("BPCL", "Bharat Petroleum Corp Ltd", "Energy", "large", ["NIFTY50"]),
    "BRITANNIA": StockInfo("BRITANNIA", "Britannia Industries Ltd", "FMCG", "large", ["NIFTY50"]),
    # High-Volume Intraday Penny Stocks (₹5 - ₹100)
    "YESBANK": StockInfo("YESBANK", "Yes Bank Ltd", "Banking", "small", ["NIFTYNEXT50"]),
    "SUZLON": StockInfo("SUZLON", "Suzlon Energy Ltd", "Energy", "mid", ["NIFTYMIDCAP"]),
    "IDEA": StockInfo("IDEA", "Vodafone Idea Ltd", "Telecom", "mid", ["NIFTYMIDCAP"]),
    "NHPC": StockInfo("NHPC", "NHPC Ltd", "Power", "mid", ["NIFTYMIDCAP"]),
    "SJVN": StockInfo("SJVN", "SJVN Ltd", "Power", "mid", ["NIFTYMIDCAP"]),
    "IOB": StockInfo("IOB", "Indian Overseas Bank", "Banking", "mid", ["NIFTYMIDCAP"]),
    "UCOBANK": StockInfo("UCOBANK", "UCO Bank", "Banking", "small", ["NIFTYMIDCAP"]),
    "CENTRALBK": StockInfo("CENTRALBK", "Central Bank of India", "Banking", "small", ["NIFTYMIDCAP"]),
    "INFIBEAM": StockInfo("INFIBEAM", "Infibeam Avenues Ltd", "IT", "small", ["NIFTYMIDCAP"]),
    "SOUTHBANK": StockInfo("SOUTHBANK", "South Indian Bank Ltd", "Banking", "small", ["NIFTYMIDCAP"]),
    "IFCI": StockInfo("IFCI", "IFCI Ltd", "NBFC", "small", ["NIFTYMIDCAP"]),
    "ALOKINDS": StockInfo("ALOKINDS", "Alok Industries Ltd", "Textiles", "small", ["NIFTYMIDCAP"]),
    "JPPOWER": StockInfo("JPPOWER", "Jaiprakash Power Ventures Ltd", "Power", "small", ["NIFTYMIDCAP"]),
    "RPOWER": StockInfo("RPOWER", "Reliance Power Ltd", "Power", "small", ["NIFTYMIDCAP"]),
}

INDICES: Dict[str, str] = {
    "NIFTY50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANKNIFTY": "^NSEBANK",
    "VIX": "^INDIAVIX",
}


def get_all_symbols() -> List[str]:
    return list(NSE_UNIVERSE.keys())


def get_symbols_by_sector(sector: str) -> List[str]:
    return [s for s, info in NSE_UNIVERSE.items() if info.sector.lower() == sector.lower()]


def get_nifty50_symbols() -> List[str]:
    return [s for s, info in NSE_UNIVERSE.items() if "NIFTY50" in info.index_membership]


def get_stock_info(symbol: str) -> Optional[StockInfo]:
    return NSE_UNIVERSE.get(symbol.upper())


def get_all_sectors() -> List[str]:
    return list(set(info.sector for info in NSE_UNIVERSE.values()))
