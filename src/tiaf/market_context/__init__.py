"""Public provider-neutral sector and macro context evidence foundation."""

from .enums import (
    ContextObservationKind,
    MacroEvidenceFamily,
    MappingQuality,
    SectorEvidenceFamily,
    SensitivityDirection,
)
from .gateway import (
    MacroContextEvidenceGateway,
    SectorContextEvidenceGateway,
    macro_evidence_pack,
    macro_gateway_attributes,
    sector_evidence_pack,
    sector_gateway_attributes,
)
from .models import (
    ContextObservation,
    MacroContextRequest,
    MacroContextSnapshot,
    SectorContextRequest,
    SectorContextSnapshot,
    SectorIdentity,
    SubjectMacroSensitivity,
    context_fingerprint,
)
from .provider import (
    InMemoryMacroContextProvider,
    InMemorySectorContextProvider,
    MacroContextProvider,
    MarketContextProviderError,
    SectorContextProvider,
)

__all__ = [
    "ContextObservation",
    "ContextObservationKind",
    "InMemoryMacroContextProvider",
    "InMemorySectorContextProvider",
    "MacroContextEvidenceGateway",
    "MacroContextProvider",
    "MacroContextRequest",
    "MacroContextSnapshot",
    "MacroEvidenceFamily",
    "MappingQuality",
    "MarketContextProviderError",
    "SectorContextEvidenceGateway",
    "SectorContextProvider",
    "SectorContextRequest",
    "SectorContextSnapshot",
    "SectorEvidenceFamily",
    "SectorIdentity",
    "SensitivityDirection",
    "SubjectMacroSensitivity",
    "context_fingerprint",
    "macro_evidence_pack",
    "macro_gateway_attributes",
    "sector_evidence_pack",
    "sector_gateway_attributes",
]
