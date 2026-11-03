"""
Playwright E2E Tests: Checkout Flow, Form Validation & Error Handling.
Verifies modal transitions, inline field validation, payment method toggles,
invalid input rejections, and successful order confirmation with receipt.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.playwright
class TestCheckoutAndValidation:
    """Verifies checkout form validation, error messaging, and order generation."""

    def test_open_checkout_modal_from_cart(self, app_page: Page):
        """Verify clicking Proceed to Checkout opens checkout modal with order summary."""
        # Add item
        app_page.click(".product-card[data-product-id='p1'] .add-cart-btn")
        app_page.click("#cart-btn")

        # Proceed to checkout
        app_page.click("#proceed-checkout-btn")

        checkout_modal = app_page.locator("#checkout-modal")
        expect(checkout_modal).not_to_have_class("modal-overlay hidden")
        expect(app_page.locator("#checkout-title")).to_contain_text("Checkout & Order")

        # Check order summary inside checkout
        expect(app_page.locator("#checkout-items-list")).to_be_visible()
        expect(app_page.locator("#checkout-total")).to_contain_text("$104.99")

    def test_empty_form_submission_triggers_validation_errors(self, app_page: Page):
        """Verify submitting empty checkout form highlights all required fields."""
        app_page.click(".product-card[data-product-id='p1'] .add-cart-btn")
        app_page.click("#cart-btn")
        app_page.click("#proceed-checkout-btn")

        # Submit empty form
        app_page.click("#place-order-btn")

        # Checkout modal must stay open
        expect(app_page.locator("#checkout-modal")).not_to_have_class("modal-overlay hidden")

        # All required field error messages must be populated
        expect(app_page.locator("#cust-name-error")).not_to_be_empty()
        expect(app_page.locator("#cust-email-error")).not_to_be_empty()
        expect(app_page.locator("#cust-phone-error")).not_to_be_empty()
        expect(app_page.locator("#cust-address-error")).not_to_be_empty()
        expect(app_page.locator("#cust-city-error")).not_to_be_empty()
        expect(app_page.locator("#cust-state-error")).not_to_be_empty()
        expect(app_page.locator("#cust-zip-error")).not_to_be_empty()

    def test_invalid_email_and_phone_handling(self, app_page: Page):
        """Verify entering malformed email and short phone displays specific errors."""
        app_page.click(".product-card[data-product-id='p1'] .add-cart-btn")
        app_page.click("#cart-btn")
        app_page.click("#proceed-checkout-btn")

        app_page.fill("#cust-name", "John Doe")
        app_page.fill("#cust-email", "not-a-valid-email")
        app_page.fill("#cust-phone", "123")
        app_page.fill("#cust-address", "123 Main St")
        app_page.fill("#cust-city", "Springfield")
        app_page.fill("#cust-state", "IL")
        app_page.fill("#cust-zip", "62704")

        app_page.click("#place-order-btn")

        expect(app_page.locator("#cust-email-error")).to_contain_text("valid email")
        expect(app_page.locator("#cust-phone-error")).to_contain_text("at least 10 digits")

    def test_payment_method_toggle_fields(self, app_page: Page):
        """Verify switching payment methods dynamically reveals and hides field groups."""
        app_page.click(".product-card[data-product-id='p1'] .add-cart-btn")
        app_page.click("#cart-btn")
        app_page.click("#proceed-checkout-btn")

        card_group = app_page.locator("#card-fields-group")
        upi_group = app_page.locator("#upi-fields-group")

        # Initial default is Card
        expect(card_group).to_be_visible()
        expect(upi_group).to_have_class("card-details-box hidden")

        # Select COD
        app_page.click("input[name='paymentMethod'][value='cod']")
        expect(card_group).to_have_class("card-details-box hidden")
        expect(upi_group).to_have_class("card-details-box hidden")

        # Select UPI
        app_page.click("input[name='paymentMethod'][value='upi']")
        expect(card_group).to_have_class("card-details-box hidden")
        expect(upi_group).to_be_visible()

    def test_successful_order_placement_cod(self, app_page: Page):
        """Verify complete successful checkout with COD generates confirmed order receipt."""
        # Add item
        app_page.click(".product-card[data-product-id='p1'] .add-cart-btn")
        app_page.click("#cart-btn")
        app_page.click("#proceed-checkout-btn")

        # Fill valid details
        app_page.fill("#cust-name", "Jane Doe")
        app_page.fill("#cust-email", "jane.doe@example.com")
        app_page.fill("#cust-phone", "9876543210")
        app_page.fill("#cust-address", "742 Evergreen Terrace")
        app_page.fill("#cust-city", "Springfield")
        app_page.fill("#cust-state", "IL")
        app_page.fill("#cust-zip", "62704")

        # Select Cash on Delivery
        app_page.click("input[name='paymentMethod'][value='cod']")

        # Place Order
        app_page.click("#place-order-btn")

        # Success modal opens
        success_modal = app_page.locator("#order-success-modal")
        expect(success_modal).not_to_have_class("modal-overlay hidden")
        expect(app_page.locator("#success-title")).to_contain_text("Order Confirmed!")

        # Verify receipt details
        expect(app_page.locator("#receipt-order-id")).to_contain_text("ORD-")
        expect(app_page.locator("#receipt-name")).to_contain_text("Jane Doe")
        expect(app_page.locator("#receipt-email")).to_contain_text("jane.doe@example.com")
        expect(app_page.locator("#receipt-payment")).to_contain_text("Cash on Delivery")

        # Finish shopping closes modal and cart is emptied
        app_page.click("#finish-shopping-btn")
        expect(success_modal).to_have_class("modal-overlay hidden")
        expect(app_page.locator("#cart-badge")).to_contain_text("0")
