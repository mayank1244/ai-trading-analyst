"""Unit tests for Technical Indicators."""

import numpy as np
import pandas as pd
import pytest
from app.technical.indicators import indicators


@pytest.fixture
def sample_df():
    dates = pd.date_range(start="2024-01-01", periods=100)
    prices = 100 + np.cumsum(np.random.randn(100))
    df = pd.DataFrame(
        {
            "Open": prices + np.random.randn(100) * 0.5,
            "High": prices + np.abs(np.random.randn(100)),
            "Low": prices - np.abs(np.random.randn(100)),
            "Close": prices,
            "Volume": np.random.randint(1000, 100000, 100),
        },
        index=dates,
    )
    return df


def test_indicators_compute_all(sample_df):
    df, results = indicators.compute_all(sample_df)
    assert "EMA_9" in df.columns
    assert "EMA_50" in df.columns
    assert "RSI_14" in df.columns
    assert "MACD" in df.columns
    assert "Supertrend" in df.columns

    assert "RSI" in results
    assert "MACD" in results
    assert "EMA" in results
    assert "Supertrend" in results
