"""Live-documented Dhan request policies for the A1.6 runtime gate."""

from tiaf.data.runtime import RateLimitScope, RatePolicy, RatePolicyRegistry

DHAN_QUOTE_RATE_POLICY = RatePolicy(
    provider="dhan",
    operation="quote",
    minimum_interval_seconds=1.0,
    key_scope=RateLimitScope.OPERATION,
    metadata={
        "documentation": "https://dhanhq.co/docs/v2/market-quote/",
        "basis": "market quote API documents one request per second",
    },
)

DHAN_OPTION_CHAIN_RATE_POLICY = RatePolicy(
    provider="dhan",
    operation="option_chain",
    minimum_interval_seconds=3.0,
    key_scope=RateLimitScope.REQUEST_KEY,
    metadata={
        "documentation": "https://dhanhq.co/docs/v2/option-chain/",
        "basis": "option chain API documents one unique request every three seconds",
    },
)

DHAN_RATE_POLICIES = (
    DHAN_QUOTE_RATE_POLICY,
    DHAN_OPTION_CHAIN_RATE_POLICY,
)


def dhan_rate_policy_registry() -> RatePolicyRegistry:
    """Return a new registry containing only Dhan rules with exact support."""
    return RatePolicyRegistry(DHAN_RATE_POLICIES)
