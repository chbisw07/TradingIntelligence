"""Bounded offline A3.9 acceptance on persisted synthetic/A3.8 sparse captures."""

import json

from _a3_9_cases import CASES, load_case

from tiaf.service.opportunity_intelligence import (
    assemble_opportunity_intelligence,
    capture_intelligence,
    default_policy,
    replay_intelligence,
    request_from_capture,
    verify_intelligence,
)


def main() -> int:
    print("A3.9 OFFLINE ACCEPTANCE: synthetic observations, not market recommendations")
    passed = 0
    for name, expected in CASES:
        request = request_from_capture(
            load_case(name), request_id=f"acceptance:{name}", policy=default_policy()
        )
        run = assemble_opportunity_intelligence(request)
        captured = capture_intelligence(run)
        verification = verify_intelligence(captured)
        assert replay_intelligence(captured) == run
        assert verification.exact_match
        result = run.result
        assert result.summary.state.value == expected, (name, result.summary.state, expected)
        assert run.assembly_usage.llm_calls == run.assembly_usage.tool_calls == 0
        assert run.assembly_usage.input_tokens == run.assembly_usage.output_tokens == 0
        assert run.assembly_usage.cost_units == 0
        print(
            json.dumps(
                {
                    "case": name,
                    "subject": result.subject,
                    "horizon": result.horizon.model_dump(mode="json"),
                    "baseline": {
                        "direction": result.baseline.direction,
                        "class": result.baseline.candidate_class,
                        "score": result.baseline.opportunity_score,
                    },
                    "state": result.summary.state,
                    "bias": result.summary.bias.headline,
                    "quality": result.summary.quality.value if result.summary.quality else None,
                    "risk": result.summary.risk.value if result.summary.risk else None,
                    "maturity": result.summary.maturity.value if result.summary.maturity else None,
                    "extension": result.summary.extension.value
                    if result.summary.extension
                    else None,
                    "completeness": result.completeness.model_dump(mode="json"),
                    "contradictions": [c.code for c in result.contradictions],
                    "reasons": [
                        {"code": r.code, "category": r.category}
                        for r in result.reasons
                        if r.category != "CONTEXT"
                    ],
                    "prerequisites": [p.requirement_id for p in result.prerequisites],
                    "imported_a38_usage": result.audit.imported_usage.model_dump(mode="json"),
                    "new_a39_usage": run.assembly_usage.model_dump(mode="json"),
                    "fingerprint": run.fingerprint,
                    "replay": verification.exact_match,
                },
                sort_keys=True,
            )
        )
        passed += 1
    print(f"PASS: {passed} / FAIL: 0 — zero new provider/model/specialist execution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
