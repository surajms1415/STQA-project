"""
Playwright E2E Tests: Homepage Loading & Navigation.
Verifies page metadata, navigation links, brand elements, controls bar, and inter-dashboard routing.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.playwright
class TestHomepageAndNavigation:
    """Verifies homepage structure, brand presence, and navigation links."""

    def test_homepage_title_and_meta(self, app_page: Page):
        """Verify page title and core document metadata."""
        expect(app_page).to_have_title("AuraMart | E-Commerce Store")

    def test_brand_logo_and_tagline(self, app_page: Page):
        """Verify brand header elements and tagline are visible."""
        brand = app_page.locator("#brand-logo")
        expect(brand).to_be_visible()
        expect(brand).to_contain_text("AuraMart")
        expect(brand).to_contain_text("Pure Vanilla E-Commerce")

    def test_navbar_action_buttons_present(self, app_page: Page):
        """Verify all top navigation bar buttons and links are present."""
        expect(app_page.locator("#test-dash-btn")).to_be_visible()
        expect(app_page.locator("#defect-dash-btn")).to_be_visible()
        expect(app_page.locator("#qa-report-btn")).to_be_visible()
        expect(app_page.locator("#orders-btn")).to_be_visible()
        expect(app_page.locator("#cart-btn")).to_be_visible()

    def test_controls_bar_elements(self, app_page: Page):
        """Verify category tabs, in-stock checkbox, and sort dropdown exist."""
        expect(app_page.locator("#category-tabs")).to_be_visible()
        expect(app_page.locator("#stock-filter")).to_be_attached()
        expect(app_page.locator("#sort-select")).to_be_visible()
        expect(app_page.locator("#results-count")).to_be_visible()

    def test_cart_button_initial_zero_badge(self, app_page: Page):
        """Verify initial cart badge reflects 0 items."""
        cart_badge = app_page.locator("#cart-badge")
        expect(cart_badge).to_contain_text("0")

    def test_navigation_to_test_dashboard(self, app_page: Page):
        """Verify clicking Test Suite link navigates to test-dashboard.html."""
        app_page.click("#test-dash-btn")
        app_page.wait_for_url("**/test-dashboard.html")
        expect(app_page).to_have_title("AuraMart | QA Testing Dashboard")
        expect(app_page.locator("h1")).to_contain_text("AuraMart QA Test Suite")

    def test_navigation_to_defect_dashboard(self, app_page: Page):
        """Verify clicking Defects & QA link navigates to defect-dashboard.html."""
        app_page.click("#defect-dash-btn")
        app_page.wait_for_url("**/defect-dashboard.html")
        expect(app_page).to_have_title("AuraMart | Defect Management & QA Module")
        expect(app_page.locator("h1")).to_contain_text("Defect Management")

    def test_navigation_to_qa_report(self, app_page: Page):
        """Verify clicking QA Report link navigates to qa-report.html."""
        app_page.click("#qa-report-btn")
        app_page.wait_for_url("**/qa-report.html")
        expect(app_page).to_have_title("AuraMart | Final QA & Deployment Readiness Report")
        expect(app_page.locator("h1").first).to_contain_text("AuraMart STQA")



    def test_open_orders_history_modal(self, app_page: Page):
        """Verify clicking Orders button opens the order history modal."""
        modal = app_page.locator("#orders-history-modal")
        expect(modal).to_have_class("modal-overlay hidden")

        app_page.click("#orders-btn")
        expect(modal).not_to_have_class("modal-overlay hidden")
        expect(app_page.locator("#history-title")).to_be_visible()

        # Close modal
        app_page.click("#close-orders-btn")
        expect(modal).to_have_class("modal-overlay hidden")
