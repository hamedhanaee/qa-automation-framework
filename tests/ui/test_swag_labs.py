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


def test_user_can_purchase_product(swag_labs: SwagLabsPage) -> None:
    product_name = "Sauce Labs Backpack"
    swag_labs.open()
    swag_labs.log_in(STANDARD_USER, STANDARD_PASSWORD)
    swag_labs.add_product_to_cart(product_name)
    swag_labs.open_cart()

    expect(swag_labs.page.get_by_text(product_name, exact=True)).to_be_visible()

    swag_labs.complete_checkout("Sam", "Tester", "10001")

    expect(
        swag_labs.page.get_by_role("heading", name="Thank you for your order!")
    ).to_be_visible()
    expect(swag_labs.page.get_by_text("Your order has been dispatched")).to_be_visible()


def test_invalid_credentials_show_login_error(swag_labs: SwagLabsPage) -> None:
    swag_labs.open()
    swag_labs.log_in("invalid_user", "invalid_password")

    expect(swag_labs.page.get_by_test_id("error")).to_contain_text(
        "Username and password do not match"
    )
    expect(swag_labs.page.get_by_role("button", name="Login")).to_be_visible()


def test_products_can_be_sorted_by_price_low_to_high(
    swag_labs: SwagLabsPage,
) -> None:
    swag_labs.open()
    swag_labs.log_in(STANDARD_USER, STANDARD_PASSWORD)
    swag_labs.sort_products("lohi")

    prices = swag_labs.product_prices()
    assert len(prices) > 1
    assert prices == sorted(prices)
