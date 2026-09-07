"""Stable definitions for the initial TIAF indicator library."""

from tiaf.features.enums import FeatureSourceKind
from tiaf.indicators.enums import IndicatorParameterType
from tiaf.indicators.models import (
    IndicatorDefinition,
    IndicatorOutputDefinition,
    IndicatorParameterDefinition,
    IndicatorStateDefinition,
)


def _integer_parameter(name: str, default: int, description: str) -> IndicatorParameterDefinition:
    return IndicatorParameterDefinition(
        name=name,
        value_type=IndicatorParameterType.INTEGER,
        has_default=True,
        default=default,
        minimum_exclusive=0,
        description=description,
    )


def _float_parameter(name: str, default: float, description: str) -> IndicatorParameterDefinition:
    return IndicatorParameterDefinition(
        name=name,
        value_type=IndicatorParameterType.FLOAT,
        has_default=True,
        default=default,
        minimum_exclusive=0,
        description=description,
    )


def _output(name: str, unit: str, description: str) -> IndicatorOutputDefinition:
    return IndicatorOutputDefinition(name=name, unit=unit, description=description)


SUPERTREND = IndicatorDefinition(
    indicator_id="supertrend",
    name="SuperTrend",
    description="ATR-based completed-bar trailing band and price relation.",
    parameters=(
        _integer_parameter("period", 10, "Wilder ATR period."),
        _float_parameter("multiplier", 3.0, "Positive ATR band multiplier."),
    ),
    required_sources=(FeatureSourceKind.HISTORY,),
    outputs=(
        _output("basic_upper_band", "price", "Latest unsmoothed upper ATR band."),
        _output("basic_lower_band", "price", "Latest unsmoothed lower ATR band."),
        _output("final_upper_band", "price", "Latest recursively constrained upper band."),
        _output("final_lower_band", "price", "Latest recursively constrained lower band."),
        _output("line", "price", "Latest active SuperTrend band."),
    ),
    states=(
        IndicatorStateDefinition(
            name="relation",
            allowed_values=("ABOVE_LINE", "BELOW_LINE", "ON_LINE"),
            description="Latest completed close relative to the line.",
        ),
        IndicatorStateDefinition(
            name="active_band",
            allowed_values=("UPPER_BAND_ACTIVE", "LOWER_BAND_ACTIVE"),
            description="Final band supplying the latest line.",
        ),
    ),
    minimum_history_bars=11,
    metadata={"price_basis": "hl2", "atr_method": "wilder"},
)

RSI = IndicatorDefinition(
    indicator_id="rsi",
    name="Relative Strength Index",
    description="Wilder-smoothed ratio of completed-close gains and losses.",
    parameters=(_integer_parameter("period", 14, "Wilder gain/loss period."),),
    outputs=(_output("rsi", "index_0_100", "Latest Wilder RSI."),),
    minimum_history_bars=15,
    metadata={"method": "wilder", "flat_series_value": 50.0},
)

MACD = IndicatorDefinition(
    indicator_id="macd",
    name="Moving Average Convergence Divergence",
    description="Difference of canonical fast/slow EMAs with an EMA signal line.",
    parameters=(
        _integer_parameter("fast_period", 12, "Fast EMA period."),
        _integer_parameter("slow_period", 26, "Slow EMA period."),
        _integer_parameter("signal_period", 9, "MACD-series signal EMA period."),
    ),
    outputs=(
        _output("macd", "price", "Latest fast EMA minus slow EMA."),
        _output("signal", "price", "Latest EMA of the MACD series."),
        _output("histogram", "price", "Latest MACD minus signal."),
    ),
    minimum_history_bars=34,
    metadata={"ema_initialization": "first_period_sma"},
)

ADX = IndicatorDefinition(
    indicator_id="adx",
    name="Average Directional Index",
    description="Wilder ADX with positive and negative directional indicators.",
    parameters=(_integer_parameter("period", 14, "Wilder smoothing period."),),
    outputs=(
        _output("adx", "index_0_100", "Latest Wilder average of DX."),
        _output("plus_di", "index_0_100", "Latest positive directional indicator."),
        _output("minus_di", "index_0_100", "Latest negative directional indicator."),
    ),
    minimum_history_bars=28,
    metadata={"method": "wilder", "warmup": "two_times_period_bars"},
)

BOLLINGER = IndicatorDefinition(
    indicator_id="bollinger",
    name="Bollinger Bands",
    description="SMA-centered population-standard-deviation bands.",
    parameters=(
        IndicatorParameterDefinition(
            name="period",
            value_type=IndicatorParameterType.INTEGER,
            has_default=True,
            default=20,
            minimum_exclusive=1,
            description="Exact completed-close window, greater than one.",
        ),
        _float_parameter("stddev_multiplier", 2.0, "Positive population deviation multiplier."),
    ),
    outputs=(
        _output("middle", "price", "Latest-period SMA."),
        _output("upper", "price", "Middle plus multiplied population deviation."),
        _output("lower", "price", "Middle minus multiplied population deviation."),
        _output("bandwidth_percent", "%", "Band width divided by middle times 100."),
        _output("percent_b", "ratio", "Latest close location between lower and upper."),
    ),
    minimum_history_bars=20,
    metadata={"dispersion": "population_standard_deviation", "flat_percent_b": 0.5},
)

DONCHIAN = IndicatorDefinition(
    indicator_id="donchian",
    name="Donchian Channel",
    description="Exact completed-bar high/low channel and close position.",
    parameters=(_integer_parameter("period", 20, "Exact completed-bar window."),),
    outputs=(
        _output("upper", "price", "Highest high in the exact period."),
        _output("lower", "price", "Lowest low in the exact period."),
        _output("middle", "price", "Arithmetic midpoint of channel bounds."),
        _output("position_percent", "%", "Latest close position within channel."),
    ),
    minimum_history_bars=20,
    metadata={"flat_channel": "insufficient_data"},
)

BUILTIN_INDICATOR_DEFINITIONS = (
    SUPERTREND,
    RSI,
    MACD,
    ADX,
    BOLLINGER,
    DONCHIAN,
)
