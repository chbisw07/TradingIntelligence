"""Thread-safe provider-neutral in-memory factual cache."""

from collections import OrderedDict
from threading import RLock
from typing import Any, Protocol

from tiaf.data.runtime.enums import CacheDisposition
from tiaf.data.runtime.models import CacheEntry, CacheKey, CacheStats


class CacheBackend(Protocol):
    """Minimum cache behavior required by the data runtime."""

    def get(self, key: CacheKey) -> CacheEntry[Any] | None: ...

    def put(self, key: CacheKey, entry: CacheEntry[Any]) -> CacheEntry[Any]: ...

    def delete(self, key: CacheKey) -> bool: ...

    def clear(self) -> None: ...

    def contains(self, key: CacheKey) -> bool: ...

    def invalidate_namespace(self, namespace: str) -> int: ...

    def invalidate_instrument(self, instrument_identity: str) -> int: ...

    def record_disposition(self, disposition: CacheDisposition) -> None: ...

    def stats(self) -> CacheStats: ...


class InMemoryCacheBackend:
    """Deterministic LRU cache guarded by one short-lived re-entrant lock."""

    def __init__(self, max_entries: int | None = None) -> None:
        if max_entries is not None and max_entries <= 0:
            raise ValueError("max_entries must be positive")
        self._max_entries = max_entries
        self._entries: OrderedDict[CacheKey, CacheEntry[Any]] = OrderedDict()
        self._lock = RLock()
        self._hits = 0
        self._misses = 0
        self._fresh_hits = 0
        self._aging_hits = 0
        self._stale_hits = 0
        self._puts = 0
        self._evictions = 0

    def get(self, key: CacheKey) -> CacheEntry[Any] | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                self._misses += 1
                return None
            self._hits += 1
            self._entries.move_to_end(key)
            return entry

    def put(self, key: CacheKey, entry: CacheEntry[Any]) -> CacheEntry[Any]:
        if entry.key != key:
            raise ValueError("cache entry key does not match put key")
        with self._lock:
            current = self._entries.get(key)
            generation = 1 if current is None else current.generation + 1
            stored = entry.model_copy(update={"generation": generation})
            self._entries[key] = stored
            self._entries.move_to_end(key)
            self._puts += 1
            if self._max_entries is not None and len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)
                self._evictions += 1
            return stored

    def delete(self, key: CacheKey) -> bool:
        with self._lock:
            return self._entries.pop(key, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    def contains(self, key: CacheKey) -> bool:
        with self._lock:
            return key in self._entries

    def invalidate_namespace(self, namespace: str) -> int:
        normalized = namespace.strip().casefold()
        with self._lock:
            keys = tuple(key for key in self._entries if key.namespace == normalized)
            for key in keys:
                del self._entries[key]
            return len(keys)

    def invalidate_instrument(self, instrument_identity: str) -> int:
        normalized = instrument_identity.strip()
        with self._lock:
            keys = tuple(
                key for key in self._entries if key.instrument_identity == normalized
            )
            for key in keys:
                del self._entries[key]
            return len(keys)

    def record_disposition(self, disposition: CacheDisposition) -> None:
        with self._lock:
            if disposition is CacheDisposition.HIT_FRESH:
                self._fresh_hits += 1
            elif disposition is CacheDisposition.HIT_AGING:
                self._aging_hits += 1
            elif disposition is CacheDisposition.HIT_STALE:
                self._stale_hits += 1

    def stats(self) -> CacheStats:
        with self._lock:
            return CacheStats(
                entries=len(self._entries),
                hits=self._hits,
                misses=self._misses,
                fresh_hits=self._fresh_hits,
                aging_hits=self._aging_hits,
                stale_hits=self._stale_hits,
                puts=self._puts,
                evictions=self._evictions,
            )
