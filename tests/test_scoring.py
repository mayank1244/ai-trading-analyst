"""Unit tests for Quantitative Scoring Engine."""

import numpy as np
import pandas as pd
import pytest
from app.patterns.candlestick import pattern_detector
from app.price_action.detector import price_action_detector
from app.strategy.scoring import scoring_engine
from app.technical.indicators import indicators


def test_quant_scoring_engine():
    dates = pd.date_range(start="2024-01-01", periods=60)
    prices = np.linspace(100, 150, 60)
    df = pd.DataFrame(
        {
            "Open": prices,
            "High": prices + 2,
            "Low": prices - 2,
            "Close": prices + 1,
            "Volume": [50000] * 60,
        },
        index=dates,
    )

    df_ind, ind_res = indicators.compute_all(df)
    pa_res = price_action_detector.analyze(df_ind)
    pat_res = pattern_detector.detect_all(df_ind)

    quant_res = scoring_engine.compute(df_ind, ind_res, pa_res, pat_res)

    assert 0.0 <= quant_res.total_score <= 100.0
    assert quant_res.direction in ["BULLISH", "BEARISH", "NEUTRAL"]
