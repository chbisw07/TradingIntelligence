"""FF canonical projection over the existing SHA-256 digest, without I/O.

This preserves original clocks; it deliberately does not use planner.semantic.
The serializer profile is tiaf.ff.canonical-json/1.0.
"""

import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Annotated, Literal

from pydantic import AfterValidator, BeforeValidator, ConfigDict, Field

from tiaf.contracts.common import TIAF_TIMEZONE, ContractModel, TiafDateTime
from tiaf.planner.digests import digest
from tiaf.planner.models import Sha256
from tiaf.source_semantics.contracts import QualifiedId


def _logical_id(value: str) -> str:
    if any(part in value for part in ("/", "\\", "..", "%")):
        raise ValueError("logical identity cannot be a path or URL")
    return value


LogicalId = Annotated[QualifiedId, AfterValidator(_logical_id)]


def _instant(value: object) -> object:
    if not isinstance(value, (str, datetime)):
        raise ValueError("instant requires an aware datetime or ISO timestamp")
    return value


ForecastDateTime = Annotated[TiafDateTime, BeforeValidator(_instant)]


def exact_decimal(value: object) -> Decimal:
    """Never claim that a floating price reconstructs source decimal precision."""
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError("exact price requires a source decimal string, integer or Decimal")
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid exact decimal") from exc
    if not result.is_finite():
        raise ValueError("exact decimal must be finite")
    return result


ExactPositivePrice = Annotated[
    Decimal, BeforeValidator(exact_decimal), Field(gt=0, allow_inf_nan=False)
]


def decimal_text(value: Decimal) -> str:
    """Context-independent formatting: Decimal.normalize can round long values."""
    if not value.is_finite():
        raise ValueError("nonfinite decimal")
    if value == 0:
        return "0"
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _canonical(value: object) -> object:
    if isinstance(value, ContractModel):
        value = value.model_dump(mode="python")
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("canonical object keys must be strings")
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("canonical timestamps must be timezone-aware")
        return value.astimezone(TIAF_TIMEZONE).isoformat()
    if isinstance(value, Decimal):
        return decimal_text(value)
    if isinstance(value, Enum):
        return value.value
    return value


def canonical_json(value: object) -> str:
    return json.dumps(
        _canonical(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def semantic_fingerprint(value: object) -> str:
    """Same digest primitive as existing captures; a lossless FF projection."""
    return digest(_canonical(value))


class ForecastContract(ContractModel):
    """Additive version discipline, defensive reconstruction, safe error rendering."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        revalidate_instances="always",
        hide_input_in_errors=True,
    )
    schema_version: Literal["1.0"] = "1.0"


class ArtifactReference(ForecastContract):
    """Existing captured artifact identity, not a loader or authority grant."""

    artifact_id: LogicalId
    artifact_version: str = Field(min_length=1, max_length=40, pattern=r"^[A-Za-z0-9_.-]+$")
    fingerprint: Sha256


class CapturedBlobReference(ForecastContract):
    """Pin semantic content and its exact immutable storage envelope separately."""

    artifact: ArtifactReference
    blob_hash: Sha256
