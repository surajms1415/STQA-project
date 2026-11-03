"""
Negative Testing Suite for AuraMart E-Commerce Application.
Verifies application error handling, graceful rejection, and defensive mechanisms against:
1. Malformed quantities (negative, decimals, booleans, strings, None).
2. Non-existent product IDs and ghost entities.
3. Empty, None, or corrupted shopping carts during checkout.
4. Missing, empty, or whitespace-only customer profile fields.
5. Malformed payment data (past expiration, bad CVV, invalid UPI, unsupported gateway methods).
6. Security / injection string payloads (XSS, script injection).
"""

import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.negative
class TestNegativeCartOperations:
    """Negative testing on shopping cart mutations and invalid parameters."""

    @pytest.fixture(autouse=True)
    def setup_catalog(self):
        self.products = [
            {"id": "p1", "name": "Audio Item", "price": 49.99, "stock": 5}
        ]

    @pytest.mark.parametrize(
        "invalid_qty",
        [-1, -10, 0, 2.5, "1", "five", True, False, None, [1], {"qty": 1}],
    )
    def test_neg_add_to_cart_rejects_malformed_quantity(self, invalid_qty):
        """NEG-CART-01: Rejects non-integer, negative, or boolean quantities."""
        res = Core.add_to_cart([], self.products, "p1", invalid_qty)
        assert res["success"] is False
        assert "Invalid quantity" in res.get("error", "")

    def test_neg_add_nonexistent_product_id(self):
        """NEG-CART-02: Adding non-existent product ID fails with 'Product not found'."""
        res = Core.add_to_cart([], self.products, "p_ghost_999", 1)
        assert res["success"] is False
        assert "Product not found" in res.get("error", "")

    def test_neg_update_quantity_item_not_in_cart(self):
        """NEG-CART-03: Updating quantity of an item not in cart fails cleanly."""
        res = Core.update_cart_quantity([], self.products, "p1", 2)
        assert res["success"] is False
        assert "Item not in cart" in res.get("error", "")

    def test_neg_update_quantity_nonexistent_product(self):
        """NEG-CART-04: Updating quantity of non-existent product ID fails cleanly."""
        cart = [{"id": "p_ghost", "quantity": 1}]
        res = Core.update_cart_quantity(cart, self.products, "p_ghost", 2)
        assert res["success"] is False
        assert "Product not found" in res.get("error", "")


@pytest.mark.negative
class TestNegativeOrderProcessing:
    """Negative testing on order placement with corrupt, missing, or invalid state."""

    @pytest.fixture(autouse=True)
    def setup_catalog(self):
        self.products = [
            {"id": "p1", "name": "Headphones", "price": 99.99, "stock": 2}
        ]

    @pytest.mark.parametrize("bad_cart", [[], None, "", False])
    def test_neg_checkout_with_empty_or_null_cart(self, bad_cart, valid_customer, cod_payment):
        """NEG-ORD-01: Rejects checkout when cart is empty, None, or invalid type."""
        res = Core.process_order(bad_cart, self.products, valid_customer, cod_payment)
        assert res["success"] is False
        assert "empty cart" in res.get("error", "").lower()

    def test_neg_checkout_with_insufficient_stock(self, valid_customer, cod_payment):
        """NEG-ORD-02: Order fails when requested quantity exceeds available stock."""
        cart = [{"id": "p1", "quantity": 10}]  # available stock is 2
        res = Core.process_order(cart, self.products, valid_customer, cod_payment)
        assert res["success"] is False
        assert "Insufficient stock" in res.get("error", "")

    def test_neg_checkout_with_unregistered_product(self, valid_customer, cod_payment):
        """NEG-ORD-03: Order fails when cart contains an ID missing from catalog."""
        cart = [{"id": "p_phantom", "quantity": 1}]
        res = Core.process_order(cart, self.products, valid_customer, cod_payment)
        assert res["success"] is False
        assert "does not exist" in res.get("error", "")

    def test_neg_checkout_with_unsupported_payment_method(self, valid_customer):
        """NEG-ORD-04: Order fails when unsupported payment method is provided."""
        cart = [{"id": "p1", "quantity": 1}]
        bad_payment = {"method": "crypto", "wallet": "0x123abc"}
        res = Core.process_order(cart, self.products, valid_customer, bad_payment)
        assert res["success"] is False
        assert "Validation failed" in res.get("error", "")
        assert "paymentMethod" in res.get("errors", {})


@pytest.mark.negative
class TestNegativeCustomerAndPaymentValidation:
    """Negative testing on malformed customer fields and security payload attempts."""

    @pytest.mark.parametrize(
        "bad_email",
        [
            "",
            "plainaddress",
            "@missinguser.com",
            "missingdomain@.com",
            "spaces in@domain.com",
            "two@@at.com",
            "no_extension@domain",
        ],
    )
    def test_neg_rejects_malformed_emails(self, bad_email):
        """NEG-VAL-01: Rejects various malformed email formats."""
        assert Core.ValidationRules.validate_email(bad_email) is False

    @pytest.mark.parametrize(
        "bad_phone",
        [
            "",
            "123",
            "CALL-US-NOW",
            "abcdefghij",
            "12345ABCDE",
            "++--**",
        ],
    )
    def test_neg_rejects_malformed_phones(self, bad_phone):
        """NEG-VAL-02: Rejects alphanumeric or short phone numbers."""
        assert Core.ValidationRules.validate_phone(bad_phone) is False

    @pytest.mark.parametrize(
        "bad_card_expiry",
        [
            "01/20",     # Past year
            "13/28",     # Invalid month 13
            "00/28",     # Invalid month 00
            "MM/YY",     # Placeholder string
            "2026/12",   # Inverted format
            "",
        ],
    )
    def test_neg_rejects_invalid_card_expiries(self, bad_card_expiry):
        """NEG-VAL-03: Rejects expired cards and invalid month specifications."""
        assert Core.ValidationRules.validate_card_expiry(bad_card_expiry) is False

    @pytest.mark.parametrize(
        "bad_upi",
        [
            "",
            "user",
            "user@",
            "@bank",
            "user@bank@extra",
            "user bank",
        ],
    )
    def test_neg_rejects_malformed_upi_ids(self, bad_upi):
        """NEG-VAL-04: Rejects malformed UPI handles."""
        assert Core.ValidationRules.validate_upi_id(bad_upi) is False

    def test_neg_xss_injection_in_name_rejected(self):
        """NEG-SEC-01: Rejects script tags or HTML entities in customer name."""
        xss_name = "<script>alert('pwned')</script>"
        assert Core.ValidationRules.validate_name(xss_name) is False

    def test_neg_empty_name_or_whitespace_only(self):
        """NEG-VAL-05: Rejects empty or whitespace-only names."""
        assert Core.ValidationRules.validate_name("   ") is False
        assert Core.ValidationRules.validate_name("") is False
