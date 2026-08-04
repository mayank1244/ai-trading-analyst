"""Risk Calculator module."""

from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass
class RiskParams:
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    risk_amount: float
    reward_1: float
    reward_2: float
    risk_reward_1: float
    risk_reward_2: float
    holding_period: str
    position_size_pct: float
    atr: float
    stop_loss_pct: float
    target_1_pct: float
    target_2_pct: float


class RiskCalculator:
    def compute(
        self, df: pd.DataFrame, recommendation: str, current_price: Optional[float] = None
    ) -> RiskParams:
        price = current_price if current_price else float(df["Close"].iloc[-1])

        # Approximate ATR
        if "ATR_14" in df.columns:
            atr = float(df["ATR_14"].iloc[-1])
        else:
            high_low = df["High"] - df["Low"]
            atr = float(high_low.tail(14).mean())

        if atr <= 0 or pd.isna(atr):
            atr = price * 0.02

        if recommendation in ["BUY", "STRONG_BUY"]:
            sl = round(price - 1.5 * atr, 2)
            t1 = round(price + 2.0 * atr, 2)
            t2 = round(price + 3.5 * atr, 2)
        elif recommendation in ["SELL", "STRONG_SELL"]:
            sl = round(price + 1.5 * atr, 2)
            t1 = round(price - 2.0 * atr, 2)
            t2 = round(price - 3.5 * atr, 2)
        else:  # HOLD / WATCHLIST
            sl = round(price - 1.5 * atr, 2)
            t1 = round(price + 2.0 * atr, 2)
            t2 = round(price + 3.5 * atr, 2)

        risk = abs(price - sl)
        reward1 = abs(t1 - price)
        reward2 = abs(t2 - price)

        rr1 = round(reward1 / risk, 2) if risk > 0 else 1.0
        rr2 = round(reward2 / risk, 2) if risk > 0 else 2.0

        sl_pct = round((sl - price) / price * 100, 2)
        t1_pct = round((t1 - price) / price * 100, 2)
        t2_pct = round((t2 - price) / price * 100, 2)

        holding = "1-2 weeks" if atr / price < 0.025 else "3-5 days"

        return RiskParams(
            entry_price=round(price, 2),
            stop_loss=sl,
            target_1=t1,
            target_2=t2,
            risk_amount=round(risk, 2),
            reward_1=round(reward1, 2),
            reward_2=round(reward2, 2),
            risk_reward_1=rr1,
            risk_reward_2=rr2,
            holding_period=holding,
            position_size_pct=5.0,
            atr=round(atr, 2),
            stop_loss_pct=sl_pct,
            target_1_pct=t1_pct,
            target_2_pct=t2_pct,
        )


risk_calculator = RiskCalculator()
