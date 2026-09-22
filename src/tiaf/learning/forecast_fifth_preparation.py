"""Project only cutoff-safe qualified TRAIN data; never decode protected values."""

import json
from datetime import date, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Self, cast

from pydantic import Field, TypeAdapter, model_validator

from tiaf.evaluation.forecast_research_truth import ResearchOutcomeEntry
from tiaf.forecasting.contracts import BinaryProbabilityOutput
from tiaf.forecasting.identity import ForecastDateTime, semantic_fingerprint
from tiaf.forecasting.logistic_projection import _end, _space, object_spans
from tiaf.forecasting.research_contracts import (
    AdjustedFF1FeatureSchema,
    AdjustedResearchProfile,
    FeatureVector,
)
from tiaf.forecasting.support import BaseRatePolicy

from .forecast_artifacts import (
    FIFTH_CUTOFF,
    FifthFoldGrant,
    Five,
    FoldManifest,
    PopulationAudit,
    SealedResearch,
    TrainingInput,
    TrainingRow,
)
from .forecast_training import read_bounded


class FifthBaseRateState(SealedResearch):
    authority: FifthFoldGrant
    cutoff: ForecastDateTime = FIFTH_CUTOFF
    policy: BaseRatePolicy = Field(default_factory=BaseRatePolicy)
    scheduled_ids: tuple[str, ...] = Field(max_length=20)
    support: tuple[ResearchOutcomeEntry, ...] = Field(max_length=20)
    output: BinaryProbabilityOutput | None

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if (
            self.cutoff != self.authority.cutoff
            or self.scheduled_ids != tuple(e.observation_id for e in self.support)
            or tuple(e.reference_date for e in self.support)
            != tuple(sorted({e.reference_date for e in self.support}))
            or any(
                e.target_closes_at + timedelta(minutes=30) >= self.cutoff
                or e.qualification_blob != self.authority.qualification_blob
                or e.qualification_fingerprint != self.authority.qualification_fingerprint
                or e.dataset_fingerprint != self.authority.dataset_fingerprint
                or e.profile_fingerprint != self.authority.research_profile_fingerprint
                for e in self.support
            )
        ):
            raise ValueError("FIFTH_BASELINE_LINEAGE_MISMATCH")
        eligible = tuple(
            e
            for e in self.support
            if e.label is not None
            and e.assumed_label_available_at is not None
            and e.assumed_label_available_at < self.cutoff
        )
        p = None if len(eligible) != 20 else sum(cast(int, e.label) for e in eligible) / 20
        if (None if self.output is None else self.output.probability) != p:
            raise ValueError("FIFTH_BASELINE_ARITHMETIC_MISMATCH")
        return self


class FifthPreparation(SealedResearch):
    training: TrainingInput
    baseline: FifthBaseRateState
    purged_ids: tuple[str, ...]
    protected_purge_ids: tuple[str, ...] = Field(max_length=1)
    scheduled_pre_cutoff_ids: tuple[str, ...] = Field(max_length=4096)

    @model_validator(mode="after")
    def joined(self) -> Self:
        m = self.training.manifest
        if (
            not isinstance(m.grant, FifthFoldGrant)
            or self.baseline.authority != m.grant
            or self.baseline.scheduled_ids != self.scheduled_pre_cutoff_ids[-20:]
            or len(set(self.scheduled_pre_cutoff_ids)) != len(self.scheduled_pre_cutoff_ids)
            or not set(m.observation_ids).issubset(self.scheduled_pre_cutoff_ids)
            or len(self.purged_ids)
            != (m.audit.purge_only + m.audit.embargo + len(self.protected_purge_ids))
            or not set(self.protected_purge_ids).issubset(self.purged_ids)
            or any(oid != "ff1-adjusted:RELIANCE:2024-12-31" for oid in self.protected_purge_ids)
            or set(self.purged_ids).intersection(m.observation_ids)
            or any(r.target_date >= FIFTH_CUTOFF.date() for r in self.training.rows)
        ):
            raise ValueError("FIFTH_PREPARATION_MEMBERSHIP_MISMATCH")
        return self


def _objects(raw: str) -> tuple[dict[str, str], ...]:
    """Structural spans only, not recursive JSON decoding."""
    rows, i = [], 1
    while (i := _space(raw, i)) < len(raw) - 1:
        end = _end(raw, i)
        rows.append(object_spans(raw[i:end]))
        if len(rows) > 4096:
            raise ValueError("FIFTH_SOURCE_ROW_LIMIT")
        i = _space(raw, end)
        if raw[i] == "]":
            break
        if raw[i] != ",":
            raise ValueError("FIFTH_SOURCE_SYNTAX")
        i += 1
    return tuple(rows)


def prepare_fifth(path: Path, grant: FifthFoldGrant) -> FifthPreparation:
    grant = FifthFoldGrant.model_validate(grant.model_dump())
    raw = read_bounded(path)
    if sha256(raw).hexdigest() != grant.qualification_blob:
        raise ValueError("FIFTH_QUALIFICATION_BYTE_PIN")
    top = object_spans(raw.decode().strip())
    if (
        json.loads(top["fingerprint"]) != grant.qualification_fingerprint
        or json.loads(top["dataset_fingerprint"]) != grant.dataset_fingerprint
        or json.loads(top["empirical_fitting_authorized"]) is not True
        or json.loads(top["blocking_reasons"]) != []
        or AdjustedResearchProfile.model_validate_json(top["profile"]).fingerprint
        != grant.research_profile_fingerprint
        or AdjustedFF1FeatureSchema.model_validate_json(top["feature_schema"]).fingerprint
        != grant.feature_schema_fingerprint
        or json.loads(object_spans(top["audit"])["holdout_status"]) != "SEALED"
    ):
        raise ValueError("FIFTH_QUALIFIED_PIN_OR_AUTHORITY_MISMATCH")
    assessed = datetime.fromisoformat(json.loads(top["assessed_at"]))
    if assessed.tzinfo is None or assessed > grant.issued_at:
        raise ValueError("FIFTH_QUALIFICATION_CLOCK")
    matches = [f for f in _objects(top["folds"]) if json.loads(f["test_year"]) == 2025]
    if len(matches) != 1:
        raise ValueError("FIFTH_SOURCE_FOLD_MISSING")
    f = matches[0]
    # Only TRAIN metadata. No test labels, test counts or protected outcome summaries.
    cutoff = datetime.fromisoformat(json.loads(f["fit_cutoff"]))
    embargo = date.fromisoformat(json.loads(f["embargo_date"]))
    if cutoff != FIFTH_CUTOFF or embargo != FIFTH_CUTOFF.date():
        raise ValueError("FIFTH_SOURCE_CUTOFF_MISMATCH")
    support_ids = tuple(json.loads(f["baseline_support_ids"]))
    buckets = dict.fromkeys(
        ("train", "ineligible", "purge_only", "embargo", "sealed", "later_unsealed"), 0
    )
    rows, purged, protected_purge, scheduled, support, dates = [], [], [], [], [], []
    for fields in _objects(top["observations"]):
        ref = date.fromisoformat(json.loads(fields["reference_date"]))
        target_raw = json.loads(fields["target_date"])
        target = None if target_raw is None else date.fromisoformat(target_raw)
        dates.append(ref)
        # BEFORE label, state, availability or feature decoding, including 2024->2025.
        if ref.year >= 2025 or (target is not None and target.year >= 2025):
            buckets["sealed"] += 1
            if ref == embargo:
                # Structural overlap: embargo origin is also protected. Count once
                # in the disjoint sealed bucket, retain both boundary facets/IDs.
                oid = f"ff1-adjusted:RELIANCE:{ref.isoformat()}"
                purged.append(oid)
                protected_purge.append(oid)
            continue
        if ref < date(2018, 1, 1):
            raise ValueError("FIFTH_TRAIN_START_POLICY")
        oid = json.loads(fields["observation_id"])
        closes_raw = json.loads(fields["target_closes_at"])
        opens_raw = json.loads(fields["target_opens_at"])
        if closes_raw is None or opens_raw is None:
            raise ValueError("FIFTH_TRAIN_CLOCK_MISSING")
        closes = datetime.fromisoformat(closes_raw)
        if closes + timedelta(minutes=30) >= cutoff:
            purged.append(oid)
            buckets["embargo" if ref == embargo else "purge_only"] += 1
            continue
        scheduled.append(oid)
        if oid in support_ids:
            support.append(
                ResearchOutcomeEntry(
                    **{
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
                    },
                    qualification_fingerprint=grant.qualification_fingerprint,
                    qualification_blob=grant.qualification_blob,
                    dataset_fingerprint=grant.dataset_fingerprint,
                    source_assessed_at=assessed,
                )
            )
        feature_raw, label = json.loads(fields["features"]), json.loads(fields["label"])
        if feature_raw is None or label is None:
            buckets["ineligible"] += 1
            continue
        features = FeatureVector.model_validate(feature_raw)
        info = datetime.fromisoformat(json.loads(fields["information_cutoff"]))
        available = datetime.fromisoformat(json.loads(fields["assumed_label_available_at"]))
        if (
            features.feature_schema.fingerprint != grant.feature_schema_fingerprint
            or json.loads(fields["profile_fingerprint"]) != grant.research_profile_fingerprint
            or json.loads(fields["label_state"]) != "ELIGIBLE"
            or info >= cutoff
            or available >= cutoff
            or target is None
            or available != closes + timedelta(minutes=30)
        ):
            raise ValueError("FIFTH_TRAIN_LEAKAGE_OR_SCHEMA")
        rows.append(
            TrainingRow(
                observation_id=oid,
                reference_date=ref,
                target_date=target,
                label_available_at=available,
                values=TypeAdapter(Five).validate_python(features.values),
                label=label,
            )
        )
        buckets["train"] += 1
    ids = tuple(r.observation_id for r in rows)
    positive = sum(r.label for r in rows)
    if (
        dates != sorted(set(dates))
        or ids != tuple(json.loads(f["train_ids"]))
        or tuple(purged) != tuple(json.loads(f["purged_ids"]))
        or positive != json.loads(f["train_positive"])
        or len(rows) - positive != json.loads(f["train_zero"])
        or tuple(scheduled[-20:]) != support_ids
        or not rows
    ):
        raise ValueError("FIFTH_QUALIFIED_MEMBERSHIP_MISMATCH")
    eligible = tuple(e for e in support if e.label is not None)
    output = (
        None
        if len(eligible) != 20
        else BinaryProbabilityOutput(probability=sum(cast(int, e.label) for e in eligible) / 20)
    )
    return FifthPreparation(
        training=TrainingInput(
            manifest=FoldManifest(
                grant=grant,
                fold_id=2025,
                fit_cutoff=cutoff,
                embargo_date=embargo,
                train_start=rows[0].reference_date,
                train_end=rows[-1].reference_date,
                observation_ids=ids,
                observation_order_fingerprint=semantic_fingerprint(ids),
                training_values_fingerprint=semantic_fingerprint(tuple(rows)),
                audit=PopulationAudit.model_validate(
                    {
                        "requested": len(dates),
                        "positive": positive,
                        "zero": len(rows) - positive,
                        **buckets,
                    }
                ),
            ),
            rows=tuple(rows),
        ),
        baseline=FifthBaseRateState(
            authority=grant, scheduled_ids=support_ids, support=tuple(support), output=output
        ),
        purged_ids=tuple(purged),
        protected_purge_ids=tuple(protected_purge),
        scheduled_pre_cutoff_ids=tuple(scheduled),
    )
