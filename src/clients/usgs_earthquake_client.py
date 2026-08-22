from collections.abc import Mapping
from typing import Any

import requests

from config import USGS_EARTHQUAKE_BASE_URL, get_request_timeout


class UsgsEarthquakeClient:
    def __init__(
        self,
        base_url: str = USGS_EARTHQUAKE_BASE_URL,
        timeout: float | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout if timeout is not None else get_request_timeout()
        self.session = requests.Session()

    def get(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
    ) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/{path.lstrip('/')}",
            params=params,
            timeout=self.timeout,
        )

    def query(self, params: Mapping[str, Any]) -> requests.Response:
        return self.get("query", params=params)

    def close(self) -> None:
        self.session.close()
