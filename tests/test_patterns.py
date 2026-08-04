"""Unit tests for Candlestick Patterns."""

import numpy as np
import pandas as pd
import pytest
from app.patterns.candlestick import pattern_detector


def test_candlestick_detector():
    dates = pd.date_range(start="2024-01-01", periods=10)
    df = pd.DataFrame(
        {
            "Open": [100, 102, 104, 103, 105, 107, 106, 108, 110, 100],
            "High": [105, 106, 108, 107, 109, 110, 109, 112, 114, 102],
            "Low": [98, 100, 102, 101, 103, 105, 104, 106, 108, 90],  # hammer-like at last
            "Close": [102, 104, 103, 105, 107, 106, 108, 110, 108, 101],
            "Volume": [1000] * 10,
        },
        index=dates,
    )

    res = pattern_detector.detect_all(df)
    assert hasattr(res, "pattern_score")
    assert 0.0 <= res.pattern_score <= 100.0
