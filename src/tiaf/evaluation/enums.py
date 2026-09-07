"""Stable classifications for replay and factual outcome evaluation."""

from enum import StrEnum


class ProducerType(StrEnum):
    """Decision producer identity; A2.10 executes only the deterministic baseline."""

    DETERMINISTIC_BASELINE = "DETERMINISTIC_BASELINE"
    AGENT_SYSTEM = "AGENT_SYSTEM"
    HUMAN = "HUMAN"
    EXTERNAL = "EXTERNAL"


class RegressionStatus(StrEnum):
    """Exact replay-regression result."""

    PASS = "PASS"
    FAIL = "FAIL"
