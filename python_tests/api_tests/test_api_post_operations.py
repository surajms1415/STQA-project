"""
AuraMart STQA API Testing Demonstration: POST Operations.
Validates HTTP 201 Created status codes, resource creation payloads,
missing parameter validation (400 Bad Request), type errors, and response times.
"""

import pytest
from python_tests.api_tests.conftest import APIClient


@pytest.mark.api
class TestAPIPostOperations:
    """Demonstration of RESTful POST testing capabilities using Python Requests."""

    def test_post_create_product_success(self, api: APIClient):
        """API-POST-01: Valid product creation returns 201 Created and new product payload."""
        payload = {
            "name": "Noise Cancelling Earbuds",
            "category": "Audio",
            "price": 79.99,
            "stock": 15,
            "description": "True wireless Bluetooth earbuds with charging case.",
        }
        res = api.post("/api/v1/products", json=payload)
        assert res.status_code == 201
        assert "application/json" in res.headers.get("Content-Type", "")

        data = res.json()
        assert data.get("success") is True
        created = data.get("data", {})
        assert created.get("name") == payload["name"]
        assert created.get("price") == payload["price"]
        assert created.get("stock") == payload["stock"]
        assert "id" in created
        api.assert_latency(res, max_ms=500.0)

    def test_post_place_order_success(self, api: APIClient):
        """API-POST-02: Placing an order returns 201 Created with unique order ID."""
        payload = {
            "items": [{"id": "p1", "quantity": 2, "price": 99.99}],
            "customer": {
                "name": "Alice Tester",
                "email": "alice@qa.org",
                "phone": "9876543210",
                "address": "123 Test St",
            },
            "payment": {"method": "cod"},
            "total": 209.98,
        }
        res = api.post("/api/v1/orders", json=payload)
        assert res.status_code == 201

        data = res.json()
        assert data.get("success") is True
        assert data.get("orderId", "").startswith("ORD-")
        assert data.get("data", {}).get("status") == "Confirmed"

    def test_post_missing_parameters_returns_400(self, api: APIClient):
        """API-POST-03: Missing required fields returns 400 Bad Request with field-specific errors."""
        incomplete_payload = {
            # 'name' is missing
            "category": "Audio",
            # 'price' is missing
            "stock": 10,
        }
        res = api.post("/api/v1/products", json=incomplete_payload)
        assert res.status_code == 400

        data = res.json()
        assert data.get("success") is False
        errors = data.get("errors", {})
        assert "name" in errors
        assert "price" in errors

    @pytest.mark.parametrize(
        "bad_payload, expected_error_key",
        [
            ({"name": "X", "category": "Audio", "price": 50, "stock": 5}, "name"),            # Short name
            ({"name": "Valid Name", "category": "Audio", "price": -10, "stock": 5}, "price"),   # Negative price
            ({"name": "Valid Name", "category": "Audio", "price": "free", "stock": 5}, "price"), # Non-numeric price
            ({"name": "Valid Name", "category": "Audio", "price": 50, "stock": -2}, "stock"),   # Negative stock
            ({"name": "Valid Name", "category": "Audio", "price": 50, "stock": 3.5}, "stock"),  # Decimal stock
        ],
    )
    def test_post_incorrect_input_values_returns_400(self, api: APIClient, bad_payload, expected_error_key):
        """API-POST-04: Incorrect field types and invalid values trigger 400 validation error."""
        res = api.post("/api/v1/products", json=bad_payload)
        assert res.status_code == 400
        errors = res.json().get("errors", {})
        assert expected_error_key in errors

    def test_post_order_with_empty_items_returns_400(self, api: APIClient):
        """API-POST-05: Submitting order with empty items array returns 400 Bad Request."""
        empty_order = {
            "items": [],
            "customer": {"email": "test@domain.com"},
        }
        res = api.post("/api/v1/orders", json=empty_order)
        assert res.status_code == 400
        assert "at least one item" in res.json().get("error", "").lower()
