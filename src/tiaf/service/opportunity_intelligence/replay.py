"""Portable exact capture and verification of A3.9 assembly only."""

import json

from tiaf.planner.digests import digest

from .assembly import assemble_opportunity_intelligence
from .contracts import CaptureIntegrityError, DeterministicComparison, IntelligenceRunRecord
from .handoff import baseline_view, validate_handoff
from .policy import require_supported_policy


def capture_intelligence(record: IntelligenceRunRecord) -> str:
    record = IntelligenceRunRecord.model_validate_json(record.model_dump_json())
    data = record.model_dump(mode="json")
    return json.dumps({"record": data, "checksum": digest(data)}, sort_keys=True)


def replay_intelligence(content: str) -> IntelligenceRunRecord:
    try:
        data = json.loads(content)
        if digest(data["record"]) != data["checksum"]:
            raise ValueError("intelligence capture checksum mismatch")
        record = IntelligenceRunRecord.model_validate(data["record"])
        require_supported_policy(record.request.policy)
        source = validate_handoff(record.request)
        if (
            source.fingerprint != record.result.audit.semantic_fingerprint
            or source.result.a2_fingerprint != record.result.baseline.evidence_fingerprint
            or record.request.capture_checksum != record.result.audit.capture_checksum
            or baseline_view(source) != record.result.baseline
            or record.result.subject != source.request.subject
            or record.result.horizon != source.request.horizon
            or record.result.as_of != source.request.as_of
        ):
            raise ValueError("intelligence/source identity mismatch")
        return record
    except (ValueError, KeyError, TypeError) as exc:
        raise CaptureIntegrityError(str(exc)) from exc


def verify_intelligence(content: str) -> DeterministicComparison:
    record = replay_intelligence(content)
    verified = assemble_opportunity_intelligence(record.request)
    return DeterministicComparison(
        exact_match=verified.fingerprint == record.fingerprint,
        recorded_fingerprint=record.fingerprint,
        verified_fingerprint=verified.fingerprint,
    )
