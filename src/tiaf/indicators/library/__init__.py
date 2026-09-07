"""Initial deterministic completed-history indicator calculators."""

from tiaf.indicators.library.adx import AdxCalculator
from tiaf.indicators.library.bollinger import BollingerCalculator
from tiaf.indicators.library.donchian import DonchianCalculator
from tiaf.indicators.library.macd import MacdCalculator
from tiaf.indicators.library.rsi import RsiCalculator
from tiaf.indicators.library.supertrend import SuperTrendCalculator

BUILTIN_INDICATOR_CALCULATORS = (
    SuperTrendCalculator(),
    RsiCalculator(),
    MacdCalculator(),
    AdxCalculator(),
    BollingerCalculator(),
    DonchianCalculator(),
)

__all__ = ["BUILTIN_INDICATOR_CALCULATORS"]
