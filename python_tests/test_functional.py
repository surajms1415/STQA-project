"""
Functional Testing Suite for AuraMart E-Commerce Application.
Validates end-to-end user journeys: catalog search, cart operations, checkout processing, and stock updates.
"""

import copy
import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.functional
class TestFunctionalScenarios:
    """End-to-end and functional user journey test suite."""

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

    def test_ft_e2e_01_full_purchasing_workflow(self, initial_products):
        """FT-E2E-01: End-to-End full purchasing workflow."""
        # 1. Catalog & Initial State
        products = copy.deepcopy(initial_products)
        cart = []

        # 2. Search product
        search_results = Core.filter_and_sort_products(products, {"search": "Mouse"})
        selected_product = search_results[0]  # p4
        initial_stock = selected_product["stock"]

        # 3. Add to Cart
        add_res = Core.add_to_cart(cart, products, selected_product["id"], 2)
        cart = add_res["cart"]

        # 4. Validate Cart Totals
        totals = Core.calculate_cart_totals(cart, products)

        # 5. Customer Checkout
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

        # 6. Verify End State
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
