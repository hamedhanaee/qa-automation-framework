import logging
from datetime import timedelta

import pytest
import requests

from clients.request_diagnostics import (
    REDACTED_VALUE,
    _safe_request_url,
    log_request_failure,
    log_response,
)

pytestmark = pytest.mark.regression


def test_safe_request_url_redacts_credentials_and_sensitive_query_values() -> None:
    url = (
        "https://user:password@example.test/events?"
        "date=2010&api_key=api-secret&client_secret=client-secret&"
        "refresh-token=refresh-secret#private-fragment"
    )

    safe_url = _safe_request_url(url)

    assert safe_url.startswith("https://example.test/events?")
    assert "date=2010" in safe_url
    assert safe_url.count("%5BREDACTED%5D") == 3
    assert REDACTED_VALUE not in safe_url
    assert "password" not in safe_url
    assert "api-secret" not in safe_url
    assert "client-secret" not in safe_url
    assert "refresh-secret" not in safe_url
    assert "private-fragment" not in safe_url


def test_safe_request_url_preserves_repeated_non_sensitive_parameters() -> None:
    safe_url = _safe_request_url("https://example.test/events?country=USA&country=CAN")

    assert safe_url == "https://example.test/events?country=USA&country=CAN"


def test_log_response_includes_request_context_without_sensitive_value(
    caplog: pytest.LogCaptureFixture,
) -> None:
    response = requests.Response()
    response.status_code = 200
    response.request = requests.Request(
        "GET",
        "https://example.test/events",
        params={"date": "2010", "api_key": "api-secret"},
    ).prepare()
    response.elapsed = timedelta(milliseconds=125)
    logger = logging.getLogger("tests.response_diagnostics")
    caplog.set_level(logging.INFO, logger=logger.name)

    log_response(logger, response)

    assert "method=GET" in caplog.text
    assert (
        "url=https://example.test/events?date=2010&api_key=%5BREDACTED%5D"
        in caplog.text
    )
    assert "status=200" in caplog.text
    assert "elapsed_ms=125.0" in caplog.text
    assert "api-secret" not in caplog.text


def test_log_request_failure_uses_prepared_request_and_redacts_secret(
    caplog: pytest.LogCaptureFixture,
) -> None:
    prepared_request = requests.Request(
        "GET",
        "https://example.test/events",
        params={"access_token": "token-secret"},
    ).prepare()
    error = requests.ConnectionError("connection failed", request=prepared_request)
    logger = logging.getLogger("tests.request_diagnostics")
    caplog.set_level(logging.ERROR, logger=logger.name)

    log_request_failure(logger, error, "https://fallback.example.test")

    assert "method=GET" in caplog.text
    assert "url=https://example.test/events?access_token=%5BREDACTED%5D" in caplog.text
    assert "error=ConnectionError" in caplog.text
    assert "token-secret" not in caplog.text
