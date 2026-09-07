"""Deterministic provider-neutral features for one normalized option chain."""

from enum import StrEnum

from tiaf.context import AnalysisContext
from tiaf.contracts import OptionType
from tiaf.contracts.common import Metadata
from tiaf.features._derivatives_calculation import (
    DerivativesCalculator,
    MalformedDerivativeDataError,
    MissingDerivativeDataError,
    OptionChainInput,
    StrikeWindow,
    atm_strike_snapshot,
    chain_spot,
    exact_strike_window,
    finite_number,
    nonnegative_integer,
    option_side,
)
from tiaf.features.enums import FeatureCategory, FeatureSourceKind, FeatureValueType
from tiaf.features.errors import FeatureParameterError
from tiaf.features.models import FeatureDefinition, FeatureRequest, FeatureResult, FeatureValue
from tiaf.features.registry import FeatureCalculator


def _strikes_each_side(request: FeatureRequest) -> int:
    value = request.parameter("strikes_each_side")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise FeatureParameterError("strikes_each_side must be a nonnegative integer")
    return value


def _definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    value_type: FeatureValueType,
    unit: str,
    windowed: bool = False,
    category: FeatureCategory = FeatureCategory.DERIVATIVES,
    metadata: Metadata | None = None,
) -> FeatureDefinition:
    definition_metadata: Metadata = {
        "expiry_semantics": "one_explicit_analysis_context_option_expiry",
        "source_price_semantics": "option_chain_underlying_ltp",
    }
    if windowed:
        definition_metadata["window_semantics"] = (
            "exact_atm_plus_n_lower_and_n_higher_listed_strikes"
        )
    definition_metadata.update(metadata or {})
    return FeatureDefinition(
        feature_id=feature_id,
        name=name,
        category=category,
        description=description,
        value_type=value_type,
        unit=unit,
        required_sources=(FeatureSourceKind.OPTION_CHAIN,),
        metadata=definition_metadata,
    )


EXPIRY_DATE = _definition(
    "derivatives.expiry_date",
    "Option-chain expiry date",
    "ISO-8601 expiry date of the single normalized option-chain snapshot.",
    value_type=FeatureValueType.CATEGORY,
    unit="date",
)
DAYS_TO_EXPIRY = _definition(
    "derivatives.days_to_expiry",
    "Calendar days to expiry",
    "Calendar-day difference between chain expiry and chain source as-of date.",
    value_type=FeatureValueType.INTEGER,
    unit="days",
)
STRIKE_COUNT = _definition(
    "derivatives.strike_count",
    "Listed strike count",
    "Number of unique normalized listed strikes in the selected-expiry chain.",
    value_type=FeatureValueType.INTEGER,
    unit="strikes",
)
ATM_STRIKE = _definition(
    "derivatives.atm_strike",
    "Nearest ATM listed strike",
    "Listed strike nearest chain underlying LTP; equal-distance ties choose lower.",
    value_type=FeatureValueType.LEVEL,
    unit="price",
    metadata={"tie_rule": "lower_strike"},
)
ATM_DISTANCE_PERCENT = _definition(
    "derivatives.atm_distance_percent",
    "Spot distance from ATM strike",
    "Chain underlying LTP minus ATM strike, divided by chain underlying LTP.",
    value_type=FeatureValueType.FLOAT,
    unit="%",
    metadata={"formula": "(spot-atm_strike)/spot*100"},
)

ATM_CE_LTP = _definition(
    "derivatives.atm_ce_ltp",
    "ATM CE LTP",
    "Provider-supplied CE last-traded price at the resolved ATM strike.",
    value_type=FeatureValueType.FLOAT,
    unit="price",
)
ATM_PE_LTP = _definition(
    "derivatives.atm_pe_ltp",
    "ATM PE LTP",
    "Provider-supplied PE last-traded price at the resolved ATM strike.",
    value_type=FeatureValueType.FLOAT,
    unit="price",
)
ATM_STRADDLE_PREMIUM = _definition(
    "derivatives.atm_straddle_premium",
    "ATM combined premium",
    "Sum of provider-supplied ATM CE and PE last-traded prices.",
    value_type=FeatureValueType.FLOAT,
    unit="price",
    metadata={"formula": "atm_ce_ltp+atm_pe_ltp"},
)
ATM_STRADDLE_PERCENT = _definition(
    "derivatives.atm_straddle_percent_of_spot",
    "ATM combined premium percentage of spot",
    "ATM combined premium divided by chain underlying LTP.",
    value_type=FeatureValueType.FLOAT,
    unit="%",
    metadata={"formula": "(atm_ce_ltp+atm_pe_ltp)/spot*100"},
)
ATM_CE_IV = _definition(
    "derivatives.atm_ce_iv",
    "ATM CE implied volatility",
    "Provider-supplied implied volatility for the ATM CE contract.",
    value_type=FeatureValueType.FLOAT,
    unit="iv",
)
ATM_PE_IV = _definition(
    "derivatives.atm_pe_iv",
    "ATM PE implied volatility",
    "Provider-supplied implied volatility for the ATM PE contract.",
    value_type=FeatureValueType.FLOAT,
    unit="iv",
)
ATM_MEAN_IV = _definition(
    "derivatives.atm_mean_iv",
    "ATM mean implied volatility",
    "Arithmetic mean of provider-supplied ATM CE and PE implied volatility.",
    value_type=FeatureValueType.FLOAT,
    unit="iv",
)
ATM_IV_DIFFERENCE = _definition(
    "derivatives.atm_iv_difference",
    "ATM CE minus PE implied volatility",
    "Provider-supplied ATM CE implied volatility minus ATM PE implied volatility.",
    value_type=FeatureValueType.FLOAT,
    unit="iv",
)


def _window_definition(
    feature_id: str,
    name: str,
    description: str,
    *,
    value_type: FeatureValueType,
    unit: str,
) -> FeatureDefinition:
    return _definition(
        feature_id,
        name,
        description,
        value_type=value_type,
        unit=unit,
        windowed=True,
    )


CE_IV_MEAN = _window_definition(
    "derivatives.ce_iv_mean",
    "CE mean implied volatility",
    "Arithmetic mean of provider-supplied CE IV over the exact ATM-centered window.",
    value_type=FeatureValueType.FLOAT,
    unit="iv",
)
PE_IV_MEAN = _window_definition(
    "derivatives.pe_iv_mean",
    "PE mean implied volatility",
    "Arithmetic mean of provider-supplied PE IV over the exact ATM-centered window.",
    value_type=FeatureValueType.FLOAT,
    unit="iv",
)
CE_OI_TOTAL = _window_definition(
    "derivatives.ce_oi_total",
    "CE open-interest total",
    "Sum of CE open interest over the exact ATM-centered strike window.",
    value_type=FeatureValueType.INTEGER,
    unit="contracts",
)
PE_OI_TOTAL = _window_definition(
    "derivatives.pe_oi_total",
    "PE open-interest total",
    "Sum of PE open interest over the exact ATM-centered strike window.",
    value_type=FeatureValueType.INTEGER,
    unit="contracts",
)
OI_PUT_CALL_RATIO = _window_definition(
    "derivatives.oi_put_call_ratio",
    "PE to CE open-interest ratio",
    "PE open-interest total divided by CE total over the same exact strike window.",
    value_type=FeatureValueType.FLOAT,
    unit="ratio",
)
CE_VOLUME_TOTAL = _window_definition(
    "derivatives.ce_volume_total",
    "CE option-volume total",
    "Sum of CE option volume over the exact ATM-centered strike window.",
    value_type=FeatureValueType.INTEGER,
    unit="contracts",
)
PE_VOLUME_TOTAL = _window_definition(
    "derivatives.pe_volume_total",
    "PE option-volume total",
    "Sum of PE option volume over the exact ATM-centered strike window.",
    value_type=FeatureValueType.INTEGER,
    unit="contracts",
)
VOLUME_PUT_CALL_RATIO = _window_definition(
    "derivatives.volume_put_call_ratio",
    "PE to CE option-volume ratio",
    "PE option-volume total divided by CE total over the same exact strike window.",
    value_type=FeatureValueType.FLOAT,
    unit="ratio",
)
CE_MAX_OI_STRIKE = _window_definition(
    "derivatives.ce_max_oi_strike",
    "CE maximum-OI strike",
    "Strike with maximum CE open interest in the exact ATM-centered window.",
    value_type=FeatureValueType.LEVEL,
    unit="price",
)
PE_MAX_OI_STRIKE = _window_definition(
    "derivatives.pe_max_oi_strike",
    "PE maximum-OI strike",
    "Strike with maximum PE open interest in the exact ATM-centered window.",
    value_type=FeatureValueType.LEVEL,
    unit="price",
)
CE_MAX_OI = _window_definition(
    "derivatives.ce_max_oi",
    "CE maximum open interest",
    "Maximum CE open-interest value in the exact ATM-centered window.",
    value_type=FeatureValueType.INTEGER,
    unit="contracts",
)
PE_MAX_OI = _window_definition(
    "derivatives.pe_max_oi",
    "PE maximum open interest",
    "Maximum PE open-interest value in the exact ATM-centered window.",
    value_type=FeatureValueType.INTEGER,
    unit="contracts",
)
CE_OI_TOP1_FRACTION = _window_definition(
    "derivatives.ce_oi_top1_fraction",
    "CE top-strike OI fraction",
    "Largest CE strike OI divided by total CE OI in the exact window.",
    value_type=FeatureValueType.FLOAT,
    unit="fraction",
)
PE_OI_TOP1_FRACTION = _window_definition(
    "derivatives.pe_oi_top1_fraction",
    "PE top-strike OI fraction",
    "Largest PE strike OI divided by total PE OI in the exact window.",
    value_type=FeatureValueType.FLOAT,
    unit="fraction",
)
CE_OI_WEIGHTED_STRIKE = _window_definition(
    "derivatives.ce_oi_weighted_strike",
    "CE OI-weighted strike",
    "Open-interest-weighted CE strike center over the exact strike window.",
    value_type=FeatureValueType.LEVEL,
    unit="price",
)
PE_OI_WEIGHTED_STRIKE = _window_definition(
    "derivatives.pe_oi_weighted_strike",
    "PE OI-weighted strike",
    "Open-interest-weighted PE strike center over the exact strike window.",
    value_type=FeatureValueType.LEVEL,
    unit="price",
)


def _greek_definition(option_type: str, greek: str) -> FeatureDefinition:
    return _definition(
        f"derivatives.atm_{option_type}_{greek}",
        f"ATM {option_type.upper()} {greek}",
        f"Provider-supplied {greek} for the ATM {option_type.upper()} contract.",
        value_type=FeatureValueType.FLOAT,
        unit=greek,
    )


ATM_CE_DELTA = _greek_definition("ce", "delta")
ATM_PE_DELTA = _greek_definition("pe", "delta")
ATM_CE_GAMMA = _greek_definition("ce", "gamma")
ATM_PE_GAMMA = _greek_definition("pe", "gamma")
ATM_CE_THETA = _greek_definition("ce", "theta")
ATM_PE_THETA = _greek_definition("pe", "theta")
ATM_CE_VEGA = _greek_definition("ce", "vega")
ATM_PE_VEGA = _greek_definition("pe", "vega")

ATM_CE_SPREAD_PERCENT = _definition(
    "derivatives.atm_ce_bid_ask_spread_percent",
    "ATM CE bid-ask spread percentage",
    "ATM CE ask minus bid, divided by their midpoint and expressed as a percentage.",
    value_type=FeatureValueType.FLOAT,
    unit="%",
    category=FeatureCategory.LIQUIDITY,
)
ATM_PE_SPREAD_PERCENT = _definition(
    "derivatives.atm_pe_bid_ask_spread_percent",
    "ATM PE bid-ask spread percentage",
    "ATM PE ask minus bid, divided by their midpoint and expressed as a percentage.",
    value_type=FeatureValueType.FLOAT,
    unit="%",
    category=FeatureCategory.LIQUIDITY,
)


class _GeometryMode(StrEnum):
    EXPIRY = "expiry"
    DTE = "dte"
    COUNT = "count"
    ATM = "atm"
    ATM_DISTANCE = "atm_distance"


class GeometryCalculator(DerivativesCalculator):
    """Calculate explicit-expiry and nearest-listed-strike geometry."""

    def __init__(self, definition: FeatureDefinition, mode: _GeometryMode) -> None:
        self._definition = definition
        self._mode = mode

    def compute(self, context: AnalysisContext, request: FeatureRequest) -> FeatureResult:
        self._validate_derivatives_request(request)
        prepared, failure = self._prepare_option_chain(context, request)
        if failure is not None:
            return failure
        assert prepared is not None
        try:
            value: FeatureValue
            if self._mode is _GeometryMode.EXPIRY:
                value = prepared.chain.expiry.isoformat()
            elif self._mode is _GeometryMode.DTE:
                value = (prepared.chain.expiry - prepared.chain.observed_at.date()).days
            elif self._mode is _GeometryMode.COUNT:
                value = len(prepared.strikes)
            else:
                atm = atm_strike_snapshot(prepared)
                if self._mode is _GeometryMode.ATM:
                    value = float(atm.strike)
                else:
                    spot = chain_spot(prepared)
                    value = (spot - float(atm.strike)) / spot * 100
        except (MissingDerivativeDataError, MalformedDerivativeDataError) as exc:
            return self._derivative_failure(context, request, prepared, exc)
        return self._option_chain_result(context, request, prepared, value=value)


class _AtmMode(StrEnum):
    LTP = "ltp"
    STRADDLE = "straddle"
    STRADDLE_PERCENT = "straddle_percent"
    IV = "iv"
    IV_MEAN = "iv_mean"
    IV_DIFFERENCE = "iv_difference"
    GREEK = "greek"
    SPREAD_PERCENT = "spread_percent"


class AtmContractCalculator(DerivativesCalculator):
    """Calculate one field-local ATM contract measurement."""

    def __init__(
        self,
        definition: FeatureDefinition,
        mode: _AtmMode,
        option_type: OptionType | None = None,
        greek: str | None = None,
    ) -> None:
        self._definition = definition
        self._mode = mode
        self._option_type = option_type
        self._greek = greek

    @staticmethod
    def _ltp(prepared: OptionChainInput, option_type: OptionType) -> float:
        side = option_side(atm_strike_snapshot(prepared), option_type)
        return finite_number(side.ltp, f"ATM {option_type.value} ltp", nonnegative=True)

    @staticmethod
    def _iv(prepared: OptionChainInput, option_type: OptionType) -> float:
        side = option_side(atm_strike_snapshot(prepared), option_type)
        return finite_number(
            side.implied_volatility,
            f"ATM {option_type.value} implied_volatility",
            nonnegative=True,
        )

    def _calculate(self, prepared: OptionChainInput) -> float:
        if self._mode is _AtmMode.LTP:
            assert self._option_type is not None
            return self._ltp(prepared, self._option_type)
        if self._mode in {_AtmMode.STRADDLE, _AtmMode.STRADDLE_PERCENT}:
            premium = self._ltp(prepared, OptionType.CE) + self._ltp(
                prepared, OptionType.PE
            )
            if self._mode is _AtmMode.STRADDLE_PERCENT:
                return premium / chain_spot(prepared) * 100
            return premium
        if self._mode is _AtmMode.IV:
            assert self._option_type is not None
            return self._iv(prepared, self._option_type)
        if self._mode in {_AtmMode.IV_MEAN, _AtmMode.IV_DIFFERENCE}:
            ce_iv = self._iv(prepared, OptionType.CE)
            pe_iv = self._iv(prepared, OptionType.PE)
            return (ce_iv + pe_iv) / 2 if self._mode is _AtmMode.IV_MEAN else ce_iv - pe_iv
        assert self._option_type is not None
        side = option_side(atm_strike_snapshot(prepared), self._option_type)
        if self._mode is _AtmMode.GREEK:
            assert self._greek is not None
            value = finite_number(
                getattr(side.greeks, self._greek, None),
                f"ATM {self._option_type.value} {self._greek}",
            )
            if self._greek == "delta" and not -1 <= value <= 1:
                raise MalformedDerivativeDataError("option delta must be between -1 and 1")
            return value
        bid = finite_number(side.bid, f"ATM {self._option_type.value} bid", nonnegative=True)
        ask = finite_number(side.ask, f"ATM {self._option_type.value} ask", nonnegative=True)
        if bid == 0 or ask == 0:
            raise MissingDerivativeDataError(
                f"ATM {self._option_type.value} positive bid and ask are unavailable"
            )
        if ask < bid:
            raise MalformedDerivativeDataError(
                f"ATM {self._option_type.value} ask is below bid"
            )
        midpoint = (bid + ask) / 2
        if midpoint == 0:
            raise MalformedDerivativeDataError("bid-ask midpoint is zero")
        return (ask - bid) / midpoint * 100

    def compute(self, context: AnalysisContext, request: FeatureRequest) -> FeatureResult:
        self._validate_derivatives_request(request)
        prepared, failure = self._prepare_option_chain(context, request)
        if failure is not None:
            return failure
        assert prepared is not None
        try:
            value = self._calculate(prepared)
        except (MissingDerivativeDataError, MalformedDerivativeDataError) as exc:
            return self._derivative_failure(context, request, prepared, exc)
        return self._option_chain_result(context, request, prepared, value=value)


class _PositionMode(StrEnum):
    IV_MEAN = "iv_mean"
    OI_TOTAL = "oi_total"
    OI_RATIO = "oi_ratio"
    VOLUME_TOTAL = "volume_total"
    VOLUME_RATIO = "volume_ratio"
    MAX_OI_STRIKE = "max_oi_strike"
    MAX_OI = "max_oi"
    TOP1 = "top1"
    WEIGHTED = "weighted"


class WindowPositionCalculator(DerivativesCalculator):
    """Calculate exact-window OI and option-volume positioning primitives."""

    def __init__(
        self,
        definition: FeatureDefinition,
        mode: _PositionMode,
        option_type: OptionType | None = None,
    ) -> None:
        self._definition = definition
        self._mode = mode
        self._option_type = option_type

    @staticmethod
    def _values(
        window: StrikeWindow,
        option_type: OptionType,
        field: str,
    ) -> tuple[int, ...]:
        return tuple(
            nonnegative_integer(
                getattr(option_side(strike, option_type), field, None),
                f"{option_type.value} {field} at strike {strike.strike:g}",
            )
            for strike in window.strikes
        )

    @classmethod
    def _oi_values(
        cls,
        window: StrikeWindow,
        option_type: OptionType,
    ) -> tuple[int, ...]:
        return cls._values(window, option_type, "open_interest")

    def _calculate(self, window: StrikeWindow) -> int | float:
        if self._mode is _PositionMode.IV_MEAN:
            assert self._option_type is not None
            values = tuple(
                finite_number(
                    option_side(strike, self._option_type).implied_volatility,
                    f"{self._option_type.value} implied_volatility at "
                    f"strike {strike.strike:g}",
                    nonnegative=True,
                )
                for strike in window.strikes
            )
            return sum(values) / len(values)
        if self._mode in {_PositionMode.OI_RATIO, _PositionMode.VOLUME_RATIO}:
            field = (
                "open_interest"
                if self._mode is _PositionMode.OI_RATIO
                else "volume"
            )
            ce_total = sum(self._values(window, OptionType.CE, field))
            pe_total = sum(self._values(window, OptionType.PE, field))
            if ce_total == 0:
                raise MalformedDerivativeDataError(
                    f"PE/CE {field} ratio is undefined for zero CE total"
                )
            return pe_total / ce_total

        assert self._option_type is not None
        if self._mode in {_PositionMode.OI_TOTAL, _PositionMode.VOLUME_TOTAL}:
            field = (
                "open_interest"
                if self._mode is _PositionMode.OI_TOTAL
                else "volume"
            )
            return sum(self._values(window, self._option_type, field))

        values = self._oi_values(window, self._option_type)
        if self._mode in {_PositionMode.MAX_OI_STRIKE, _PositionMode.MAX_OI}:
            maximum = max(values)
            candidates = tuple(
                strike
                for strike, value in zip(window.strikes, values, strict=True)
                if value == maximum
            )
            selected = min(
                candidates,
                key=lambda strike: (
                    abs(float(strike.strike) - float(window.atm.strike)),
                    strike.strike,
                ),
            )
            return float(selected.strike) if self._mode is _PositionMode.MAX_OI_STRIKE else maximum

        total = sum(values)
        if total == 0:
            raise MalformedDerivativeDataError("OI statistic is undefined for zero total OI")
        if self._mode is _PositionMode.TOP1:
            return max(values) / total
        return sum(
            float(strike.strike) * value
            for strike, value in zip(window.strikes, values, strict=True)
        ) / total

    def compute(self, context: AnalysisContext, request: FeatureRequest) -> FeatureResult:
        self._validate_derivatives_request(
            request,
            parameter_names=("strikes_each_side",),
        )
        strikes_each_side = _strikes_each_side(request)
        prepared, failure = self._prepare_option_chain(context, request)
        if failure is not None:
            return failure
        assert prepared is not None
        try:
            window = exact_strike_window(prepared, strikes_each_side)
            value = self._calculate(window)
        except (MissingDerivativeDataError, MalformedDerivativeDataError) as exc:
            return self._derivative_failure(context, request, prepared, exc)
        return self._option_chain_result(
            context,
            request,
            prepared,
            value=value,
            metadata=window.metadata,
        )


DERIVATIVES_FEATURE_DEFINITIONS = (
    EXPIRY_DATE,
    DAYS_TO_EXPIRY,
    STRIKE_COUNT,
    ATM_STRIKE,
    ATM_DISTANCE_PERCENT,
    ATM_CE_LTP,
    ATM_PE_LTP,
    ATM_STRADDLE_PREMIUM,
    ATM_STRADDLE_PERCENT,
    ATM_CE_IV,
    ATM_PE_IV,
    ATM_MEAN_IV,
    ATM_IV_DIFFERENCE,
    CE_IV_MEAN,
    PE_IV_MEAN,
    CE_OI_TOTAL,
    PE_OI_TOTAL,
    OI_PUT_CALL_RATIO,
    CE_VOLUME_TOTAL,
    PE_VOLUME_TOTAL,
    VOLUME_PUT_CALL_RATIO,
    CE_MAX_OI_STRIKE,
    PE_MAX_OI_STRIKE,
    CE_MAX_OI,
    PE_MAX_OI,
    CE_OI_TOP1_FRACTION,
    PE_OI_TOP1_FRACTION,
    CE_OI_WEIGHTED_STRIKE,
    PE_OI_WEIGHTED_STRIKE,
    ATM_CE_DELTA,
    ATM_PE_DELTA,
    ATM_CE_GAMMA,
    ATM_PE_GAMMA,
    ATM_CE_THETA,
    ATM_PE_THETA,
    ATM_CE_VEGA,
    ATM_PE_VEGA,
    ATM_CE_SPREAD_PERCENT,
    ATM_PE_SPREAD_PERCENT,
)

DERIVATIVES_CALCULATORS: tuple[FeatureCalculator, ...] = (
    GeometryCalculator(EXPIRY_DATE, _GeometryMode.EXPIRY),
    GeometryCalculator(DAYS_TO_EXPIRY, _GeometryMode.DTE),
    GeometryCalculator(STRIKE_COUNT, _GeometryMode.COUNT),
    GeometryCalculator(ATM_STRIKE, _GeometryMode.ATM),
    GeometryCalculator(ATM_DISTANCE_PERCENT, _GeometryMode.ATM_DISTANCE),
    AtmContractCalculator(ATM_CE_LTP, _AtmMode.LTP, OptionType.CE),
    AtmContractCalculator(ATM_PE_LTP, _AtmMode.LTP, OptionType.PE),
    AtmContractCalculator(ATM_STRADDLE_PREMIUM, _AtmMode.STRADDLE),
    AtmContractCalculator(ATM_STRADDLE_PERCENT, _AtmMode.STRADDLE_PERCENT),
    AtmContractCalculator(ATM_CE_IV, _AtmMode.IV, OptionType.CE),
    AtmContractCalculator(ATM_PE_IV, _AtmMode.IV, OptionType.PE),
    AtmContractCalculator(ATM_MEAN_IV, _AtmMode.IV_MEAN),
    AtmContractCalculator(ATM_IV_DIFFERENCE, _AtmMode.IV_DIFFERENCE),
    WindowPositionCalculator(CE_IV_MEAN, _PositionMode.IV_MEAN, OptionType.CE),
    WindowPositionCalculator(PE_IV_MEAN, _PositionMode.IV_MEAN, OptionType.PE),
    WindowPositionCalculator(CE_OI_TOTAL, _PositionMode.OI_TOTAL, OptionType.CE),
    WindowPositionCalculator(PE_OI_TOTAL, _PositionMode.OI_TOTAL, OptionType.PE),
    WindowPositionCalculator(OI_PUT_CALL_RATIO, _PositionMode.OI_RATIO),
    WindowPositionCalculator(CE_VOLUME_TOTAL, _PositionMode.VOLUME_TOTAL, OptionType.CE),
    WindowPositionCalculator(PE_VOLUME_TOTAL, _PositionMode.VOLUME_TOTAL, OptionType.PE),
    WindowPositionCalculator(VOLUME_PUT_CALL_RATIO, _PositionMode.VOLUME_RATIO),
    WindowPositionCalculator(
        CE_MAX_OI_STRIKE, _PositionMode.MAX_OI_STRIKE, OptionType.CE
    ),
    WindowPositionCalculator(
        PE_MAX_OI_STRIKE, _PositionMode.MAX_OI_STRIKE, OptionType.PE
    ),
    WindowPositionCalculator(CE_MAX_OI, _PositionMode.MAX_OI, OptionType.CE),
    WindowPositionCalculator(PE_MAX_OI, _PositionMode.MAX_OI, OptionType.PE),
    WindowPositionCalculator(CE_OI_TOP1_FRACTION, _PositionMode.TOP1, OptionType.CE),
    WindowPositionCalculator(PE_OI_TOP1_FRACTION, _PositionMode.TOP1, OptionType.PE),
    WindowPositionCalculator(
        CE_OI_WEIGHTED_STRIKE, _PositionMode.WEIGHTED, OptionType.CE
    ),
    WindowPositionCalculator(
        PE_OI_WEIGHTED_STRIKE, _PositionMode.WEIGHTED, OptionType.PE
    ),
    AtmContractCalculator(ATM_CE_DELTA, _AtmMode.GREEK, OptionType.CE, "delta"),
    AtmContractCalculator(ATM_PE_DELTA, _AtmMode.GREEK, OptionType.PE, "delta"),
    AtmContractCalculator(ATM_CE_GAMMA, _AtmMode.GREEK, OptionType.CE, "gamma"),
    AtmContractCalculator(ATM_PE_GAMMA, _AtmMode.GREEK, OptionType.PE, "gamma"),
    AtmContractCalculator(ATM_CE_THETA, _AtmMode.GREEK, OptionType.CE, "theta"),
    AtmContractCalculator(ATM_PE_THETA, _AtmMode.GREEK, OptionType.PE, "theta"),
    AtmContractCalculator(ATM_CE_VEGA, _AtmMode.GREEK, OptionType.CE, "vega"),
    AtmContractCalculator(ATM_PE_VEGA, _AtmMode.GREEK, OptionType.PE, "vega"),
    AtmContractCalculator(
        ATM_CE_SPREAD_PERCENT, _AtmMode.SPREAD_PERCENT, OptionType.CE
    ),
    AtmContractCalculator(
        ATM_PE_SPREAD_PERCENT, _AtmMode.SPREAD_PERCENT, OptionType.PE
    ),
)
