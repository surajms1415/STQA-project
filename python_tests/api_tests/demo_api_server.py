"""
AuraMart Sample REST API Server for STQA Demonstration.
Lightweight standard library HTTP server implementing RESTful endpoints
(GET, POST, PUT, DELETE), JSON payload validation, HTTP status codes, and error responses.
"""

import copy
import json
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

DEMO_PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": "p1",
        "name": "Aura Wireless Headphones",
        "category": "Audio",
        "price": 99.99,
        "stock": 8,
        "description": "Active noise-cancelling over-ear headphones with 40h battery life.",
    },
    {
        "id": "p2",
        "name": "Pro Mechanical Keyboard",
        "category": "Electronics",
        "price": 129.50,
        "stock": 5,
        "description": "RGB mechanical keyboard with tactile brown switches.",
    },
    {
        "id": "p3",
        "name": "Smart Fitness Watch",
        "category": "Wearables",
        "price": 179.00,
        "stock": 4,
        "description": "AMOLED tracker with heart-rate and GPS.",
    },
]


class DemoRESTHandler(BaseHTTPRequestHandler):
    """HTTP request handler implementing full RESTful specification for API demonstration."""

    # Thread-shared database state for test execution
    products_db = copy.deepcopy(DEMO_PRODUCTS)
    orders_db: List[Dict[str, Any]] = []

    def log_message(self, format, *args):
        # Silence default stderr logging during test runs
        pass

    def _send_json(self, status_code: int, data: Any):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("X-Powered-By", "AuraMart-STQA-Demo-API")
        self.end_headers()
        self.wfile.write(response_bytes)

    def _read_json_body(self) -> Optional[Any]:
        content_len_header = self.headers.get("Content-Length")
        if not content_len_header:
            return None
        try:
            length = int(content_len_header)
            raw = self.rfile.read(length).decode("utf-8")
            if not raw.strip():
                return None
            return json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("Malformed JSON payload")
        except Exception:
            return None

    # --------------------------------------------------------------------------
    # GET Handlers
    # --------------------------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Health Check
        if path == "/api/v1/health":
            self._send_json(200, {
                "status": "ok",
                "service": "AuraMart Demo REST API",
                "timestamp": int(time.time()),
            })
            return

        # List Products (with optional query filter)
        if path == "/api/v1/products":
            items = list(self.products_db)
            if "category" in query:
                cat = query["category"][0].lower()
                items = [p for p in items if p["category"].lower() == cat]
            if "search" in query:
                q = query["search"][0].lower()
                items = [p for p in items if q in p["name"].lower()]

            self._send_json(200, {
                "success": True,
                "count": len(items),
                "data": items,
            })
            return

        # Single Product Detail
        match_prod = re.match(r"^/api/v1/products/([^/]+)$", path)
        if match_prod:
            pid = match_prod.group(1)
            found = next((p for p in self.products_db if p["id"] == pid), None)
            if not found:
                self._send_json(404, {
                    "success": False,
                    "error": f"Product with id '{pid}' not found",
                })
                return
            self._send_json(200, {
                "success": True,
                "data": found,
            })
            return

        # List Orders
        if path == "/api/v1/orders":
            self._send_json(200, {
                "success": True,
                "count": len(self.orders_db),
                "data": self.orders_db,
            })
            return

        # Not Found
        self._send_json(404, {
            "success": False,
            "error": "Endpoint not found",
            "path": path,
        })

    # --------------------------------------------------------------------------
    # POST Handlers
    # --------------------------------------------------------------------------
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_json_body()
        except ValueError as e:
            self._send_json(400, {"success": False, "error": str(e)})
            return

        # Create Product
        if path == "/api/v1/products":
            if not body or not isinstance(body, dict):
                self._send_json(400, {"success": False, "error": "Request body must be a JSON object"})
                return

            errors = {}
            name = body.get("name")
            if not name or not isinstance(name, str) or len(name.strip()) < 3:
                errors["name"] = "Field 'name' is required and must have at least 3 characters"

            price = body.get("price")
            if price is None or not isinstance(price, (int, float)) or price <= 0:
                errors["price"] = "Field 'price' is required and must be a positive number"

            stock = body.get("stock")
            if stock is None or not isinstance(stock, int) or stock < 0:
                errors["stock"] = "Field 'stock' is required and must be a non-negative integer"

            category = body.get("category")
            if not category or not isinstance(category, str):
                errors["category"] = "Field 'category' is required"

            if errors:
                self._send_json(400, {"success": False, "errors": errors})
                return

            new_id = f"p{len(self.products_db) + 1}_{int(time.time() * 1000) % 10000}"
            new_item = {
                "id": new_id,
                "name": name.strip(),
                "price": round(float(price), 2),
                "stock": stock,
                "category": category.strip(),
                "description": body.get("description", ""),
            }
            self.products_db.append(new_item)
            self._send_json(201, {
                "success": True,
                "message": "Product created successfully",
                "data": new_item,
            })
            return

        # Place Order
        if path == "/api/v1/orders":
            if not body or not isinstance(body, dict):
                self._send_json(400, {"success": False, "error": "Request body must be a JSON object"})
                return

            items = body.get("items")
            if not items or not isinstance(items, list) or len(items) == 0:
                self._send_json(400, {"success": False, "error": "Order must contain at least one item"})
                return

            customer = body.get("customer")
            if not customer or not isinstance(customer, dict) or not customer.get("email"):
                self._send_json(400, {"success": False, "error": "Valid customer information with email is required"})
                return

            order_id = f"ORD-{int(time.time() * 1000) % 1000000:06d}"
            order_record = {
                "orderId": order_id,
                "customer": customer,
                "items": items,
                "total": body.get("total", 0.0),
                "status": "Confirmed",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            self.orders_db.append(order_record)
            self._send_json(201, {
                "success": True,
                "orderId": order_id,
                "data": order_record,
            })
            return

        self._send_json(404, {"success": False, "error": "Endpoint not found"})

    # --------------------------------------------------------------------------
    # PUT Handlers
    # --------------------------------------------------------------------------
    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_json_body()
        except ValueError as e:
            self._send_json(400, {"success": False, "error": str(e)})
            return

        match_prod = re.match(r"^/api/v1/products/([^/]+)$", path)
        if match_prod:
            pid = match_prod.group(1)
            found = next((p for p in self.products_db if p["id"] == pid), None)
            if not found:
                self._send_json(404, {"success": False, "error": f"Product with id '{pid}' not found"})
                return

            if not body or not isinstance(body, dict):
                self._send_json(400, {"success": False, "error": "Request body must be a JSON object"})
                return

            # Apply valid updates
            if "price" in body:
                if not isinstance(body["price"], (int, float)) or body["price"] <= 0:
                    self._send_json(400, {"success": False, "error": "Price must be a positive number"})
                    return
                found["price"] = round(float(body["price"]), 2)

            if "stock" in body:
                if not isinstance(body["stock"], int) or body["stock"] < 0:
                    self._send_json(400, {"success": False, "error": "Stock must be a non-negative integer"})
                    return
                found["stock"] = body["stock"]

            if "name" in body:
                if not isinstance(body["name"], str) or len(body["name"].strip()) < 3:
                    self._send_json(400, {"success": False, "error": "Name must be at least 3 characters"})
                    return
                found["name"] = body["name"].strip()

            self._send_json(200, {
                "success": True,
                "message": "Product updated successfully",
                "data": found,
            })
            return

        self._send_json(404, {"success": False, "error": "Endpoint not found"})

    # --------------------------------------------------------------------------
    # DELETE Handlers
    # --------------------------------------------------------------------------
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        match_prod = re.match(r"^/api/v1/products/([^/]+)$", path)
        if match_prod:
            pid = match_prod.group(1)
            idx = next((i for i, p in enumerate(self.products_db) if p["id"] == pid), None)
            if idx is None:
                self._send_json(404, {"success": False, "error": f"Product with id '{pid}' not found"})
                return

            deleted_item = self.products_db.pop(idx)
            self._send_json(200, {
                "success": True,
                "message": f"Product '{deleted_item['name']}' deleted successfully",
                "deletedId": pid,
            })
            return

        self._send_json(404, {"success": False, "error": "Endpoint not found"})


def reset_demo_db():
    """Reset in-memory databases to initial baseline state."""
    DemoRESTHandler.products_db = copy.deepcopy(DEMO_PRODUCTS)
    DemoRESTHandler.orders_db = []
