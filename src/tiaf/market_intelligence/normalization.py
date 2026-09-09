"""Explicit semantic normalization with an auditable mapping journal."""

import hashlib
from dataclasses import dataclass

from .enums import DerivationClass, ProviderFailureKind, SemanticMappingQuality
from .models import (
    CanonicalEvidenceProjection,
    MarketIntelligenceRequest,
    NormalizationRecord,
    NormalizedEvidenceBatch,
    ProviderFailure,
    ProviderFetchResult,
)


@dataclass(frozen=True, slots=True)
class SemanticRule:
    native_field: str
    canonical_metric: str | None
    quality: SemanticMappingQuality
    rule_id: str
    derivation_class: DerivationClass = DerivationClass.REPORTED
    requires_period: bool = True


class RuleBasedNormalizer:
    """Maps only explicitly declared semantics and preserves every native value."""

    def __init__(self, provider_id: str, rules: tuple[SemanticRule, ...] = ()) -> None:
        self._provider_id = provider_id
        self._rules = {rule.native_field.casefold(): rule for rule in rules}

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def normalize(
        self,
        request: MarketIntelligenceRequest,
        result: ProviderFetchResult,
    ) -> NormalizedEvidenceBatch:
        records: list[NormalizationRecord] = []
        canonical: list[CanonicalEvidenceProjection] = []
        gaps = list(result.failures)
        for observation in result.observations:
            rule = self._rules.get(observation.native_field.casefold())
            if rule is None:
                rule = SemanticRule(
                    observation.native_field,
                    None,
                    SemanticMappingQuality.AMBIGUOUS,
                    rule_id="unmapped-native-field",
                    derivation_class=observation.derivation_class,
                )
            record_id = hashlib.sha256(
                f"{observation.observation_id}|{rule.rule_id}|1.0".encode()
            ).hexdigest()
            emit = (
                rule.canonical_metric is not None
                and rule.quality
                in {SemanticMappingQuality.EXACT, SemanticMappingQuality.WELL_SUPPORTED}
                and observation.source_reference is not None
                and (observation.period_label is not None or not rule.requires_period)
            )
            warnings: list[str] = []
            if rule.quality in {
                SemanticMappingQuality.AMBIGUOUS,
                SemanticMappingQuality.PROVIDER_DEFINED,
            }:
                warnings.append("native meaning is not safely equivalent to a canonical metric")
                gaps.append(
                    ProviderFailure(
                        kind=ProviderFailureKind.AMBIGUOUS_MAPPING,
                        provider_id=result.provider_id,
                        capability=result.capability,
                        message=f"ambiguous native field: {observation.native_field}",
                    )
                )
            if observation.source_reference is None:
                warnings.append("source reference absent; canonical emission withheld")
                gaps.append(
                    ProviderFailure(
                        kind=ProviderFailureKind.MISSING_SOURCE_REFERENCE,
                        provider_id=result.provider_id,
                        capability=result.capability,
                        message=f"missing source reference for {observation.native_field}",
                    )
                )
            if observation.period_label is None and rule.requires_period:
                warnings.append("reporting period absent; canonical emission withheld")
                gaps.append(
                    ProviderFailure(
                        kind=ProviderFailureKind.MISSING_PERIOD,
                        provider_id=result.provider_id,
                        capability=result.capability,
                        message=f"missing period for {observation.native_field}",
                    )
                )
            if observation.availability_basis.value == "ESTIMATED_DATE":
                gaps.append(
                    ProviderFailure(
                        kind=ProviderFailureKind.ESTIMATED_AVAILABILITY,
                        provider_id=result.provider_id,
                        capability=result.capability,
                        message=(f"estimated availability boundary for {observation.native_field}"),
                    )
                )
            evidence_id = f"canonical:{record_id}" if emit else None
            records.append(
                NormalizationRecord(
                    record_id=record_id,
                    observation_id=observation.observation_id,
                    provider_id=result.provider_id,
                    native_field=observation.native_field,
                    canonical_metric=rule.canonical_metric,
                    mapping_quality=rule.quality,
                    derivation_class=rule.derivation_class,
                    rule_id=rule.rule_id,
                    rule_version="1.0",
                    source_observation_ids=(observation.observation_id,),
                    emitted_evidence_id=evidence_id,
                    warnings=tuple(warnings),
                )
            )
            if emit:
                assert evidence_id is not None
                assert rule.canonical_metric is not None
                assert observation.source_reference is not None
                evidence = CanonicalEvidenceProjection(
                    evidence_id=evidence_id,
                    metric=rule.canonical_metric,
                    value=observation.value,
                    unit=observation.unit,
                    currency=observation.currency,
                    period=observation.period_label,
                    available_from=observation.available_from,
                    source_reference=observation.source_reference,
                    provider_id=observation.provider_id,
                    source_observation_id=observation.observation_id,
                    mapping_quality=rule.quality,
                    derivation_class=rule.derivation_class,
                )
                canonical.append(evidence)
        return NormalizedEvidenceBatch(
            provider_id=result.provider_id,
            capability=result.capability,
            native_observations=result.observations,
            normalization_records=tuple(records),
            canonical_evidence=tuple(canonical),
            gaps=tuple(gaps),
        )


def tapetide_normalizer() -> RuleBasedNormalizer:
    """Conservative mappings for live-validated Tapetide labels."""
    return RuleBasedNormalizer(
        "tapetide",
        (
            SemanticRule(
                "Revenue from Operations",
                "fundamental.revenue",
                SemanticMappingQuality.EXACT,
                rule_id="tapetide-revenue-from-operations",
            ),
            SemanticRule(
                "Net Profit",
                "fundamental.net_income",
                SemanticMappingQuality.WELL_SUPPORTED,
                rule_id="tapetide-net-profit",
            ),
            SemanticRule(
                "yearly_revenue",
                None,
                SemanticMappingQuality.AMBIGUOUS,
                rule_id="tapetide-yearly-revenue-native-only",
            ),
            SemanticRule(
                "Sales",
                None,
                SemanticMappingQuality.PROVIDER_DEFINED,
                rule_id="tapetide-sales-provider-defined",
            ),
            SemanticRule(
                "Borrowings",
                None,
                SemanticMappingQuality.AMBIGUOUS,
                rule_id="tapetide-borrowings-native-only",
            ),
            SemanticRule(
                "Free Cash Flow",
                None,
                SemanticMappingQuality.PROVIDER_DEFINED,
                rule_id="tapetide-free-cash-flow-provider-derived",
                derivation_class=DerivationClass.PROVIDER_DERIVED,
            ),
        ),
    )
