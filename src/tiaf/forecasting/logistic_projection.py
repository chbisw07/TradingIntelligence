"""Pinned, outcome-blind FF-1.1A -> FF-1.3 boundary.

The qualified source also contains truth. Never decode that whole document. The
span scanner visits JSON syntax only; the allow-list decodes feature/clock and
exclusion metadata only, after checking the externally accepted byte digest.
"""

import json
from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from tiaf.forecasting.identity import ForecastDateTime
from tiaf.forecasting.research_contracts import (
    AdjustedFF1FeatureSchema,
    AdjustedResearchProfile,
    FeatureVector,
    ResearchContract,
    ResearchDate,
)
from tiaf.learning.forecast_artifacts import TrainingGrant
from tiaf.learning.forecast_training import read_bounded
from tiaf.planner.models import Sha256


class ForecastOrigin(ResearchContract):
    observation_id: str
    reference_date: ResearchDate
    target_date: ResearchDate | None
    profile_fingerprint: Sha256
    input_fingerprint: Sha256
    price_series_basis: Literal["CORPORATE_ACTION_ADJUSTED"]
    reference_closes_at: ForecastDateTime
    information_cutoff: ForecastDateTime
    simulation_as_of: ForecastDateTime
    target_opens_at: ForecastDateTime | None
    feature_window_dates: tuple[ResearchDate, ...]
    features: FeatureVector | None
    reasons: tuple[str, ...]

    @property
    def protected(self) -> bool:
        return self.target_date is not None and self.target_date.year >= 2025

    @model_validator(mode="after")
    def safe(self) -> Self:
        if not 2021 <= self.reference_date.year <= 2024:
            raise ValueError("FORECAST_FOLD_NOT_AUTHORIZED")
        if (
            self.observation_id != f"ff1-adjusted:RELIANCE:{self.reference_date.isoformat()}"
            or self.reference_closes_at.date() != self.reference_date
            or self.information_cutoff != self.reference_closes_at + timedelta(minutes=30)
            or self.simulation_as_of != self.information_cutoff + timedelta(minutes=5)
            or (self.target_date is not None and self.target_date <= self.reference_date)
            or (self.target_date is None) != (self.target_opens_at is None)
            or (
                self.target_opens_at is not None
                and (
                    self.target_opens_at.date() != self.target_date
                    or self.simulation_as_of >= self.target_opens_at
                )
            )
            or any(d > self.reference_date for d in self.feature_window_dates)
        ):
            raise ValueError("FORECAST_ORIGIN_CLOCK_OR_ID_MISMATCH")
        f = self.features
        if self.protected and (f is not None or self.feature_window_dates):
            raise ValueError("PROTECTED_FEATURES_FORBIDDEN")
        if f is not None and (
            not isinstance(f.feature_schema, AdjustedFF1FeatureSchema)
            or f.feature_schema.profile.fingerprint != self.profile_fingerprint
            or f.input_fingerprint != self.input_fingerprint
            or len(self.feature_window_dates) != 21
            or self.feature_window_dates[-1] != self.reference_date
            or tuple(sorted(set(self.feature_window_dates))) != self.feature_window_dates
        ):
            raise ValueError("FORECAST_FEATURE_LINEAGE_MISMATCH")
        return self


class ForecastProjection(ResearchContract):
    qualification_blob: Sha256
    qualification_fingerprint: Sha256
    dataset_fingerprint: Sha256
    profile: AdjustedResearchProfile
    feature_schema: AdjustedFF1FeatureSchema
    origins: tuple[ForecastOrigin, ...] = Field(min_length=1, max_length=4096)

    @model_validator(mode="after")
    def coherent(self) -> Self:
        dates = tuple(o.reference_date for o in self.origins)
        if (
            dates != tuple(sorted(set(dates)))
            or self.feature_schema.profile != self.profile
            or any(o.profile_fingerprint != self.profile.fingerprint for o in self.origins)
            or any(
                o.features is not None and o.features.feature_schema != self.feature_schema
                for o in self.origins
            )
        ):
            raise ValueError("PROJECTION_MEMBERSHIP_MISMATCH")
        return self


def _end(text: str, start: int) -> int:
    """Skip one raw JSON value without deserializing it (including any outcomes)."""
    stack: list[str] = []
    quoted = False
    escaped = False
    for i in range(start, len(text)):
        c = text[i]
        if quoted:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                quoted = False
                if not stack:
                    return i + 1
        elif c == '"':
            quoted = True
        elif c in "[{":
            stack.append(c)
            if len(stack) > 64:
                raise ValueError("PROJECTION_DEPTH_LIMIT")
        elif c in "]}":
            if not stack:
                return i
            if stack.pop() != ("[" if c == "]" else "{"):
                raise ValueError("PROJECTION_SYNTAX")
            if not stack:
                return i + 1
        elif not stack and (c == "," or c.isspace()):
            return i
    raise ValueError("PROJECTION_UNTERMINATED_VALUE")


def _space(text: str, i: int) -> int:
    while i < len(text) and text[i].isspace():
        i += 1
    return i


def object_spans(text: str) -> dict[str, str]:
    """Keys decoded, values opaque. Duplicate keys rejected even if not selected."""
    if not text.startswith("{") or not text.endswith("}"):
        raise ValueError("PROJECTION_OBJECT_REQUIRED")
    result: dict[str, str] = {}
    i = _space(text, 1)
    while i < len(text) - 1:
        end = _end(text, i)
        key = json.loads(text[i:end])
        i = _space(text, end)
        if not isinstance(key, str) or key in result or text[i] != ":":
            raise ValueError("PROJECTION_DUPLICATE_OR_INVALID_KEY")
        i = _space(text, i + 1)
        end = _end(text, i)
        result[key] = text[i:end]
        i = _space(text, end)
        if text[i] == "}":
            break
        if text[i] != ",":
            raise ValueError("PROJECTION_SYNTAX")
        i = _space(text, i + 1)
    return result


def project_qualification(path: Path, blob: str, grant: TrainingGrant) -> ForecastProjection:
    raw = read_bounded(path)
    if sha256(raw).hexdigest() != blob:
        raise ValueError("QUALIFICATION_BYTE_PIN_MISMATCH")
    top = object_spans(raw.decode("utf-8").strip())
    # Do not parse audit, folds, label values or label availability timestamps.
    if (
        json.loads(top["fingerprint"]) != grant.qualification_fingerprint
        or json.loads(top["dataset_fingerprint"]) != grant.dataset_fingerprint
        or json.loads(top["empirical_fitting_authorized"]) is not True
        or json.loads(top["blocking_reasons"]) != []
    ):
        raise ValueError("QUALIFICATION_NOT_AUTHORIZED")
    profile = AdjustedResearchProfile.model_validate_json(top["profile"])
    schema = AdjustedFF1FeatureSchema.model_validate_json(top["feature_schema"])
    if (
        profile.fingerprint != grant.research_profile_fingerprint
        or schema.fingerprint != grant.feature_schema_fingerprint
    ):
        raise ValueError("QUALIFICATION_PROFILE_PIN_MISMATCH")
    rows = top["observations"]
    if not rows.startswith("[") or not rows.endswith("]"):
        raise ValueError("PROJECTION_ARRAY_REQUIRED")
    i = _space(rows, 1)
    origins = []
    count = 0
    while i < len(rows) - 1:
        end = _end(rows, i)
        fields = object_spans(rows[i:end])
        count += 1
        if count > 4096:
            raise ValueError("PROJECTION_POPULATION_LIMIT")
        ref = date.fromisoformat(json.loads(fields["reference_date"]))
        if 2021 <= ref.year <= 2024:
            target = json.loads(fields["target_date"])
            protected = target is not None and date.fromisoformat(target).year >= 2025
            selected: dict[str, Any] = {}
            for key in ForecastOrigin.model_fields:
                if key == "schema_version":
                    continue
                if protected and key in ("features", "feature_window_dates"):
                    selected[key] = None if key == "features" else []
                else:
                    selected[key] = json.loads(fields[key])
            origins.append(ForecastOrigin.model_validate(selected))
        i = _space(rows, end)
        if rows[i] == "]":
            break
        if rows[i] != ",":
            raise ValueError("PROJECTION_SYNTAX")
        i = _space(rows, i + 1)
    return ForecastProjection(
        qualification_blob=blob,
        qualification_fingerprint=grant.qualification_fingerprint,
        dataset_fingerprint=grant.dataset_fingerprint,
        profile=profile,
        feature_schema=schema,
        origins=tuple(origins),
    )
