"""Backtesting Engine module."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class TradeRecord:
    symbol: str
    action: str
    entry_price: float
    entry_date: datetime
    stop_loss: float
    target_1: float
    target_2: float
    confidence: float
    quant_score: float
    exit_price: Optional[float] = None
    exit_date: Optional[datetime] = None
    exit_reason: str = "OPEN"
    actual_return_pct: float = 0.0
    holding_days: int = 0
    status: str = "OPEN"


@dataclass
class BacktestMetrics:
    total_trades: int
    win_rate: float
    avg_return: float
    win_count: int
    loss_count: int
    trades: List[TradeRecord] = field(default_factory=list)


class BacktestEngine:
    def __init__(self):
        self._trades: List[TradeRecord] = []

    def add_trade(self, rec) -> TradeRecord:
        trade = TradeRecord(
            symbol=rec.symbol,
            action=rec.action,
            entry_price=rec.entry_price,
            entry_date=datetime.now(),
            stop_loss=rec.stop_loss,
            target_1=rec.target_1,
            target_2=rec.target_2,
            confidence=rec.confidence,
            quant_score=rec.quant_score,
        )
        self._trades.append(trade)
        return trade

    def compute_metrics(self) -> BacktestMetrics:
        closed = [t for t in self._trades if t.status == "CLOSED"]
        if not closed:
            return BacktestMetrics(
                total_trades=len(self._trades),
                win_rate=0.0,
                avg_return=0.0,
                win_count=0,
                loss_count=0,
                trades=self._trades,
            )

        wins = [t for t in closed if (t.actual_return_pct or 0) > 0]
        losses = [t for t in closed if (t.actual_return_pct or 0) <= 0]

        win_rate = len(wins) / len(closed) * 100
        avg_ret = sum(t.actual_return_pct or 0 for t in closed) / len(closed)

        return BacktestMetrics(
            total_trades=len(self._trades),
            win_rate=round(win_rate, 1),
            avg_return=round(avg_ret, 2),
            win_count=len(wins),
            loss_count=len(losses),
            trades=self._trades,
        )


backtest_engine = BacktestEngine()
