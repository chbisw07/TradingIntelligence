"""Classification from explicit source action codes, never headline sentiment."""

from .enums import EventFamily, EventType

CLASSIFICATION_VERSION = "1.0"

_ACTION_MAP: dict[str, tuple[EventFamily, EventType]] = {
    "QUARTERLY_RESULTS": (EventFamily.CORPORATE_RESULTS, EventType.RESULTS_REPORTED),
    "GUIDANCE_RAISED": (EventFamily.GUIDANCE, EventType.GUIDANCE_RAISED),
    "GUIDANCE_CUT": (EventFamily.GUIDANCE, EventType.GUIDANCE_CUT),
    "DIVIDEND_DECLARED": (EventFamily.DIVIDEND, EventType.DIVIDEND_DECLARED),
    "BUYBACK_APPROVED": (EventFamily.BUYBACK, EventType.BUYBACK_APPROVED),
    "ORDER_AWARDED": (EventFamily.ORDER_CONTRACT, EventType.ORDER_AWARDED),
    "ORDER_LOST": (EventFamily.ORDER_CONTRACT, EventType.ORDER_LOST),
    "CAPEX_ANNOUNCED": (EventFamily.CAPEX, EventType.CAPEX_ANNOUNCED),
    "REGULATORY_APPROVAL": (EventFamily.REGULATORY, EventType.REGULATORY_APPROVAL),
    "REGULATORY_ACTION": (EventFamily.REGULATORY, EventType.REGULATORY_ACTION),
    "RATING_UPGRADE": (EventFamily.CREDIT_RATING, EventType.RATING_UPGRADE),
    "RATING_DOWNGRADE": (EventFamily.CREDIT_RATING, EventType.RATING_DOWNGRADE),
}


def classify_explicit_action(action_code: str | None) -> tuple[EventFamily, EventType]:
    """Map a provider-declared action or preserve ambiguity as OTHER/UNKNOWN."""
    if action_code is None:
        return EventFamily.OTHER, EventType.UNKNOWN
    return _ACTION_MAP.get(action_code.strip().upper(), (EventFamily.OTHER, EventType.UNKNOWN))
