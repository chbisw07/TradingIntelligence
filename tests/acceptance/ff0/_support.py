"""Test-only fixture authoring; CLI reads serialized packets, never imports tests."""

from importlib import import_module
from pathlib import Path

from tiaf.forecasting.engineering import EngineeringConfig, InputRegistration
from tiaf.forecasting.engineering_inputs import ForecastInput, OutcomeInput
from tiaf.forecasting.identity import semantic_fingerprint

FIXTURES = Path(__file__).parents[2] / "fixtures/forecasting/ff0"


def authored_inputs(root: Path) -> tuple[ForecastInput | OutcomeInput, ...]:
    fixture = import_module("tests.unit.forecasting._runtime_support").fixture
    owner = import_module("tests.unit.forecasting.test_baserate_runtime").owner
    outcome_packet = import_module("tests.unit.forecasting._capture_support").outcome_packet
    packets: list[ForecastInput | OutcomeInput] = []
    for name, simulated, n in (
        ("actual", False, 20),
        ("simulated", True, 20),
        ("insufficient", True, 19),
    ):
        f = fixture(simulated=simulated, included=n)
        packets.append(
            ForecastInput(
                input_id="ff-request:reliance-s21-" + name,
                configuration=f.config,
                artifact=f.artifact,
                request=f.request,
                snapshot=f.snapshot,
                artifacts=f.blobs,
                build=f.build,
            )
        )
        if name == "actual":
            capture = owner(f, root).run(f.request, f.snapshot, f.blobs)
            truth, blobs = outcome_packet(capture, f.blobs)
            packets.append(
                OutcomeInput(
                    input_id="ff-outcome-input:reliance-s21-up",
                    target=truth.target,
                    window=truth.window,
                    terminal=truth.terminal,
                    check_evidence=truth.check_evidence,
                    artifacts=blobs,
                )
            )
    return tuple(packets)


def config_for(
    packets: tuple[ForecastInput | OutcomeInput, ...], corpus: Path
) -> EngineeringConfig:
    return EngineeringConfig(
        input_root=".",
        corpus_root=str(corpus),
        inputs=tuple(
            InputRegistration(
                input_id=p.input_id,
                kind="FORECAST" if isinstance(p, ForecastInput) else "OUTCOME",
                filename=p.input_id.split(":")[1] + ".json",
                fingerprint=semantic_fingerprint(p),
            )
            for p in packets
        ),
    )
