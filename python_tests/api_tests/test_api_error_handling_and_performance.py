"""
AuraMart STQA API Testing Demonstration: Error Handling & Performance.
Validates malformed payloads (400), invalid endpoints (404),
header contracts, and latency benchmarking against strict SLAs.
"""

import pytest
import requests
from python_tests.api_tests.conftest import APIClient


@pytest.mark.api
class TestAPIErrorHandlingAndPerformance:
    """Demonstration of API error resilience and performance benchmarking."""

    def test_invalid_endpoint_path_returns_404(self, api: APIClient):
        """API-ERR-01: Accessing undefined URL path returns 404 Not Found."""
        res = api.get("/api/v1/invalid/route/endpoint")
        assert res.status_code == 404
        assert res.json().get("success") is False

    def test_malformed_json_body_returns_400(self, api_base_url: str):
        """API-ERR-02: Sending syntactically broken JSON body returns 400 Bad Request."""
        url = f"{api_base_url}/api/v1/products"
        broken_json = '{"name": "Broken JSON without closing brace'

        res = requests.post(
            url,
            data=broken_json,
            headers={"Content-Type": "application/json", "Content-Length": str(len(broken_json))},
            timeout=5,
        )
        assert res.status_code == 400
        data = res.json()
        assert data.get("success") is False
        assert "malformed" in data.get("error", "").lower()

    def test_response_headers_contract(self, api: APIClient):
        """API-PERF-01: Verifies mandatory security and content headers."""
        res = api.get("/api/v1/health")
        headers = res.headers

        assert "Content-Type" in headers
        assert "application/json" in headers["Content-Type"]
        assert "Content-Length" in headers
        assert "X-Powered-By" in headers

    def test_performance_latency_batch_sla(self, api: APIClient):
        """API-PERF-02: Validates that consecutive API calls remain within strict latency SLA (< 200ms avg)."""
        latencies_ms = []

        for _ in range(10):
            res = api.get("/api/v1/products")
            assert res.status_code == 200
            latencies_ms.append(res.elapsed.total_seconds() * 1000.0)

        avg_latency = sum(latencies_ms) / len(latencies_ms)
        max_latency = max(latencies_ms)

        print(f"\n[LATENCY BENCHMARK] 10 iterations: Avg={avg_latency:.2f}ms | Max={max_latency:.2f}ms")
        assert avg_latency < 200.0, f"Average latency too high: {avg_latency}ms"
        assert max_latency < 500.0, f"Max latency spike exceeded SLA: {max_latency}ms"
