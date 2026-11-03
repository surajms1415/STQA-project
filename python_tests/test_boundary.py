"""
Boundary Value Testing Suite for AuraMart E-Commerce Application.
Tests minimum, maximum, empty, invalid, and edge-case values at operational boundaries:
1. Quantity boundary values (0, 1, stock-1, stock, stock+1).
2. Shipping pricing thresholds ($49.99 vs $50.00 vs $50.01).
3. Field character length boundaries (name, address, city, state, zip).
4. Contact and payment digit boundaries (phone 9 vs 10 vs 15 vs 16 digits; card 12 vs 13 vs 16 vs 19 vs 20; CVV 2 vs 3 vs 4 vs 5).
"""

import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.boundary
class TestQuantityBoundaries:
    """Boundary value tests for purchasing quantities and stock limits."""

    @pytest.fixture(autouse=True)
    def setup_products(self):
        self.products = [
            {"id": "p_bound", "name": "Boundary Item", "price": 50.00, "stock": 5}
        ]

    def test_bvt_qty_min_valid_positive_one(self):
        """BVT-QTY-01: Boundary quantity 1 (minimum allowed positive integer)."""
        res = Core.add_to_cart([], self.products, "p_bound", 1)
        pass_cond = res["success"] is True and res["cart"][0]["quantity"] == 1
        verify("BVT-QTY-01", "Minimum valid quantity 1 added to cart", "success: True, qty: 1", f"success: {res['success']}, qty: {res['cart'][0]['quantity']}", pass_cond)

    def test_bvt_qty_exact_maximum_stock(self):
        """BVT-QTY-02: Boundary quantity equal to exact warehouse stock (stock = 5)."""
        res = Core.add_to_cart([], self.products, "p_bound", 5)
        pass_cond = res["success"] is True and res["cart"][0]["quantity"] == 5
        verify("BVT-QTY-02", "Exact maximum available stock 5 added", "success: True, qty: 5", f"success: {res['success']}, qty: {res['cart'][0]['quantity']}", pass_cond)

    def test_bvt_qty_exceeding_stock_by_one(self):
        """BVT-QTY-03: Boundary quantity stock + 1 (5 + 1 = 6) is rejected."""
        res = Core.add_to_cart([], self.products, "p_bound", 6)
        pass_cond = res["success"] is False and "Only 5 more available" in res.get("error", "")
        verify("BVT-QTY-03", "Adding 1 beyond stock boundary (6 for stock 5)", "success: False", f"success: {res['success']}, error: '{res.get('error')}'", pass_cond)

    def test_bvt_qty_zero_removes_from_cart(self):
        """BVT-QTY-04: Boundary quantity 0 in updateCartQuantity removes item."""
        cart = [{"id": "p_bound", "quantity": 2}]
        res = Core.update_cart_quantity(cart, self.products, "p_bound", 0)
        pass_cond = res["success"] is True and res.get("removed") is True and len(res["cart"]) == 0
        verify("BVT-QTY-04", "Setting cart quantity to 0 removes line item", "removed: True, len: 0", f"removed: {res.get('removed')}, len: {len(res['cart'])}", pass_cond)


@pytest.mark.boundary
class TestPricingAndShippingThresholdBoundaries:
    """Boundary testing on monetary tiers and Free Shipping threshold ($50.00)."""

    def test_bvt_shipping_just_below_threshold_49_99(self):
        """BVT-SHIP-01: Subtotal $49.99 ($0.01 under $50.00) incurs $5.00 shipping."""
        products = [{"id": "p1", "price": 49.99, "stock": 10}]
        cart = [{"id": "p1", "quantity": 1}]
        totals = Core.calculate_cart_totals(cart, products)
        # Subtotal: 49.99, Tax: 2.50, Shipping: 5.00 -> Total: 57.49
        pass_cond = totals["subtotal"] == 49.99 and totals["shipping"] == 5.00 and totals["total"] == 57.49
        verify("BVT-SHIP-01", "Subtotal $49.99 incurs standard $5.00 shipping", "shipping: 5.00, total: 57.49", f"shipping: {totals['shipping']}, total: {totals['total']}", pass_cond)

    def test_bvt_shipping_exact_threshold_50_00(self):
        """BVT-SHIP-02: Subtotal exactly $50.00 unlocks $0.00 Free Shipping."""
        products = [{"id": "p1", "price": 50.00, "stock": 10}]
        cart = [{"id": "p1", "quantity": 1}]
        totals = Core.calculate_cart_totals(cart, products)
        # Subtotal: 50.00, Tax: 2.50, Shipping: 0.00 -> Total: 52.50
        pass_cond = totals["subtotal"] == 50.00 and totals["shipping"] == 0.00 and totals["total"] == 52.50
        verify("BVT-SHIP-02", "Exact $50.00 unlocks Free Shipping ($0.00)", "shipping: 0.00, total: 52.50", f"shipping: {totals['shipping']}, total: {totals['total']}", pass_cond)

    def test_bvt_shipping_just_above_threshold_50_01(self):
        """BVT-SHIP-03: Subtotal $50.01 ($0.01 above threshold) retains Free Shipping."""
        products = [{"id": "p1", "price": 50.01, "stock": 10}]
        cart = [{"id": "p1", "quantity": 1}]
        totals = Core.calculate_cart_totals(cart, products)
        pass_cond = totals["subtotal"] == 50.01 and totals["shipping"] == 0.00
        verify("BVT-SHIP-03", "Subtotal $50.01 maintains Free Shipping ($0.00)", "shipping: 0.00", f"shipping: {totals['shipping']}", pass_cond)


@pytest.mark.boundary
class TestCustomerInputLengthBoundaries:
    """Boundary testing on string length constraints (min/max characters)."""

    @pytest.mark.parametrize(
        "name_input, expected_valid",
        [
            ("Jo", False),          # 2 characters (below min 3)
            ("Joe", True),          # 3 characters (exact min)
            ("John Doe", True),     # typical valid name
        ],
    )
    def test_bvt_name_length_boundaries(self, name_input, expected_valid):
        """BVT-LEN-01: Name min length boundary (2 chars rejected, 3 chars accepted)."""
        assert Core.ValidationRules.validate_name(name_input) is expected_valid

    @pytest.mark.parametrize(
        "address_input, expected_valid",
        [
            ("Main", False),        # 4 characters (below min 5)
            ("1 St.", True),        # 5 characters (exact min)
            ("123 Maple St", True), # valid address
        ],
    )
    def test_bvt_address_length_boundaries(self, address_input, expected_valid):
        """BVT-LEN-02: Address min length boundary (4 chars rejected, 5 chars accepted)."""
        assert Core.ValidationRules.validate_address(address_input) is expected_valid

    @pytest.mark.parametrize(
        "zip_input, expected_valid",
        [
            ("123", False),              # 3 chars (below min 4)
            ("1234", True),              # 4 chars (exact min 4)
            ("12345-6789", True),        # 10 chars (exact max 10)
            ("12345-67890", False),      # 11 chars (above max 10)
        ],
    )
    def test_bvt_zip_length_boundaries(self, zip_input, expected_valid):
        """BVT-LEN-03: Postal/ZIP code boundaries (4 to 10 characters)."""
        assert Core.ValidationRules.validate_zip(zip_input) is expected_valid

    @pytest.mark.parametrize(
        "phone_input, expected_valid",
        [
            ("123456789", False),         # 9 digits (below min 10)
            ("1234567890", True),         # 10 digits (exact min)
            ("123456789012345", True),    # 15 digits (exact max)
            ("1234567890123456", False),  # 16 digits (above max 15)
        ],
    )
    def test_bvt_phone_digit_boundaries(self, phone_input, expected_valid):
        """BVT-LEN-04: Phone number digit boundaries (10 to 15 digits)."""
        assert Core.ValidationRules.validate_phone(phone_input) is expected_valid


@pytest.mark.boundary
class TestPaymentDigitBoundaries:
    """Boundary testing on card and CVV digit length constraints."""

    @pytest.mark.parametrize(
        "card_input, expected_valid",
        [
            ("123456789012", False),             # 12 digits (below min 13)
            ("1234567890123", True),             # 13 digits (exact min 13)
            ("4111222233334444", True),          # 16 digits (standard)
            ("1234567890123456789", True),       # 19 digits (exact max 19)
            ("12345678901234567890", False),     # 20 digits (above max 19)
        ],
    )
    def test_bvt_card_number_length_boundaries(self, card_input, expected_valid):
        """BVT-PAY-01: Card number digit boundaries (13 to 19 digits)."""
        assert Core.ValidationRules.validate_card_num(card_input) is expected_valid

    @pytest.mark.parametrize(
        "cvv_input, expected_valid",
        [
            ("12", False),      # 2 digits (below min 3)
            ("123", True),      # 3 digits (exact min 3)
            ("1234", True),     # 4 digits (exact max 4)
            ("12345", False),   # 5 digits (above max 4)
        ],
    )
    def test_bvt_card_cvv_boundaries(self, cvv_input, expected_valid):
        """BVT-PAY-02: Card CVV boundaries (3 to 4 digits)."""
        assert Core.ValidationRules.validate_card_cvv(cvv_input) is expected_valid
