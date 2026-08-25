"""Plotly chart builders for the AI Trading Analyst dashboard."""

from typing import Dict, List
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PAPER_BG = "#0d1117"
PLOT_BG = "#0d1117"
GRID_COLOR = "#21262d"
TEXT_COLOR = "#c9d1d9"


def candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name=symbol,
            increasing=dict(line=dict(color="#26a641")),
            decreasing=dict(line=dict(color="#da3633")),
        ),
        row=1,
        col=1,
    )

    for col, color in [("EMA_21", "#f0e68c"), ("EMA_50", "#87ceeb"), ("EMA_200", "#ff8c00")]:
        if col in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df[col], name=col, line=dict(color=color, width=1.5)),
                row=1,
                col=1,
            )

    if "Volume" in df.columns:
        colors = ["#26a641" if c >= o else "#da3633" for c, o in zip(df["Close"], df["Open"])]
        fig.add_trace(
            go.Bar(x=df.index, y=df["Volume"], name="Volume", marker=dict(color=colors)),
            row=2,
            col=1,
        )

    fig.update_layout(
        title=f"{symbol} Candlestick Chart",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COLOR),
        height=500,
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis_rangeslider_visible=False,
    )
    return fig


def sector_heatmap(sector_scores: Dict[str, float]) -> go.Figure:
    labels = list(sector_scores.keys())
    scores = list(sector_scores.values())
    colors = ["#26a641" if s >= 50 else "#da3633" for s in scores]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=scores,
            marker_color=colors,
            text=[f"{s:.1f}" for s in scores],
            textposition="auto",
        )
    )
    fig.update_layout(
        title="Sector Strength (0-100)",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COLOR),
        height=350,
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


def score_radar_chart(scores: dict) -> go.Figure:
    categories = ["Trend", "Momentum", "Volume", "S/R", "Pattern", "Sector", "Market", "Volatility"]
    values = [float(scores.get(c, 50)) for c in categories]

    fig = go.Figure(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(124,106,247,0.2)",
            line=dict(color="#7c6af7"),
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor=PLOT_BG,
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=GRID_COLOR),
            angularaxis=dict(gridcolor=GRID_COLOR),
        ),
        paper_bgcolor=PAPER_BG,
        font=dict(color=TEXT_COLOR),
        height=300,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def why_up_down_chart(bullish_signals: List[str], bearish_signals: List[str], quant_score: float = 50.0) -> go.Figure:
    """Build a visual comparison chart showing why stock might go UP vs DOWN."""
    b_count = max(len(bullish_signals), 1)
    br_count = max(len(bearish_signals), 1)

    total = b_count + br_count
    up_pct = round(quant_score, 1) if quant_score != 50.0 else round((b_count / total) * 100, 1)
    down_pct = round(100.0 - up_pct, 1)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=["🟢 Upside Driver (UP)", "🔴 Downside Risk (DOWN)"],
            x=[up_pct, down_pct],
            orientation="h",
            marker=dict(color=["#26a641", "#da3633"]),
            text=[f"🟢 UP Probability: {up_pct}%", f"🔴 DOWN Risk: {down_pct}%"],
            textposition="auto",
            hovertemplate="%{y}: %{x}%<extra></extra>",
        )
    )

    fig.update_layout(
        title="<b>Why It Might Go UP vs. Why It Might Go DOWN</b>",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COLOR),
        height=260,
        xaxis=dict(range=[0, 100], title="Probability / Signal Weight (%)", gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


def live_analyzer_chart(candles: List[dict], symbol: str, timeframe: str = "15m") -> go.Figure:
    """Build a TradingView-style 4-panel interactive Plotly chart with Candlesticks, EMAs, BB, Volume, RSI, & MACD."""
    if not candles:
        fig = go.Figure()
        fig.update_layout(
            title=f"No chart data available for {symbol}",
            paper_bgcolor=PAPER_BG,
            font=dict(color=TEXT_COLOR),
        )
        return fig

    times = [c["time"] for c in candles]
    opens = [c["open"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    closes = [c["close"] for c in candles]
    volumes = [c["volume"] for c in candles]

    ema_20s = [c.get("ema_20") for c in candles]
    ema_50s = [c.get("ema_50") for c in candles]
    bb_uppers = [c.get("bb_upper") for c in candles]
    bb_lowers = [c.get("bb_lower") for c in candles]
    vwaps = [c.get("vwap") for c in candles]

    rsis = [c.get("rsi") for c in candles]
    macds = [c.get("macd") for c in candles]
    macd_sigs = [c.get("macd_sig") for c in candles]
    macd_hists = [c.get("macd_hist") for c in candles]

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.48, 0.14, 0.19, 0.19],
        subplot_titles=(
            f"<b>{symbol} ({timeframe.upper()}) Live Chart — Price, EMAs & Bollinger Bands</b>",
            "<b>Volume</b>",
            "<b>RSI (14) Indicator</b>",
            "<b>MACD (12, 26, 9)</b>",
        ),
    )

    # 1. Main Candlesticks (Row 1)
    fig.add_trace(
        go.Candlestick(
            x=times,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name=f"{symbol} OHLC",
            increasing=dict(line=dict(color="#26a641", width=1.2), fillcolor="#26a641"),
            decreasing=dict(line=dict(color="#ef4444", width=1.2), fillcolor="#ef4444"),
        ),
        row=1,
        col=1,
    )

    # EMA 20 & EMA 50
    if any(ema_20s):
        fig.add_trace(
            go.Scatter(x=times, y=ema_20s, name="EMA 20", line=dict(color="#eab308", width=1.8)),
            row=1,
            col=1,
        )
    if any(ema_50s):
        fig.add_trace(
            go.Scatter(x=times, y=ema_50s, name="EMA 50", line=dict(color="#3b82f6", width=1.8)),
            row=1,
            col=1,
        )

    # Bollinger Bands
    if any(bb_uppers) and any(bb_lowers):
        fig.add_trace(
            go.Scatter(
                x=times,
                y=bb_uppers,
                name="BB Upper",
                line=dict(color="#a855f7", width=1, dash="dot"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=times,
                y=bb_lowers,
                name="BB Lower",
                line=dict(color="#a855f7", width=1, dash="dot"),
                fill="tonexty",
                fillcolor="rgba(168,85,247,0.06)",
            ),
            row=1,
            col=1,
        )

    # VWAP
    if any(vwaps):
        fig.add_trace(
            go.Scatter(
                x=times,
                y=vwaps,
                name="VWAP",
                line=dict(color="#ec4899", width=1.5, dash="dash"),
            ),
            row=1,
            col=1,
        )

    # 2. Volume (Row 2)
    vol_colors = ["#26a641" if c >= o else "#ef4444" for c, o in zip(closes, opens)]
    fig.add_trace(
        go.Bar(x=times, y=volumes, name="Volume", marker=dict(color=vol_colors)),
        row=2,
        col=1,
    )

    # 3. RSI Subplot (Row 3)
    if any(rsis):
        fig.add_trace(
            go.Scatter(x=times, y=rsis, name="RSI (14)", line=dict(color="#38bdf8", width=1.8)),
            row=3,
            col=1,
        )
        fig.add_hline(
            y=70,
            line_dash="dash",
            line_color="#ef4444",
            row=3,
            col=1,
            annotation_text="Overbought (70)",
        )
        fig.add_hline(
            y=30,
            line_dash="dash",
            line_color="#26a641",
            row=3,
            col=1,
            annotation_text="Oversold (30)",
        )

    # 4. MACD Subplot (Row 4)
    if any(macds) and any(macd_sigs):
        fig.add_trace(
            go.Scatter(x=times, y=macds, name="MACD", line=dict(color="#3b82f6", width=1.8)),
            row=4,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=times, y=macd_sigs, name="Signal Line", line=dict(color="#f97316", width=1.5)
            ),
            row=4,
            col=1,
        )
        if any(macd_hists):
            hist_colors = ["#26a641" if (h is not None and h >= 0) else "#ef4444" for h in macd_hists]
            fig.add_trace(
                go.Bar(x=times, y=macd_hists, name="MACD Hist", marker=dict(color=hist_colors)),
                row=4,
                col=1,
            )

    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COLOR),
        height=820,
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_rangeslider_visible=False,
    )

    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)

    return fig


def swing_analyzer_chart(symbol_or_candles, candles_or_symbol=None) -> go.Figure:
    """Build a 3-panel Daily Swing Trading chart (Price+EMA20/50/200, Volume, Daily RSI)."""
    if isinstance(symbol_or_candles, list):
        candles = symbol_or_candles
        symbol = str(candles_or_symbol) if candles_or_symbol else ""
    elif isinstance(candles_or_symbol, list):
        candles = candles_or_symbol
        symbol = str(symbol_or_candles) if symbol_or_candles else ""
    else:
        candles = []
        symbol = str(symbol_or_candles) if symbol_or_candles else ""

    if not candles:
        fig = go.Figure()
        fig.update_layout(
            title=f"No daily chart data for {symbol}",
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=PLOT_BG,
            font=dict(color=TEXT_COLOR),
        )
        return fig

    times = [c["time"] if isinstance(c, dict) else str(c) for c in candles]
    opens = [c["open"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    closes = [c["close"] for c in candles]
    volumes = [c["volume"] for c in candles]
    ema_20s = [c.get("ema_20") for c in candles]
    ema_50s = [c.get("ema_50") for c in candles]
    ema_200s = [c.get("ema_200") for c in candles]
    rsis = [c.get("rsi") for c in candles]

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.55, 0.20, 0.25],
        subplot_titles=(
            f"📈 {symbol} Daily Price + EMA 20/50/200",
            "📊 Volume (Surge)",
            "🟢 Daily RSI (14)",
        ),
    )

    # 1. Price Candlesticks
    fig.add_trace(
        go.Candlestick(
            x=times,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name="OHLC",
            increasing_line_color="#26a641",
            decreasing_line_color="#ef4444",
        ),
        row=1,
        col=1,
    )

    # Daily EMAs
    if any(ema_20s):
        fig.add_trace(
            go.Scatter(x=times, y=ema_20s, name="EMA 20 (Daily)", line=dict(color="#eab308", width=2)),
            row=1,
            col=1,
        )
    if any(ema_50s):
        fig.add_trace(
            go.Scatter(x=times, y=ema_50s, name="EMA 50 (Daily)", line=dict(color="#3b82f6", width=2)),
            row=1,
            col=1,
        )
    if any(ema_200s):
        fig.add_trace(
            go.Scatter(x=times, y=ema_200s, name="EMA 200 (Daily)", line=dict(color="#a855f7", width=1.8, dash="dash")),
            row=1,
            col=1,
        )

    # 2. Volume
    vol_colors = ["#26a641" if (c is not None and o is not None and c >= o) else "#ef4444" for c, o in zip(closes, opens)]
    fig.add_trace(
        go.Bar(x=times, y=volumes, name="Volume", marker=dict(color=vol_colors)),
        row=2,
        col=1,
    )

    # 3. Daily RSI
    if any(rsis):
        fig.add_trace(
            go.Scatter(x=times, y=rsis, name="RSI (14)", line=dict(color="#38bdf8", width=2)),
            row=3,
            col=1,
        )
        fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", row=3, col=1, annotation_text="Overbought (70)")
        fig.add_hline(y=50, line_dash="dot", line_color="#94a3b8", row=3, col=1, annotation_text="50 Line")
        fig.add_hline(y=40, line_dash="dash", line_color="#26a641", row=3, col=1, annotation_text="Oversold (40)")

    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COLOR),
        height=750,
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_rangeslider_visible=False,
    )

    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)

    return fig
