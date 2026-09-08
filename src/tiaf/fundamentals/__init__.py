"""Public provider-neutral A3.4 fundamental evidence API."""

from .enums import (
    FactBasis,
    FundamentalFamily,
    FundamentalMetric,
    FundamentalSourceQuality,
    FundamentalUnit,
    MetricResultStatus,
    ReportingPeriodKind,
    ValueScale,
)
from .gateway import (
    FundamentalEvidenceGateway,
    fundamental_evidence_pack,
    fundamental_gateway_attributes,
)
from .metrics import (
    FORMULA_VERSION,
    compound_annual_growth_rate,
    growth_rate,
    metric_result_to_fact,
    ratio_metric,
    trailing_twelve_months,
)
from .models import (
    CompanyIdentity,
    FundamentalDataset,
    FundamentalDerivation,
    FundamentalFact,
    FundamentalMetricResult,
    FundamentalRequest,
    PeriodRequirement,
    ReportingPeriod,
    fundamental_fingerprint,
)
from .normalization import (
    FundamentalNormalizationError,
    ensure_compatible_values,
    is_financial_company,
    normalize_percent,
    normalize_scale,
    point_in_time_facts,
    preferred_fact,
    resolve_revisions,
    validate_unit_for_metric,
)
from .provider import (
    FundamentalProvider,
    FundamentalProviderError,
    InMemoryFundamentalProvider,
)
from .serialization import fundamental_dataset_json, load_fundamental_dataset_json

__all__ = [
    "FORMULA_VERSION",
    "CompanyIdentity",
    "FactBasis",
    "FundamentalDataset",
    "FundamentalDerivation",
    "FundamentalEvidenceGateway",
    "FundamentalFact",
    "FundamentalFamily",
    "FundamentalMetric",
    "FundamentalMetricResult",
    "FundamentalNormalizationError",
    "FundamentalProvider",
    "FundamentalProviderError",
    "FundamentalRequest",
    "FundamentalSourceQuality",
    "FundamentalUnit",
    "InMemoryFundamentalProvider",
    "MetricResultStatus",
    "PeriodRequirement",
    "ReportingPeriod",
    "ReportingPeriodKind",
    "ValueScale",
    "compound_annual_growth_rate",
    "ensure_compatible_values",
    "fundamental_dataset_json",
    "fundamental_evidence_pack",
    "fundamental_fingerprint",
    "fundamental_gateway_attributes",
    "growth_rate",
    "is_financial_company",
    "load_fundamental_dataset_json",
    "metric_result_to_fact",
    "normalize_percent",
    "normalize_scale",
    "point_in_time_facts",
    "preferred_fact",
    "ratio_metric",
    "resolve_revisions",
    "trailing_twelve_months",
    "validate_unit_for_metric",
]

