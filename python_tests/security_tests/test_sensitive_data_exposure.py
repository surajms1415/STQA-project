"""
Security Testing - Sensitive Information Exposure & Data Privacy Verification.
Verifies that customer financial data (CVV, full card numbers) and server internals
(stack traces, private keys, environment secrets) are never leaked in receipts,
stored state, API responses, or error payloads.
"""

import json
import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.security
class TestSensitiveDataExposure:
    """Security tests verifying that sensitive information is never exposed."""

    def test_sec_exposure_01_card_cvv_never_persisted_in_order(self, valid_customer):
        """1. Verify Credit Card CVV is Never Included in Generated Order Invoices or Records."""
        payment_payload = {
            "method": "card",
            "cardNum": "4111222233334444",
            "cardExpiry": "12/29",
            "cardCvv": "789",  # Sensitive security code
        }

        cart = [{"id": "p1", "quantity": 1}]
        res = Core.process_order(cart, Core.INITIAL_PRODUCTS, valid_customer, payment_payload)

        assert res["success"] is True, f"Valid order should succeed: {res.get('error')}"
        order = res["order"]

        # Serialize order to JSON string to inspect all fields recursively
        order_json_str = json.dumps(order)

        # CVV must NEVER appear anywhere in the order object
        assert "789" not in order_json_str, "CVV number '789' was found in order record!"
        assert "cardCvv" not in order_json_str, "'cardCvv' field was serialized in order record!"
        assert "cvv" not in order_json_str.lower(), "CVV field reference found in order record!"

    def test_sec_exposure_02_full_card_pan_not_exposed_in_plaintext_receipt(self, valid_customer):
        """2. Verify Full 16-Digit Card Number (PAN) is Not Stored as Plaintext in Order Summary."""
        raw_card_num = "4111222233334444"
        payment_payload = {
            "method": "card",
            "cardNum": raw_card_num,
            "cardExpiry": "12/29",
            "cardCvv": "456",
        }

        cart = [{"id": "p1", "quantity": 1}]
        res = Core.process_order(cart, Core.INITIAL_PRODUCTS, valid_customer, payment_payload)

        assert res["success"] is True
        order = res["order"]
        order_json_str = json.dumps(order)

        # Full 16-digit number must NOT be saved in plaintext
        assert raw_card_num not in order_json_str, "Full 16-digit credit card number leaked in plaintext!"
        assert order.get("paymentMethod") == "Credit/Debit Card", "Payment method should be clean descriptive label"

    def test_sec_exposure_03_error_messages_do_not_leak_system_internals(self, valid_customer):
        """3. Verify Error Messages Return Safe User-Facing Text Without Leaking System Internals."""
        # Intentionally submit invalid payloads to trigger error pathways
        invalid_payloads = [
            ({"method": "unknown_gateway"}, "Unsupported gateway"),
            ({"method": "card", "cardNum": "0000"}, "Malformed card"),
            ({}, "Empty payment"),
        ]

        sensitive_keywords = [
            "Traceback (most recent call last)",
            "C:\\Users\\",
            "/home/",
            "/etc/passwd",
            "password",
            "secret_key",
            "DATABASE_URL",
            "eval(",
            "SQL syntax",
        ]

        for payment, label in invalid_payloads:
            res = Core.process_order([{"id": "p1", "quantity": 1}], Core.INITIAL_PRODUCTS, valid_customer, payment)
            assert res["success"] is False, f"Invalid payment should fail: {label}"

            error_text = json.dumps(res)
            for leak in sensitive_keywords:
                assert leak.lower() not in error_text.lower(), \
                    f"Sensitive system keyword '{leak}' leaked in error response: {error_text}"

    def test_sec_exposure_04_storage_keys_and_payload_isolation(self, mock_storage):
        """4. Verify LocalStorage State Serialization Isolates Sensitive Data."""
        # Ensure only products, cart, and orders keys are used
        expected_keys = {"auramart_products_v1", "auramart_cart_v1", "auramart_orders_v1"}
        actual_keys = set(Core.STORAGE_KEYS.values())

        assert actual_keys == expected_keys, f"Expected storage keys {expected_keys}, got {actual_keys}"

        # No secret keys or session tokens should be in STORAGE_KEYS
        for k in Core.STORAGE_KEYS.keys():
            assert "token" not in k.lower()
            assert "secret" not in k.lower()
            assert "password" not in k.lower()
