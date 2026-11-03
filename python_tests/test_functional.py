"""
Functional Testing Suite for AuraMart E-Commerce Application.
Validates all major e-commerce features according to requirements:
1. Product catalog browsing, searching, and category filtering.
2. Sorting by price, name, and stock.
3. In-stock availability filtering.
4. Cart drawer operations (add, remove, quantity update).
5. Customer checkout and payment methods (Card, UPI, COD).
6. Complete End-to-End order fulfillment.
"""

import copy
import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.functional
class TestFunctionalCatalogAndSearch:
    """Functional tests for product search, categorization, and sorting."""

    def test_ft_srch_01_search_matches_query(self, initial_products):
        """FT-SRCH-01: Search returns relevant products matching query string."""
        results = Core.filter_and_sort_products(initial_products, {"search": "Headphones"})
        pass_cond = len(results) > 0 and any("Headphones" in p["name"] for p in results)
        verify(
            "FT-SRCH-01",
            "Search 'Headphones' finds matching product",
            "found >= 1 item",
            f"found {len(results)} items",
            pass_cond,
        )

    def test_ft_srch_02_search_nonexistent_query(self, initial_products):
        """FT-SRCH-02: Search for nonexistent query returns empty array."""
        results = Core.filter_and_sort_products(initial_products, {"search": "xyz987nonexistent"})
        pass_cond = len(results) == 0
        verify(
            "FT-SRCH-02",
            "Search nonexistent item returns 0 items",
            "0 items",
            f"{len(results)} items",
            pass_cond,
        )

    @pytest.mark.parametrize(
        "category_name, min_expected",
        [
            ("Audio", 2),
            ("Electronics", 3),
            ("Wearables", 1),
            ("Home", 2),
            ("Accessories", 2),
        ],
    )
    def test_ft_filter_by_category(self, initial_products, category_name, min_expected):
        """FT-CAT-01: Category filter returns only products belonging to that category."""
        filtered = Core.filter_and_sort_products(initial_products, {"category": category_name})
        assert len(filtered) >= min_expected
        assert all(p["category"] == category_name for p in filtered)

    def test_ft_in_stock_only_filter(self, initial_products):
        """FT-FLTR-01: In-stock only filter eliminates out-of-stock items (stock == 0)."""
        filtered = Core.filter_and_sort_products(initial_products, {"inStockOnly": True})
        assert all(p["stock"] > 0 for p in filtered)
        assert not any(p["id"] == "p10" for p in filtered)  # p10 is intentionally out of stock

    @pytest.mark.parametrize(
        "sort_key, validator",
        [
            ("price-asc", lambda res: all(res[i]["price"] <= res[i + 1]["price"] for i in range(len(res) - 1))),
            ("price-desc", lambda res: all(res[i]["price"] >= res[i + 1]["price"] for i in range(len(res) - 1))),
            ("name-asc", lambda res: all(res[i]["name"].lower() <= res[i + 1]["name"].lower() for i in range(len(res) - 1))),
            ("stock-desc", lambda res: all(res[i]["stock"] >= res[i + 1]["stock"] for i in range(len(res) - 1))),
        ],
    )
    def test_ft_sort_catalog_options(self, initial_products, sort_key, validator):
        """FT-SORT-01: Catalog sorting arranges items correctly by price, name, or stock."""
        sorted_res = Core.filter_and_sort_products(initial_products, {"sortBy": sort_key})
        assert len(sorted_res) == len(initial_products)
        assert validator(sorted_res)


@pytest.mark.functional
class TestFunctionalCartAndOrderWorkflow:
    """Functional tests for cart operations and end-to-end checkout."""

    def test_ft_cart_01_add_to_cart_updates_count(self, initial_products):
        """FT-CART-01: Functional Add to Cart updates item and count correctly."""
        cart = []
        item_to_add = initial_products[0]  # p1
        res = Core.add_to_cart(cart, initial_products, item_to_add["id"], 2)
        cart = res["cart"]

        added_item = next((i for i in cart if i["id"] == item_to_add["id"]), None)
        pass_cond = res["success"] is True and added_item is not None and added_item["quantity"] == 2
        verify(
            "FT-CART-01",
            "Add 2 units of product to cart",
            "qty: 2 in cart",
            f"qty: {added_item['quantity'] if added_item else None}",
            pass_cond,
        )

    def test_ft_cart_02_remove_from_cart_deletes_item(self):
        """FT-CART-02: Functional Remove from Cart completely deletes item."""
        cart = [{"id": "p1", "quantity": 2}, {"id": "p2", "quantity": 1}]
        res = Core.remove_from_cart(cart, "p1")
        cart = res["cart"]

        pass_cond = (
            res["success"] is True
            and len(cart) == 1
            and not any(i["id"] == "p1" for i in cart)
        )
        verify(
            "FT-CART-02",
            "Remove p1 from cart",
            "p1 removed, length: 1",
            f"length: {len(cart)}, hasP1: {any(i['id'] == 'p1' for i in cart)}",
            pass_cond,
        )

    def test_ft_e2e_01_full_purchasing_workflow_upi(self, initial_products):
        """FT-E2E-01: End-to-End full purchasing workflow with UPI payment."""
        products = copy.deepcopy(initial_products)
        cart = []

        # 1. Search product
        search_results = Core.filter_and_sort_products(products, {"search": "Mouse"})
        selected_product = search_results[0]  # p4
        initial_stock = selected_product["stock"]

        # 2. Add to Cart
        add_res = Core.add_to_cart(cart, products, selected_product["id"], 2)
        cart = add_res["cart"]

        # 3. Validate Cart Totals
        totals = Core.calculate_cart_totals(cart, products)

        # 4. Customer Checkout
        customer = {
            "name": "Alexander Graham",
            "email": "alex@telecom.org",
            "phone": "8005550199",
            "address": "109 Court St",
            "city": "Boston",
            "state": "MA",
            "zip": "02108",
        }
        payment = {"method": "upi", "upiId": "alex@okaxis"}

        order_res = Core.process_order(cart, products, customer, payment)

        # 5. Verify End State
        order_created = order_res["success"] is True and order_res["order"]["total"] == totals["total"]
        updated_p = next(p for p in order_res["updatedProducts"] if p["id"] == selected_product["id"])
        stock_reduced = updated_p["stock"] == (initial_stock - 2)
        cart_emptied = len(order_res["clearedCart"]) == 0

        pass_cond = order_created and stock_reduced and cart_emptied
        verify(
            "FT-E2E-01",
            "End-to-End: Search -> Add -> Totals -> Checkout -> Stock Decrement -> Cart Clear",
            "All steps succeed",
            f"order: {order_res['success']}, stockReduced: {stock_reduced}, cartCleared: {cart_emptied}",
            pass_cond,
        )

    def test_ft_e2e_02_full_purchasing_workflow_card(self, initial_products, valid_customer, valid_card_payment):
        """FT-E2E-02: End-to-End full purchasing workflow with Credit/Debit card payment."""
        products = copy.deepcopy(initial_products)
        cart = []

        # Add p1 (Headphones: $99.99, stock: 8)
        add_res = Core.add_to_cart(cart, products, "p1", 1)
        cart = add_res["cart"]

        # Process order
        order_res = Core.process_order(cart, products, valid_customer, valid_card_payment)
        assert order_res["success"] is True
        assert order_res["order"]["status"] == "Confirmed"
        assert order_res["order"]["paymentMethod"] == "Credit/Debit Card"
        assert order_res["order"]["subtotal"] == 99.99
        assert order_res["order"]["shipping"] == 0.0  # Free shipping >= $50
