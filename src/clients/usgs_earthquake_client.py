import logging
from collections.abc import Mapping
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

from config import get_request_timeout, get_usgs_earthquake_base_url

LOGGER = logging.getLogger(__name__)
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


class UsgsEarthquakeClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.base_url = (base_url or get_usgs_earthquake_base_url()).rstrip("/")
        self.timeout = timeout if timeout is not None else get_request_timeout()
        if self.timeout <= 0:
            raise ValueError("Request timeout must be greater than zero")
        self.session = requests.Session()

    def get(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
    ) -> requests.Response:
        request_url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.get(
                request_url,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as error:
            prepared_request = error.request
            method = prepared_request.method if prepared_request else "GET"
            url = prepared_request.url if prepared_request else request_url
            LOGGER.error(
                "HTTP request failed method=%s url=%s error=%s",
                method,
                _safe_request_url(url),
                type(error).__name__,
            )
            raise

        LOGGER.info(
            "HTTP request completed method=%s url=%s status=%s elapsed_ms=%.1f",
            response.request.method,
            _safe_request_url(response.request.url),
            response.status_code,
            response.elapsed.total_seconds() * 1000,
        )
        return response

    def query(self, params: Mapping[str, Any]) -> requests.Response:
        return self.get("query", params=params)

    def close(self) -> None:
        self.session.close()
