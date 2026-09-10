"""Public A3.8 black-box acceptance; synthetic/captured inputs, zero live calls."""

from __future__ import annotations

import argparse
from collections.abc import Callable

from _a3_8_fixtures import confirmation_services, financial_services, reference, request

from tiaf.contracts import EvidenceType, TradeStyle
from tiaf.data import InstrumentType
from tiaf.planner import OrchestrationRequest
from tiaf.workflows import (
    ControlledServices,
    EvidenceRevision,
    capture_json,
    default_registry,
    run_serial,
    verify_deterministic,
)


def cases() -> tuple[tuple[str, OrchestrationRequest, Callable[[], ControlledServices]], ...]:
    cash = request(fno=False)
    rich = request()
    missing = request(financials=False)
    confirmation = request().model_copy(update={"permit_confirmation": True})
    limited = request(financials=False, calls=0)
    chain = reference(
        rich.subject,
        "chain",
        EvidenceType.DERIVATIVES,
        {
            "derivatives.atm_mean_iv": 60.0,
            "derivatives.days_to_expiry": 2,
        },
    )
    index = rich.model_copy(
        update={
            "instrument": rich.instrument.model_copy(
                update={"instrument_type": InstrumentType.INDEX}
            )
        }
    )
    unknown = request(fno=None)
    unmapped = rich.model_copy(
        update={
            "instrument": rich.instrument.model_copy(
                update={
                    "benchmark_reference": None,
                    "sector_reference": None,
                }
            )
        }
    )
    unsupported = rich.model_copy(
        update={
            "instrument": rich.instrument.model_copy(
                update={"instrument_type": InstrumentType.UNKNOWN}
            )
        }
    )
    day = rich.model_copy(update={"trade_style": TradeStyle.DAY})
    return (
        ("A non-F&O", cash, ControlledServices),
        ("B existing inputs", rich, ControlledServices),
        ("C acquire financials", missing, lambda: financial_services(missing)),
        ("D confirm material claim", confirmation, lambda: confirmation_services(confirmation)),
        ("E rate-limit fallback", missing, lambda: financial_services(missing, fallback=True)),
        ("F unsupported gap", missing, ControlledServices),
        (
            "G selective rerun",
            rich,
            lambda: ControlledServices(
                revisions=(
                    EvidenceRevision(
                        after_round=0, references=(chain,), reason="changed captured chain"
                    ),
                )
            ),
        ),
        ("H budget exhausted", limited, lambda: financial_services(limited)),
        ("I index", index, ControlledServices),
        ("J unknown eligibility", unknown, ControlledServices),
        ("K missing mapping", unmapped, ControlledServices),
        ("L unsupported instrument", unsupported, ControlledServices),
        ("M DAY shallow", day, ControlledServices),
        ("N KAYNES 14–42 days", rich, ControlledServices),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--adapter",
        choices=("serial", "both"),
        default="both",
        help="both compares the optional LangGraph adapter with the serial oracle",
    )
    args = parser.parse_args()
    print("A3.8 SYNTHETIC ACCEPTANCE — zero live provider/model calls; not market recommendations")
    print("case | workflow | attempts | fixture calls | plans | replay/parity")
    passed = 0
    for name, req, services in cases():
        serial = run_serial(req, default_registry(), services())
        assert verify_deterministic(capture_json(serial), default_registry()) == serial
        assert serial.result.a2_fingerprint == req.inventory.a2_pack.evidence_fingerprint
        assert serial.result.usage.llm_calls == 0
        assert serial.result.usage.input_tokens == serial.result.usage.output_tokens == 0
        assert serial.result.usage.cost_units == 0
        if args.adapter == "both":
            from tiaf.workflows.langgraph_adapter import run_langgraph

            parallel = run_langgraph(req, default_registry(), services())
            assert parallel.fingerprint == serial.fingerprint, f"{name}: adapter parity mismatch"
            assert verify_deterministic(capture_json(parallel), default_registry()) == parallel
        active_ids = {o.specialist.value for o in serial.result.opinions}
        if name.startswith("A"):
            assert "DERIVATIVES_CONTEXT" not in {n.node_id for n in serial.plans[0].nodes}
            assert "OPPORTUNITY_RISK" in active_ids
        if name.startswith(("B", "H")):
            assert serial.result.provider_calls == 0
        if name.startswith("C"):
            assert serial.result.provider_calls == 1
        if name.startswith("D"):
            assert len(serial.result.confirmation_ids) == 1
        if name.startswith("E"):
            assert serial.result.provider_calls == 2
            assert "RATE_LIMITED" in serial.artifacts[0].canonical_json
        if name.startswith("G"):
            assert len(serial.plans) == 2
            assert {a.node_id for a in serial.attempts if a.plan_version == 2} == {
                "DERIVATIVES_CONTEXT",
                "OPPORTUNITY_QUALITY",
                "OPPORTUNITY_RISK",
            }
        if name.startswith("H"):
            assert serial.result.primary_stop.value == "BUDGET_EXHAUSTED"
        if name.startswith("I"):
            assert "FUNDAMENTAL" not in {n.node_id for n in serial.plans[0].nodes}
        if name.startswith("J"):
            assert "UNKNOWN_FNO_ELIGIBILITY" in serial.result.gaps
        if name.startswith("K"):
            assert "MISSING_SECTOR_MAPPING" in serial.result.gaps
        if name.startswith("L"):
            assert not serial.plans[0].nodes
        if name.startswith("M"):
            assert any(s.reason == "DAY_SHALLOW_COMPANY_SCOPE" for s in serial.result.skipped)
        print(
            f"{name} | {serial.result.status} | {len(serial.attempts)} | "
            f"{serial.result.provider_calls} | {len(serial.plans)} | PASS"
        )
        passed += 1
    print(f"PASS: {passed} / FAIL: 0. Partial/insufficient evidence remains explicit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
