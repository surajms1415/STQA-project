"""
Validation Testing Suite for AuraMart E-Commerce Application.
Validates form validation rules, schema integrity, quantity restrictions,
pricing sanity, and product data consistency.
"""

import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.validation
class TestProductCatalogSchemaValidation:
    """Validates baseline catalog integrity and product model constraints."""

    def test_val_catalog_non_empty(self, initial_products):
        """VAL-CAT-01: Product catalog contains items."""
        assert len(initial_products) >= 10, "Baseline catalog should contain at least 10 products"

    def test_val_product_id_uniqueness(self, initial_products):
        """VAL-CAT-02: Every product ID in the catalog is strictly unique."""
        ids = [p["id"] for p in initial_products]
        assert len(ids) == len(set(ids)), "Product IDs must be globally unique across catalog"

    def test_val_product_field_constraints(self, initial_products):
        """VAL-CAT-03: Every product adheres to data schema constraints (name, price, stock, category)."""
        valid_categories = {"Audio", "Electronics", "Wearables", "Home", "Accessories"}
        for p in initial_products:
            assert isinstance(p["id"], str) and len(p["id"]) > 0, f"Invalid product ID: {p}"
            assert isinstance(p["name"], str) and len(p["name"]) >= 3, f"Invalid product name: {p}"
            assert isinstance(p["price"], (int, float)) and p["price"] > 0, f"Invalid price in: {p}"
            assert isinstance(p["stock"], int) and p["stock"] >= 0, f"Invalid stock in: {p}"
            assert p["category"] in valid_categories, f"Invalid category {p['category']} in: {p}"
            assert isinstance(p["description"], str) and len(p["description"]) > 5, f"Short description in: {p}"


@pytest.mark.validation
class TestFormInputValidationRules:
    """Validates granular input rule functions."""

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("John Doe", True),
            ("Mary-Jane O'Connor", True),
            ("Dr. Smith", True),
            ("Al", False),             # Too short
            ("John123", False),        # Contains numbers
            ("!@#$%^", False),         # Symbols
        ],
    )
    def test_val_name_rule(self, name, expected):
        """VAL-RULE-01: Name validation rule (letters, periods, hyphens, min 3 chars)."""
        assert Core.ValidationRules.validate_name(name) is expected

    @pytest.mark.parametrize(
        "email, expected",
        [
            ("alice@example.com", True),
            ("support.user@tech.co.uk", True),
            ("invalid-email", False),
            ("user@domain", False),
        ],
    )
    def test_val_email_rule(self, email, expected):
        """VAL-RULE-02: Email validation rule."""
        assert Core.ValidationRules.validate_email(email) is expected

    @pytest.mark.parametrize(
        "phone, expected",
        [
            ("9876543210", True),
            ("(555) 123-4567", True),
            ("+1-800-555-0199", True),
            ("12345", False),
        ],
    )
    def test_val_phone_rule(self, phone, expected):
        """VAL-RULE-03: Phone validation extracts digits and checks length (10-15)."""
        assert Core.ValidationRules.validate_phone(phone) is expected

    @pytest.mark.parametrize(
        "zip_val, expected",
        [
            ("90210", True),
            ("SW1A 1AA", True),
            ("123", False),
        ],
    )
    def test_val_zip_rule(self, zip_val, expected):
        """VAL-RULE-04: ZIP code validation."""
        assert Core.ValidationRules.validate_zip(zip_val) is expected


@pytest.mark.validation
class TestPaymentAndCheckoutPayloadValidation:
    """Validates complete checkout payload checking and multi-field error reporting."""

    def test_val_checkout_valid_card_payload(self, valid_customer, valid_card_payment):
        """VAL-PAY-01: Valid customer with card payment passes all checks."""
        res = Core.validate_checkout_payload(valid_customer, valid_card_payment)
        assert res["isValid"] is True
        assert len(res["errors"]) == 0

    def test_val_checkout_valid_upi_payload(self, valid_customer, upi_payment):
        """VAL-PAY-02: Valid customer with UPI payment passes all checks."""
        res = Core.validate_checkout_payload(valid_customer, upi_payment)
        assert res["isValid"] is True
        assert len(res["errors"]) == 0

    def test_val_checkout_valid_cod_payload(self, valid_customer, cod_payment):
        """VAL-PAY-03: Valid customer with COD payment passes all checks."""
        res = Core.validate_checkout_payload(valid_customer, cod_payment)
        assert res["isValid"] is True
        assert len(res["errors"]) == 0

    def test_val_checkout_reports_field_specific_errors(self):
        """VAL-PAY-04: Malformed checkout reports exact field keys that failed."""
        customer = {
            "name": "A",             # Fails: too short
            "email": "not-an-email",  # Fails: invalid format
            "phone": "1",             # Fails: too short
            "address": "4",           # Fails: too short
            "city": "C",              # Fails: too short
            "state": "",              # Fails: empty
            "zip": "9",               # Fails: too short
        }
        res = Core.validate_checkout_payload(customer, {"method": "cod"})
        assert res["isValid"] is False
        errors = res["errors"]
        for key in ["name", "email", "phone", "address", "city", "state", "zip"]:
            assert key in errors, f"Expected validation error for field '{key}'"
