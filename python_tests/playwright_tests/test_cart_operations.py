"""
Playwright E2E Tests: Cart Operations & Price Calculations.
Verifies adding/removing items, slide-over drawer transitions, quantity increments/decrements,
subtotal, 5% sales tax, tiered shipping rules ($5 vs Free), and cart clearing.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.playwright
class TestCartOperationsAndCalculations:
    """Verifies shopping cart drawer, line item management, and financial calculations."""

    def test_add_product_to_cart_updates_badge(self, app_page: Page):
        """Verify clicking Add to Cart increments badge and updates button state."""
        # Add p1 (Aura Wireless Headphones, $99.99)
        p1_card = app_page.locator(".product-card[data-product-id='p1']")
        add_btn = p1_card.locator(".add-cart-btn")
        add_btn.click()

        # Check badge updates to 1
        cart_badge = app_page.locator("#cart-badge")
        expect(cart_badge).to_contain_text("1")
        expect(add_btn).to_contain_text("Added (1)")

    def test_open_and_close_cart_drawer(self, app_page: Page):
        """Verify opening and closing the slide-out cart drawer."""
        drawer = app_page.locator("#cart-drawer")
        expect(drawer).not_to_have_class("cart-drawer open")

        # Open cart
        app_page.click("#cart-btn")
        expect(drawer).to_have_class("cart-drawer open")
        expect(app_page.locator("#cart-title")).to_contain_text("Your Cart")

        # Close cart
        app_page.click("#close-cart-btn")
        expect(drawer).not_to_have_class("cart-drawer open")

    def test_cart_item_rendering_and_details(self, app_page: Page):
        """Verify added item is listed in the drawer with price and quantity."""
        # Add p4 (Ergonomic Wireless Mouse, $49.99)
        app_page.click(".product-card[data-product-id='p4'] .add-cart-btn")

        # Open cart
        app_page.click("#cart-btn")

        cart_item = app_page.locator("#cart-items-container .cart-item[data-cart-id='p4']")
        expect(cart_item).to_be_visible()
        expect(cart_item.locator(".cart-item-name")).to_contain_text("Ergonomic Wireless Mouse")
        expect(cart_item.locator(".cart-item-unit-price")).to_contain_text("$49.99")
        expect(cart_item.locator(".qty-display")).to_contain_text("1")
        expect(cart_item.locator(".cart-item-total")).to_contain_text("$49.99")

    def test_cart_quantity_increment_and_price_recalculation(self, app_page: Page):
        """Verify increasing quantity updates line total, subtotal, tax, and shipping."""
        # Add p4 ($49.99, subtotal under $50 -> shipping is $5.00)
        app_page.click(".product-card[data-product-id='p4'] .add-cart-btn")
        app_page.click("#cart-btn")

        # Verify initial breakdown for 1 item ($49.99)
        # Subtotal: $49.99, Tax: $2.50, Shipping: $5.00, Total: $57.49
        expect(app_page.locator("#cart-subtotal")).to_contain_text("$49.99")
        expect(app_page.locator("#cart-tax")).to_contain_text("$2.50")
        expect(app_page.locator("#cart-shipping")).to_contain_text("$5.00")
        expect(app_page.locator("#cart-total")).to_contain_text("$57.49")

        # Click '+' to increment quantity to 2 (Subtotal: 49.99 * 2 = 99.98 >= $50 -> Free shipping!)
        app_page.click(".cart-item[data-cart-id='p4'] .qty-btn[data-action='inc-qty']")

        # Verify updated values
        # Subtotal: $99.98, Tax: $5.00, Shipping: Free, Total: $104.98
        expect(app_page.locator(".cart-item[data-cart-id='p4'] .qty-display")).to_contain_text("2")
        expect(app_page.locator("#cart-subtotal")).to_contain_text("$99.98")
        expect(app_page.locator("#cart-tax")).to_contain_text("$5.00")
        expect(app_page.locator("#cart-shipping")).to_contain_text("Free")
        expect(app_page.locator("#cart-total")).to_contain_text("$104.98")

    def test_cart_quantity_decrement(self, app_page: Page):
        """Verify decreasing quantity reduces count and line total."""
        app_page.click(".product-card[data-product-id='p4'] .add-cart-btn")
        app_page.click("#cart-btn")

        # Increase to 2
        app_page.click(".cart-item[data-cart-id='p4'] .qty-btn[data-action='inc-qty']")
        expect(app_page.locator(".qty-display")).to_contain_text("2")

        # Decrease back to 1
        app_page.click(".cart-item[data-cart-id='p4'] .qty-btn[data-action='dec-qty']")
        expect(app_page.locator(".qty-display")).to_contain_text("1")
        expect(app_page.locator("#cart-subtotal")).to_contain_text("$49.99")

    def test_remove_product_from_cart(self, app_page: Page):
        """Verify removing item displays empty cart view."""
        app_page.click(".product-card[data-product-id='p1'] .add-cart-btn")
        app_page.click("#cart-btn")

        expect(app_page.locator(".cart-item")).to_have_count(1)

        # Click remove button
        app_page.click(".cart-item[data-cart-id='p1'] .remove-item-btn")

        # Item removed, empty view displayed
        expect(app_page.locator("#empty-cart-view")).not_to_have_class("empty-cart hidden")
        expect(app_page.locator("#empty-cart-view")).to_contain_text("Your cart is empty")
        expect(app_page.locator("#cart-badge")).to_contain_text("0")

    def test_clear_cart_action(self, app_page: Page):
        """Verify clicking Clear Cart empties all items after confirmation."""
        # Handle browser confirmation dialog automatically
        app_page.on("dialog", lambda dialog: dialog.accept())

        # Add two different items
        app_page.click(".product-card[data-product-id='p1'] .add-cart-btn")
        app_page.click(".product-card[data-product-id='p2'] .add-cart-btn")

        app_page.click("#cart-btn")
        expect(app_page.locator(".cart-item")).to_have_count(2)

        # Clear cart
        app_page.click("#clear-cart-btn")

        # Verify cart is empty
        expect(app_page.locator("#empty-cart-view")).to_be_visible()
        expect(app_page.locator("#cart-badge")).to_contain_text("0")
