"""Persisted acceptance inputs; loading never executes A3.8 or a specialist."""

import base64
import gzip
from pathlib import Path

CASES = (
    ("aligned", "OPPORTUNITY"),
    ("weak_company", "CONFLICTED"),
    ("valuation", "WATCH"),
    ("poor_timing", "WAIT"),
    ("extended", "WAIT"),
    ("critical", "AVOID"),
    ("event_risk", "WAIT"),
    ("disputed_event", "CONFLICTED"),
    ("conflict", "CONFLICTED"),
    ("baseline_watch", "WATCH"),
    ("baseline_no_trade", "NO_TRADE"),
    ("abstain", "INSUFFICIENT_EVIDENCE"),
    ("stale", "INSUFFICIENT_EVIDENCE"),
    ("non_fno", "OPPORTUNITY"),
    ("unknown_fno", "WATCH"),
    ("index", "OPPORTUNITY"),
    ("negative", "OPPORTUNITY"),
    ("sparse_kaynes", "INSUFFICIENT_EVIDENCE"),
)


def load_case(name: str) -> str:
    if name not in dict(CASES):
        raise ValueError("unknown acceptance case")
    root = Path(__file__).resolve().parents[1] / "tests/fixtures/opportunity_intelligence"
    return gzip.decompress(base64.b64decode((root / f"{name}.json.gz.b64").read_text())).decode()
