"""Public portable orchestration API; the optional framework adapter is not imported."""

from .composition import (
    CompositionEnvelope,
    CompositionParticipant,
    CompositionParticipantStatus,
    CompositionRequiredness,
    CompositionUsageKnowledge,
    PinnedVerificationError,
    PinnedVerificationFailure,
    build_orchestration_composition,
    specialist_capability_id,
)
from .coordinator import OrchestrationCoordinator, run_serial
from .records import OrchestrationRunRecord
from .registry import default_registry
from .replay import capture_json, replay_recorded, verify_deterministic
from .services import ControlledServices, EvidenceAcquisition, EvidenceRevision

__all__ = [
    "OrchestrationCoordinator",
    "OrchestrationRunRecord",
    "CompositionEnvelope",
    "CompositionParticipant",
    "CompositionParticipantStatus",
    "CompositionRequiredness",
    "CompositionUsageKnowledge",
    "PinnedVerificationError",
    "PinnedVerificationFailure",
    "build_orchestration_composition",
    "specialist_capability_id",
    "run_serial",
    "default_registry",
    "capture_json",
    "replay_recorded",
    "verify_deterministic",
    "ControlledServices",
    "EvidenceAcquisition",
    "EvidenceRevision",
]
