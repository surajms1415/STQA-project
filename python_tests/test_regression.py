"""
Regression Testing Suite for AuraMart E-Commerce Application.
Ensures that previously working features and fixed defects continue to behave correctly
across code updates, state mutations, and repeated workflows.
"""

import copy
import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.regression
class TestDefectFixRegression:
    """Verifies that none of the 6 identified bugs (BUG-001 through BUG-006) regress."""

    def test_reg_bug_001_floating_point_rounding(self):
        """REG-BUG-001: Floating-point line calculation precision remains 139.93 (19.99 * 7)."""
        line_total = Core.calculate_line_total(19.99, 7)
        assert line_total == 139.93, f"Regression detected in BUG-001: expected 139.93, got {line_total}"

    def test_reg_bug_002_fractional_quantity_rejection(self):
        """REG-BUG-002: Fractional/decimal quantities remain strictly rejected."""
        assert Core.ValidationRules.validate_quantity(2.5, 10) is False
        res = Core.add_to_cart([], [{"id": "p1", "stock": 10}], "p1", 2.5)
        assert res["success"] is False

    def test_reg_bug_003_cumulative_stock_check(self):
        """REG-BUG-003: Adding items across multiple actions respects cumulative warehouse stock."""
        products = [{"id": "p1", "stock": 5, "price": 20.0}]
        cart = [{"id": "p1", "quantity": 3}]  # already has 3
        # Attempting to add 4 more (total 7 > stock 5) must be rejected
        res = Core.add_to_cart(cart, products, "p1", 4)
        assert res["success"] is False
        assert "Only 2 more available" in res.get("error", "")

    def test_reg_bug_004_empty_checkout_blocked(self, valid_customer, cod_payment):
        """REG-BUG-004: Empty cart checkout cannot create ghost orders."""
        res = Core.process_order([], Core.INITIAL_PRODUCTS, valid_customer, cod_payment)
        assert res["success"] is False
        assert "empty cart" in res.get("error", "").lower()

    def test_reg_bug_005_whitespace_and_alphanumeric_inputs_rejected(self):
        """REG-BUG-005: Whitespace-only name and alphanumeric phone strings remain rejected."""
        assert Core.ValidationRules.validate_name("   ") is False
        assert Core.ValidationRules.validate_phone("12345ABCDE") is False

    def test_reg_bug_006_past_expiry_and_short_cvv_rejected(self):
        """REG-BUG-006: Past expiry dates and single digit CVVs remain rejected."""
        assert Core.ValidationRules.validate_card_expiry("01/20") is False
        assert Core.ValidationRules.validate_card_cvv("9") is False


@pytest.mark.regression
class TestStateStabilityRegression:
    """Verifies idempotency, repeated execution stability, and non-corruption."""

    def test_reg_calculation_idempotency(self, sample_products):
        """REG-STAB-01: Repeated calculations yield deterministic, invariant results."""
        cart = [{"id": "p1", "quantity": 2}, {"id": "p2", "quantity": 1}]
        first_run = Core.calculate_cart_totals(cart, sample_products)

        for _ in range(50):
            repeated = Core.calculate_cart_totals(cart, sample_products)
            assert repeated == first_run, "Cart totals drifted across repeated calculations"

    def test_reg_cart_add_remove_cycle_restores_state(self, initial_products):
        """REG-STAB-02: Adding and immediately removing an item restores pristine empty cart."""
        cart = []
        # Add item
        res_add = Core.add_to_cart(cart, initial_products, "p1", 2)
        cart = res_add["cart"]
        assert len(cart) == 1

        # Remove item
        res_remove = Core.remove_from_cart(cart, "p1")
        cart = res_remove["cart"]
        assert len(cart) == 0

    def test_reg_stock_depletion_does_not_go_below_zero(self, valid_customer, cod_payment):
        """REG-STAB-03: Multiple orders cannot drive warehouse stock below zero."""
        products = [{"id": "p1", "name": "Limited Item", "price": 10.0, "stock": 2}]
        cart = [{"id": "p1", "quantity": 2}]

        # First order uses all 2 units
        res1 = Core.process_order(cart, products, valid_customer, cod_payment)
        assert res1["success"] is True
        p1_stock = next(p for p in res1["updatedProducts"] if p["id"] == "p1")["stock"]
        assert p1_stock == 0

        # Second order with the updated catalog must fail with insufficient stock
        res2 = Core.process_order(cart, res1["updatedProducts"], valid_customer, cod_payment)
        assert res2["success"] is False
        assert "Insufficient stock" in res2.get("error", "")
