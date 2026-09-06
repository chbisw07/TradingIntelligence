"""Stable human-readable inspection for deterministic feature bundles."""

from tiaf.features.models import FeatureBundle, FeatureRequest, JSONScalar


def _parameter_value(value: JSONScalar) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _request_label(request: FeatureRequest) -> str:
    if not request.parameters:
        return request.feature_id
    parameters = ",".join(
        f"{name}={_parameter_value(value)}" for name, value in request.parameters
    )
    return f"{request.feature_id}[{parameters}]"


def summarize_feature_bundle(bundle: FeatureBundle) -> str:
    """Render factual feature diagnostics without interpretive language."""
    lines = [
        f"{bundle.subject_symbol} FEATURE BUNDLE",
        "=" * 48,
        f"Bundle ID : {bundle.bundle_id}",
        f"Context ID: {bundle.context_id}",
        f"Complete  : {'YES' if bundle.complete else 'NO'}",
        f"Quality   : {bundle.overall_quality.value}",
        f"Created   : {bundle.created_at.isoformat()}",
    ]
    for result in bundle.results:
        lines.extend(
            (
                "",
                _request_label(result.request),
                f"  Status : {result.status.value}",
                f"  Value  : {result.value if result.value is not None else '-'}",
                f"  Unit   : {result.unit or '-'}",
                f"  Quality: {result.quality.value}",
                f"  As Of  : {result.as_of.isoformat()}",
                f"  Source : {', '.join(result.source_evidence)}",
            )
        )
        for warning in result.warnings:
            lines.append(f"  Warning: {warning}")
    return "\n".join(lines)
