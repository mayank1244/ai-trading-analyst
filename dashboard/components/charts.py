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
