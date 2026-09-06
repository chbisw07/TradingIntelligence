"""Public A1.6 runtime contract exports."""

import inspect

import tiaf.data.runtime as runtime


def test_runtime_public_inventory() -> None:
    expected = {
        "CacheBackend",
        "CacheDisposition",
        "CacheEntry",
        "CacheKey",
        "DataFetchCoordinator",
        "FetchDisposition",
        "FetchResult",
        "FreshnessPolicyRegistry",
        "FreshnessRequirement",
        "InMemoryCacheBackend",
        "ProviderScheduleBlockedError",
        "ProviderScheduler",
        "RatePolicy",
        "RequestPriority",
        "RuntimeStats",
    }
    assert expected <= set(runtime.__all__)


def test_runtime_implementation_contains_no_sleep_call() -> None:
    assert "time.sleep" not in inspect.getsource(runtime.ProviderScheduler)
    assert "time.sleep" not in inspect.getsource(runtime.DataFetchCoordinator)
