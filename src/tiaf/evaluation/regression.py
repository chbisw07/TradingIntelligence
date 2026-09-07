"""Golden-corpus deterministic replay regression harness."""

from collections.abc import Callable
from datetime import datetime
from uuid import NAMESPACE_URL, uuid5

from tiaf.baseline import BaselinePolicy

from .enums import RegressionStatus
from .errors import EvaluationError
from .models import (
    CapturedBaselineCase,
    FieldDifference,
    RegressionCheckResult,
    RegressionReport,
    ReplayRequest,
)
from .replay import replay
from .snapshot import canonical_json

PolicyResolver = Callable[[str, str], BaselinePolicy]


def _check_id(case: CapturedBaselineCase) -> str:
    return str(
        uuid5(
            NAMESPACE_URL,
            f"tiaf:regression-check:{case.snapshot.fingerprint}:{case.run_record.run_id}",
        )
    )


def run_regression(
    cases: tuple[CapturedBaselineCase, ...],
    resolve_policy: PolicyResolver,
    *,
    replay_time: datetime,
) -> RegressionReport:
    """Replay all captured cases and report exact leaf-level differences."""
    results: list[RegressionCheckResult] = []
    for case in sorted(cases, key=lambda item: item.run_record.run_id):
        snapshot = case.snapshot
        run = case.run_record
        try:
            policy = resolve_policy(snapshot.policy_id, snapshot.policy_version)
            result = replay(
                ReplayRequest(
                    snapshot=snapshot,
                    policy=policy,
                    expected_assessment=run.assessment,
                    replay_time=replay_time,
                )
            )
            status = RegressionStatus.PASS if result.exact_match else RegressionStatus.FAIL
            differences = result.differences
        except (EvaluationError, ValueError) as exc:
            status = RegressionStatus.FAIL
            differences = (
                FieldDifference(
                    path="$replay_error",
                    expected="successful exact replay",
                    actual=str(exc),
                ),
            )
        results.append(
            RegressionCheckResult(
                check_id=_check_id(case),
                status=status,
                snapshot_id=snapshot.snapshot_id,
                run_id=run.run_id,
                policy_id=snapshot.policy_id,
                policy_version=snapshot.policy_version,
                evidence_fingerprint=snapshot.fingerprint,
                differences=differences,
            )
        )
    result_tuple = tuple(results)
    identity = canonical_json([item.model_dump(mode="json") for item in result_tuple])
    return RegressionReport(
        report_id=str(uuid5(NAMESPACE_URL, f"tiaf:regression-report:{identity}")),
        results=result_tuple,
        pass_count=sum(item.status is RegressionStatus.PASS for item in result_tuple),
        fail_count=sum(item.status is RegressionStatus.FAIL for item in result_tuple),
    )
