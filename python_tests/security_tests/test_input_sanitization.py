"""
Security Testing - Input Validation, Sanitization, and Boundary Handling.
Verifies that the application strictly sanitizes inputs, resists control characters,
handles unexpected data types safely, and prevents memory or denial-of-service abuse.
"""

import math
import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.security
class TestInputValidationAndSanitization:
    """Security tests covering input sanitization, control characters, and malformed inputs."""

    def test_sec_input_01_whitespace_sanitization(self, valid_customer):
        """1. Verify Leading and Trailing Whitespace is Sanitized in Checkout Processing."""
        customer = dict(valid_customer)
        customer["name"] = "   Johnathan Doe   "
        customer["address"] = "   123 Secure Boulevard   "
        customer["city"] = "   Metropolis   "
        customer["state"] = "   NY   "
        customer["zip"] = "   10001   "

        cart = [{"id": "p1", "quantity": 1}]
        res = Core.process_order(cart, Core.INITIAL_PRODUCTS, customer, {"method": "cod"})

        assert res["success"] is True, f"Valid padded input should succeed: {res.get('error')}"
        stored_customer = res["order"]["customer"]

        assert stored_customer["name"] == "Johnathan Doe", "Leading/trailing whitespace in name must be stripped"
        assert "123 Secure Boulevard" in stored_customer["address"], "Whitespace in address must be sanitized"
        assert stored_customer["name"] != customer["name"], "Customer name must not retain raw surrounding whitespace"

    @pytest.mark.parametrize("malicious_char,desc", [
        ("\x00", "Null byte"),
        ("\r\n\r\n", "CRLF sequence"),
        ("\x1b[31mRed\x1b[0m", "ANSI escape sequences"),
        ("\x08\x08", "Backspace control characters"),
        ("\t\t\t\n", "Tabs and newline control characters"),
    ])
    def test_sec_input_02_control_character_injection(self, malicious_char, desc):
        """2. Verify Control Characters and Null Bytes are Rejected in Sensitive Fields."""
        # Test in customer name
        assert Core.ValidationRules.validate_name(f"Alice{malicious_char}Smith") is False, \
            f"Name containing {desc} must be rejected"

        # Test in customer email
        assert Core.ValidationRules.validate_email(f"user{malicious_char}@example.com") is False, \
            f"Email containing {desc} must be rejected"

        # Test in customer phone
        assert Core.ValidationRules.validate_phone(f"98765{malicious_char}43210") is False, \
            f"Phone containing {desc} must be rejected"

    def test_sec_input_03_buffer_overflow_and_dos_length_inputs(self, valid_customer):
        """3. Verify Excessive Payload Lengths (Buffer DOS) Are Handled Safely."""
        huge_string_10k = "A" * 10000
        huge_string_50k = "X" * 50000

        # Excessively long name should be rejected by name length constraints
        assert Core.ValidationRules.validate_name(huge_string_10k) is False, \
            "10,000 character name must be rejected"

        # Excessively long zip code should be rejected
        assert Core.ValidationRules.validate_zip(huge_string_10k) is False, \
            "10,000 character ZIP must be rejected"

        # Excessively long search keyword should handle safely without throwing
        results = Core.filter_and_sort_products(Core.INITIAL_PRODUCTS, {"search": huge_string_50k})
        assert isinstance(results, list), "Huge search string must return list safely"
        assert len(results) == 0, "No products should match 50,000 character string"

        # Test order processing with huge string doesn't crash runtime
        customer_huge = dict(valid_customer)
        customer_huge["name"] = huge_string_10k
        res = Core.process_order([{"id": "p1", "quantity": 1}], Core.INITIAL_PRODUCTS, customer_huge, {"method": "cod"})
        assert res["success"] is False, "Order with 10k character name must fail validation safely"
        assert "error" in res or "errors" in res, "Must return structured error message"

    @pytest.mark.parametrize("payload,expected_valid", [
        ("\u200b\u200b\u200b", False),  # Zero-width spaces
        ("\ufeffJohn", False),           # Byte Order Mark (BOM) in name
        ("J\u00a0ohn", False),           # Non-breaking space inside name
        ("John\u202eDoe", False),        # Right-to-Left Override (RTLO)
    ])
    def test_sec_input_04_zero_width_and_homoglyph_characters(self, payload, expected_valid):
        """4. Verify Non-Standard Unicode and Zero-Width Characters Are Strictly Regulated."""
        result = Core.ValidationRules.validate_name(payload)
        assert result is expected_valid, f"Payload {repr(payload)} expected valid={expected_valid}, got {result}"

    @pytest.mark.parametrize("type_payload,expected_valid", [
        (True, False),
        (False, False),
        (None, False),
        ([], False),
        ({}, False),
        (12345, False),
        ([1, 2, 3], False),
        ({"name": "Admin"}, False),
    ])
    def test_sec_input_05_type_confusion_attacks(self, type_payload, expected_valid):
        """5. Verify Non-String Payloads Disguised in Form Fields Fail Safely."""
        # Test validate_name
        assert Core.ValidationRules.validate_name(type_payload) is expected_valid, \
            f"validate_name should return {expected_valid} for type {type(type_payload)}"

        # Test validate_email
        assert Core.ValidationRules.validate_email(type_payload) is expected_valid, \
            f"validate_email should return {expected_valid} for type {type(type_payload)}"

        # Test validate_phone
        assert Core.ValidationRules.validate_phone(type_payload) is expected_valid, \
            f"validate_phone should return {expected_valid} for type {type(type_payload)}"

    @pytest.mark.parametrize("bad_number", [
        float("nan"),
        float("inf"),
        float("-inf"),
        1e308,
        -1e308,
        -0.0,
    ])
    def test_sec_input_06_extreme_numerical_boundary_resilience(self, bad_number):
        """6. Verify NaN, Infinity, and Overflowing Numbers Do Not Corrupt Accounting."""
        # Price formatting with NaN / Inf
        price_str = Core.format_price(bad_number)
        assert isinstance(price_str, str), "format_price must always return a string"
        assert not math.isnan(float(price_str.replace("$", ""))), "Formatted price must never be literal NaN"

        # Line total calculation with NaN / Inf
        line_total = Core.calculate_line_total(bad_number, 2)
        assert isinstance(line_total, (int, float)), "calculate_line_total must return a number"
        assert not math.isnan(line_total), "Line total must not be NaN"
        assert not math.isinf(line_total), "Line total must not be Inf"

        # Quantity validation rejects non-finite or extreme values
        assert Core.ValidationRules.validate_quantity(bad_number, 10) is False, \
            f"Quantity validation must reject {bad_number}"

    def test_sec_input_07_invalid_cart_structure_handled_safely(self, valid_customer):
        """7. Verify Malformed or Non-List Cart Structures Fail Safely without Unhandled Exceptions."""
        # Non-list cart structures
        malformed_carts = [
            None,
            "cart_string",
            12345,
            {"id": "p1", "quantity": 1},  # object instead of array
            [None],
            [{}],
            [{"id": 12345}],
            [{"id": "p1", "quantity": "three"}],
        ]

        for bad_cart in malformed_carts:
            # calculate_cart_totals should not crash
            totals = Core.calculate_cart_totals(bad_cart, Core.INITIAL_PRODUCTS)
            assert isinstance(totals, dict), "calculate_cart_totals must return dict safely"
            assert "total" in totals, "Totals dict must contain 'total'"
            assert totals["total"] == 0.0 or totals["total"] >= 0.0, "Total must be non-negative"

            # process_order should reject safely with error
            res = Core.process_order(bad_cart, Core.INITIAL_PRODUCTS, valid_customer, {"method": "cod"})
            assert res["success"] is False, f"process_order must reject malformed cart: {bad_cart}"
            assert "error" in res, "Must return descriptive error"
