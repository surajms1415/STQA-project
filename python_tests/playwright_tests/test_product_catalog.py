"""
Playwright E2E Tests: Product Listing & Selection.
Verifies product card rendering, stock badges, category filtering, search, sorting, and empty state.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.playwright
class TestProductCatalog:
    """Verifies product catalog rendering, search, filters, and sorting behaviors."""

    def test_catalog_renders_all_products(self, app_page: Page):
        """Verify baseline product grid displays all 10 products."""
        cards = app_page.locator("#product-grid .product-card")
        expect(cards).to_have_count(10)

        # Check results counter
        results_count = app_page.locator("#results-count")
        expect(results_count).to_contain_text("Showing 10 of 10 products")

    def test_product_card_structure_and_details(self, app_page: Page):
        """Verify each product card contains title, price, category, and action button."""
        first_card = app_page.locator("#product-grid .product-card").first
        expect(first_card.locator(".product-title")).to_be_visible()
        expect(first_card.locator(".product-price")).to_be_visible()
        expect(first_card.locator(".badge-tag")).to_be_visible()
        expect(first_card.locator(".stock-tag")).to_be_visible()
        expect(first_card.locator(".add-cart-btn")).to_be_visible()

    def test_out_of_stock_product_state(self, app_page: Page):
        """Verify p10 (Leather Tech Sleeve) displays Out of Stock and disabled button."""
        out_of_stock_card = app_page.locator(".product-card[data-product-id='p10']")
        expect(out_of_stock_card).to_have_class("product-card out-of-stock")
        expect(out_of_stock_card.locator(".stock-tag")).to_contain_text("Out of Stock")

        add_btn = out_of_stock_card.locator(".add-cart-btn")
        expect(add_btn).to_be_disabled()

    def test_filter_by_category_tabs(self, app_page: Page):
        """Verify clicking category tabs filters products accurately."""
        # Click 'Audio' category
        app_page.click(".tab-btn[data-category='Audio']")
        audio_cards = app_page.locator("#product-grid .product-card")
        expect(audio_cards).to_have_count(2)

        for i in range(2):
            expect(audio_cards.nth(i).locator(".badge-tag")).to_have_text("Audio")

        # Click 'Electronics' category
        app_page.click(".tab-btn[data-category='Electronics']")
        elec_cards = app_page.locator("#product-grid .product-card")
        expect(elec_cards).to_have_count(3)

        # Return to 'All Products'
        app_page.click(".tab-btn[data-category='all']")
        expect(app_page.locator("#product-grid .product-card")).to_have_count(10)

    def test_search_input_filtering(self, app_page: Page):
        """Verify searching by text dynamically updates the product grid."""
        search_input = app_page.locator("#search-input")
        search_input.fill("Backpack")

        cards = app_page.locator("#product-grid .product-card")
        expect(cards).to_have_count(1)
        expect(cards.first.locator(".product-title")).to_contain_text("Backpack")

        # Clear search via clear button
        app_page.click("#clear-search-btn")
        expect(search_input).to_have_value("")
        expect(app_page.locator("#product-grid .product-card")).to_have_count(10)

    def test_search_nonexistent_product_shows_empty_state(self, app_page: Page):
        """Verify searching for nonexistent string shows empty state."""
        app_page.fill("#search-input", "xyz999nonexistentitem")

        empty_state = app_page.locator("#no-products")
        expect(empty_state).not_to_have_class("empty-state hidden")
        expect(empty_state).to_contain_text("No matching products found")
        expect(app_page.locator("#product-grid .product-card")).to_have_count(0)

        # Reset via empty reset button
        app_page.click("#empty-reset-btn")
        expect(app_page.locator("#product-grid .product-card")).to_have_count(10)

    def test_in_stock_only_checkbox_filter(self, app_page: Page):
        """Verify 'In Stock Only' checkbox excludes out-of-stock items."""
        app_page.check("#stock-filter")

        # Stock count should now be 9 (excluding p10 which has stock 0)
        cards = app_page.locator("#product-grid .product-card")
        expect(cards).to_have_count(9)
        expect(app_page.locator(".product-card[data-product-id='p10']")).to_have_count(0)

        # Uncheck returns 10
        app_page.uncheck("#stock-filter")
        expect(app_page.locator("#product-grid .product-card")).to_have_count(10)

    def test_sort_dropdown_price_low_to_high(self, app_page: Page):
        """Verify sorting by Price: Low to High arranges products ascendingly."""
        app_page.select_option("#sort-select", "price-asc")

        prices = app_page.locator("#product-grid .product-price").all_inner_texts()
        numeric_prices = [float(p.replace("$", "")) for p in prices]

        assert len(numeric_prices) == 10
        assert numeric_prices == sorted(numeric_prices), f"Prices not sorted ascendingly: {numeric_prices}"
