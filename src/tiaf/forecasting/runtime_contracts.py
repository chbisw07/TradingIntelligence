"""Internal COLD declarations, not an extension of the public R5 startup schema."""

from typing import Annotated, Literal, Self

from pydantic import Field, StrictInt, model_validator

from tiaf.evaluation.forecast_contracts import ForecastTargetSpec

from .contracts import ForecastArtifactIdentity, ForecastComposition
from .identity import ArtifactReference, ForecastContract, ForecastDateTime, LogicalId


class SimulationProfile(ForecastContract):
    schema_id: Literal["tiaf.ff.simulation-profile"] = "tiaf.ff.simulation-profile"
    profile_id: LogicalId
    knowledge_policy: Literal["PRESERVE_ORIGINAL_AVAILABILITY_AND_LATER_ACQUISITION"] = (
        "PRESERVE_ORIGINAL_AVAILABILITY_AND_LATER_ACQUISITION"
    )
    purpose: Literal["SYNTHETIC_ENGINEERING"] = "SYNTHETIC_ENGINEERING"
    data_basis: Literal["SYNTHETIC_FIXTURE"] = "SYNTHETIC_FIXTURE"
    comparison_policy: Literal["NO_MIXED_MODE_POOLING"] = "NO_MIXED_MODE_POOLING"


class ColdForecastConfig(ForecastContract):
    schema_id: Literal["tiaf.ff.cold-config"] = "tiaf.ff.cold-config"
    profile_id: LogicalId
    profile_version: Literal["1.0"] = "1.0"
    forecaster_id: LogicalId
    implementation_version: str = Field(min_length=1, max_length=40)
    target: ForecastTargetSpec
    composition: ForecastComposition
    descriptor_ref: ArtifactReference
    simulation_profile_ref: ArtifactReference | None
    minimum_support: Annotated[StrictInt, Field(ge=20, le=20)] = 20
    local_deadline_seconds: Annotated[StrictInt, Field(ge=1, le=1)] = 1
    max_attempts: Annotated[StrictInt, Field(ge=1, le=1)] = 1
    strict_total_currency_cap: Literal[False] = False
    basis: Literal["SYNTHETIC_FIXTURE"] = "SYNTHETIC_FIXTURE"
    purpose: Literal["SYNTHETIC_ENGINEERING"] = "SYNTHETIC_ENGINEERING"

    @model_validator(mode="after")
    def mode_profile(self) -> Self:
        simulated = self.composition.nodes[0].realization_mode.value == "SIMULATED_ISSUANCE"
        if simulated != (self.simulation_profile_ref is not None):
            raise ValueError("COLD_SIMULATION_PROFILE_MISMATCH")
        return self


class ForecastBinding(ForecastContract):
    schema_id: Literal["tiaf.ff.cold-binding"] = "tiaf.ff.cold-binding"
    configuration_ref: ArtifactReference
    composition_ref: ArtifactReference
    descriptor_ref: ArtifactReference
    artifact_identity: ForecastArtifactIdentity
    build_ref: ArtifactReference
    dependency_versions_ref: ArtifactReference
    bound_at: ForecastDateTime
