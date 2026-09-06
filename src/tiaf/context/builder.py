"""Dependency-injected factual AnalysisContext builder."""

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any, TypeVar
from uuid import uuid4

from tiaf.context.enums import BatchItemStatus, EvidenceRequirement, EvidenceStatus
from tiaf.context.errors import (
    AnalysisContextBuildError,
    AnalysisContextDeferredError,
    AnalysisContextError,
    AnalysisContextResolutionError,
    RequiredEvidenceUnavailableError,
)
from tiaf.context.models import (
    AnalysisContext,
    AnalysisContextBatchItem,
    AnalysisSubject,
    EvidenceDescriptor,
)
from tiaf.context.requirements import (
    AnalysisContextRequirement,
    HistoricalOptionRequirement,
)
from tiaf.contracts import DataQuality, FreshnessState
from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.data import (
    DerivativesDataProvider,
    HistoricalOptionsDataProvider,
    HistoricalOptionSeries,
    HistoricalSeries,
    InstrumentQuery,
    MarketDataProvider,
    OptionChainSnapshot,
    QuoteSnapshot,
    TIAFDataError,
)
from tiaf.data.normalization import normalize_datetime_to_ist
from tiaf.data.resolution import InstrumentResolver, ResolvedInstrument
from tiaf.data.runtime import (
    CacheDisposition,
    CacheKey,
    DataFetchCoordinator,
    FetchDisposition,
    FetchResult,
    FreshnessPolicyRegistry,
    FreshnessRequirement,
    ProviderScheduleBlockedError,
)

T = TypeVar("T")


def _wall_now() -> datetime:
    return datetime.now(TIAF_TIMEZONE)


def _new_context_id() -> str:
    return str(uuid4())


class AnalysisContextBuilder:
    """Assemble normalized evidence exclusively through the A1.6 coordinator."""

    def __init__(
        self,
        resolver: InstrumentResolver,
        market_data_provider: MarketDataProvider,
        coordinator: DataFetchCoordinator,
        *,
        derivatives_provider: DerivativesDataProvider | None = None,
        historical_options_provider: HistoricalOptionsDataProvider | None = None,
        freshness_policies: FreshnessPolicyRegistry | None = None,
        clock: Callable[[], datetime] = _wall_now,
        context_id_factory: Callable[[], str] = _new_context_id,
    ) -> None:
        self._resolver = resolver
        self._market_data_provider = market_data_provider
        self._derivatives_provider = derivatives_provider
        self._historical_options_provider = historical_options_provider
        self._coordinator = coordinator
        self._freshness_policies = freshness_policies or FreshnessPolicyRegistry()
        self._clock = clock
        self._context_id_factory = context_id_factory

    def build(
        self,
        symbol_or_query: str | InstrumentQuery,
        requirements: AnalysisContextRequirement,
        *,
        context_id: str | None = None,
        correlation_id: str | None = None,
        source_system: str | None = None,
    ) -> AnalysisContext:
        """Resolve one subject, fetch selected facts, and aggregate deterministically."""
        requested_at = normalize_datetime_to_ist(self._clock())
        query = self._query(symbol_or_query)
        resolved = self._resolve(query)
        subject = AnalysisSubject(
            symbol=resolved.instrument.symbol,
            resolved_instrument=resolved,
            requested_at=requested_at,
            source_system=source_system,
            correlation_id=correlation_id,
        )
        instrument_identity = (
            f"{resolved.instrument.segment.value}:{resolved.provider_instrument_id}"
        )

        evidence: list[EvidenceDescriptor] = []
        acceptable: set[str] = set()
        warnings: list[str] = []
        quote: QuoteSnapshot | None = None
        history: HistoricalSeries | None = None
        option_chain: OptionChainSnapshot | None = None
        historical_options: list[HistoricalOptionSeries] | None = None

        if requirements.include_quote:
            freshness = self._freshness(requirements.quote_freshness, "quote")
            quote_result, descriptor = self._fetch_slot(
                name="quote",
                required=requirements.require_quote,
                requirement=freshness,
                context_requirement=requirements,
                key=CacheKey(
                    namespace="market",
                    provider=self._market_data_provider.provider_name(),
                    instrument_identity=instrument_identity,
                    operation="quote",
                ),
                provider=self._market_data_provider.provider_name(),
                operation="quote",
                fetch_fn=lambda: self._market_data_provider.get_quote(resolved.instrument),
                observed_at_getter=lambda value: value.received_at,
            )
            evidence.append(descriptor)
            if quote_result is not None:
                quote = quote_result.value
            self._record_acceptability(
                descriptor, freshness, requirements.allow_partial, acceptable, warnings
            )
        else:
            evidence.append(self._not_requested("quote", requirements.require_quote))

        if requirements.include_history:
            assert requirements.history_interval is not None
            assert requirements.history_lookback_days is not None
            freshness = self._freshness(requirements.history_freshness, "historical")
            history_to = requested_at
            history_from = history_to - timedelta(days=requirements.history_lookback_days)
            history_result, descriptor = self._fetch_slot(
                name="history",
                required=requirements.require_history,
                requirement=freshness,
                context_requirement=requirements,
                key=CacheKey(
                    namespace="market",
                    provider=self._market_data_provider.provider_name(),
                    instrument_identity=instrument_identity,
                    operation="historical",
                    parameters=(
                        ("from", history_from.isoformat()),
                        ("interval", requirements.history_interval),
                        ("to", history_to.isoformat()),
                    ),
                ),
                provider=self._market_data_provider.provider_name(),
                operation="historical",
                fetch_fn=lambda: self._market_data_provider.get_historical(
                    resolved.instrument,
                    requirements.history_interval or "",
                    history_from,
                    history_to,
                ),
            )
            evidence.append(descriptor)
            if history_result is not None:
                history = history_result.value
            self._record_acceptability(
                descriptor, freshness, requirements.allow_partial, acceptable, warnings
            )
        else:
            evidence.append(self._not_requested("history", requirements.require_history))

        if requirements.include_derivatives:
            freshness = self._freshness(
                requirements.derivatives_freshness, "option_chain"
            )
            chain_result, descriptor = self._fetch_option_chain(
                resolved,
                instrument_identity,
                requirements,
                freshness,
            )
            evidence.append(descriptor)
            if chain_result is not None:
                option_chain = chain_result.value
            self._record_acceptability(
                descriptor, freshness, requirements.allow_partial, acceptable, warnings
            )
        else:
            evidence.append(
                self._not_requested("option_chain", requirements.require_derivatives)
            )

        if requirements.include_historical_options:
            historical_options = []
            freshness = self._freshness(
                requirements.historical_options_freshness, "historical_options"
            )
            for index, request in enumerate(requirements.historical_option_requests):
                name = f"historical_options[{index}]"
                option_result, descriptor = self._fetch_historical_options(
                    name,
                    resolved,
                    instrument_identity,
                    request,
                    requirements,
                    freshness,
                )
                evidence.append(descriptor)
                if option_result is not None:
                    historical_options.append(option_result.value)
                self._record_acceptability(
                    descriptor,
                    freshness,
                    requirements.allow_partial,
                    acceptable,
                    warnings,
                )
        else:
            evidence.append(
                self._not_requested(
                    "historical_options", requirements.require_historical_options
                )
            )

        required_names = tuple(item.evidence_name for item in evidence if item.required)
        missing_required = tuple(name for name in required_names if name not in acceptable)
        complete = not missing_required
        deferred = tuple(
            item for item in evidence if item.status is EvidenceStatus.DEFERRED
        )
        if missing_required and not requirements.allow_partial and not deferred:
            raise RequiredEvidenceUnavailableError(
                missing_required[0], "required evidence did not satisfy its policy"
            )

        overall_quality = self._aggregate_quality(evidence, missing_required)
        overall_retrieval_freshness = self._aggregate_retrieval_freshness(evidence)
        created_at = normalize_datetime_to_ist(self._clock())
        context = AnalysisContext(
            context_id=context_id or self._context_id_factory(),
            subject=subject,
            requirements=requirements,
            quote=quote,
            history=history,
            option_chain=option_chain,
            historical_options=(
                tuple(historical_options) if historical_options is not None else None
            ),
            evidence=tuple(evidence),
            created_at=created_at,
            overall_quality=overall_quality,
            overall_retrieval_freshness=overall_retrieval_freshness,
            complete=complete,
            missing_required_evidence=missing_required,
            warnings=tuple(warnings),
        )
        if deferred:
            first = deferred[0]
            assert first.deferred_provider is not None
            assert first.deferred_operation is not None
            assert first.deferred_reason is not None
            assert first.gate_state is not None
            raise AnalysisContextDeferredError(
                evidence_name=first.evidence_name,
                provider=first.deferred_provider,
                operation=first.deferred_operation,
                retry_after_seconds=first.retry_after_seconds,
                reason=first.deferred_reason,
                gate_state=first.gate_state,
                partial_context=context,
            )
        return context

    def build_many(
        self,
        symbols: tuple[str, ...],
        requirements: AnalysisContextRequirement,
        *,
        correlation_id: str | None = None,
        source_system: str | None = None,
    ) -> tuple[AnalysisContextBatchItem, ...]:
        """Build sequentially in input order and retain every explicit outcome."""
        results: list[AnalysisContextBatchItem] = []
        for symbol in symbols:
            try:
                context = self.build(
                    symbol,
                    requirements,
                    correlation_id=correlation_id,
                    source_system=source_system,
                )
            except AnalysisContextDeferredError as exc:
                context = exc.partial_context
                results.append(
                    AnalysisContextBatchItem(
                        symbol=symbol,
                        status=BatchItemStatus.DEFERRED,
                        context=context,
                        error_type="ProviderScheduleBlockedError",
                        error_detail=str(exc),
                        reason=exc.reason,
                        provider=exc.provider,
                        operation=exc.operation,
                        retry_after_seconds=exc.retry_after_seconds,
                        gate_state=exc.gate_state,
                        context_id=context.context_id,
                        correlation_id=context.subject.correlation_id,
                    )
                )
            except Exception as exc:
                detail = (
                    str(exc)
                    if isinstance(exc, AnalysisContextError)
                    else "context build failed"
                )
                results.append(
                    AnalysisContextBatchItem(
                        symbol=symbol,
                        status=BatchItemStatus.ERROR,
                        error_type=type(exc).__name__,
                        error_detail=detail,
                        correlation_id=correlation_id,
                    )
                )
            else:
                results.append(
                    AnalysisContextBatchItem(
                        symbol=symbol,
                        status=(
                            BatchItemStatus.COMPLETE_CONTEXT
                            if context.complete
                            else BatchItemStatus.PARTIAL_CONTEXT
                        ),
                        context=context,
                        context_id=context.context_id,
                        correlation_id=context.subject.correlation_id,
                    )
                )
        return tuple(results)

    @staticmethod
    def _query(symbol_or_query: str | InstrumentQuery) -> InstrumentQuery:
        if isinstance(symbol_or_query, InstrumentQuery):
            return symbol_or_query
        return InstrumentQuery(symbol=symbol_or_query)

    def _resolve(self, query: InstrumentQuery) -> ResolvedInstrument:
        try:
            result = self._resolver.resolve(query)
        except Exception as exc:
            raise AnalysisContextResolutionError(
                f"instrument resolution failed with {type(exc).__name__}"
            ) from exc
        if result.ambiguous:
            raise AnalysisContextResolutionError(
                f"instrument query is ambiguous across {len(result.matches)} matches"
            )
        if result.not_found or result.resolved is None:
            raise AnalysisContextResolutionError("instrument query was not found")
        return result.resolved

    def _freshness(
        self,
        explicit: FreshnessRequirement | None,
        operation: str,
    ) -> FreshnessRequirement:
        if explicit is not None:
            return explicit
        registered = self._freshness_policies.get(operation)
        if registered is None:
            raise AnalysisContextBuildError(
                f"no explicit or registered freshness policy for {operation!r}"
            )
        return registered

    def _fetch_option_chain(
        self,
        resolved: ResolvedInstrument,
        instrument_identity: str,
        context_requirement: AnalysisContextRequirement,
        freshness: FreshnessRequirement,
    ) -> tuple[FetchResult[OptionChainSnapshot] | None, EvidenceDescriptor]:
        provider = self._derivatives_provider
        if provider is None:
            return self._missing_dependency(
                "option_chain", context_requirement.require_derivatives, context_requirement
            )
        expiry = context_requirement.option_expiry
        assert expiry is not None
        return self._fetch_slot(
            name="option_chain",
            required=context_requirement.require_derivatives,
            requirement=freshness,
            context_requirement=context_requirement,
            key=CacheKey(
                namespace="derivatives",
                provider=provider.provider_name(),
                instrument_identity=instrument_identity,
                operation="option_chain",
                parameters=(("expiry", expiry.isoformat()),),
            ),
            provider=provider.provider_name(),
            operation="option_chain",
            fetch_fn=lambda: provider.get_option_chain(resolved.instrument, expiry),
            observed_at_getter=lambda value: value.received_at,
        )

    def _fetch_historical_options(
        self,
        name: str,
        resolved: ResolvedInstrument,
        instrument_identity: str,
        request: HistoricalOptionRequirement,
        context_requirement: AnalysisContextRequirement,
        freshness: FreshnessRequirement,
    ) -> tuple[FetchResult[HistoricalOptionSeries] | None, EvidenceDescriptor]:
        provider = self._historical_options_provider
        if provider is None:
            return self._missing_dependency(
                name, context_requirement.require_historical_options, context_requirement
            )
        return self._fetch_slot(
            name=name,
            required=context_requirement.require_historical_options,
            requirement=freshness,
            context_requirement=context_requirement,
            key=CacheKey(
                namespace="derivatives",
                provider=provider.provider_name(),
                instrument_identity=instrument_identity,
                operation="historical_options",
                parameters=(
                    ("end_date", request.end_date.isoformat()),
                    ("expiry_code", str(int(request.expiry_code))),
                    ("expiry_flag", request.expiry_flag.value),
                    ("interval", request.interval),
                    ("option_type", request.option_type.value),
                    ("relative_strike", str(request.relative_strike)),
                    ("start_date", request.start_date.isoformat()),
                ),
            ),
            provider=provider.provider_name(),
            operation="historical_options",
            fetch_fn=lambda: provider.get_historical_options(
                resolved.instrument,
                request.interval,
                request.expiry_flag,
                request.expiry_code,
                request.relative_strike,
                request.option_type,
                request.start_date,
                request.end_date,
            ),
        )

    def _fetch_slot(
        self,
        *,
        name: str,
        required: bool,
        requirement: FreshnessRequirement,
        context_requirement: AnalysisContextRequirement,
        key: CacheKey,
        provider: str,
        operation: str,
        fetch_fn: Callable[[], T],
        observed_at_getter: Callable[[T], datetime | None] | None = None,
    ) -> tuple[FetchResult[T] | None, EvidenceDescriptor]:
        try:
            result = self._coordinator.get_or_fetch(
                key,
                requirement,
                fetch_fn,
                provider,
                operation,
                allow_stale_on_error=context_requirement.allow_stale_on_error,
                observed_at_getter=observed_at_getter,
            )
        except ProviderScheduleBlockedError as exc:
            return None, self._deferred(name, required, exc)
        except Exception as exc:
            descriptor = self._failed(name, required, exc)
            if required and not context_requirement.allow_partial:
                raise RequiredEvidenceUnavailableError(
                    name, descriptor.error_detail or "failed"
                ) from exc
            return None, descriptor
        return result, self._descriptor(name, required, result)

    def _missing_dependency(
        self,
        name: str,
        required: bool,
        context_requirement: AnalysisContextRequirement,
    ) -> tuple[None, EvidenceDescriptor]:
        error = AnalysisContextBuildError(f"no provider dependency injected for {name}")
        descriptor = self._failed(name, required, error)
        if required and not context_requirement.allow_partial:
            raise RequiredEvidenceUnavailableError(name, descriptor.error_detail or "failed")
        return None, descriptor

    def _descriptor(
        self,
        name: str,
        required: bool,
        result: FetchResult[Any],
    ) -> EvidenceDescriptor:
        value = result.value
        quality = getattr(value, "quality", DataQuality.GOOD)
        if not isinstance(quality, DataQuality):
            quality = DataQuality.DEGRADED
        received_at = getattr(value, "received_at", None)
        source_observed_at = getattr(value, "observed_at", result.observed_at)
        observation_age_seconds = None
        if isinstance(source_observed_at, datetime):
            normalized_observed_at = normalize_datetime_to_ist(source_observed_at)
            observation_age = (
                normalize_datetime_to_ist(self._clock()) - normalized_observed_at
            ).total_seconds()
            if observation_age >= 0:
                observation_age_seconds = observation_age
        if quality is DataQuality.UNAVAILABLE:
            status = EvidenceStatus.MISSING
        elif result.freshness is FreshnessState.STALE:
            status = EvidenceStatus.STALE
        elif quality in {DataQuality.PARTIAL, DataQuality.DEGRADED}:
            status = EvidenceStatus.PARTIAL
        else:
            status = EvidenceStatus.AVAILABLE
        cache_disposition = None
        if result.disposition is FetchDisposition.CACHE:
            cache_disposition = {
                FreshnessState.FRESH: CacheDisposition.HIT_FRESH,
                FreshnessState.AGING: CacheDisposition.HIT_AGING,
                FreshnessState.STALE: CacheDisposition.HIT_STALE,
                FreshnessState.UNKNOWN: CacheDisposition.HIT_STALE,
            }[result.freshness]
        return EvidenceDescriptor(
            evidence_name=name,
            requested=True,
            required=required,
            requirement_role=(
                EvidenceRequirement.REQUIRED
                if required
                else EvidenceRequirement.OPTIONAL_REQUESTED
            ),
            status=status,
            retrieval_freshness=result.freshness,
            quality=quality,
            source_provider=result.source_provider,
            source_observed_at=source_observed_at,
            received_at=received_at,
            retrieval_age_seconds=result.age_seconds,
            observation_age_seconds=observation_age_seconds,
            source_observation_semantics=self._observation_semantics(name, value),
            cache_disposition=cache_disposition,
            fetch_disposition=result.disposition,
            stale_fallback_used=result.stale_fallback_used,
        )

    @staticmethod
    def _failed(name: str, required: bool, error: Exception) -> EvidenceDescriptor:
        safe_detail = "evidence fetch failed"
        if isinstance(
            error,
            (TIAFDataError, AnalysisContextError),
        ):
            safe_detail = str(error)
        return EvidenceDescriptor(
            evidence_name=name,
            requested=True,
            required=required,
            requirement_role=(
                EvidenceRequirement.REQUIRED
                if required
                else EvidenceRequirement.OPTIONAL_REQUESTED
            ),
            status=EvidenceStatus.FAILED,
            quality=DataQuality.UNAVAILABLE,
            error_type=type(error).__name__,
            error_detail=safe_detail,
        )

    @staticmethod
    def _deferred(
        name: str,
        required: bool,
        error: ProviderScheduleBlockedError,
    ) -> EvidenceDescriptor:
        return EvidenceDescriptor(
            evidence_name=name,
            requested=True,
            required=required,
            requirement_role=(
                EvidenceRequirement.REQUIRED
                if required
                else EvidenceRequirement.OPTIONAL_REQUESTED
            ),
            status=EvidenceStatus.DEFERRED,
            deferred_reason=error.reason,
            deferred_provider=error.provider,
            deferred_operation=error.operation,
            retry_after_seconds=error.retry_after_seconds,
            gate_state=error.gate_state,
        )

    @staticmethod
    def _not_requested(name: str, required: bool) -> EvidenceDescriptor:
        return EvidenceDescriptor(
            evidence_name=name,
            requested=False,
            required=required,
            requirement_role=EvidenceRequirement.NOT_REQUESTED,
            status=EvidenceStatus.NOT_REQUESTED,
        )

    @staticmethod
    def _record_acceptability(
        descriptor: EvidenceDescriptor,
        requirement: FreshnessRequirement,
        allow_partial: bool,
        acceptable: set[str],
        warnings: list[str],
    ) -> None:
        freshness_acceptable = (
            descriptor.retrieval_freshness is FreshnessState.FRESH
            or (
                descriptor.retrieval_freshness is FreshnessState.AGING
                and requirement.allow_aging
            )
            or (
                descriptor.retrieval_freshness is FreshnessState.STALE
                and (
                    descriptor.stale_fallback_used
                    or (
                        requirement.allow_stale
                        and requirement.max_stale_seconds is not None
                        and descriptor.retrieval_age_seconds is not None
                        and descriptor.retrieval_age_seconds
                        <= requirement.max_stale_seconds
                    )
                )
            )
        )
        status_acceptable = descriptor.status in {
            EvidenceStatus.AVAILABLE,
            EvidenceStatus.STALE,
        } or (descriptor.status is EvidenceStatus.PARTIAL and allow_partial)
        if status_acceptable and freshness_acceptable:
            acceptable.add(descriptor.evidence_name)
        if descriptor.status not in {EvidenceStatus.AVAILABLE, EvidenceStatus.NOT_REQUESTED}:
            warnings.append(
                f"{descriptor.evidence_name}: {descriptor.status.value.casefold()}"
            )

    @staticmethod
    def _aggregate_quality(
        evidence: list[EvidenceDescriptor],
        missing_required: tuple[str, ...],
    ) -> DataQuality:
        statuses = {item.evidence_name: item.status for item in evidence}
        unavailable_required = tuple(
            name
            for name in missing_required
            if statuses.get(name) is not EvidenceStatus.DEFERRED
        )
        if any(name in {"quote", "history"} for name in unavailable_required):
            return DataQuality.UNAVAILABLE
        if unavailable_required:
            return DataQuality.DEGRADED
        if missing_required:
            return DataQuality.PARTIAL
        required = [item for item in evidence if item.required]
        if any(
            item.status is EvidenceStatus.STALE or item.quality is DataQuality.DEGRADED
            for item in required
        ):
            return DataQuality.DEGRADED
        requested = [item for item in evidence if item.status is not EvidenceStatus.NOT_REQUESTED]
        if any(
            item.status
            in {
                EvidenceStatus.PARTIAL,
                EvidenceStatus.STALE,
                EvidenceStatus.FAILED,
                EvidenceStatus.MISSING,
                EvidenceStatus.DEFERRED,
            }
            or item.quality is DataQuality.PARTIAL
            for item in requested
        ):
            return DataQuality.PARTIAL
        return DataQuality.GOOD

    @staticmethod
    def _aggregate_retrieval_freshness(
        evidence: list[EvidenceDescriptor],
    ) -> FreshnessState:
        if any(
            item.required and item.status is EvidenceStatus.DEFERRED
            for item in evidence
        ):
            return FreshnessState.UNKNOWN
        values = tuple(
            item.retrieval_freshness
            for item in evidence
            if item.required and item.retrieval_freshness is not None
        )
        if not values:
            return FreshnessState.UNKNOWN
        if FreshnessState.STALE in values:
            return FreshnessState.STALE
        if FreshnessState.UNKNOWN in values:
            return FreshnessState.UNKNOWN
        if FreshnessState.AGING in values:
            return FreshnessState.AGING
        return FreshnessState.FRESH

    @staticmethod
    def _observation_semantics(name: str, value: object) -> str:
        if name == "quote":
            metadata = getattr(value, "metadata", {})
            source = metadata.get("observed_at_source") if isinstance(metadata, dict) else None
            if source == "last_trade_time":
                return "quote_last_trade_time"
            if source == "retrieval_time":
                return "quote_retrieval_time_fallback"
            return "quote_snapshot_observed_at"
        if name == "option_chain":
            return "option_chain_acquisition_time_no_authoritative_market_timestamp"
        if name == "history":
            return "historical_series_retrieval_time; bars retain market intervals"
        return "historical_option_series_retrieval_time; bars retain market intervals"
