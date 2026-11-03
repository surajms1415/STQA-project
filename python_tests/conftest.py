"""
Shared Pytest Fixtures and Diagnostic Hooks for AuraMart STQA Suite.
"""

import copy
import json
import pytest
from typing import Any, Dict, List

from python_tests import stqa_core as Core


class MockLocalStorage:
    """Mock localStorage for browser-equivalent storage testing in Python."""

    def __init__(self):
        self.store: Dict[str, str] = {}

    def get_item(self, key: str) -> Any:
        return self.store.get(key, None)

    def set_item(self, key: str, value: Any) -> None:
        self.store[key] = str(value)

    def remove_item(self, key: str) -> None:
        if key in self.store:
            del self.store[key]

    def clear(self) -> None:
        self.store.clear()

    # camelCase aliases matching JavaScript localStorage API
    getItem = get_item
    setItem = set_item
    removeItem = remove_item


def verify(test_id: str, description: str, expected: Any, actual: Any, condition: bool) -> None:
    """
    Standard verification helper conforming to project requirements:
    Displays test case ID, description, expected result, actual result, and PASS/FAIL.
    """
    pass_status = bool(condition)
    status_str = "\033[32mPASS\033[0m" if pass_status else "\033[31mFAIL\033[0m"
    print(f"\n  [{test_id}] {description}")
    print(f"     Expected: {expected}")
    print(f"     Actual:   {actual} -> {status_str}")
    assert pass_status, f"Test {test_id} failed: expected '{expected}', got '{actual}'"


@pytest.fixture
def mock_storage() -> MockLocalStorage:
    """Provides a clean in-memory localStorage instance."""
    return MockLocalStorage()


@pytest.fixture
def initial_products() -> List[Dict[str, Any]]:
    """Fresh copy of the baseline catalog products."""
    return copy.deepcopy(Core.INITIAL_PRODUCTS)


@pytest.fixture
def sample_products() -> List[Dict[str, Any]]:
    """Standardized multi-tier pricing products for cart and tax testing."""
    return [
        {"id": "p1", "name": "Item Alpha", "price": 100.00, "stock": 10, "category": "Audio"},
        {"id": "p2", "name": "Item Beta", "price": 20.00, "stock": 10, "category": "Electronics"},
    ]


@pytest.fixture
def empty_cart() -> List[Dict[str, Any]]:
    """Clean empty cart instance."""
    return []


@pytest.fixture
def valid_customer() -> Dict[str, str]:
    """Valid customer address and contact data."""
    return {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "9876543210",
        "address": "742 Evergreen Terrace",
        "city": "Springfield",
        "state": "IL",
        "zip": "62704",
    }


@pytest.fixture
def invalid_customer() -> Dict[str, str]:
    """Malformed customer input failing multiple validation rules."""
    return {
        "name": "X",
        "email": "bad-email-address",
        "phone": "12",
        "address": "St",
        "city": "A",
        "state": "",
        "zip": "1",
    }


@pytest.fixture
def valid_card_payment() -> Dict[str, str]:
    """Valid credit/debit card details."""
    return {
        "method": "card",
        "cardNum": "4111222233334444",
        "cardExpiry": "12/29",
        "cardCvv": "789",
    }


@pytest.fixture
def invalid_card_payment() -> Dict[str, str]:
    """Malformed card details (too short, expired, short CVV)."""
    return {
        "method": "card",
        "cardNum": "123",
        "cardExpiry": "01/20",
        "cardCvv": "9",
    }


@pytest.fixture
def defect_manager() -> Core.DefectManager:
    """Instance of the Defect Lifecycle and Regression Manager."""
    return Core.DefectManager()
