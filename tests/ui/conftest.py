import os
from collections.abc import Iterator

import pytest
from playwright.sync_api import Page, Playwright

from pages.swag_labs_page import SwagLabsPage

DEFAULT_SAUCEDEMO_BASE_URL = "https://www.saucedemo.com"


@pytest.fixture(scope="session", autouse=True)
def configure_saucedemo_test_ids(playwright: Playwright) -> Iterator[None]:
    playwright.selectors.set_test_id_attribute("data-test")
    yield
    playwright.selectors.set_test_id_attribute("data-testid")


@pytest.fixture
def swag_labs(page: Page) -> SwagLabsPage:
    base_url = os.getenv("SAUCEDEMO_BASE_URL", DEFAULT_SAUCEDEMO_BASE_URL).rstrip("/")
    return SwagLabsPage(page, base_url)
