from playwright.sync_api import Page


class SwagLabsPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    def open(self) -> None:
        self.page.goto(self.base_url)

    def log_in(self, username: str, password: str) -> None:
        self.page.get_by_placeholder("Username").fill(username)
        self.page.get_by_placeholder("Password").fill(password)
        self.page.get_by_role("button", name="Login").click()

    def log_out(self) -> None:
        self.page.get_by_role("button", name="Open Menu").click()
        logout_link = self.page.get_by_test_id("logout-sidebar-link")
        logout_link.wait_for(state="visible")
        logout_link.click()

    def add_product_to_cart(self, product_name: str) -> None:
        product = self.page.get_by_test_id("inventory-item").filter(
            has_text=product_name
        )
        product.get_by_role("button", name="Add to cart").click()

    def open_cart(self) -> None:
        self.page.get_by_test_id("shopping-cart-link").click()

    def remove_product_from_cart(self, product_name: str) -> None:
        product = self.page.get_by_test_id("inventory-item").filter(
            has_text=product_name
        )
        product.get_by_role("button", name="Remove").click()

    def start_checkout(self) -> None:
        self.page.get_by_role("button", name="Checkout").click()

    def submit_checkout_information(
        self, first_name: str, last_name: str, postal_code: str
    ) -> None:
        self.page.get_by_placeholder("First Name").fill(first_name)
        self.page.get_by_placeholder("Last Name").fill(last_name)
        self.page.get_by_placeholder("Zip/Postal Code").fill(postal_code)
        self.page.get_by_role("button", name="Continue").click()

    def finish_checkout(self) -> None:
        self.page.get_by_role("button", name="Finish").click()

    def sort_products(self, option: str) -> None:
        self.page.get_by_test_id("product-sort-container").select_option(option)

    def product_names(self) -> list[str]:
        return self.page.get_by_test_id("inventory-item-name").all_text_contents()

    def product_prices(self) -> list[float]:
        return [
            float(price.removeprefix("$"))
            for price in self.page.get_by_test_id(
                "inventory-item-price"
            ).all_text_contents()
        ]
