"""Versioned, secret-free COLD startup declarations and recorded resolution."""

import json
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StrictBool, ValidationError, model_validator

from tiaf.agents._validation import validate_no_secrets
from tiaf.planner.digests import digest


class StartupFailure(StrEnum):
    CONFIG_SCHEMA_INVALID = "CONFIG_SCHEMA_INVALID"
    UNKNOWN_COMPONENT_ID = "UNKNOWN_COMPONENT_ID"
    REQUIRED_COMPONENT_UNAVAILABLE = "REQUIRED_COMPONENT_UNAVAILABLE"
    CONFIGURATION_CONFLICT = "CONFIGURATION_CONFLICT"
    INCOMPATIBLE_COMPONENT_VERSION = "INCOMPATIBLE_COMPONENT_VERSION"
    UNSUPPORTED_COMPOSITION = "UNSUPPORTED_COMPOSITION"
    SECRET_CONFIGURATION_INVALID = "SECRET_CONFIGURATION_INVALID"
    COMPONENT_IMPORT_FAILED = "COMPONENT_IMPORT_FAILED"


class StartupError(RuntimeError):
    """Safe public startup error: never interpolates rejected configuration values."""

    def __init__(self, failure: StartupFailure) -> None:
        self.failure = failure
        super().__init__(f"COLD startup rejected: {failure.value}")


class StartupContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)


class RuntimeProfile(StrEnum):
    LOCAL_CAPTURED = "LOCAL_CAPTURED"
    LOCAL_ENGINEERING = "LOCAL_ENGINEERING"


class MissingSelectionPolicy(StrEnum):
    FAIL_STARTUP = "FAIL_STARTUP"
    RECORD_UNAVAILABLE = "RECORD_UNAVAILABLE"


class ComponentSelection(StartupContract):
    component_id: str = Field(min_length=1, max_length=100)
    implementation_version: str = Field(default="1.0", min_length=1, max_length=30)
    required: StrictBool = True
    on_missing: MissingSelectionPolicy = MissingSelectionPolicy.FAIL_STARTUP

    @model_validator(mode="after")
    def required_cannot_degrade(self) -> Self:
        if self.required and self.on_missing is not MissingSelectionPolicy.FAIL_STARTUP:
            raise StartupError(StartupFailure.CONFIGURATION_CONFLICT)
        return self


_SPECIALIST_IDS = (
    "specialist:derivatives-context",
    "specialist:fundamental",
    "specialist:macro",
    "specialist:news-event",
    "specialist:opportunity-quality",
    "specialist:opportunity-risk",
    "specialist:relative-strength",
    "specialist:sector",
    "specialist:technical",
)


class ColdStartupConfig(StartupContract):
    schema_version: Literal["1.0"] = "1.0"
    runtime_profile: RuntimeProfile = RuntimeProfile.LOCAL_CAPTURED
    selected_adapters: tuple[ComponentSelection, ...] = ()
    selected_specialists: tuple[ComponentSelection, ...] = tuple(
        ComponentSelection(component_id=item) for item in _SPECIALIST_IDS
    )
    selected_workflow: ComponentSelection = ComponentSelection(component_id="workflow.serial")

    @model_validator(mode="after")
    def closed_selection(self) -> Self:
        items = (*self.selected_adapters, *self.selected_specialists, self.selected_workflow)
        ids = tuple(item.component_id for item in items)
        if len(ids) != len(set(ids)):
            raise StartupError(StartupFailure.CONFIGURATION_CONFLICT)
        if not self.selected_workflow.required:
            raise StartupError(StartupFailure.UNSUPPORTED_COMPOSITION)
        return self


def resolve_startup_config(
    explicit: ColdStartupConfig | dict[str, object] | None = None,
) -> ColdStartupConfig:
    """Explicit trusted fields replace code defaults; tuples replace whole selections.

    No environment, deployment overlay, implicit config search or per-module merge.
    Revalidation also protects callers that used Pydantic model_copy/model_construct.
    """
    payload = (
        explicit.model_dump(mode="json") if isinstance(explicit, ColdStartupConfig) else explicit
    )
    try:
        validate_no_secrets(payload)
    except ValueError:
        raise StartupError(StartupFailure.SECRET_CONFIGURATION_INVALID) from None
    try:
        config = ColdStartupConfig.model_validate({} if payload is None else payload)
    except ValidationError:
        raise StartupError(StartupFailure.CONFIG_SCHEMA_INVALID) from None
    return ColdStartupConfig.model_validate(
        config.model_dump(mode="python")
        | {
            "selected_adapters": tuple(
                sorted(config.selected_adapters, key=lambda x: x.component_id)
            ),
            "selected_specialists": tuple(
                sorted(config.selected_specialists, key=lambda x: x.component_id)
            ),
        }
    )


class ComponentResolution(StartupContract):
    selection: ComponentSelection
    status: Literal["IMPORT_RESOLVED", "UNAVAILABLE"]
    failure: Literal["OPTIONAL_DEPENDENCY_MISSING"] | None = None

    @model_validator(mode="after")
    def consistent_resolution(self) -> Self:
        if (self.status == "UNAVAILABLE") != (self.failure is not None):
            raise ValueError("inconsistent startup resolution")
        if self.status == "UNAVAILABLE" and (
            self.selection.required
            or self.selection.on_missing is not MissingSelectionPolicy.RECORD_UNAVAILABLE
        ):
            raise ValueError("selection does not permit degraded startup")
        return self


class StartupComposition(StartupContract):
    schema_version: Literal["1.0"] = "1.0"
    config: ColdStartupConfig
    authority_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    resolutions: tuple[ComponentResolution, ...]
    configuration_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    startup_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def verify_identity(self) -> Self:
        expected = resolve_startup_config(self.config)
        if expected != self.config:
            raise ValueError("startup config must have canonical order")
        items = (
            *expected.selected_adapters,
            *expected.selected_specialists,
            expected.selected_workflow,
        )
        if tuple(r.selection for r in self.resolutions) != tuple(
            sorted(items, key=lambda x: x.component_id)
        ):
            raise ValueError("startup resolution must cover exactly the selected components")
        configuration = digest(
            {
                "schema": "tiaf.cold-configuration/1.0",
                "config": expected.model_dump(mode="json"),
                "authority_fingerprint": self.authority_fingerprint,
            }
        )
        startup = digest(
            {
                "schema": "tiaf.cold-startup/1.0",
                "configuration_fingerprint": configuration,
                "resolutions": [r.model_dump(mode="json") for r in self.resolutions],
            }
        )
        if (configuration, startup) != (self.configuration_fingerprint, self.startup_fingerprint):
            raise ValueError("startup fingerprint mismatch")
        return self

    @property
    def degraded(self) -> bool:
        return any(item.status == "UNAVAILABLE" for item in self.resolutions)

    @classmethod
    def seal(
        cls,
        config: ColdStartupConfig,
        authority_fingerprint: str,
        resolutions: tuple[ComponentResolution, ...],
    ) -> Self:
        configuration = digest(
            {
                "schema": "tiaf.cold-configuration/1.0",
                "config": config.model_dump(mode="json"),
                "authority_fingerprint": authority_fingerprint,
            }
        )
        ordered = tuple(sorted(resolutions, key=lambda x: x.selection.component_id))
        startup = digest(
            {
                "schema": "tiaf.cold-startup/1.0",
                "configuration_fingerprint": configuration,
                "resolutions": [r.model_dump(mode="json") for r in ordered],
            }
        )
        return cls(
            config=config,
            authority_fingerprint=authority_fingerprint,
            resolutions=ordered,
            configuration_fingerprint=configuration,
            startup_fingerprint=startup,
        )


def replay_startup_composition(content: str) -> StartupComposition:
    """Validate recorded metadata only; never resolve imports or construct a runtime."""
    try:
        payload = json.loads(content)
        validate_no_secrets(payload)
    except (ValueError, TypeError):
        raise StartupError(StartupFailure.CONFIG_SCHEMA_INVALID) from None
    try:
        return StartupComposition.model_validate(payload)
    except ValidationError:
        raise StartupError(StartupFailure.CONFIG_SCHEMA_INVALID) from None
