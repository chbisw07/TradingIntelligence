"""Pure provider-neutral option-chain preparation and numerical guards."""

import math
from dataclasses import dataclass
from typing import Any, cast

from tiaf.context import AnalysisContext, EvidenceDescriptor
from tiaf.contracts import DataQuality, OptionType
from tiaf.contracts.common import Metadata
from tiaf.data import OptionChainSnapshot, OptionMarketSnapshot, OptionStrikeSnapshot
from tiaf.features._calculation import (
    A22Calculator,
    evidence,
    evidence_status,
    evidence_warnings,
    source_quality,
)
from tiaf.features.enums import FeatureStatus
from tiaf.features.errors import FeatureParameterError
from tiaf.features.models import FeatureRequest, FeatureResult, FeatureValue


class MissingDerivativeDataError(ValueError):
    """Required normalized option-chain fact is absent."""


class MalformedDerivativeDataError(ValueError):
    """Option-chain fact is present but numerically or structurally invalid."""


@dataclass(frozen=True)
class OptionChainInput:
    """Validated single-expiry option chain and its source provenance."""

    chain: OptionChainSnapshot
    strikes: tuple[OptionStrikeSnapshot, ...]
    descriptor: EvidenceDescriptor
    status: FeatureStatus
    quality: DataQuality
    metadata: Metadata
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class StrikeWindow:
    """Exact ATM-centered window over actual listed strikes."""

    strikes: tuple[OptionStrikeSnapshot, ...]
    atm: OptionStrikeSnapshot
    strikes_each_side: int

    @property
    def metadata(self) -> Metadata:
        return {
            "window_semantics": "exact_atm_centered_listed_strikes",
            "strikes_each_side": self.strikes_each_side,
            "requested_strike_count": 2 * self.strikes_each_side + 1,
            "actual_strike_count": len(self.strikes),
            "window_min_strike": float(self.strikes[0].strike),
            "window_max_strike": float(self.strikes[-1].strike),
        }


def finite_number(value: Any, field_name: str, *, nonnegative: bool = False) -> float:
    """Return one finite numeric fact, distinguishing missing from malformed."""
    if value is None:
        raise MissingDerivativeDataError(f"{field_name} is unavailable")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MalformedDerivativeDataError(f"{field_name} is not numeric")
    result = float(value)
    if not math.isfinite(result):
        raise MalformedDerivativeDataError(f"{field_name} is non-finite")
    if nonnegative and result < 0:
        raise MalformedDerivativeDataError(f"{field_name} is negative")
    return result


def nonnegative_integer(value: Any, field_name: str) -> int:
    """Return one nonnegative integral count without coercing malformed facts."""
    if value is None:
        raise MissingDerivativeDataError(f"{field_name} is unavailable")
    if isinstance(value, bool) or not isinstance(value, int):
        raise MalformedDerivativeDataError(f"{field_name} is not an integer")
    if value < 0:
        raise MalformedDerivativeDataError(f"{field_name} is negative")
    return cast(int, value)


def chain_spot(prepared: OptionChainInput) -> float:
    """Return the snapshot-consistent positive chain underlying LTP."""
    spot = finite_number(
        prepared.chain.underlying_ltp,
        "option-chain underlying_ltp",
        nonnegative=True,
    )
    if spot == 0:
        raise MalformedDerivativeDataError("option-chain underlying_ltp must be positive")
    return spot


def atm_strike_snapshot(prepared: OptionChainInput) -> OptionStrikeSnapshot:
    """Resolve nearest listed strike; equal distances choose the lower strike."""
    spot = chain_spot(prepared)
    return min(prepared.strikes, key=lambda item: (abs(float(item.strike) - spot), item.strike))


def exact_strike_window(
    prepared: OptionChainInput,
    strikes_each_side: int,
) -> StrikeWindow:
    """Select exactly N listed strikes below and above ATM or fail explicitly."""
    atm = atm_strike_snapshot(prepared)
    index = prepared.strikes.index(atm)
    start = index - strikes_each_side
    stop = index + strikes_each_side + 1
    if start < 0 or stop > len(prepared.strikes):
        raise MissingDerivativeDataError(
            "exact ATM-centered window is unavailable at the chain edge: "
            f"requires {strikes_each_side} listed strikes on each side"
        )
    return StrikeWindow(
        strikes=prepared.strikes[start:stop],
        atm=atm,
        strikes_each_side=strikes_each_side,
    )


def option_side(
    strike: OptionStrikeSnapshot,
    option_type: OptionType,
) -> OptionMarketSnapshot:
    """Return the explicitly keyed option side without adjacency assumptions."""
    side = strike.call if option_type is OptionType.CE else strike.put
    if side is None:
        raise MissingDerivativeDataError(
            f"{option_type.value} side is unavailable at strike {strike.strike:g}"
        )
    return side


def _validate_chain_structure(
    context: AnalysisContext,
    chain: OptionChainSnapshot,
) -> tuple[OptionStrikeSnapshot, ...]:
    if not chain.strikes:
        raise MissingDerivativeDataError("option chain contains no strikes")
    if chain.expiry != context.requirements.option_expiry:
        raise MalformedDerivativeDataError(
            "option-chain expiry does not match the explicitly requested expiry"
        )
    if chain.expiry < chain.observed_at.date():
        raise MalformedDerivativeDataError("option-chain expiry is before its as-of date")
    if chain.underlying != context.subject.resolved_instrument.instrument:
        raise MalformedDerivativeDataError("option chain does not match context subject")

    normalized: list[tuple[float, OptionStrikeSnapshot]] = []
    for strike in chain.strikes:
        numeric_strike = finite_number(strike.strike, "strike")
        if numeric_strike <= 0:
            raise MalformedDerivativeDataError("strike must be positive")
        for expected, side in ((OptionType.CE, strike.call), (OptionType.PE, strike.put)):
            if side is None:
                continue
            if side.option_type is not expected:
                raise MalformedDerivativeDataError("option side identity is inconsistent")
            if side.strike != strike.strike:
                raise MalformedDerivativeDataError("option side strike is inconsistent")
            if side.expiry != chain.expiry:
                raise MalformedDerivativeDataError("option side expiry is inconsistent")
        normalized.append((numeric_strike, strike))
    normalized.sort(key=lambda pair: pair[0])
    values = tuple(pair[0] for pair in normalized)
    if len(values) != len(set(values)):
        raise MalformedDerivativeDataError("option chain contains duplicate strikes")
    return tuple(pair[1] for pair in normalized)


class DerivativesCalculator(A22Calculator):
    """Base for deterministic features over one embedded option-chain snapshot."""

    def _validate_derivatives_request(
        self,
        request: FeatureRequest,
        *,
        parameter_names: tuple[str, ...] = (),
    ) -> None:
        self._validate_request(request, parameter_names=parameter_names)
        if request.interval is not None:
            raise FeatureParameterError(
                f"feature {request.feature_id!r} does not accept an interval"
            )

    def _prepare_option_chain(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
    ) -> tuple[OptionChainInput | None, FeatureResult | None]:
        descriptor = evidence(context, "option_chain")
        chain = context.option_chain
        quality = source_quality(descriptor, chain.quality if chain is not None else None)
        status = evidence_status(descriptor, chain.quality if chain is not None else None)
        as_of = (
            chain.observed_at
            if chain is not None
            else (
                descriptor.source_observed_at
                if descriptor is not None and descriptor.source_observed_at is not None
                else context.created_at
            )
        )
        metadata: Metadata = {
            "source_time_semantics": (
                descriptor.source_observation_semantics
                if descriptor is not None
                and descriptor.source_observation_semantics is not None
                else "option_chain_source_observation"
            ),
            "expiry_provenance": "analysis_context.requirements.option_expiry",
        }
        if chain is not None:
            metadata.update(
                {
                    "option_chain_expiry": chain.expiry.isoformat(),
                    "option_chain_observed_at": chain.observed_at.isoformat(),
                    "option_chain_received_at": chain.received_at.isoformat(),
                    "underlying_ltp_source": "option_chain_snapshot",
                }
            )
            if chain.snapshot_id is not None:
                metadata["option_chain_snapshot_id"] = chain.snapshot_id
        if status not in {FeatureStatus.AVAILABLE, FeatureStatus.PARTIAL}:
            return None, self._result(
                context,
                request,
                status=status,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("option_chain",),
                source_observed_at=as_of if chain is not None else None,
                warnings=evidence_warnings(descriptor),
                metadata=metadata,
            )
        if chain is None or descriptor is None:
            return None, self._result(
                context,
                request,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("option_chain",),
                source_observed_at=None,
                warnings=("usable option-chain evidence has no embedded snapshot",),
                metadata=metadata,
            )
        try:
            strikes = _validate_chain_structure(context, chain)
        except MissingDerivativeDataError as exc:
            return None, self._result(
                context,
                request,
                status=FeatureStatus.INSUFFICIENT_DATA,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("option_chain",),
                source_observed_at=as_of,
                warnings=(str(exc),),
                metadata=metadata,
            )
        except MalformedDerivativeDataError as exc:
            return None, self._result(
                context,
                request,
                status=FeatureStatus.FAILED,
                value=None,
                quality=quality,
                as_of=as_of,
                source_evidence=("option_chain",),
                source_observed_at=as_of,
                warnings=(str(exc),),
                metadata=metadata,
            )
        return (
            OptionChainInput(
                chain=chain,
                strikes=strikes,
                descriptor=descriptor,
                status=status,
                quality=quality,
                metadata=metadata,
                warnings=evidence_warnings(descriptor),
            ),
            None,
        )

    def _option_chain_result(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
        prepared: OptionChainInput,
        *,
        value: FeatureValue,
        status: FeatureStatus | None = None,
        warnings: tuple[str, ...] = (),
        metadata: Metadata | None = None,
    ) -> FeatureResult:
        return self._result(
            context,
            request,
            status=status or prepared.status,
            value=value,
            quality=prepared.quality,
            as_of=prepared.chain.observed_at,
            source_evidence=("option_chain",),
            source_observed_at=prepared.chain.observed_at,
            warnings=prepared.warnings + warnings,
            metadata={**prepared.metadata, **(metadata or {})},
        )

    def _derivative_failure(
        self,
        context: AnalysisContext,
        request: FeatureRequest,
        prepared: OptionChainInput,
        error: MissingDerivativeDataError | MalformedDerivativeDataError,
        *,
        metadata: Metadata | None = None,
    ) -> FeatureResult:
        status = (
            FeatureStatus.INSUFFICIENT_DATA
            if isinstance(error, MissingDerivativeDataError)
            else FeatureStatus.FAILED
        )
        return self._option_chain_result(
            context,
            request,
            prepared,
            status=status,
            value=None,
            warnings=(str(error),),
            metadata=metadata,
        )
