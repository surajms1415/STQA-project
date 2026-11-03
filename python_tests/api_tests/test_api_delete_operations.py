"""
AuraMart STQA API Testing Demonstration: DELETE Operations.
Validates HTTP 200 deletion confirmation, resource removal,
and 404 response on attempting to delete non-existent resources.
"""

import pytest
from python_tests.api_tests.conftest import APIClient


@pytest.mark.api
class TestAPIDeleteOperations:
    """Demonstration of RESTful DELETE testing capabilities using Python Requests."""

    def test_delete_existing_product_success(self, api: APIClient):
        """API-DEL-01: Deleting existing product returns 200 OK and confirms deletion."""
        # Create temporary product first to keep other tests independent
        create_res = api.post("/api/v1/products", json={
            "name": "Disposable Test Item",
            "category": "Accessories",
            "price": 10.00,
            "stock": 5,
        })
        assert create_res.status_code == 201
        temp_id = create_res.json().get("data", {}).get("id")

        # Delete the created product
        del_res = api.delete(f"/api/v1/products/{temp_id}")
        assert del_res.status_code == 200

        del_data = del_res.json()
        assert del_data.get("success") is True
        assert del_data.get("deletedId") == temp_id

        # Verify resource is gone via GET
        get_res = api.get(f"/api/v1/products/{temp_id}")
        assert get_res.status_code == 404
        api.assert_latency(del_res, max_ms=500.0)

    def test_delete_nonexistent_product_returns_404(self, api: APIClient):
        """API-DEL-02: Deleting non-existent product ID returns 404 Not Found."""
        res = api.delete("/api/v1/products/p_ghost_888")
        assert res.status_code == 404
        assert "not found" in res.json().get("error", "").lower()
