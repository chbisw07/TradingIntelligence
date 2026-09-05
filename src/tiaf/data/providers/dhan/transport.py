"""Replaceable HTTP transport restricted to Dhan read-only data endpoints."""

from collections.abc import Mapping
from typing import Any, Protocol

import httpx

from tiaf.data import (
    InstrumentNotFoundError,
    ProviderAuthError,
    ProviderBadResponseError,
    ProviderNetworkError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from tiaf.data.providers.dhan.config import DhanConfig

_AUTH_CODES = {"DH-901", "807", "808", "809", "810"}
_RATE_LIMIT_CODES = {"DH-904", "805"}
_NOT_FOUND_CODES = {"813"}


class DhanTransport(Protocol):
    """Minimal injectable transport consumed by the Dhan provider."""

    def post(self, path: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        """POST JSON to one read-only Dhan data endpoint."""
        ...


class HttpxDhanTransport:
    """Small DhanHQ v2 HTTP transport with typed failure translation."""

    def __init__(
        self,
        config: DhanConfig,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=str(config.base_url),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "access-token": config.access_token.get_secret_value(),
                "client-id": config.client_id,
            },
            timeout=config.timeout_seconds,
            transport=transport,
        )

    def __repr__(self) -> str:
        """Return a representation that cannot reveal credentials."""
        return "HttpxDhanTransport(provider='dhan')"

    def close(self) -> None:
        """Close the underlying connection pool."""
        self._client.close()

    def post(self, path: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        """POST a data request and translate transport/provider failures."""
        try:
            response = self._client.post(path.lstrip("/"), json=dict(payload))
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(
                "Dhan data request timed out",
                provider="DHAN",
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderNetworkError(
                "Dhan data request failed at the network boundary",
                provider="DHAN",
            ) from exc

        parsed = self._parse_json(response)
        self._raise_for_failure(response.status_code, parsed)
        return parsed

    @staticmethod
    def _parse_json(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise ProviderBadResponseError(
                "Dhan returned non-JSON data",
                provider="DHAN",
            ) from exc
        if not isinstance(payload, dict):
            raise ProviderBadResponseError(
                "Dhan returned a non-object JSON payload",
                provider="DHAN",
            )
        return payload

    @staticmethod
    def _raise_for_failure(status_code: int, payload: Mapping[str, Any]) -> None:
        code = str(payload.get("errorCode", ""))
        status = str(payload.get("status", "")).casefold()
        if status_code < 400 and not code and status not in {"failure", "error"}:
            return

        message_value = payload.get("errorMessage") or payload.get("message")
        message = str(message_value).strip() if message_value is not None else "request failed"
        detail = f"Dhan API error {code}: {message}" if code else f"Dhan API error: {message}"

        if status_code in {401, 403} or code in _AUTH_CODES:
            raise ProviderAuthError(detail, provider="DHAN")
        if status_code == 429 or code in _RATE_LIMIT_CODES:
            raise ProviderRateLimitError(detail, provider="DHAN")
        if code in _NOT_FOUND_CODES:
            raise InstrumentNotFoundError(detail, provider="DHAN")
        raise ProviderBadResponseError(detail, provider="DHAN")
