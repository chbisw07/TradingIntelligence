"""Governed one-round A4 evidence-need to A3.8 Planner bridge."""

from .admission import EvidenceNeedAdmissionError, admit_evidence_need
from .bridge import PlannerBridgeError, build_planner_bridge_plan, execute_planner_bridge
from .contracts import (
    A4EnrichmentCapture,
    A4EnrichmentChain,
    A4EnrichmentOutcome,
    A4EnrichmentPolicyComparison,
    A4EnrichmentReplayResult,
    A4EnrichmentVerificationResult,
    A4PlannerBridgePlan,
    EvidenceBridgeGrant,
    EvidenceBridgePolicy,
    EvidenceNeedAdmission,
    EvidenceRoundExecution,
    FindingLineage,
    SuccessorEvidenceCapture,
)
from .enums import (
    EnrichmentStopReason,
    EvidenceCaptureStatus,
    EvidenceChangeKind,
    EvidenceNeedAdmissionOutcome,
    FindingLineageState,
    WorkflowAdapter,
)
from .replay import (
    A4EnrichmentReplayError,
    capture_chain,
    compare_policy,
    replay_recorded,
    verify_deterministic,
)
from .runtime import CapturedEvidenceProjector, run_governed_enrichment
from .successor import (
    SuccessorProjectionError,
    build_successor_outcome,
    capture_successor_evidence,
    denied_outcome,
)

__all__ = [
    "A4EnrichmentCapture",
    "A4EnrichmentChain",
    "A4EnrichmentOutcome",
    "A4EnrichmentPolicyComparison",
    "A4EnrichmentReplayError",
    "A4EnrichmentReplayResult",
    "A4EnrichmentVerificationResult",
    "A4PlannerBridgePlan",
    "CapturedEvidenceProjector",
    "EnrichmentStopReason",
    "EvidenceBridgeGrant",
    "EvidenceBridgePolicy",
    "EvidenceCaptureStatus",
    "EvidenceChangeKind",
    "EvidenceNeedAdmission",
    "EvidenceNeedAdmissionError",
    "EvidenceNeedAdmissionOutcome",
    "EvidenceRoundExecution",
    "FindingLineage",
    "FindingLineageState",
    "PlannerBridgeError",
    "SuccessorEvidenceCapture",
    "SuccessorProjectionError",
    "WorkflowAdapter",
    "admit_evidence_need",
    "build_planner_bridge_plan",
    "build_successor_outcome",
    "capture_chain",
    "capture_successor_evidence",
    "compare_policy",
    "denied_outcome",
    "execute_planner_bridge",
    "replay_recorded",
    "run_governed_enrichment",
    "verify_deterministic",
]
