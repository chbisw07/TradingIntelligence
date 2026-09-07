"""Stable factual human-readable indicator inspection."""

from tiaf.indicators.models import IndicatorBundle


def summarize_indicator_bundle(bundle: IndicatorBundle) -> str:
    """Render indicator evidence without strategy or recommendation language."""
    lines = [
        f"{bundle.subject_symbol} INDICATOR BUNDLE",
        "=" * 48,
        f"Bundle ID : {bundle.bundle_id}",
        f"Registry  : {bundle.registry_version}",
        f"Context ID: {bundle.context_id}",
        f"Complete  : {'YES' if bundle.complete else 'NO'}",
        f"Quality   : {bundle.overall_quality.value}",
        f"Created   : {bundle.created_at.isoformat()}",
    ]
    for result in bundle.results:
        parameters = ", ".join(
            f"{name}={value}" for name, value in result.parameters
        )
        lines.extend(
            (
                "",
                result.indicator_id,
                f"  Status     : {result.status.value}",
                f"  Parameters : {parameters or '-'}",
                f"  Quality    : {result.quality.value}",
                f"  As Of      : {result.as_of.isoformat()}",
                f"  Source     : {', '.join(result.source_evidence)}",
            )
        )
        for value in result.values:
            lines.append(f"  {value.name:<11}: {value.value} {value.unit}")
        for state in result.states:
            lines.append(f"  {state.name:<11}: {state.value}")
        for warning in result.warnings:
            lines.append(f"  Warning    : {warning}")
    return "\n".join(lines)
