"""INTERNAL offline adjusted FF-1 qualification; never fits or opens holdout values."""

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation.forecast_qualification import ResearchQualificationRuntime
from tiaf.evaluation.forecast_retrospective_contracts import RetrospectiveQualification
from tiaf.evaluation.forecast_retrospective_io import load_reviewed_dataset
from tiaf.evaluation.snapshot import validate_no_secrets
from tiaf.forecasting.identity import canonical_json, semantic_fingerprint
from tiaf.forecasting.research_contracts import AdjustedResearchProfile

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs/qualification_records/ff1_1a/adjusted_research_review_20260921.json"


def sanitized_report(result: RetrospectiveQualification, review: dict[str, Any]) -> dict[str, Any]:
    folds = []
    for fold in result.folds:
        counts = fold.model_dump(
            mode="json",
            exclude={
                "train_ids",
                "test_ids",
                "purged_ids",
                "paired_potential_ids",
                "baseline_support_ids",
            },
        )
        counts.update(
            {
                "train_count": len(fold.train_ids),
                "test_count": len(fold.test_ids),
                "purge_count": len(fold.purged_ids),
                "paired_potential_count": None
                if fold.test_outcomes_sealed
                else (len(fold.paired_potential_ids)),
                "membership_fingerprint": semantic_fingerprint(fold),
            }
        )
        folds.append(counts)
    body = {
        "report_id": "ff1.adjusted_research.qualification/1.0",
        "verdict": "FF1_1A_QUALIFICATION_COMPLETE"
        if result.empirical_fitting_authorized
        else ("HOLD_FF1_1A_QUALIFICATION"),
        "adjusted_data_research_profile_accepted": True,
        "empirical_fitting_authorized": result.empirical_fitting_authorized,
        "assessed_at": result.assessed_at.isoformat(),
        "profile": result.profile.model_dump(mode="json"),
        "profile_fingerprint": result.profile.fingerprint,
        "feature_schema_fingerprint": result.feature_schema.fingerprint,
        "dataset_fingerprint": result.dataset_fingerprint,
        "context_fingerprint": result.context_fingerprint,
        "qualification_fingerprint": result.fingerprint,
        "review_fingerprint": semantic_fingerprint(review),
        "previous_evidence_resolution_fingerprint": review[
            "previous_evidence_resolution_fingerprint"
        ],
        "audit": result.model_dump(mode="json")["audit"],
        "folds": folds,
        "blocking_reasons": result.blocking_reasons,
    }
    # Native canonical serializer handles aware clocks/date-only audit values.
    body = json.loads(canonical_json(body))
    body["report_fingerprint"] = semantic_fingerprint(body)
    validate_no_secrets(body)
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data/ff1/reliance",
        help="existing pinned provisioning directory; offline only",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="new Git-ignored directory for private qualification and safe summary",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "data/ff1") or output.exists():
        parser.error("output must be a new directory within data/ff1 (no overwrite)")
    ignored = (
        subprocess.run(
            ["git", "check-ignore", "-q", str(output / "qualification.json")], cwd=ROOT, check=False
        ).returncode
        == 0
    )
    if not ignored:
        parser.error("private qualification output must be Git-ignored")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    try:
        dataset = load_reviewed_dataset(args.input, review)
        runtime = ResearchQualificationRuntime(retrospective_profile=AdjustedResearchProfile())
        result = runtime.qualify_retrospective(dataset, assessed_at=datetime.now(TIAF_TIMEZONE))
        # Verify persisted reconstruction, not just a fingerprint over an in-memory object.
        serialized = result.model_dump_json()
        replayed = RetrospectiveQualification.model_validate_json(serialized)
        if replayed != result or replayed.fingerprint != result.fingerprint:
            raise ValueError("QUALIFICATION_ROUND_TRIP_MISMATCH")
        report = sanitized_report(result, review)
    except (ValueError, OSError, KeyError) as exc:
        print(f"HOLD_FF1_1A_QUALIFICATION: {type(exc).__name__}; no fitting authorized")
        return 1
    output.mkdir(parents=True)
    (output / "qualification.json").write_text(serialized + "\n", encoding="utf-8")
    (output / "summary.json").write_text(canonical_json(report) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if result.empirical_fitting_authorized else 1


if __name__ == "__main__":
    raise SystemExit(main())
