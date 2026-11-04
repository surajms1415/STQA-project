"""
Security Testing - SQL Injection (SQLi) Pattern Handling & Data Integrity.
Verifies that database-style injection strings, union operators, and quote breakouts
are treated strictly as literal data, rejected by format validators, and do not
cause unhandled exceptions, data manipulation, or query bypasses.
"""

import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify

SQLI_PATTERNS = [
    ("' OR '1'='1", "Tautology quote breakout"),
    ("' OR '1'='1' --", "Tautology with line comment"),
    ("' OR 1=1 #", "Hash comment tautology"),
    ("admin' --", "Classic auth bypass pattern"),
    ("1' UNION SELECT null, username, password FROM users --", "Union based extraction"),
    ("'; DROP TABLE products; --", "Piggybacked destructive query"),
    ("1; EXEC xp_cmdshell('dir');--", "Command execution via SQL statement"),
    ("' AND SLEEP(5) --", "Time-based blind injection pattern"),
    ("' AND 1=0 UNION ALL SELECT 'test'--", "Union all syntax pattern"),
]


@pytest.mark.security
class TestSQLInjectionPatternHandling:
    """Security tests verifying application resilience against SQL injection-style inputs."""

    @pytest.mark.parametrize("payload,pattern_desc", SQLI_PATTERNS)
    def test_sec_sqli_01_strictly_typed_fields_reject_sqli(self, payload, pattern_desc):
        """1. Verify Strictly Formatted Fields Reject SQL Injection Strings."""
        # Phone numbers must only contain digits
        assert Core.ValidationRules.validate_phone(payload) is False, \
            f"Phone validator must reject SQLi payload {pattern_desc}"

        # ZIP codes must follow postal format
        assert Core.ValidationRules.validate_zip(payload) is False, \
            f"ZIP validator must reject SQLi payload {pattern_desc}"

        # Card expiry must follow MM/YY format
        assert Core.ValidationRules.validate_card_expiry(payload) is False, \
            f"Card expiry validator must reject SQLi payload {pattern_desc}"

        # Card CVV must only contain 3-4 digits
        assert Core.ValidationRules.validate_card_cvv(payload) is False, \
            f"Card CVV validator must reject SQLi payload {pattern_desc}"

    @pytest.mark.parametrize("payload,pattern_desc", SQLI_PATTERNS)
    def test_sec_sqli_02_catalog_search_treats_sqli_literally(self, payload, pattern_desc):
        """2. Verify Search Filter Treats SQLi Strings as Literal Substrings Without Corrupting Catalog."""
        initial_count = len(Core.INITIAL_PRODUCTS)

        # Performing search with SQLi syntax
        matches = Core.filter_and_sort_products(Core.INITIAL_PRODUCTS, {"search": payload})
        assert isinstance(matches, list), "Search must return a list"

        # Searching for ' OR '1'='1 should NOT return all products (classic tautology bypass)
        assert len(matches) == 0, f"SQLi payload {pattern_desc} must not bypass filter logic"

        # Verify catalog inventory did not get dropped or altered
        assert len(Core.INITIAL_PRODUCTS) == initial_count, "Catalog products must remain intact"

    @pytest.mark.parametrize("payload,pattern_desc", SQLI_PATTERNS)
    def test_sec_sqli_03_product_id_lookup_treats_sqli_safely(self, payload, pattern_desc):
        """3. Verify Product ID Lookup with Injected Strings Returns False Safely."""
        # Lookup in products
        found = next((p for p in Core.INITIAL_PRODUCTS if p["id"] == payload), None)
        assert found is None, f"SQLi string {payload} must not match legitimate product IDs"

        # Add to cart with SQLi product ID fails cleanly
        cart = []
        res = Core.add_to_cart(cart, Core.INITIAL_PRODUCTS, payload, 1)
        assert res["success"] is False, "Adding product with SQLi ID must fail"
        assert "not found" in res["error"].lower() or "does not exist" in res["error"].lower()
        assert len(res["cart"]) == 0, "Cart must remain empty"

    def test_sec_sqli_04_destructive_statement_does_not_mutate_state(self, valid_customer):
        """4. Verify Destructive SQL Strings in Form Data Do Not Execute or Corrupt State."""
        destructive_name = "Robert'); DROP TABLE Students;--"
        destructive_customer = dict(valid_customer)
        destructive_customer["name"] = destructive_name

        cart = [{"id": "p1", "quantity": 1}]
        res = Core.process_order(cart, Core.INITIAL_PRODUCTS, destructive_customer, {"method": "cod"})

        # The name contains punctuation and parentheses, which is rejected by strict letters-only regex
        assert res["success"] is False, "Destructive injection name must fail validation"
        assert "Validation failed" in res.get("error", "")

        # Products catalog must remain completely unaffected
        assert len(Core.INITIAL_PRODUCTS) == 10
        assert Core.INITIAL_PRODUCTS[0]["id"] == "p1"
