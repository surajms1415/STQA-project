"""
Black Box Testing Suite for AuraMart E-Commerce Application.
Validates boundary values, invalid inputs, edge-cases, error-handling, and security assertions.
"""

import json
import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.blackbox
class TestBlackBoxScenarios:
    """Black box functional boundary and validation tests."""

    @pytest.fixture(autouse=True)
    def setup_catalog(self):
        self.products = [
            {"id": "p1", "name": "Item 1", "price": 50.00, "stock": 5},
            {"id": "p_out", "name": "Zero Stock Item", "price": 20.00, "stock": 0},
        ]

    def test_bb_chk_01_empty_checkout_blocked(self, valid_customer):
        """BB-CHK-01: Empty checkout attempt is blocked."""
        empty_cart = []
        payment = {"method": "cod"}

        res = Core.process_order(empty_cart, self.products, valid_customer, payment)
        pass_cond = res["success"] is False and "empty" in res.get("error", "").lower()
        verify(
            "BB-CHK-01",
            "Reject checkout on empty cart",
            "success: false",
            f"success: {res['success']}, msg: '{res.get('error')}'",
            pass_cond,
        )

    def test_bb_cust_01_rejects_invalid_customer(self, invalid_customer):
        """BB-CUST-01: Rejects invalid customer details (short name, bad email, bad phone)."""
        res = Core.validate_checkout_payload(invalid_customer, {"method": "cod"})
        errors = res.get("errors", {})
        pass_cond = (
            res["isValid"] is False
            and "name" in errors
            and "email" in errors
            and "phone" in errors
        )
        verify(
            "BB-CUST-01",
            "Reject malformed customer info",
            "isValid: false with field errors",
            f"isValid: {res['isValid']}, errorCount: {len(errors)}",
            pass_cond,
        )

    def test_bb_qty_01_rejects_negative_quantity(self):
        """BB-QTY-01: Rejects negative quantity attempt."""
        res = Core.add_to_cart([], self.products, "p1", -3)
        pass_cond = res["success"] is False
        verify(
            "BB-QTY-01",
            "Reject adding negative quantity (-3)",
            "success: false",
            f"success: {res['success']}, error: '{res.get('error')}'",
            pass_cond,
        )

    def test_bb_qty_02_zero_quantity_removes_item(self):
        """BB-QTY-02: Zero quantity removes item from cart cleanly."""
        cart = [{"id": "p1", "quantity": 2}]
        res = Core.update_cart_quantity(cart, self.products, "p1", 0)
        pass_cond = (
            res["success"] is True
            and res.get("removed") is True
            and len(res["cart"]) == 0
        )
        verify(
            "BB-QTY-02",
            "Setting quantity to 0 removes item",
            "removed: true, cart: []",
            f"removed: {res.get('removed')}, count: {len(res['cart'])}",
            pass_cond,
        )

    def test_bb_stock_01_out_of_stock_addition_blocked(self):
        """BB-STOCK-01: Out-of-stock product addition is blocked."""
        res = Core.add_to_cart([], self.products, "p_out", 1)
        pass_cond = res["success"] is False and "out of stock" in res.get("error", "").lower()
        verify(
            "BB-STOCK-01",
            "Reject adding out-of-stock product",
            "success: false, out of stock",
            f"success: {res['success']}, error: '{res.get('error')}'",
            pass_cond,
        )

    def test_bb_inp_01_rejects_invalid_card_payment(self, invalid_card_payment):
        """BB-INP-01: Rejects invalid card payment details (expired, short number)."""
        customer = {
            "name": "Valid Name",
            "email": "valid@example.com",
            "phone": "9876543210",
            "address": "123 Valid St",
            "city": "City",
            "state": "ST",
            "zip": "12345",
        }
        res = Core.validate_checkout_payload(customer, invalid_card_payment)
        errors = res.get("errors", {})
        pass_cond = (
            res["isValid"] is False
            and "cardNum" in errors
            and "cardExpiry" in errors
            and "cardCvv" in errors
        )
        verify(
            "BB-INP-01",
            "Reject expired card and invalid card digits",
            "isValid: false with card errors",
            f"isValid: {res['isValid']}, errors: {list(errors.keys())}",
            pass_cond,
        )

    def test_bb_inp_02_accepts_valid_customer_and_card(self, valid_card_payment):
        """BB-INP-02: Accepts complete, valid customer and card payment input."""
        valid_customer = {
            "name": "Sarah Connor",
            "email": "sarah@resistance.org",
            "phone": "3105551212",
            "address": "420 South Vermont Avenue",
            "city": "Los Angeles",
            "state": "CA",
            "zip": "90020",
        }
        res = Core.validate_checkout_payload(valid_customer, valid_card_payment)
        errors = res.get("errors", {})
        pass_cond = res["isValid"] is True and len(errors) == 0
        verify(
            "BB-INP-02",
            "Accept fully valid checkout details",
            "isValid: true, errors: {}",
            f"isValid: {res['isValid']}, errors: {json.dumps(errors)}",
            pass_cond,
        )
