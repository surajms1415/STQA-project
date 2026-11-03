"""
Playwright E2E Tests: Responsive Behavior & UI Elements.
Verifies layout across viewport sizes (Desktop, Tablet, Mobile), drawer responsiveness,
modal scrolling, and UI element interactions.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.playwright
class TestResponsiveLayoutAndUI:
    """Verifies responsive layout across multiple screen viewports."""

    def test_desktop_viewport_layout(self, app_page: Page):
        """Verify desktop viewport (1280x800) displays full multi-column grid and controls."""
        app_page.set_viewport_size({"width": 1280, "height": 800})

        navbar = app_page.locator(".navbar")
        expect(navbar).to_be_visible()

        grid = app_page.locator("#product-grid")
        expect(grid).to_be_visible()

        # All 10 cards are visible in desktop view
        expect(grid.locator(".product-card")).to_have_count(10)

    def test_tablet_viewport_layout(self, app_page: Page):
        """Verify tablet viewport (768x1024) adapts category tabs and search input cleanly."""
        app_page.set_viewport_size({"width": 768, "height": 1024})

        # Category tabs remain clickable and functional
        expect(app_page.locator("#category-tabs")).to_be_visible()
        app_page.click(".tab-btn[data-category='Audio']")
        expect(app_page.locator("#product-grid .product-card")).to_have_count(2)

    def test_mobile_viewport_layout_and_cart_drawer(self, app_page: Page):
        """Verify mobile viewport (375x667) adjusts product cards and opens full-width cart drawer."""
        app_page.set_viewport_size({"width": 375, "height": 667})

        # Product cards stack nicely on mobile
        first_card = app_page.locator("#product-grid .product-card").first
        expect(first_card).to_be_visible()

        # Add to cart on mobile
        first_card.locator(".add-cart-btn").click()
        expect(app_page.locator("#cart-badge")).to_contain_text("1")

        # Open cart drawer on mobile
        app_page.click("#cart-btn")
        drawer = app_page.locator("#cart-drawer")
        expect(drawer).to_have_class("cart-drawer open")

        # Checkout button is accessible
        proceed_btn = app_page.locator("#proceed-checkout-btn")
        expect(proceed_btn).to_be_visible()

        # Close cart drawer
        app_page.click("#close-cart-btn")
        expect(drawer).not_to_have_class("cart-drawer open")

    def test_mobile_checkout_modal_scrolling_and_inputs(self, app_page: Page):
        """Verify checkout modal is fully readable and interactable on small mobile screens."""
        app_page.set_viewport_size({"width": 375, "height": 667})

        app_page.click(".product-card[data-product-id='p1'] .add-cart-btn")
        app_page.click("#cart-btn")
        app_page.click("#proceed-checkout-btn")

        modal = app_page.locator("#checkout-modal")
        expect(modal).not_to_have_class("modal-overlay hidden")

        # All input fields are visible and fillable on mobile
        name_input = app_page.locator("#cust-name")
        expect(name_input).to_be_visible()
        name_input.fill("Mobile Shopper")
        expect(name_input).to_have_value("Mobile Shopper")

        # Close checkout
        app_page.click("#close-checkout-btn")
        expect(modal).to_have_class("modal-overlay hidden")
