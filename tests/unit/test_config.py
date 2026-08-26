from collections.abc import Callable

import pytest

from config import (
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
    DEFAULT_USGS_EARTHQUAKE_BASE_URL,
    DEFAULT_WORLD_BANK_INDICATORS_BASE_URL,
    get_request_timeout,
    get_usgs_earthquake_base_url,
    get_world_bank_indicators_base_url,
)

pytestmark = pytest.mark.regression


@pytest.mark.parametrize(
    ("environment_variable", "getter", "expected_default"),
    [
        pytest.param(
            "USGS_EARTHQUAKE_BASE_URL",
            get_usgs_earthquake_base_url,
            DEFAULT_USGS_EARTHQUAKE_BASE_URL,
            id="usgs",
        ),
        pytest.param(
            "WORLD_BANK_INDICATORS_BASE_URL",
            get_world_bank_indicators_base_url,
            DEFAULT_WORLD_BANK_INDICATORS_BASE_URL,
            id="world-bank",
        ),
    ],
)
def test_base_url_uses_public_default_when_override_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable: str,
    getter: Callable[[], str],
    expected_default: str,
) -> None:
    monkeypatch.delenv(environment_variable, raising=False)

    assert getter() == expected_default


@pytest.mark.parametrize(
    ("environment_variable", "getter"),
    [
        pytest.param(
            "USGS_EARTHQUAKE_BASE_URL",
            get_usgs_earthquake_base_url,
            id="usgs",
        ),
        pytest.param(
            "WORLD_BANK_INDICATORS_BASE_URL",
            get_world_bank_indicators_base_url,
            id="world-bank",
        ),
    ],
)
def test_base_url_override_removes_trailing_slash(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable: str,
    getter: Callable[[], str],
) -> None:
    monkeypatch.setenv(environment_variable, "https://api.example.test/v2/")

    assert getter() == "https://api.example.test/v2"


@pytest.mark.parametrize(
    ("environment_variable", "getter"),
    [
        pytest.param(
            "USGS_EARTHQUAKE_BASE_URL",
            get_usgs_earthquake_base_url,
            id="usgs",
        ),
        pytest.param(
            "WORLD_BANK_INDICATORS_BASE_URL",
            get_world_bank_indicators_base_url,
            id="world-bank",
        ),
    ],
)
def test_empty_base_url_override_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    environment_variable: str,
    getter: Callable[[], str],
) -> None:
    monkeypatch.setenv(environment_variable, "")

    with pytest.raises(ValueError, match=f"{environment_variable} must not be empty"):
        getter()


def test_request_timeout_uses_default_when_override_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("API_REQUEST_TIMEOUT_SECONDS", raising=False)

    assert get_request_timeout() == DEFAULT_REQUEST_TIMEOUT_SECONDS


def test_request_timeout_uses_numeric_environment_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("API_REQUEST_TIMEOUT_SECONDS", "2.5")

    assert get_request_timeout() == 2.5


@pytest.mark.parametrize(
    "configured_timeout",
    [
        pytest.param("0", id="zero"),
        pytest.param("-1", id="negative"),
    ],
)
def test_non_positive_request_timeout_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    configured_timeout: str,
) -> None:
    monkeypatch.setenv("API_REQUEST_TIMEOUT_SECONDS", configured_timeout)

    with pytest.raises(
        ValueError,
        match="API_REQUEST_TIMEOUT_SECONDS must be greater than zero",
    ):
        get_request_timeout()


def test_non_numeric_request_timeout_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("API_REQUEST_TIMEOUT_SECONDS", "not-a-number")

    with pytest.raises(ValueError, match="could not convert string to float"):
        get_request_timeout()
