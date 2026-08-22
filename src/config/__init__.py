import os

USGS_EARTHQUAKE_BASE_URL = os.getenv(
    "USGS_EARTHQUAKE_BASE_URL",
    "https://earthquake.usgs.gov/fdsnws/event/1",
)
DEFAULT_REQUEST_TIMEOUT_SECONDS = 15.0


def get_request_timeout() -> float:
    configured_timeout = os.getenv("API_REQUEST_TIMEOUT_SECONDS")
    if configured_timeout is None:
        return DEFAULT_REQUEST_TIMEOUT_SECONDS

    timeout = float(configured_timeout)
    if timeout <= 0:
        raise ValueError("API_REQUEST_TIMEOUT_SECONDS must be greater than zero")
    return timeout
