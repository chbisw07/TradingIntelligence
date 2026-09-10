"""HTTP transport isolated beneath authoritative official-source adapters."""

from collections.abc import Callable
from datetime import datetime
from urllib.parse import urljoin

import httpx

from tiaf.contracts.common import TIAF_TIMEZONE

from ..enums import ProviderFailureKind
from .authoritative import OfficialDocumentResponse, OfficialDocumentTransportError


class HttpxOfficialDocumentTransport:
    """Bounded read-only GET transport with validation before every redirect."""

    def __init__(self, *, user_agent: str = "TradingIntelligence/0.1 read-only") -> None:
        self._user_agent = user_agent

    def fetch(
        self,
        url: str,
        *,
        validate_url: Callable[[str], None],
        max_bytes: int,
        timeout_seconds: float,
    ) -> OfficialDocumentResponse:
        current = url
        validate_url(current)
        try:
            with httpx.Client(
                follow_redirects=False,
                timeout=timeout_seconds,
                headers={
                    "User-Agent": self._user_agent,
                    "Accept": "application/pdf,text/html,text/plain,application/xhtml+xml",
                },
            ) as client:
                for _ in range(5):
                    with client.stream("GET", current) as response:
                        if response.status_code in {301, 302, 303, 307, 308}:
                            location = response.headers.get("location")
                            if not location:
                                raise OfficialDocumentTransportError(
                                    "official source redirect omitted Location",
                                    kind=ProviderFailureKind.INVALID_REDIRECT,
                                )
                            current = urljoin(current, location)
                            validate_url(current)
                            continue
                        return self._response(url, current, response, max_bytes)
        except httpx.TimeoutException as exc:
            raise OfficialDocumentTransportError(
                "official source request timed out",
                kind=ProviderFailureKind.TIMEOUT,
            ) from exc
        except httpx.NetworkError as exc:
            raise OfficialDocumentTransportError(
                "official source network request failed",
                kind=ProviderFailureKind.NETWORK,
            ) from exc
        raise OfficialDocumentTransportError(
            "official source exceeded redirect limit",
            kind=ProviderFailureKind.INVALID_REDIRECT,
        )

    @staticmethod
    def _response(
        requested_url: str,
        final_url: str,
        response: httpx.Response,
        max_bytes: int,
    ) -> OfficialDocumentResponse:
        if response.status_code in {401, 403}:
            raise OfficialDocumentTransportError(
                f"official source restricted access with HTTP {response.status_code}",
                kind=ProviderFailureKind.ACCESS_RESTRICTED,
            )
        if response.status_code == 404:
            raise OfficialDocumentTransportError(
                "official document was not found",
                kind=ProviderFailureKind.DOCUMENT_UNAVAILABLE,
            )
        if response.status_code == 429:
            raise OfficialDocumentTransportError(
                "official source rate limited the bounded request",
                kind=ProviderFailureKind.ACCESS_RESTRICTED,
            )
        if response.status_code >= 500:
            raise OfficialDocumentTransportError(
                f"official source unavailable with HTTP {response.status_code}",
                kind=ProviderFailureKind.PROVIDER_UNAVAILABLE,
            )
        declared_length = response.headers.get("content-length")
        if declared_length is not None:
            try:
                if int(declared_length) > max_bytes:
                    raise OfficialDocumentTransportError(
                        "official document exceeds configured size limit",
                        kind=ProviderFailureKind.MALFORMED_PAYLOAD,
                    )
            except ValueError:
                pass
        content_parts: list[bytes] = []
        received = 0
        for chunk in response.iter_bytes():
            received += len(chunk)
            if received > max_bytes:
                raise OfficialDocumentTransportError(
                    "official document exceeds configured size limit",
                    kind=ProviderFailureKind.MALFORMED_PAYLOAD,
                )
            content_parts.append(chunk)
        content = b"".join(content_parts)
        return OfficialDocumentResponse(
            requested_url=requested_url,
            final_url=final_url,
            status_code=response.status_code,
            mime_type=response.headers.get("content-type", "application/octet-stream"),
            content=content,
            acquired_at=datetime.now(TIAF_TIMEZONE),
        )
