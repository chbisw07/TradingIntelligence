"""HTTP boundary tests using HTTPX's in-memory mock transport."""

import httpx
import pytest

from tiaf.data import (
    InstrumentNotFoundError,
    ProviderAuthError,
    ProviderBadResponseError,
    ProviderNetworkError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from tiaf.data.providers.dhan import HttpxDhanTransport

from ._support import dhan_config


def transport_returning(response: httpx.Response) -> HttpxDhanTransport:
    mock = httpx.MockTransport(lambda request: response)
    return HttpxDhanTransport(dhan_config(), transport=mock)


@pytest.mark.parametrize(
    ("status_code", "body", "error_type"),
    [
        (401, {"errorCode": "808", "errorMessage": "Authentication failed"}, ProviderAuthError),
        (429, {"errorCode": "805", "errorMessage": "Too many requests"}, ProviderRateLimitError),
        (
            400,
            {"errorCode": "813", "errorMessage": "Invalid SecurityId"},
            InstrumentNotFoundError,
        ),
        (
            500,
            {"errorCode": "800", "errorMessage": "Internal server error"},
            ProviderBadResponseError,
        ),
    ],
)
def test_http_and_dhan_errors_are_translated(
    status_code: int,
    body: dict[str, str],
    error_type: type[Exception],
) -> None:
    response = httpx.Response(status_code, json=body)

    with pytest.raises(error_type):
        transport_returning(response).post("/marketfeed/quote", {})


def test_non_json_response_is_bad_response() -> None:
    response = httpx.Response(502, text="upstream unavailable")

    with pytest.raises(ProviderBadResponseError, match="non-JSON"):
        transport_returning(response).post("/marketfeed/quote", {})


def test_transport_preserves_v2_base_path_and_required_headers() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["client_id"] = request.headers["client-id"]
        captured["access_token"] = request.headers["access-token"]
        return httpx.Response(200, json={"status": "success", "data": {}})

    transport = HttpxDhanTransport(
        dhan_config(),
        transport=httpx.MockTransport(handler),
    )
    transport.post("/marketfeed/quote", {})

    assert captured == {
        "url": "https://api.dhan.co/v2/marketfeed/quote",
        "client_id": "test-client-id",
        "access_token": "test-token-value",
    }


def test_timeout_is_translated() -> None:
    def timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    transport = HttpxDhanTransport(dhan_config(), transport=httpx.MockTransport(timeout))

    with pytest.raises(ProviderTimeoutError):
        transport.post("/charts/historical", {})


def test_connection_error_is_translated() -> None:
    def connection_error(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    transport = HttpxDhanTransport(
        dhan_config(),
        transport=httpx.MockTransport(connection_error),
    )

    with pytest.raises(ProviderNetworkError):
        transport.post("/charts/intraday", {})


def test_access_token_is_absent_from_transport_repr_and_errors() -> None:
    token = "highly-sensitive-test-token"
    config = dhan_config(token)
    response = httpx.Response(
        401,
        json={"errorCode": "808", "errorMessage": "Authentication failed"},
    )
    transport = HttpxDhanTransport(config, transport=httpx.MockTransport(lambda request: response))

    with pytest.raises(ProviderAuthError) as captured:
        transport.post("/marketfeed/quote", {})

    assert token not in repr(transport)
    assert token not in str(captured.value)
    assert token not in repr(captured.value)
