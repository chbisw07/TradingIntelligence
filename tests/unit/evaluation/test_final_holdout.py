"""Entirely synthetic final-opening proofs; no private empirical files or fits."""

import csv
import io
import math
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from tiaf.contracts.common import TIAF_TIMEZONE
from tiaf.evaluation.forecast_comparison_metrics import bootstrap, losses
from tiaf.evaluation.forecast_final_custody import FinalAttempt, FinalProtocolStore
from tiaf.evaluation.forecast_final_outcomes import final_outcome
from tiaf.evaluation.forecast_final_protocol import FinalPopulation, FinalProtocol, FinalSlot
from tiaf.evaluation.forecast_final_scoring import (
    FinalEvaluation,
    FinalTable,
    pair_final,
    summarize_final,
)
from tiaf.evaluation.forecast_final_store import (
    FinalExecution,
    FinalLedger,
    FinalOpening,
    FinalStore,
    execute_final,
    validate_artifacts,
    verify_final,
)
from tiaf.evaluation.forecast_research_truth import ResearchOutcomeEntry
from tiaf.evaluation.forecast_retrospective import _observations
from tiaf.evaluation.forecast_retrospective_contracts import ResearchCalendar, RetrospectiveDataset
from tiaf.forecasting.final_inputs import (
    FinalInput,
    FinalSource,
    capture_source,
    final_features,
    final_inputs,
    infer_final,
    windows,
)
from tiaf.forecasting.identity import semantic_fingerprint
from tiaf.forecasting.research_contracts import AdjustedFF1FeatureSchema, AdjustedResearchProfile
from tiaf.learning.forecast_artifacts import (
    FIFTH_CUTOFF,
    FifthFoldGrant,
    Five,
    LibraryVersions,
    LogisticArtifact,
    Reconstruction,
    ScalerArtifact,
    reconstruct,
)
from tiaf.learning.forecast_fifth_preparation import FifthBaseRateState
from tiaf.learning.forecast_fifth_store import FifthHandoff

from ..forecasting.test_adjusted_retrospective_research import dataset
from ..forecasting.test_logistic_training import training

AT = datetime(2026, 9, 21, 18, tzinfo=TIAF_TIMEZONE)
ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/evaluate_ff1_final_holdout.py"


def update(value: Any, **fields: Any) -> Any:
    return type(value).model_validate({**value.model_dump(exclude={"fingerprint"}), **fields})


@dataclass(frozen=True)
class Case:
    protocol: FinalProtocol
    context: RetrospectiveDataset
    raw: bytes
    model: LogisticArtifact
    baseline: FifthBaseRateState
    handoff: FifthHandoff


@pytest.fixture(scope="module")
def case() -> Case:
    """Explicit toy coefficients, not trained and not an empirical artifact."""
    profile = AdjustedResearchProfile()
    schema = AdjustedFF1FeatureSchema(profile=profile)
    calendar = ResearchCalendar(
        start=date(2024, 11, 1),
        end=date(2026, 1, 2),
        closed_dates=(),
        special_sessions=(),
        source_urls=("https://example.test/synthetic",),
        reviewed_at=AT,
        qualified=True,
        limitations=("SYNTHETIC_ONLY",),
    )
    sessions = calendar.sessions()
    slots = tuple(
        FinalSlot(
            observation_id=f"ff1-adjusted:RELIANCE:{day}",
            reference_date=day,
            target_date=sessions[i + 1][0],
        )
        for i, (day, _, _) in enumerate(sessions)
        if day.year == 2025 and (day.month == 1 or day == date(2025, 12, 31))
    )
    text = io.StringIO()
    writer = csv.writer(text)
    writer.writerow(("date", "open", "high", "low", "close", "volume"))
    for i, (day, _, _) in enumerate(sessions):
        price = 100 + math.sin(i) + i * 0.01
        if day == date(2026, 1, 1):
            writer.writerow(
                (day, "DO_NOT_DECODE", "DO_NOT_DECODE", "DO_NOT_DECODE", price, "DO_NOT_DECODE")
            )
        elif day.year == 2026 or day < date(2024, 12, 1):
            writer.writerow((day, *(["DO_NOT_DECODE"] * 5)))
        else:
            writer.writerow((day, price, price + 1, price - 1, price, 1000 + i % 20))
    raw = text.getvalue().encode()
    fp = "a" * 64
    context = update(
        dataset(),
        calendar=calendar,
        acquired_at=AT,
        dataset_sha256=sha256(raw).hexdigest(),
        reference_end=date(2025, 12, 31),
        rows=({"session_date": date(2025, 1, 1), "protected": True, "bar": None},),
    )
    grant = FifthFoldGrant(
        basis="SYNTHETIC_ENGINEERING",
        qualification_fingerprint=fp,
        qualification_blob=fp,
        dataset_fingerprint=context.dataset_sha256,
        research_profile_fingerprint=profile.fingerprint,
        feature_schema_fingerprint=schema.fingerprint,
        protocol_fingerprint=fp,
        authority_document_fingerprint=fp,
        dependency_lock_fingerprint=fp,
        code_fingerprint=fp,
        issued_at=AT,
    )
    m = update(
        training().manifest,
        grant=grant,
        fold_id=2025,
        fit_cutoff=FIFTH_CUTOFF,
        embargo_date=FIFTH_CUTOFF.date(),
    )
    scaler = ScalerArtifact(
        n=m.audit.train,
        means=(0.0, 0.0, 0.0, 0.0, 0.0),
        variances=(1.0, 1.0, 1.0, 1.0, 1.0),
        scales=(1.0, 1.0, 1.0, 1.0, 1.0),
        constant_columns=(),
        training_fingerprint=m.scientific_fingerprint,
    )
    reconstruction = Reconstruction(
        scaler=scaler, coefficients=(0.01, 0.02, 0.03, 0.01, 0.02), intercept=0.1
    )
    model = LogisticArtifact(
        manifest=m,
        reconstruction=reconstruction,
        versions=LibraryVersions(python="3.12.3", numeric_backends=("SYNTHETIC_NO_FIT",)),
        n_iter=1,
        created_at=AT,
        reconstruction_max_error=0.0,
    )
    entries = []
    for i in range(20):
        day = date(2024, 12, 1) + timedelta(days=i)
        closes = datetime.combine(day, datetime.min.time(), TIAF_TIMEZONE) + timedelta(hours=15.5)
        entries.append(
            ResearchOutcomeEntry(
                observation_id=f"ff1-adjusted:RELIANCE:{day}",
                reference_date=day,
                target_date=day + timedelta(days=1),
                reference_closes_at=closes,
                information_cutoff=closes + timedelta(minutes=30),
                simulation_as_of=closes + timedelta(minutes=35),
                target_opens_at=closes + timedelta(hours=17.75),
                target_closes_at=closes + timedelta(days=1),
                assumed_label_available_at=closes + timedelta(days=1, minutes=30),
                label=int(i < 8),
                label_state="ELIGIBLE",
                reasons=(),
                input_fingerprint=fp,
                profile_fingerprint=profile.fingerprint,
                qualification_fingerprint=fp,
                qualification_blob=fp,
                dataset_fingerprint=context.dataset_sha256,
                source_assessed_at=AT,
            )
        )
    baseline = FifthBaseRateState.model_validate(
        {
            "authority": grant,
            "scheduled_ids": tuple(e.observation_id for e in entries),
            "support": tuple(entries),
            "output": {"probability": 0.4},
        }
    )
    handoff = FifthHandoff(
        authority_fingerprint=cast(str, grant.fingerprint),
        preparation_fingerprint=fp,
        attempt_fingerprint=fp,
        job_fingerprint=fp,
        qualification_fingerprint=fp,
        dataset_fingerprint=context.dataset_sha256,
        research_profile_fingerprint=profile.fingerprint,
        training_population_fingerprint=m.observation_order_fingerprint,
        training_values_fingerprint=m.training_values_fingerprint,
        scaler_fingerprint=cast(str, scaler.fingerprint),
        model_artifact_fingerprint=cast(str, model.fingerprint),
        baserate_state_fingerprint=cast(str, baseline.fingerprint),
        dependency_lock_fingerprint=fp,
        engineering_probe_probabilities=(0.5, 0.5, 0.5, 0.5, 0.5),
        created_at=AT,
    )
    pins: dict[str, Any] = {k: fp for k in FinalProtocol.model_fields if k.endswith("_fingerprint")}
    pins.update(
        fifth_handoff_fingerprint=handoff.fingerprint,
        model_fingerprint=model.fingerprint,
        scaler_fingerprint=scaler.fingerprint,
        training_population_fingerprint=m.observation_order_fingerprint,
        authority_fingerprint=grant.fingerprint,
        baserate_state_fingerprint=baseline.fingerprint,
        dataset_fingerprint=context.dataset_sha256,
        research_profile_fingerprint=profile.fingerprint,
        feature_schema_fingerprint=schema.fingerprint,
    )
    protocol = FinalProtocol(
        **pins,
        qualification_blob=fp,
        source_pins=(("synthetic.py", fp),),
        population=FinalPopulation(
            qualification_blob=fp, qualification_fingerprint=fp, context_fingerprint=fp, slots=slots
        ),
        authorized=True,
        created_at=AT,
    )
    return Case(protocol, context, raw, model, baseline, handoff)


def source(case: Case) -> FinalSource:
    p = case.protocol
    return capture_source(
        case.raw,
        p,
        FinalAttempt(protocol_fingerprint=cast(str, p.fingerprint)),
        "b" * 64,
        case.context,
        AT,
    )


def execution(case: Case) -> FinalExecution:
    return FinalExecution(
        protocol_fingerprint=cast(str, case.protocol.fingerprint),
        authority_document_fingerprint="a" * 64,
        implementation_pins=(("synthetic.py", "b" * 64),),
        created_at=AT,
    )


def run(case: Case, tmp: Path, *, fail: bool = False) -> tuple[FinalStore, str, FinalProtocolStore]:
    custody = FinalProtocolStore(tmp / "custody", create=True)
    pin = custody.put("protocol", case.protocol)
    store = FinalStore(tmp / "closure", create=True)

    def read() -> bytes:
        assert len(tuple(custody.root.glob("attempt-*.json"))) == 1
        assert len(tuple(store.root.glob("opening-*.json"))) == 1
        if fail:
            raise OSError("synthetic source failure AFTER claim")
        return case.raw

    ledger = execute_final(
        custody,
        store,
        case.protocol,
        execution(case),
        case.model,
        case.baseline,
        case.handoff,
        case.context,
        read,
        approved=pin,
    )
    return store, ledger, custody


def test_one_shot_complete_replay_no_refit_and_no_retry(case: Case, tmp_path: Path) -> None:
    store, pin, custody = run(case, tmp_path)
    ledger = cast(FinalLedger, store.get("ledger", pin))
    report = cast(FinalEvaluation, store.get("evaluation", ledger.evaluation))
    assert report.summary.n == len(case.protocol.population.slots)
    assert report.summary.exclusions == ()
    assert report.decision.classification == "INSUFFICIENT_EVIDENCE"  # deliberately tiny toy
    assert not report.automatic_promotion and not report.post_holdout_refit_allowed
    before = {p.name: p.read_bytes() for p in store.root.iterdir()}
    assert verify_final(FinalStore(store.root), pin) == "MATCH"
    assert before == {p.name: p.read_bytes() for p in store.root.iterdir()}
    with pytest.raises(ValueError, match="ALREADY_CONSUMED"):
        custody.consume_once(
            cast(str, case.protocol.fingerprint),
            approved_protocol=cast(str, case.protocol.fingerprint),
        )
    with pytest.raises(ValueError, match="ALREADY_CONSUMED"):
        execute_final(
            custody,
            store,
            case.protocol,
            execution(case),
            case.model,
            case.baseline,
            case.handoff,
            case.context,
            lambda: pytest.fail("second source access"),
            approved=cast(str, case.protocol.fingerprint),
        )
    claim = next(custody.root.glob("attempt-*.json"))
    assert claim.read_bytes() == next(store.root.glob("attempt-*.json")).read_bytes()
    opening = cast(FinalOpening, store.get("opening", ledger.opening))
    assert opening.consumed_at.isoformat().endswith("+05:30")
    assert FinalEvaluation.model_validate_json(report.model_dump_json()) == report
    with pytest.raises(ValidationError):
        update(report, automatic_promotion=True)
    with pytest.raises(ValidationError):
        report.one_shot_consumed = False  # type: ignore[assignment]


def test_failed_opening_consumes_and_cannot_retry(case: Case, tmp_path: Path) -> None:
    with pytest.raises(OSError, match="AFTER claim"):
        run(case, tmp_path, fail=True)
    custody = FinalProtocolStore(tmp_path / "custody")
    assert len(tuple(custody.root.glob("attempt-*.json"))) == 1
    assert len(tuple((tmp_path / "closure").glob("failure-*.json"))) == 1
    assert not tuple((tmp_path / "closure").glob("ledger-*.json"))
    with pytest.raises(ValueError, match="ALREADY_CONSUMED"):
        custody.consume_once(
            cast(str, case.protocol.fingerprint),
            approved_protocol=cast(str, case.protocol.fingerprint),
        )


@pytest.mark.parametrize(
    "field",
    [
        "model_fingerprint",
        "scaler_fingerprint",
        "baserate_state_fingerprint",
        "training_population_fingerprint",
        "dataset_fingerprint",
        "fifth_handoff_fingerprint",
    ],
)
def test_changed_pin_rejected_pre_open(case: Case, field: str, tmp_path: Path) -> None:
    p = update(case.protocol, **{field: "f" * 64})
    custody = FinalProtocolStore(tmp_path / "custody", create=True)
    custody.put("protocol", p)
    store = FinalStore(tmp_path / "closure", create=True)
    with pytest.raises(ValueError, match="FROZEN_IDENTITY"):
        execute_final(
            custody,
            store,
            p,
            update(execution(case), protocol_fingerprint=p.fingerprint),
            case.model,
            case.baseline,
            case.handoff,
            case.context,
            lambda: pytest.fail("protected access"),
            approved=cast(str, p.fingerprint),
        )
    assert not tuple(custody.root.glob("attempt-*.json"))


def test_wrong_protocol_rejected_pre_open(case: Case) -> None:
    with pytest.raises(ValueError, match="FROZEN_IDENTITY"):
        validate_artifacts(
            case.protocol, case.model, case.baseline, case.handoff, approved="f" * 64
        )


def test_exact_frozen_scope_terminal_close_only_and_causal_inputs(case: Case) -> None:
    s = source(case)  # out-of-scope fields are nonnumeric sentinels
    assert s.rows[-1].session_date == date(2026, 1, 1) and s.rows[-1].bar is None
    assert not any(r.session_date > date(2026, 1, 1) for r in s.rows)
    expected = {d for w in windows(case.protocol, case.context) for d in w}
    expected.update(s.target_date for s in case.protocol.population.slots if s.target_date)
    assert {r.session_date for r in s.rows} == expected
    for q in final_inputs(case.protocol, s):
        assert len(q.bars) == 21 and q.window_dates[-1] == q.slot.reference_date
        assert q.slot.target_date not in q.window_dates
        assert "label" not in q.model_dump()
        assert FinalInput.model_validate_json(q.model_dump_json()) == q
        assert isinstance(q.model_dump(mode="json")["bars"], list)
    with pytest.raises(ValidationError):
        update(final_inputs(case.protocol, s)[0], captured_at=AT.replace(tzinfo=None))
    with pytest.raises(ValidationError):
        update(case.protocol.population.slots[0], reference_date=date(2024, 12, 31))


def test_ground_truth_external_kernel_and_outcome_blind_forecasts(case: Case) -> None:
    s = source(case)
    q = final_inputs(case.protocol, s)[-1]
    a = infer_final(q, case.context, case.model, case.baseline, AT)
    truth = final_outcome(case.protocol, s, q, AT)
    last = s.rows[-1]
    modified = update(s, rows=(*s.rows[:-1], update(last, close=1.0)))
    q2 = final_inputs(case.protocol, modified)[-1]
    assert q == q2
    assert infer_final(q2, case.context, case.model, case.baseline, AT) == a
    changed = final_outcome(case.protocol, modified, q2, AT)
    assert truth.fingerprint != changed.fingerprint
    assert changed.label == 0 and changed.revision == 0
    assert a[0].features is not None
    assert a[0].probability == reconstruct(
        case.model.reconstruction, cast(Five, a[0].features.values)
    )
    assert a[1].probability == 0.4


def test_missing_features_and_truth_kept_in_mask_no_posthoc_filter(case: Case) -> None:
    s = source(case)
    missing = update(s, rows=s.rows[1:-1])
    pairs, dispositions, grid = [], [], []
    for q in final_inputs(case.protocol, missing):
        a, b = infer_final(q, case.context, case.model, case.baseline, AT)
        truth = final_outcome(case.protocol, missing, q, AT)
        pair, disposition = pair_final(case.protocol, q, a, b, truth, AT)
        dispositions.append(disposition)
        if pair:
            pairs.append(pair)
        grid.append(None if pair is None else (pair.brier_difference, pair.logloss_difference))
    summary = summarize_final(case.protocol, tuple(pairs), tuple(dispositions))
    assert summary.candidate == len(case.protocol.population.slots)
    assert summary.n == summary.candidate - 2
    assert summary.bootstrap.model_dump(exclude={"scope"}) == bootstrap((tuple(grid),)).model_dump(
        exclude={"scope"}
    )
    assert summary.bootstrap.scope == "FINAL_HOLDOUT"
    assert ("MISSING_FEATURE_BAR", 1) in summary.exclusions
    assert ("TARGET_UNAVAILABLE", 1) in summary.exclusions
    with pytest.raises(ValueError, match="POPULATION_MISMATCH"):
        summarize_final(case.protocol, tuple(pairs), tuple(dispositions[:-1]))


def test_identity_mismatch_fails_instead_of_excluding(case: Case) -> None:
    s = source(case)
    q = final_inputs(case.protocol, s)[0]
    a, b = infer_final(q, case.context, case.model, case.baseline, AT)
    truth = final_outcome(case.protocol, s, q, AT)
    with pytest.raises(ValueError, match="INTEGRITY_MISMATCH"):
        pair_final(case.protocol, q, a, update(b, common_request_fingerprint="f" * 64), truth, AT)


def test_feature_adapter_matches_frozen_admission_algorithm() -> None:
    # Compare all available/absent feature fields against the unchanged old adapter
    # on unprotected toy bars; the final scope contract deliberately rejects 2018.
    d = dataset()
    observations = _observations(
        d,
        AdjustedFF1FeatureSchema(profile=AdjustedResearchProfile()),
        d.calendar.sessions(),
        AT,
        "a" * 64,
        False,
    )
    for old in observations[:3]:
        # Shift only session clocks/identity so the same bars enter the final seam.
        shift = date(2025, 1, 1) - old.reference_date
        rows = {r.session_date: r.bar for r in d.rows}
        bars = tuple(
            update(rows[day], start_at=rows[day].start_at + shift, end_at=rows[day].end_at + shift)  # type: ignore[union-attr]
            for day in old.feature_window_dates
        )
        dates = tuple(day + shift for day in old.feature_window_dates)
        q = FinalInput(
            protocol_fingerprint="a" * 64,
            execution_fingerprint="b" * 64,
            source_context_fingerprint="a" * 64,
            slot=FinalSlot(
                observation_id="ff1-adjusted:RELIANCE:2025-01-01",
                reference_date=date(2025, 1, 1),
                target_date=date(2025, 1, 2),
            ),
            reference_closes_at=old.reference_closes_at + shift,
            information_cutoff=old.information_cutoff + shift,
            simulation_as_of=old.simulation_as_of + shift,
            target_opens_at=datetime(2025, 1, 2, 9, 15, tzinfo=TIAF_TIMEZONE),
            target_closes_at=datetime(2025, 1, 2, 15, 30, tzinfo=TIAF_TIMEZONE),
            window_dates=dates,
            bars=bars,
            captured_at=AT,
            input_fingerprint=semantic_fingerprint(
                (
                    "a" * 64,
                    "2025-01-01",
                    tuple((d.isoformat(), b) for d, b in zip(dates, bars, strict=True)),
                )
            ),
        )
        features, drift, reasons = final_features(q, d, AT)
        assert features is not None and old.features is not None
        assert features.values == old.features.values
        assert drift == old.precision_feature_drift and not reasons


@pytest.mark.parametrize(
    "variant,reason",
    [
        ("missing", "MISSING_FEATURE_BAR"),
        ("oversized_volume", "VOLUME_NUMERIC_UNQUALIFIED"),
        ("zero_prior_volume", "ZERO_VOLUME_BASELINE"),
        ("unsupported_action", "FEATURE_ACTION_RIGHTS"),
    ],
)
def test_frozen_feature_absences(case: Case, variant: str, reason: str) -> None:
    s = source(case)
    q = final_inputs(case.protocol, s)[0]
    context = case.context
    bars = list(q.bars)
    if variant == "missing":
        bars[0] = None
    elif variant == "oversized_volume":
        bars[0] = update(bars[0], volume=2**53 + 1)
    elif variant == "zero_prior_volume":
        bars[:-1] = [update(b, volume=0) for b in bars[:-1]]
    else:
        context = update(
            context,
            actions=(
                {
                    "boundary": q.slot.reference_date,
                    "kind": "RIGHTS",
                    "provider_adjustment_supported": False,
                    "source_url": "https://example.test/synthetic",
                },
            ),
        )
    q = update(
        q,
        bars=tuple(bars),
        input_fingerprint=semantic_fingerprint(
            (
                q.source_context_fingerprint,
                q.slot.reference_date.isoformat(),
                tuple((d.isoformat(), b) for d, b in zip(q.window_dates, bars, strict=True)),
            )
        ),
    )
    features, _, reasons = final_features(q, context, AT)
    assert features is None and reason in reasons


def test_zero_current_volume_is_factual_not_missing(case: Case) -> None:
    s = source(case)
    q = final_inputs(case.protocol, s)[0]
    bars = (*q.bars[:-1], update(q.bars[-1], volume=0))
    q = update(
        q,
        bars=bars,
        input_fingerprint=semantic_fingerprint(
            (
                q.source_context_fingerprint,
                q.slot.reference_date.isoformat(),
                tuple((d.isoformat(), b) for d, b in zip(q.window_dates, bars, strict=True)),
            )
        ),
    )
    features, _, reasons = final_features(q, case.context, AT)
    assert features is not None and features.values[-1] == 0.0 and not reasons


def test_near_tie_truth_unavailable_not_zero(case: Case) -> None:
    s = source(case)
    q = final_inputs(case.protocol, s)[-1]
    first = next(r for r in s.rows if r.session_date == q.slot.reference_date)
    last = update(s.rows[-1], close=math.nextafter(first.close, math.inf))
    modified = update(s, rows=(*s.rows[:-1], last))
    truth = final_outcome(case.protocol, modified, q, AT)
    assert truth.label is None and truth.reasons == ("PRECISION_NEAR_TIE",)
    assert truth.assumed_label_available_at is None


def test_wrong_source_or_claim_rejected_before_csv_decode(case: Case) -> None:
    claim = FinalAttempt(protocol_fingerprint=cast(str, case.protocol.fingerprint))
    with pytest.raises(ValueError, match="SOURCE_OR_AUTHORITY_PIN"):
        capture_source(b"not CSV", case.protocol, claim, "b" * 64, case.context, AT)
    with pytest.raises(ValueError, match="SOURCE_OR_AUTHORITY_PIN"):
        capture_source(
            case.raw,
            case.protocol,
            update(claim, protocol_fingerprint="f" * 64),
            "b" * 64,
            case.context,
            AT,
        )


@pytest.mark.parametrize("p,y,expected", [(0.4, 1, 0.36), (0.4, 0, 0.16), (0.5, 1, 0.25)])
def test_losses_and_sign(p: float, y: int, expected: float) -> None:
    brier, logloss = losses(p, y)
    assert brier == pytest.approx(expected)
    assert logloss == pytest.approx(-math.log(p if y else 1 - p))
    assert losses(0.8, 1)[0] - losses(0.4, 1)[0] < 0
    assert losses(0.8, 0)[0] - losses(0.4, 0)[0] > 0


def test_tamper_detected_and_offline_replay_without_source(case: Case, tmp_path: Path) -> None:
    store, pin, _ = run(case, tmp_path)
    ledger = cast(FinalLedger, store.get("ledger", pin))
    table = cast(FinalTable, store.get("table", ledger.table))
    assert len(table.pairs) == len(case.protocol.population.slots)
    code = """
import sys
from pathlib import Path
from scripts.evaluate_ff1_final_holdout import install_guard
from tiaf.evaluation.forecast_final_store import FinalStore, verify_final
install_guard(execute=False, replay=True)
blocked = {'sklearn', 'scipy', 'joblib', 'threadpoolctl'}
assert not any(k.split('.')[0] in blocked for k in sys.modules)
assert verify_final(FinalStore(Path(sys.argv[1])), sys.argv[2]) == 'MATCH'
print('MATCH offline no fit')
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(store.root), pin],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "MATCH offline no fit" in result.stdout
    path = next(store.root.glob("forecast-*.json"))
    path.write_bytes(path.read_bytes().replace(b'"probability":', b'"changed_probability":', 1))
    assert verify_final(FinalStore(store.root), pin) == "MISMATCH"


@pytest.mark.parametrize(
    "operation",
    [
        "import sklearn",
        "import scipy",
        "import socket; socket.socket()",
        "import subprocess; subprocess.run(['true'])",
        "open('.env')",
    ],
)
def test_process_guard_refuses_fit_network_subprocess_and_secrets(operation: str) -> None:
    code = (
        "from scripts.evaluate_ff1_final_holdout import install_guard; "
        "install_guard(execute=False, replay=True); " + operation
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode != 0 and "FORBIDDEN" in result.stderr


def test_cli_safe_default_and_explicit_wrong_pin() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True
    )
    assert "Safe: no operation" in result.stdout
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--execute", "--approved-protocol", "bad"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1 and "no opening" in result.stdout
    help_text = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, check=True
    ).stdout
    for forbidden in ("--force", "--seed", "--output", "--refit", "--resume"):
        assert forbidden not in help_text
