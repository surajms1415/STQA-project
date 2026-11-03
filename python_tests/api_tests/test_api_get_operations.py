"""
AuraMart STQA API Testing Demonstration: GET Operations.
Validates HTTP 200 status codes, JSON schema structures, query parameter filtering,
404 error responses for non-existent resources, and latency thresholds.
"""

import pytest
from python_tests.api_tests.conftest import APIClient


@pytest.mark.api
class TestAPIGetOperations:
    """Demonstration of RESTful GET testing capabilities using Python Requests."""

    def test_get_api_health_check(self, api: APIClient):
        """API-GET-01: Health check endpoint returns 200 OK and status confirmation."""
        res = api.get("/api/v1/health")
        assert res.status_code == 200
        assert "application/json" in res.headers.get("Content-Type", "")

        data = res.json()
        assert data.get("status") == "ok"
        assert "service" in data
        assert "timestamp" in data
        api.assert_latency(res, max_ms=500.0)

    def test_get_all_products_structure(self, api: APIClient):
        """API-GET-02: Listing products returns 200 OK with valid list schema."""
        res = api.get("/api/v1/products")
        assert res.status_code == 200

        data = res.json()
        assert data.get("success") is True
        assert isinstance(data.get("data"), list)
        assert data.get("count") == len(data["data"])
        assert data["count"] >= 3

        # Validate schema of each item
        for prod in data["data"]:
            assert "id" in prod and isinstance(prod["id"], str)
            assert "name" in prod and isinstance(prod["name"], str)
            assert "price" in prod and isinstance(prod["price"], (int, float))
            assert "stock" in prod and isinstance(prod["stock"], int)
            assert "category" in prod and isinstance(prod["category"], str)

        api.assert_latency(res, max_ms=500.0)

    def test_get_single_product_by_id(self, api: APIClient):
        """API-GET-03: Fetching specific product by ID returns 200 OK and expected details."""
        res = api.get("/api/v1/products/p1")
        assert res.status_code == 200

        data = res.json()
        assert data.get("success") is True
        prod = data.get("data", {})
        assert prod.get("id") == "p1"
        assert prod.get("name") == "Aura Wireless Headphones"
        assert prod.get("price") == 99.99
        assert prod.get("category") == "Audio"

    def test_get_products_filtered_by_category(self, api: APIClient):
        """API-GET-04: Query param ?category=Audio filters data accurately."""
        res = api.get("/api/v1/products?category=Audio")
        assert res.status_code == 200

        data = res.json()
        items = data.get("data", [])
        assert len(items) >= 1
        assert all(item["category"].lower() == "audio" for item in items)

    def test_get_products_filtered_by_search(self, api: APIClient):
        """API-GET-05: Query param ?search=Keyboard returns matching items."""
        res = api.get("/api/v1/products?search=Keyboard")
        assert res.status_code == 200

        data = res.json()
        items = data.get("data", [])
        assert len(items) >= 1
        assert any("Keyboard" in item["name"] for item in items)

    def test_get_nonexistent_product_returns_404(self, api: APIClient):
        """API-GET-06: Requesting invalid product ID returns HTTP 404 Not Found with error message."""
        res = api.get("/api/v1/products/non_existent_id_999")
        assert res.status_code == 404

        data = res.json()
        assert data.get("success") is False
        assert "not found" in data.get("error", "").lower()

    def test_get_response_time_under_threshold(self, api: APIClient):
        """API-GET-07: Validates that response latency is well under acceptable threshold (< 500ms)."""
        res = api.get("/api/v1/products")
        api.assert_latency(res, max_ms=500.0)
