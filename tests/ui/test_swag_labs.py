import pytest
from playwright.sync_api import expect

from pages.swag_labs_page import SwagLabsPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]

STANDARD_USER = "standard_user"
STANDARD_PASSWORD = "secret_sauce"


def test_adding_product_updates_cart_badge_and_cart_contents(
    swag_labs: SwagLabsPage,
) -> None:
    product_name = "Sauce Labs Backpack"
    swag_labs.open()
    swag_labs.log_in(STANDARD_USER, STANDARD_PASSWORD)
    swag_labs.add_product_to_cart(product_name)

    expect(swag_labs.page.get_by_test_id("shopping-cart-badge")).to_have_text("1")

    swag_labs.open_cart()

    cart_items = swag_labs.page.get_by_test_id("inventory-item")
    expect(cart_items).to_have_count(1)
    expect(cart_items.get_by_test_id("inventory-item-name")).to_have_text(product_name)


def test_removing_one_of_multiple_products_updates_cart_state(
    swag_labs: SwagLabsPage,
) -> None:
    product_names = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]
    swag_labs.open()
    swag_labs.log_in(STANDARD_USER, STANDARD_PASSWORD)
    for product_name in product_names:
        swag_labs.add_product_to_cart(product_name)

    expect(swag_labs.page.get_by_test_id("shopping-cart-badge")).to_have_text("2")

    swag_labs.open_cart()

    cart_items = swag_labs.page.get_by_test_id("inventory-item")
    expect(cart_items).to_have_count(2)
    expect(cart_items.get_by_test_id("inventory-item-name")).to_have_text(product_names)

    swag_labs.remove_product_from_cart(product_names[0])

    expect(swag_labs.page.get_by_test_id("shopping-cart-badge")).to_have_text("1")
    expect(cart_items).to_have_count(1)
    expect(cart_items.get_by_test_id("inventory-item-name")).to_have_text(
        product_names[1]
    )
    expect(swag_labs.page.get_by_text(product_names[0], exact=True)).to_have_count(0)


@pytest.mark.parametrize(
    ("first_name", "last_name", "postal_code", "expected_message"),
    [
        pytest.param("", "", "", "First Name is required", id="missing-first-name"),
        pytest.param(
            "Sam",
            "",
            "10001",
            "Last Name is required",
            id="missing-last-name",
        ),
        pytest.param(
            "Sam",
            "Tester",
            "",
            "Postal Code is required",
            id="missing-postal-code",
        ),
    ],
)
def test_checkout_requires_customer_information(
    swag_labs: SwagLabsPage,
    first_name: str,
    last_name: str,
    postal_code: str,
    expected_message: str,
) -> None:
    swag_labs.open()
    swag_labs.log_in(STANDARD_USER, STANDARD_PASSWORD)
    swag_labs.add_product_to_cart("Sauce Labs Backpack")
    swag_labs.open_cart()
    swag_labs.start_checkout()

    swag_labs.submit_checkout_information(first_name, last_name, postal_code)

    expect(swag_labs.page.get_by_test_id("error")).to_contain_text(expected_message)
    expect(swag_labs.page.get_by_role("button", name="Continue")).to_be_visible()


def test_user_can_complete_checkout_and_see_order_confirmation(
    swag_labs: SwagLabsPage,
) -> None:
    product_name = "Sauce Labs Backpack"
    swag_labs.open()
    swag_labs.log_in(STANDARD_USER, STANDARD_PASSWORD)
    swag_labs.add_product_to_cart(product_name)
    swag_labs.open_cart()
    swag_labs.start_checkout()
    swag_labs.submit_checkout_information("Sam", "Tester", "10001")

    expect(swag_labs.page.get_by_text("Checkout: Overview", exact=True)).to_be_visible()
    expect(swag_labs.page.get_by_text(product_name, exact=True)).to_be_visible()

    swag_labs.finish_checkout()

    expect(swag_labs.page.get_by_test_id("complete-header")).to_have_text(
        "Thank you for your order!"
    )
    expect(swag_labs.page.get_by_text("Your order has been dispatched")).to_be_visible()
    expect(swag_labs.page.get_by_test_id("shopping-cart-badge")).to_have_count(0)


def test_products_can_be_sorted_by_price_low_to_high(
    swag_labs: SwagLabsPage,
) -> None:
    swag_labs.open()
    swag_labs.log_in(STANDARD_USER, STANDARD_PASSWORD)
    swag_labs.sort_products("lohi")

    prices = swag_labs.product_prices()
    assert len(prices) > 1
    assert prices == sorted(prices)
