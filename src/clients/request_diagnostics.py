import logging
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

REDACTED_VALUE = "[REDACTED]"
SENSITIVE_QUERY_PARAMETER_NAMES = {
    "access_token",
    "api_key",
    "apikey",
    "authorization",
    "key",
    "password",
    "secret",
    "signature",
    "token",
}


def _is_sensitive_query_parameter(name: str) -> bool:
    normalized_name = name.lower().replace("-", "_")
    return normalized_name in SENSITIVE_QUERY_PARAMETER_NAMES or any(
        sensitive_part in normalized_name
        for sensitive_part in ("password", "secret", "signature", "token")
    )


def _safe_request_url(url: str) -> str:
    parsed_url = urlsplit(url)
    safe_query = urlencode(
        [
            (
                name,
                REDACTED_VALUE if _is_sensitive_query_parameter(name) else value,
            )
            for name, value in parse_qsl(parsed_url.query, keep_blank_values=True)
        ],
        doseq=True,
    )
    return urlunsplit(
        (
            parsed_url.scheme,
            parsed_url.netloc.rsplit("@", maxsplit=1)[-1],
            parsed_url.path,
            safe_query,
            "",
        )
    )


def log_response(logger: logging.Logger, response: requests.Response) -> None:
    logger.info(
        "HTTP request completed method=%s url=%s status=%s elapsed_ms=%.1f",
        response.request.method,
        _safe_request_url(response.request.url),
        response.status_code,
        response.elapsed.total_seconds() * 1000,
    )


def log_request_failure(
    logger: logging.Logger,
    error: requests.RequestException,
    request_url: str,
) -> None:
    prepared_request = error.request
    method = prepared_request.method if prepared_request else "GET"
    url = prepared_request.url if prepared_request else request_url
    logger.error(
        "HTTP request failed method=%s url=%s error=%s",
        method,
        _safe_request_url(url),
        type(error).__name__,
    )
