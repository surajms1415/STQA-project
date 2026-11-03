"""
Unit Testing Suite for AuraMart E-Commerce Application.
Tests price calculation, quantity validation, cart totals, and stock constraints.
"""

import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.unit
class TestPriceCalculation:
    """Unit tests for price formatting and mathematical line calculations."""

    def test_ut_price_01_format_price(self):
        """UT-PRICE-01: Formats decimal price into standard currency string."""
        inp = 99.99
        actual = Core.format_price(inp)
        expected = "$99.99"
        verify("UT-PRICE-01", "Format price to standard currency string", expected, actual, actual == expected)

    def test_ut_price_02_line_total(self):
        """UT-PRICE-02: Calculates accurate line total for item (price * quantity)."""
        price = 49.99
        qty = 3
        actual = Core.calculate_line_total(price, qty)
        expected = 149.97
        verify("UT-PRICE-02", "Calculate line total (49.99 * 3)", expected, actual, actual == expected)

    def test_ut_price_03_floating_point_rounding(self):
        """UT-PRICE-03: Handles floating-point rounding cleanly without artifacts."""
        price = 19.99
        qty = 7
        actual = Core.calculate_line_total(price, qty)
        expected = 139.93
        verify("UT-PRICE-03", "Float arithmetic precision (19.99 * 7)", expected, actual, actual == expected)


@pytest.mark.unit
class TestQuantityValidation:
    """Unit tests for quantity boundary and type validation."""

    def test_ut_qty_01_valid_positive_integer(self):
        """UT-QTY-01: Accepts valid positive integer within stock."""
        is_valid = Core.ValidationRules.validate_quantity(3, 5)
        verify("UT-QTY-01", "Quantity 3 with stock 5 is valid", True, is_valid, is_valid is True)

    def test_ut_qty_02_rejects_non_integer_or_decimal(self):
        """UT-QTY-02: Rejects non-integer or decimal quantity."""
        is_valid = Core.ValidationRules.validate_quantity(2.5, 5)
        verify("UT-QTY-02", "Quantity 2.5 rejected", False, is_valid, is_valid is False)

    def test_ut_qty_03_rejects_zero_quantity(self):
        """UT-QTY-03: Rejects zero quantity."""
        is_valid = Core.ValidationRules.validate_quantity(0, 5)
        verify("UT-QTY-03", "Quantity 0 rejected", False, is_valid, is_valid is False)

    def test_ut_qty_04_rejects_negative_quantity(self):
        """UT-QTY-04: Rejects negative quantity."""
        is_valid = Core.ValidationRules.validate_quantity(-2, 5)
        verify("UT-QTY-04", "Quantity -2 rejected", False, is_valid, is_valid is False)


@pytest.mark.unit
class TestCartCalculations:
    """Unit tests for cart subtotal, tax calculation, and tiered shipping."""

    def test_ut_cart_01_subtotal_calculation(self, sample_products):
        """UT-CART-01: Computes accurate subtotal for varied items."""
        cart = [{"id": "p1", "quantity": 2}, {"id": "p2", "quantity": 3}]
        totals = Core.calculate_cart_totals(cart, sample_products)
        # (100.00 * 2) + (20.00 * 3) = 260.00
        verify("UT-CART-01", "Subtotal calculation (200 + 60)", 260.00, totals["subtotal"], totals["subtotal"] == 260.00)

    def test_ut_cart_02_sales_tax(self, sample_products):
        """UT-CART-02: Computes standard 5% tax accurately."""
        cart = [{"id": "p1", "quantity": 1}]  # subtotal = 100.00
        totals = Core.calculate_cart_totals(cart, sample_products)
        # 5% of 100 = 5.00
        verify("UT-CART-02", "5% Tax on $100", 5.00, totals["tax"], totals["tax"] == 5.00)

    def test_ut_cart_03_standard_shipping_under_50(self, sample_products):
        """UT-CART-03: Applies $5.00 shipping for orders under $50.00."""
        cart = [{"id": "p2", "quantity": 2}]  # subtotal = 40.00
        totals = Core.calculate_cart_totals(cart, sample_products)
        verify("UT-CART-03", "Shipping for $40 subtotal is $5.00", 5.00, totals["shipping"], totals["shipping"] == 5.00)

    def test_ut_cart_04_free_shipping_at_or_above_50(self, sample_products):
        """UT-CART-04: Unlocks Free Shipping ($0.00) for orders >= $50.00."""
        cart = [{"id": "p1", "quantity": 1}]  # subtotal = 100.00
        totals = Core.calculate_cart_totals(cart, sample_products)
        verify("UT-CART-04", "Free shipping for $100 subtotal is $0.00", 0.00, totals["shipping"], totals["shipping"] == 0.00)

    def test_ut_cart_05_grand_total(self, sample_products):
        """UT-CART-05: Calculates correct total (subtotal + tax + shipping)."""
        cart = [{"id": "p2", "quantity": 1}]  # subtotal = 20, tax = 1.00, shipping = 5.00 -> total = 26.00
        totals = Core.calculate_cart_totals(cart, sample_products)
        verify("UT-CART-05", "Total computation: 20 + 1 + 5", 26.00, totals["total"], totals["total"] == 26.00)


@pytest.mark.unit
class TestStockValidation:
    """Unit tests for stock availability detection and remaining stock counting."""

    def test_ut_stock_01_detects_in_stock(self):
        """UT-STOCK-01: Detects product in-stock availability correctly."""
        prod = {"id": "p1", "name": "In Stock Item", "stock": 5}
        in_stock = Core.is_product_in_stock(prod)
        verify("UT-STOCK-01", "Product stock 5 is in-stock", True, in_stock, in_stock is True)

    def test_ut_stock_02_detects_out_of_stock(self):
        """UT-STOCK-02: Flags out-of-stock product when stock is 0."""
        prod = {"id": "p2", "name": "Sold Out Item", "stock": 0}
        out_of_stock = not Core.is_product_in_stock(prod)
        verify("UT-STOCK-02", "Product stock 0 is out-of-stock", True, out_of_stock, out_of_stock is True)

    def test_ut_stock_03_available_remaining_stock(self):
        """UT-STOCK-03: Computes available remaining stock accounting for cart items."""
        prod = {"id": "p1", "name": "Item Alpha", "stock": 5}
        cart = [{"id": "p1", "quantity": 2}]
        available = Core.get_available_stock(prod, cart)
        verify("UT-STOCK-03", "Available stock (5 - 2 in cart)", 3, available, available == 3)
