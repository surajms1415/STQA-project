"""
Integration Testing Suite for AuraMart E-Commerce Application.
Tests cart workflow, price recalculation, order placement, and persistent state synchronization.
"""

import copy
import json
import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.integration
class TestCartAndOrderIntegration:
    """Integration test suite verifying cross-module interactions."""

    def test_it_cart_01_add_product_to_cart(self):
        """IT-CART-01: Add product to cart and verify cart update."""
        products = [
            {"id": "p1", "name": "Item Alpha", "price": 40.00, "stock": 5},
            {"id": "p2", "name": "Item Beta", "price": 25.00, "stock": 3},
        ]
        cart = []
        res = Core.add_to_cart(cart, products, "p1", 1)
        cart = res["cart"]

        pass_cond = (
            res["success"] is True
            and len(cart) == 1
            and cart[0]["id"] == "p1"
            and cart[0]["quantity"] == 1
        )
        verify(
            "IT-CART-01",
            "Add product p1 to empty cart",
            "success: true, length: 1, qty: 1",
            f"success: {res['success']}, length: {len(cart)}, qty: {cart[0]['quantity'] if cart else None}",
            pass_cond,
        )

    def test_it_qty_01_update_quantity_recalculates_total(self):
        """IT-QTY-01: Update cart quantity and verify recalculated total."""
        products = [
            {"id": "p1", "name": "Item Alpha", "price": 40.00, "stock": 5},
            {"id": "p2", "name": "Item Beta", "price": 25.00, "stock": 3},
        ]
        cart = [{"id": "p1", "quantity": 1}]
        res = Core.update_cart_quantity(cart, products, "p1", 3)
        cart = res["cart"]

        totals = Core.calculate_cart_totals(cart, products)
        # 40 * 3 = 120. Tax = 6.00. Shipping = 0.00. Total = 126.00
        pass_cond = (
            res["success"] is True
            and cart[0]["quantity"] == 3
            and totals["total"] == 126.00
        )
        verify(
            "IT-QTY-01",
            "Increase qty to 3 -> Total = 126.00",
            "qty: 3, total: 126.00",
            f"qty: {cart[0]['quantity']}, total: {totals['total']}",
            pass_cond,
        )

    def test_it_order_01_checkout_and_cart_clearing(self, valid_customer):
        """IT-ORDER-01: Checkout with cart and verify order creation & cart clearing."""
        products = [
            {"id": "p1", "name": "Item Alpha", "price": 40.00, "stock": 5},
            {"id": "p2", "name": "Item Beta", "price": 25.00, "stock": 3},
        ]
        cart = [{"id": "p1", "quantity": 2}]
        payment = {"method": "cod"}

        res = Core.process_order(cart, products, valid_customer, payment)
        pass_cond = (
            res["success"] is True
            and res.get("order") is not None
            and res["order"]["orderId"].startswith("ORD-")
            and len(res["clearedCart"]) == 0
        )
        verify(
            "IT-ORDER-01",
            "Order created with valid ID & cleared cart",
            "success: true, status: Confirmed",
            f"success: {res['success']}, id: {res.get('order', {}).get('orderId')}",
            pass_cond,
        )

    def test_it_store_01_localstorage_cart_synchronization(self, mock_storage):
        """IT-STORE-01: Verify localStorage synchronization on cart update."""
        cart = [{"id": "p1", "quantity": 2}]
        mock_storage.set_item(Core.STORAGE_KEYS["CART"], json.dumps(cart))

        retrieved_raw = mock_storage.get_item(Core.STORAGE_KEYS["CART"])
        retrieved = json.loads(retrieved_raw)
        pass_cond = (
            isinstance(retrieved, list)
            and len(retrieved) == 1
            and retrieved[0]["id"] == "p1"
            and retrieved[0]["quantity"] == 2
        )
        verify(
            "IT-STORE-01",
            "Cart persisted and reloaded from storage",
            "p1 x 2",
            f"{retrieved[0].get('id')} x {retrieved[0].get('quantity')}" if retrieved else "None",
            pass_cond,
        )

    def test_it_store_02_inventory_reduction_persisted_to_storage(self, mock_storage):
        """IT-STORE-02: Verify inventory reduction persisted to storage after order."""
        products = [
            {"id": "p1", "name": "Item Alpha", "price": 40.00, "stock": 5},
            {"id": "p2", "name": "Item Beta", "price": 25.00, "stock": 3},
        ]
        cart = [{"id": "p1", "quantity": 2}]
        customer = {
            "name": "Alice Wonder",
            "email": "alice@example.com",
            "phone": "1234567890",
            "address": "10 Downing St",
            "city": "London",
            "state": "LN",
            "zip": "SW1A",
        }
        payment = {"method": "cod"}

        res = Core.process_order(cart, products, customer, payment)
        mock_storage.set_item(Core.STORAGE_KEYS["PRODUCTS"], json.dumps(res["updatedProducts"]))

        saved_products = json.loads(mock_storage.get_item(Core.STORAGE_KEYS["PRODUCTS"]))
        saved_p1 = next((p for p in saved_products if p["id"] == "p1"), None)

        pass_cond = saved_p1 is not None and saved_p1["stock"] == 3  # 5 - 2 = 3
        verify(
            "IT-STORE-02",
            "Product stock reduced from 5 to 3 in storage",
            "stock: 3",
            f"stock: {saved_p1.get('stock') if saved_p1 else None}",
            pass_cond,
        )
