import pytest
from playwright.sync_api import expect

from pages.swag_labs_page import SwagLabsPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


def test_inventory_displays_products_with_names_and_valid_prices(
    logged_in_swag_labs: SwagLabsPage,
) -> None:
    swag_labs = logged_in_swag_labs

    inventory_items = swag_labs.page.get_by_test_id("inventory-item")
    item_count = inventory_items.count()

    expect(swag_labs.page.get_by_test_id("inventory-list")).to_be_visible()
    assert item_count > 0
    expect(inventory_items.get_by_test_id("inventory-item-name")).to_have_count(
        item_count
    )
    expect(inventory_items.get_by_test_id("inventory-item-price")).to_have_count(
        item_count
    )
    assert all(name.strip() for name in swag_labs.product_names())
    assert all(price > 0 for price in swag_labs.product_prices())


@pytest.mark.parametrize(
    ("sort_option", "reverse"),
    [
        pytest.param("lohi", False, id="low-to-high"),
        pytest.param("hilo", True, id="high-to-low"),
    ],
)
def test_products_are_sorted_by_selected_price_order(
    logged_in_swag_labs: SwagLabsPage,
    sort_option: str,
    reverse: bool,
) -> None:
    swag_labs = logged_in_swag_labs
    swag_labs.sort_products(sort_option)

    expect(swag_labs.page.get_by_test_id("product-sort-container")).to_have_value(
        sort_option
    )
    prices = swag_labs.product_prices()
    assert len(prices) > 1
    assert prices == sorted(prices, reverse=reverse)


@pytest.mark.parametrize(
    ("sort_option", "reverse"),
    [
        pytest.param("az", False, id="a-to-z"),
        pytest.param("za", True, id="z-to-a"),
    ],
)
def test_products_are_sorted_by_selected_name_order(
    logged_in_swag_labs: SwagLabsPage,
    sort_option: str,
    reverse: bool,
) -> None:
    swag_labs = logged_in_swag_labs
    swag_labs.sort_products(sort_option)

    expect(swag_labs.page.get_by_test_id("product-sort-container")).to_have_value(
        sort_option
    )
    names = swag_labs.product_names()
    assert len(names) > 1
    assert names == sorted(names, reverse=reverse)
