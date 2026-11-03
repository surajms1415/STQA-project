"""
AuraMart STQA API Testing Demonstration: PUT Operations.
Validates HTTP 200 updates, state mutation, non-existent resource handling (404),
and invalid update values (400 Bad Request).
"""

import pytest
from python_tests.api_tests.conftest import APIClient


@pytest.mark.api
class TestAPIPutOperations:
    """Demonstration of RESTful PUT testing capabilities using Python Requests."""

    def test_put_update_existing_product_success(self, api: APIClient):
        """API-PUT-01: Updating existing product returns 200 OK and modifies resource."""
        update_payload = {
            "price": 89.50,
            "stock": 20,
        }
        res = api.put("/api/v1/products/p1", json=update_payload)
        assert res.status_code == 200

        data = res.json()
        assert data.get("success") is True
        updated = data.get("data", {})
        assert updated.get("price") == 89.50
        assert updated.get("stock") == 20

        # Verify via subsequent GET request
        get_res = api.get("/api/v1/products/p1")
        assert get_res.status_code == 200
        assert get_res.json().get("data", {}).get("price") == 89.50
        api.assert_latency(res, max_ms=500.0)

    def test_put_update_nonexistent_product_returns_404(self, api: APIClient):
        """API-PUT-02: Updating non-existent product ID returns 404 Not Found."""
        res = api.put("/api/v1/products/p_ghost_999", json={"price": 50.0})
        assert res.status_code == 404
        assert "not found" in res.json().get("error", "").lower()

    def test_put_invalid_negative_price_returns_400(self, api: APIClient):
        """API-PUT-03: Attempting to update with negative price returns 400 Bad Request."""
        res = api.put("/api/v1/products/p1", json={"price": -15.0})
        assert res.status_code == 400
        assert "positive" in res.json().get("error", "").lower()

    def test_put_invalid_negative_stock_returns_400(self, api: APIClient):
        """API-PUT-04: Attempting to update with negative stock returns 400 Bad Request."""
        res = api.put("/api/v1/products/p1", json={"stock": -5})
        assert res.status_code == 400
        assert "non-negative" in res.json().get("error", "").lower()
