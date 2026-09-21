"""Evaluation-owned v2 journal projection of already-qualified external labels.

No price comparison, label creation, full qualification decoding or protected
outcome decoding. The externally pinned qualification is the truth authority.
"""

import json
from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, StrictInt, model_validator

from tiaf.forecasting.identity import ForecastDateTime
from tiaf.forecasting.logistic_projection import _end, _space, object_spans
from tiaf.forecasting.research_contracts import ResearchDate
from tiaf.learning.forecast_artifacts import SealedResearch
from tiaf.learning.forecast_jobs import TrainingRun
from tiaf.learning.forecast_training import read_bounded
from tiaf.planner.models import Sha256


class ResearchOutcomeEntry(SealedResearch):
    schema_id: Literal["tiaf.ff.research-outcome/2.0"] = "tiaf.ff.research-outcome/2.0"
    subject: Literal["RELIANCE:NSE:NSE_EQUITY:EQUITY"] = "RELIANCE:NSE:NSE_EQUITY:EQUITY"
    target_id: Literal["equity.next_session_close.return_gt_zero/1.0"] = (
        "equity.next_session_close.return_gt_zero/1.0"
    )
    price_series_basis: Literal["CORPORATE_ACTION_ADJUSTED"] = "CORPORATE_ACTION_ADJUSTED"
    observation_id: str
    reference_date: ResearchDate
    target_date: ResearchDate
    reference_closes_at: ForecastDateTime
    information_cutoff: ForecastDateTime
    simulation_as_of: ForecastDateTime
    target_opens_at: ForecastDateTime
    target_closes_at: ForecastDateTime
    assumed_label_available_at: ForecastDateTime | None
    label: Annotated[StrictInt, Field(ge=0, le=1)] | None
    label_state: Literal["ELIGIBLE", "UNAVAILABLE"]
    label_policy: Literal["QUALIFIED_ADJUSTED_ENDPOINT_DIRECTION"] = (
        "QUALIFIED_ADJUSTED_ENDPOINT_DIRECTION"
    )
    revision: Literal[0] = 0
    reasons: tuple[str, ...]
    input_fingerprint: Sha256
    profile_fingerprint: Sha256
    qualification_fingerprint: Sha256
    qualification_blob: Sha256
    dataset_fingerprint: Sha256
    source_assessed_at: ForecastDateTime

    @model_validator(mode="after")
    def valid(self) -> Self:
        if not (
            2018 <= self.reference_date.year <= 2024
            and self.reference_date < self.target_date
            and self.target_date.year < 2025
        ):
            raise ValueError("PROTECTED_OR_OUT_OF_SCOPE_OUTCOME")
        if (
            self.observation_id != f"ff1-adjusted:RELIANCE:{self.reference_date.isoformat()}"
            or self.reference_closes_at.date() != self.reference_date
            or self.target_opens_at.date() != self.target_date
            or self.target_closes_at.date() != self.target_date
            or self.information_cutoff != self.reference_closes_at + timedelta(minutes=30)
            or self.simulation_as_of != self.information_cutoff + timedelta(minutes=5)
            or not self.simulation_as_of < self.target_opens_at < self.target_closes_at
            or (self.label is not None) != (self.label_state == "ELIGIBLE")
            or (
                self.label is not None
                and self.assumed_label_available_at != self.target_closes_at + timedelta(minutes=30)
            )
            or (self.label is None and self.assumed_label_available_at is not None)
            or self.source_assessed_at < self.target_closes_at
        ):
            raise ValueError("RESEARCH_OUTCOME_IDENTITY_OR_CLOCK_MISMATCH")
        return self


class ResearchTruthJournal(SealedResearch):
    qualification_blob: Sha256
    qualification_fingerprint: Sha256
    entries: tuple[ResearchOutcomeEntry, ...] = Field(max_length=4096)
    # Scheduled membership, not a filtered list of valid labels.
    baseline_support: tuple[tuple[int, tuple[str, ...]], ...] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def valid(self) -> Self:
        dates = tuple(e.reference_date for e in self.entries)
        if (
            dates != tuple(sorted(set(dates)))
            or tuple(y for y, _ in self.baseline_support) != (2021, 2022, 2023, 2024)
            or any(
                e.qualification_fingerprint != self.qualification_fingerprint
                or e.qualification_blob != self.qualification_blob
                for e in self.entries
            )
        ):
            raise ValueError("TRUTH_JOURNAL_MEMBERSHIP_MISMATCH")
        return self


def load_research_truth(path: Path, blob: str, training: TrainingRun) -> ResearchTruthJournal:
    raw = read_bounded(path)
    if sha256(raw).hexdigest() != blob:
        raise ValueError("QUALIFICATION_BYTE_PIN_MISMATCH")
    top = object_spans(raw.decode().strip())
    g = training.grant
    if (
        json.loads(top["fingerprint"]) != g.qualification_fingerprint
        or json.loads(top["dataset_fingerprint"]) != g.dataset_fingerprint
        or json.loads(top["empirical_fitting_authorized"]) is not True
        or json.loads(top["blocking_reasons"]) != []
    ):
        raise ValueError("QUALIFIED_EXTERNAL_TRUTH_REQUIRED")
    # Fold metadata is read by allow-list; no class balances/test summaries.
    folds, i = top["folds"], 1
    support: list[tuple[int, tuple[str, ...]]] = []
    while (i := _space(folds, i)) < len(folds) - 1:
        end = _end(folds, i)
        f = object_spans(folds[i:end])
        year = json.loads(f["test_year"])
        if year in (2021, 2022, 2023, 2024):
            support.append((year, tuple(json.loads(f["baseline_support_ids"]))))
        i = _space(folds, end)
        if folds[i] == "]":
            break
        if folds[i] != ",":
            raise ValueError("TRUTH_SOURCE_SYNTAX")
        i += 1
    needed = {oid for _, ids in support for oid in ids}
    entries = []
    rows, i, count = top["observations"], 1, 0
    while (i := _space(rows, i)) < len(rows) - 1:
        end = _end(rows, i)
        fields = object_spans(rows[i:end])
        ref = date.fromisoformat(json.loads(fields["reference_date"]))
        target_raw = json.loads(fields["target_date"])
        target = None if target_raw is None else date.fromisoformat(target_raw)
        count += 1
        if count > 4096:
            raise ValueError("TRUTH_SOURCE_LIMIT")
        # The hard guard precedes *any* label/state/availability decoding.
        if (
            2018 <= ref.year <= 2024
            and target is not None
            and target.year < 2025
            and (ref.year >= 2021 or f"ff1-adjusted:RELIANCE:{ref}" in needed)
        ):
            data = {
                key: json.loads(fields[key])
                for key in (
                    "observation_id",
                    "reference_date",
                    "target_date",
                    "reference_closes_at",
                    "information_cutoff",
                    "simulation_as_of",
                    "target_opens_at",
                    "target_closes_at",
                    "assumed_label_available_at",
                    "label",
                    "label_state",
                    "reasons",
                    "input_fingerprint",
                    "profile_fingerprint",
                )
            }
            entry = ResearchOutcomeEntry(
                **data,
                qualification_fingerprint=g.qualification_fingerprint,
                qualification_blob=blob,
                dataset_fingerprint=g.dataset_fingerprint,
                source_assessed_at=json.loads(top["assessed_at"]),
            )
            if entry.profile_fingerprint != g.research_profile_fingerprint:
                raise ValueError("TRUTH_PROFILE_MISMATCH")
            entries.append(entry)
        i = _space(rows, end)
        if rows[i] == "]":
            break
        if rows[i] != ",":
            raise ValueError("TRUTH_SOURCE_SYNTAX")
        i += 1
    return ResearchTruthJournal(
        qualification_blob=blob,
        qualification_fingerprint=g.qualification_fingerprint,
        entries=tuple(entries),
        baseline_support=tuple(support),
    )
