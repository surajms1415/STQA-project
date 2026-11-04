"""
Security Testing - Cross-Site Scripting (XSS) Prevention & Payload Resistance.
Verifies that client-side and business logic layers reject or neutralize malicious
HTML, SVG, JavaScript protocol, and DOM-based injection payloads.
"""

import html
import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify

XSS_VECTORS = [
    ("<script>alert('XSS')</script>", "Standard script tag"),
    ("<SCRIPT SRC=http://evil.example/xss.js></SCRIPT>", "Uppercase external script tag"),
    ("<img src=x onerror=alert(1)>", "Image tag with onerror event"),
    ("<svg/onload=alert('XSS')>", "SVG tag with onload event"),
    ("javascript:alert(document.cookie)", "Javascript pseudo-protocol"),
    ("'><script>alert(1)</script>", "Attribute escape sequence into script tag"),
    ('" onfocus="alert(1)" autofocus="', "Inline event attribute breakout"),
    ("<iframe src=\"javascript:alert('XSS')\"></iframe>", "Iframe embedding script"),
    ("<body onload=alert('XSS')>", "Body onload hook"),
    ("<input type=\"text\" autofocus onfocus=\"alert(1)\">", "Autofocus input vector"),
    ("<a href=\"javascript:alert('XSS')\">Click here</a>", "Anchor tag with javascript href"),
]


@pytest.mark.security
class TestCrossSiteScriptingPrevention:
    """Security tests assessing resistance against common XSS attack vectors."""

    @pytest.mark.parametrize("payload,vector_desc", XSS_VECTORS)
    def test_sec_xss_01_customer_name_rejects_xss_payloads(self, payload, vector_desc):
        """1. Verify Customer Name Input Validation Rejects All Standard XSS Payloads."""
        # Customer name only allows letters, spaces, dots, hyphens, and apostrophes
        is_valid = Core.ValidationRules.validate_name(payload)
        assert is_valid is False, f"Name validator must reject {vector_desc}: {payload}"

    @pytest.mark.parametrize("payload,vector_desc", XSS_VECTORS)
    def test_sec_xss_02_customer_email_rejects_xss_payloads(self, payload, vector_desc):
        """2. Verify Customer Email Validation Rejects All XSS Injections."""
        is_valid = Core.ValidationRules.validate_email(payload)
        assert is_valid is False, f"Email validator must reject {vector_desc}: {payload}"

    @pytest.mark.parametrize("payload,vector_desc", XSS_VECTORS)
    def test_sec_xss_03_customer_phone_rejects_xss_payloads(self, payload, vector_desc):
        """3. Verify Customer Phone Validation Rejects Script and Tag Injections."""
        is_valid = Core.ValidationRules.validate_phone(payload)
        assert is_valid is False, f"Phone validator must reject {vector_desc}: {payload}"

    @pytest.mark.parametrize("payload,vector_desc", XSS_VECTORS)
    def test_sec_xss_04_search_keyword_neutralizes_xss_payloads(self, payload, vector_desc):
        """4. Verify Catalog Search Query Treats XSS Strings as Literal Query Terms."""
        # Searching for an XSS vector should treat the string literally and return 0 matches safely
        matches = Core.filter_and_sort_products(Core.INITIAL_PRODUCTS, {"search": payload})
        assert isinstance(matches, list), "Search with XSS payload must return valid list"
        assert len(matches) == 0, f"XSS search {payload} must not match normal product names"

        # Catalog state must remain intact
        assert len(Core.INITIAL_PRODUCTS) == 10, "Catalog must remain completely intact"

    @pytest.mark.parametrize("payload,vector_desc", XSS_VECTORS)
    def test_sec_xss_05_checkout_submission_blocks_xss_orders(self, valid_customer, payload, vector_desc):
        """5. Verify Checkout Submission Blocks Orders with Injected XSS Payloads."""
        customer = dict(valid_customer)
        customer["name"] = payload

        cart = [{"id": "p1", "quantity": 1}]
        res = Core.process_order(cart, Core.INITIAL_PRODUCTS, customer, {"method": "cod"})

        assert res["success"] is False, f"Order must be blocked for {vector_desc}: {payload}"
        assert "Validation failed" in res.get("error", "") or "error" in res, \
            "Must return structured validation error"

    def test_sec_xss_06_html_entity_encoding_safety(self):
        """6. Verify HTML Special Characters Are Encoded into Safe Entities."""
        raw_malicious_string = "<script>alert('Hello & \"Welcome\"');</script>"
        encoded_string = html.escape(raw_malicious_string)

        assert "<script>" not in encoded_string, "Raw opening script tag must not exist"
        assert "</script>" not in encoded_string, "Raw closing script tag must not exist"
        assert "&lt;script&gt;" in encoded_string, "Tags must be safely converted to HTML entities"
        assert "&amp;" in encoded_string, "Ampersands must be safely encoded"
        assert "&quot;" in encoded_string, "Quotes must be safely encoded"
