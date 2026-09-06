"""Cache-key and in-memory backend behavior."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from tiaf.data.runtime import CacheEntry, CacheKey, InMemoryCacheBackend

IST = ZoneInfo("Asia/Kolkata")
NOW = datetime(2026, 9, 6, 10, 0, tzinfo=IST)


def key(**changes: object) -> CacheKey:
    values: dict[str, object] = {
        "namespace": "market",
        "provider": "DHAN",
        "instrument_identity": "NSE_EQ:2885",
        "operation": "quote",
    }
    values.update(changes)
    return CacheKey.model_validate(values)


def entry(cache_key: CacheKey, value: object = "value") -> CacheEntry[object]:
    return CacheEntry(key=cache_key, value=value, stored_at=NOW, source_provider="DHAN")


def test_cache_key_equality_and_hash_are_deterministic() -> None:
    left = key(parameters=(("to", "b"), ("from", "a")))
    right = key(parameters=[["from", "a"], ["to", "b"]])
    assert left == right
    assert hash(left) == hash(right)


def test_cache_key_canonicalizes_parameter_order() -> None:
    assert key(parameters=(("z", "2"), ("a", "1"))).parameters == (
        ("a", "1"),
        ("z", "2"),
    )


@pytest.mark.parametrize(
    "name",
    ["access_token", "api-key", "client_id", "password", "secret_value", "Authorization"],
)
def test_cache_key_rejects_credential_parameter_names(name: str) -> None:
    with pytest.raises(ValidationError, match="credentials are not permitted"):
        key(parameters=((name, "never-log-me"),))


def test_cache_key_string_and_json_are_stable() -> None:
    cache_key = key(parameters=(("expiry", "2026-09-29"),))
    assert str(cache_key) == "market:dhan:NSE_EQ:2885:quote?expiry=2026-09-29"
    assert CacheKey.model_validate_json(cache_key.model_dump_json()) == cache_key


def test_cache_miss() -> None:
    cache = InMemoryCacheBackend()
    assert cache.get(key()) is None
    assert cache.stats().misses == 1


def test_cache_put_and_get() -> None:
    cache = InMemoryCacheBackend()
    cache_key = key()
    stored = cache.put(cache_key, entry(cache_key))
    assert cache.get(cache_key) == stored
    assert cache.contains(cache_key)


def test_cache_overwrite_increments_generation() -> None:
    cache = InMemoryCacheBackend()
    cache_key = key()
    first = cache.put(cache_key, entry(cache_key, "first"))
    second = cache.put(cache_key, entry(cache_key, "second"))
    assert first.generation == 1
    assert second.generation == 2
    assert cache.get(cache_key) == second


def test_cache_rejects_mismatched_entry_key() -> None:
    cache = InMemoryCacheBackend()
    with pytest.raises(ValueError, match="does not match"):
        cache.put(key(operation="quote"), entry(key(operation="historical")))


def test_cache_delete() -> None:
    cache = InMemoryCacheBackend()
    cache_key = key()
    cache.put(cache_key, entry(cache_key))
    assert cache.delete(cache_key)
    assert not cache.delete(cache_key)


def test_cache_clear() -> None:
    cache = InMemoryCacheBackend()
    cache_key = key()
    cache.put(cache_key, entry(cache_key))
    cache.clear()
    assert cache.stats().entries == 0


def test_namespace_invalidation_is_scoped() -> None:
    cache = InMemoryCacheBackend()
    market = key(namespace="market")
    derivatives = key(namespace="derivatives", operation="option_chain")
    cache.put(market, entry(market))
    cache.put(derivatives, entry(derivatives))
    assert cache.invalidate_namespace(" MARKET ") == 1
    assert not cache.contains(market)
    assert cache.contains(derivatives)


def test_instrument_invalidation_is_scoped() -> None:
    cache = InMemoryCacheBackend()
    reliance = key(instrument_identity="NSE_EQ:2885")
    other = key(instrument_identity="NSE_EQ:123")
    cache.put(reliance, entry(reliance))
    cache.put(other, entry(other))
    assert cache.invalidate_instrument("NSE_EQ:2885") == 1
    assert cache.contains(other)


def test_lru_capacity_evicts_oldest_access_order() -> None:
    cache = InMemoryCacheBackend(max_entries=2)
    first = key(instrument_identity="1")
    second = key(instrument_identity="2")
    third = key(instrument_identity="3")
    cache.put(first, entry(first))
    cache.put(second, entry(second))
    assert cache.get(first) is not None
    cache.put(third, entry(third))
    assert cache.contains(first)
    assert not cache.contains(second)
    assert cache.stats().evictions == 1


def test_cache_entry_normalizes_timestamp_and_rejects_naive() -> None:
    cache_key = key()
    utc = ZoneInfo("UTC")
    cached = CacheEntry(key=cache_key, value=1, stored_at=NOW.astimezone(utc))
    offset = cached.stored_at.utcoffset()
    assert offset is not None
    assert offset.total_seconds() == 19_800
    with pytest.raises(ValidationError, match="timezone-aware"):
        CacheEntry(key=cache_key, value=1, stored_at=datetime(2026, 9, 6))
