"""Concise deterministic text summaries for A2.10 user workflows."""

from .models import RegressionReport, ReplayResult


def summarize_replay(result: ReplayResult) -> str:
    """Show replay identity and exact comparison without trading language."""
    assessment = result.assessment
    match = "NOT_CHECKED" if result.exact_match is None else "YES" if result.exact_match else "NO"
    lines = (
        "TIAF A2.10 OFFLINE REPLAY",
        "=" * 56,
        f"Snapshot                   : {result.snapshot_id}",
        f"Evidence fingerprint       : {result.evidence_fingerprint}",
        f"Policy                     : {result.policy_id} {result.policy_version}",
        f"Direction                  : {assessment.market_state.direction.value}",
        f"Opportunity                : {assessment.opportunity_score}",
        f"Class                      : {assessment.candidate_class.value}",
        f"Assessment ID              : {assessment.assessment_id}",
        f"Exact Match                : {match}",
    )
    return "\n".join(lines)


def summarize_regression(report: RegressionReport) -> str:
    """Render pass/fail counts and actionable field-level failures."""
    lines = [
        "TIAF A2.10 REPLAY REGRESSION",
        "=" * 56,
        f"PASS: {report.pass_count}",
        f"FAIL: {report.fail_count}",
    ]
    for result in report.results:
        lines.append(
            f"{result.status.value} {result.run_id} policy={result.policy_id}/"
            f"{result.policy_version} fingerprint={result.evidence_fingerprint}"
        )
        lines.extend(
            f"  {item.path}: expected={item.expected!r}; actual={item.actual!r}"
            for item in result.differences
        )
    return "\n".join(lines)
