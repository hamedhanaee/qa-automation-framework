import logging
from collections.abc import Mapping
from typing import Any

import requests

from clients.request_diagnostics import log_request_failure, log_response
from config import get_request_timeout, get_world_bank_indicators_base_url

LOGGER = logging.getLogger(__name__)


class WorldBankIndicatorsClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.base_url = (base_url or get_world_bank_indicators_base_url()).rstrip("/")
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
            log_request_failure(LOGGER, error, request_url)
            raise

        log_response(LOGGER, response)
        return response

    def get_indicator(
        self,
        country_codes: str,
        indicator_code: str,
        params: Mapping[str, Any] | None = None,
    ) -> requests.Response:
        query_params = {"format": "json", **(params or {})}
        return self.get(
            f"country/{country_codes}/indicator/{indicator_code}",
            params=query_params,
        )

    def close(self) -> None:
        self.session.close()
