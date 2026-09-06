"""Rate policy, provider gate, and Dhan policy tests."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from tiaf.data.providers.dhan import (
    DHAN_OPTION_CHAIN_RATE_POLICY,
    DHAN_QUOTE_RATE_POLICY,
    dhan_rate_policy_registry,
)
from tiaf.data.runtime import (
    ProviderGateState,
    ProviderScheduler,
    RateLimitScope,
    RatePolicy,
    RatePolicyRegistry,
)

IST = ZoneInfo("Asia/Kolkata")
WALL_NOW = datetime(2026, 9, 6, 12, 0, tzinfo=IST)


class Clock:
    def __init__(self, value: float = 100.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value


def scheduler_for(policy: RatePolicy) -> tuple[ProviderScheduler, Clock]:
    clock = Clock()
    scheduler = ProviderScheduler(
        RatePolicyRegistry((policy,)),
        monotonic_clock=clock,
        wall_clock=lambda: WALL_NOW,
    )
    return scheduler, clock


def policy(**changes: object) -> RatePolicy:
    values: dict[str, object] = {
        "provider": "test",
        "operation": "quote",
        "minimum_interval_seconds": 2,
    }
    values.update(changes)
    return RatePolicy.model_validate(values)


def test_unrestricted_provider_is_ready() -> None:
    scheduler = ProviderScheduler(wall_clock=lambda: WALL_NOW)
    assert scheduler.can_execute("new", "unknown", "key").state is ProviderGateState.READY


def test_minimum_interval_blocks_without_sleeping() -> None:
    scheduler, _ = scheduler_for(policy())
    assert scheduler.reserve("test", "quote").allowed
    blocked = scheduler.reserve("test", "quote")
    assert blocked.state is ProviderGateState.RATE_LIMITED
    assert blocked.retry_after_seconds == 2


def test_next_allowed_calculation_uses_monotonic_time() -> None:
    scheduler, clock = scheduler_for(policy())
    scheduler.reserve("test", "quote")
    assert scheduler.next_allowed_at("test", "quote") == 102
    clock.value = 102
    assert scheduler.can_execute("test", "quote").allowed


def test_provider_scopes_are_independent() -> None:
    registry = RatePolicyRegistry((policy(provider="one"), policy(provider="two")))
    scheduler = ProviderScheduler(registry, wall_clock=lambda: WALL_NOW)
    scheduler.reserve("one", "quote", now_monotonic=0)
    assert scheduler.can_execute("two", "quote", now_monotonic=0).allowed


def test_operation_scopes_are_independent() -> None:
    registry = RatePolicyRegistry((policy(operation="quote"), policy(operation="historical")))
    scheduler = ProviderScheduler(registry, wall_clock=lambda: WALL_NOW)
    scheduler.reserve("test", "quote", now_monotonic=0)
    assert scheduler.can_execute("test", "historical", now_monotonic=0).allowed


def test_request_key_scope_blocks_only_identical_key() -> None:
    scheduler, _ = scheduler_for(policy(key_scope=RateLimitScope.REQUEST_KEY))
    scheduler.reserve("test", "quote", "one")
    assert not scheduler.can_execute("test", "quote", "one").allowed
    assert scheduler.can_execute("test", "quote", "two").allowed


def test_request_key_scope_requires_request_key() -> None:
    scheduler, _ = scheduler_for(policy(key_scope=RateLimitScope.REQUEST_KEY))
    with pytest.raises(ValueError, match="request_key is required"):
        scheduler.can_execute("test", "quote")


def test_rolling_window_blocks_at_capacity_and_recovers() -> None:
    scheduler, clock = scheduler_for(
        policy(minimum_interval_seconds=None, max_requests=2, window_seconds=10)
    )
    scheduler.reserve("test", "quote")
    clock.value = 101
    scheduler.reserve("test", "quote")
    assert scheduler.next_allowed_at("test", "quote") == 110
    clock.value = 110
    assert scheduler.can_execute("test", "quote").allowed


@pytest.mark.parametrize(
    "values",
    [
        {"provider": "x", "operation": "x"},
        {"provider": "x", "operation": "x", "max_requests": 1},
        {"provider": "x", "operation": "x", "window_seconds": 1},
    ],
)
def test_invalid_rate_policy_shapes(values: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        RatePolicy.model_validate(values)


def test_provider_disable_and_enable() -> None:
    scheduler = ProviderScheduler(wall_clock=lambda: WALL_NOW)
    scheduler.disable_provider("TEST", "maintenance")
    blocked = scheduler.can_execute("test", "quote")
    assert blocked.state is ProviderGateState.DISABLED
    assert blocked.reason == "maintenance"
    scheduler.enable_provider("test")
    assert scheduler.can_execute("test", "quote").allowed


def test_explicit_provider_cooldown() -> None:
    scheduler, clock = scheduler_for(policy())
    scheduler.record_rate_limit("test", 5, now_monotonic=clock.value)
    blocked = scheduler.can_execute("test", "quote")
    assert blocked.state is ProviderGateState.COOLDOWN
    assert blocked.retry_after_seconds == 5
    clock.value += 5
    assert scheduler.can_execute("test", "quote").allowed


def test_dhan_option_chain_policy_is_three_seconds_per_request_key() -> None:
    assert DHAN_OPTION_CHAIN_RATE_POLICY.minimum_interval_seconds == 3
    assert DHAN_OPTION_CHAIN_RATE_POLICY.key_scope is RateLimitScope.REQUEST_KEY


def test_dhan_quote_policy_is_one_request_per_second() -> None:
    assert DHAN_QUOTE_RATE_POLICY.minimum_interval_seconds == 1
    assert DHAN_QUOTE_RATE_POLICY.key_scope is RateLimitScope.OPERATION


def test_dhan_unknown_operation_has_no_invented_rule() -> None:
    registry = dhan_rate_policy_registry()
    assert registry.policies_for("dhan", "historical") == ()
    scheduler = ProviderScheduler(registry, wall_clock=lambda: WALL_NOW)
    scheduler.reserve("dhan", "historical", now_monotonic=0)
    assert scheduler.reserve("dhan", "historical", now_monotonic=0).allowed


def test_gate_audit_timestamp_is_asia_kolkata() -> None:
    scheduler = ProviderScheduler(wall_clock=lambda: WALL_NOW)
    decision = scheduler.can_execute("test", "quote", now_monotonic=1)
    assert decision.checked_at.tzinfo == IST
    assert "+05:30" in decision.model_dump_json()
