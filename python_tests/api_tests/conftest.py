"""
Pytest Fixtures for AuraMart STQA API Testing Demonstration.
Supports configurable endpoint via CLI argument (--api-base-url) or environment variable (AURAMART_API_BASE_URL).
Spins up a lightweight background demonstration REST server if no external endpoint is supplied.
"""

import os
import threading
import time
from http.server import ThreadingHTTPServer
import pytest
import requests

from python_tests.api_tests.demo_api_server import DemoRESTHandler, reset_demo_db


def pytest_addoption(parser):
    """Add command line flag for configurable sample API endpoint."""
    try:
        parser.addoption(
            "--api-base-url",
            action="store",
            default=os.getenv("AURAMART_API_BASE_URL", "demo"),
            help="Base URL for REST API testing demonstration (default: 'demo' uses in-memory demo server)",
        )
    except ValueError:
        # Option already added by another conftest
        pass


@pytest.fixture(scope="session")
def demo_server():
    """
    Spins up an ephemeral local REST server on 127.0.0.1 for the duration of the test session.
    Runs inside the current test process to ensure full sandbox compatibility.
    """
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRESTHandler)
    host, port = server.server_address
    base_url = f"http://{host}:{port}"

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # Wait for server readiness
    time.sleep(0.1)

    yield base_url

    server.shutdown()
    server.server_close()


@pytest.fixture(scope="session")
def api_base_url(request, demo_server) -> str:
    """
    Resolves the base URL for API tests:
    - If CLI option --api-base-url is specified (and not 'demo'), uses that external URL.
    - Otherwise, falls back to the embedded demo_server URL.
    """
    cli_val = request.config.getoption("--api-base-url", default="demo")
    env_val = os.getenv("AURAMART_API_BASE_URL", "demo")

    target = cli_val if cli_val != "demo" else env_val
    if target and target != "demo":
        return target.rstrip("/")

    return demo_server


@pytest.fixture(autouse=True)
def reset_server_state(request):
    """Resets demonstration database state before each test."""
    cli_val = request.config.getoption("--api-base-url", default="demo")
    if cli_val == "demo":
        reset_demo_db()


class APIClient:
    """Wrapper around requests.Session providing REST verbs and latency validation."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AuraMart-STQA-API-Tester/1.0",
        })

    def get(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.session.get(url, timeout=5, **kwargs)

    def post(self, path: str, json: Any = None, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.session.post(url, json=json, timeout=5, **kwargs)

    def put(self, path: str, json: Any = None, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.session.put(url, json=json, timeout=5, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.session.delete(url, timeout=5, **kwargs)

    @staticmethod
    def assert_latency(response: requests.Response, max_ms: float = 1000.0):
        """Asserts that the HTTP round-trip latency is within expected threshold."""
        duration_ms = response.elapsed.total_seconds() * 1000.0
        assert duration_ms <= max_ms, (
            f"API response latency exceeded threshold: {duration_ms:.2f}ms > {max_ms}ms"
        )


@pytest.fixture
def api(api_base_url) -> APIClient:
    """Provides a pre-configured APIClient instance."""
    return APIClient(api_base_url)
