import pytest
from playwright.sync_api import expect

from pages.swag_labs_page import SwagLabsPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]

STANDARD_USER = "standard_user"
STANDARD_PASSWORD = "secret_sauce"


@pytest.mark.smoke
def test_standard_user_can_log_in_and_view_products(
    swag_labs: SwagLabsPage,
) -> None:
    swag_labs.open()
    swag_labs.log_in(STANDARD_USER, STANDARD_PASSWORD)

    expect(swag_labs.page.get_by_text("Products", exact=True)).to_be_visible()
    expect(swag_labs.page.get_by_test_id("inventory-list")).to_be_visible()


def test_invalid_credentials_show_login_error(swag_labs: SwagLabsPage) -> None:
    swag_labs.open()
    swag_labs.log_in("invalid_user", "invalid_password")

    expect(swag_labs.page.get_by_test_id("error")).to_contain_text(
        "Username and password do not match"
    )
    expect(swag_labs.page.get_by_role("button", name="Login")).to_be_visible()


@pytest.mark.parametrize(
    ("username", "password", "expected_message"),
    [
        pytest.param("", "", "Username is required", id="missing-username"),
        pytest.param(
            STANDARD_USER,
            "",
            "Password is required",
            id="missing-password",
        ),
    ],
)
def test_required_login_fields_show_validation_error(
    swag_labs: SwagLabsPage,
    username: str,
    password: str,
    expected_message: str,
) -> None:
    swag_labs.open()
    swag_labs.log_in(username, password)

    expect(swag_labs.page.get_by_test_id("error")).to_contain_text(expected_message)
    expect(swag_labs.page.get_by_role("button", name="Login")).to_be_visible()


def test_logged_in_user_can_log_out(swag_labs: SwagLabsPage) -> None:
    swag_labs.open()
    swag_labs.log_in(STANDARD_USER, STANDARD_PASSWORD)
    expect(swag_labs.page.get_by_test_id("inventory-list")).to_be_visible()

    swag_labs.log_out()

    expect(swag_labs.page.get_by_role("button", name="Login")).to_be_visible()
    expect(swag_labs.page.get_by_placeholder("Username")).to_be_empty()
