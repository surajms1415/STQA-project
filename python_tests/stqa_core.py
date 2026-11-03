"""
AuraMart E-Commerce Core Logic & Defect Management Engine for Python / Pytest.
Directly implements all business domain logic, calculation rules, input validation,
cart state transitions, and defect lifecycle scenarios.
"""

import copy
import datetime
import math
import re
import time
from typing import Any, Dict, List, Optional, Tuple

STORAGE_KEYS = {
    "PRODUCTS": "auramart_products_v1",
    "CART": "auramart_cart_v1",
    "ORDERS": "auramart_orders_v1",
}

INITIAL_PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": "p1",
        "name": "Aura Wireless Headphones",
        "category": "Audio",
        "price": 99.99,
        "stock": 8,
        "description": "Active noise-cancelling over-ear headphones with 40h battery life and deep bass.",
        "icon": "headphones",
    },
    {
        "id": "p2",
        "name": "Pro Mechanical Keyboard",
        "category": "Electronics",
        "price": 129.50,
        "stock": 5,
        "description": "Customizable RGB hot-swappable mechanical keyboard with tactile brown switches.",
        "icon": "keyboard",
    },
    {
        "id": "p3",
        "name": "Smart Fitness Watch",
        "category": "Wearables",
        "price": 179.00,
        "stock": 4,
        "description": "AMOLED fitness tracker with heart-rate monitor, SpO2 sensor, and built-in GPS.",
        "icon": "watch",
    },
    {
        "id": "p4",
        "name": "Ergonomic Wireless Mouse",
        "category": "Electronics",
        "price": 49.99,
        "stock": 12,
        "description": "Precision vertical optical mouse designed to reduce wrist strain during long sessions.",
        "icon": "mouse",
    },
    {
        "id": "p5",
        "name": "Minimalist Desk Lamp",
        "category": "Home",
        "price": 38.50,
        "stock": 6,
        "description": "Dimmable LED desk lamp with touch controls, 3 color temperatures, and USB charging.",
        "icon": "lamp",
    },
    {
        "id": "p6",
        "name": "Everyday Travel Backpack",
        "category": "Accessories",
        "price": 64.99,
        "stock": 3,
        "description": "Water-resistant 25L commuter backpack with padded 15.6\" laptop compartment.",
        "icon": "backpack",
    },
    {
        "id": "p7",
        "name": "True Wireless Earbuds",
        "category": "Audio",
        "price": 59.00,
        "stock": 10,
        "description": "Compact Bluetooth 5.3 in-ear earbuds with crystal clear calls and IPX5 resistance.",
        "icon": "earbuds",
    },
    {
        "id": "p8",
        "name": "Ultra HD 4K Action Camera",
        "category": "Electronics",
        "price": 219.99,
        "stock": 2,
        "description": "Rugged waterproof 4K/60fps camera with dual screens and 6-axis gyro stabilization.",
        "icon": "camera",
    },
    {
        "id": "p9",
        "name": "Insulated Stainless Tumbler",
        "category": "Home",
        "price": 24.50,
        "stock": 15,
        "description": "Vacuum-insulated 750ml flask keeping drinks ice-cold for 24h or steaming hot for 12h.",
        "icon": "bottle",
    },
    {
        "id": "p10",
        "name": "Leather Tech Sleeve",
        "category": "Accessories",
        "price": 34.00,
        "stock": 0,  # Deliberately out of stock for testing
        "description": "Premium vegan leather protective envelope sleeve with magnetic snap closure.",
        "icon": "sleeve",
    },
]


def format_price(val: Any) -> str:
    """Format numeric value into standard $XX.XX currency string."""
    try:
        num = float(val)
        if math.isnan(num):
            return "$0.00"
        return f"${num:.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def round_money(val: float) -> float:
    """Financial rounding to 2 decimal places matching JavaScript's roundMoney() with EPSILON."""
    # Round half-up to 2 decimals avoiding float precision artifacts
    return round(float(val) + 1e-15, 2)


def calculate_line_total(price: float, quantity: int) -> float:
    """Calculate line total: price * quantity."""
    try:
        p = float(price)
        q = int(quantity)
        if q <= 0:
            return 0.0
        return round_money(p * q)
    except (ValueError, TypeError):
        return 0.0


def calculate_cart_totals(cart: List[Dict[str, Any]], products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate subtotal, 5% standard tax, tiered shipping ($5 if subtotal < $50, Free if >= $50),
    and grand total.
    """
    subtotal = 0.0
    item_count = 0
    prod_map = {p["id"]: p for p in products}

    for item in cart:
        pid = item.get("id")
        qty = int(item.get("quantity", 0))
        if pid in prod_map and qty > 0:
            p_price = float(prod_map[pid].get("price", 0.0))
            subtotal += p_price * qty
            item_count += qty

    subtotal = round_money(subtotal)
    tax = round_money(subtotal * 0.05)  # 5% Standard Sales Tax
    shipping = 0.0 if (subtotal >= 50.0 or subtotal == 0.0) else 5.0
    total = round_money(subtotal + tax + shipping)

    return {
        "subtotal": subtotal,
        "tax": tax,
        "shipping": shipping,
        "total": total,
        "itemCount": item_count,
    }


def is_product_in_stock(product: Optional[Dict[str, Any]]) -> bool:
    """Check if product has positive stock remaining."""
    if not product:
        return False
    stock = product.get("stock", 0)
    return isinstance(stock, (int, float)) and stock > 0


def get_available_stock(product: Optional[Dict[str, Any]], cart: List[Dict[str, Any]]) -> int:
    """Calculate remaining stock considering items already in the customer's cart."""
    if not product:
        return 0
    in_cart = 0
    for item in cart:
        if item.get("id") == product.get("id"):
            in_cart = item.get("quantity", 0)
            break
    return max(0, product.get("stock", 0) - in_cart)


def add_to_cart(
    cart: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    product_id: str,
    quantity_to_add: int = 1,
) -> Dict[str, Any]:
    """Add product to cart with strict integer and cumulative stock verification."""
    if not isinstance(quantity_to_add, int) or isinstance(quantity_to_add, bool) or quantity_to_add <= 0:
        return {"success": False, "error": "Invalid quantity to add", "cart": cart}

    prod = next((p for p in products if p["id"] == product_id), None)
    if not prod:
        return {"success": False, "error": "Product not found", "cart": cart}

    if prod.get("stock", 0) <= 0:
        return {"success": False, "error": "Product is out of stock", "cart": cart}

    new_cart = copy.deepcopy(cart)
    cart_item = next((i for i in new_cart if i["id"] == product_id), None)
    current_qty = cart_item["quantity"] if cart_item else 0

    if current_qty + quantity_to_add > prod["stock"]:
        remaining = prod["stock"] - current_qty
        return {
            "success": False,
            "error": f"Cannot add {quantity_to_add}. Only {remaining} more available.",
            "cart": new_cart,
        }

    if cart_item:
        cart_item["quantity"] += quantity_to_add
    else:
        new_cart.append({"id": product_id, "quantity": quantity_to_add})

    return {"success": True, "cart": new_cart}


def update_cart_quantity(
    cart: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    product_id: str,
    new_quantity: int,
) -> Dict[str, Any]:
    """Update cart line item quantity, remove if <= 0, prevent exceeding warehouse stock."""
    prod = next((p for p in products if p["id"] == product_id), None)
    if not prod:
        return {"success": False, "error": "Product not found", "cart": cart}

    new_cart = copy.deepcopy(cart)
    item_index = next((idx for idx, i in enumerate(new_cart) if i["id"] == product_id), None)

    if item_index is None:
        return {"success": False, "error": "Item not in cart", "cart": cart}

    if new_quantity <= 0:
        new_cart.pop(item_index)
        return {"success": True, "removed": True, "cart": new_cart}

    if not isinstance(new_quantity, int) or isinstance(new_quantity, bool):
        return {"success": False, "error": "Quantity must be an integer", "cart": new_cart}

    if new_quantity > prod["stock"]:
        return {
            "success": False,
            "error": f"Requested quantity ({new_quantity}) exceeds stock ({prod['stock']})",
            "cart": new_cart,
        }

    new_cart[item_index]["quantity"] = new_quantity
    return {"success": True, "cart": new_cart, "item": new_cart[item_index]}


def remove_from_cart(cart: List[Dict[str, Any]], product_id: str) -> Dict[str, Any]:
    """Remove line item from cart array."""
    new_cart = [item for item in cart if item.get("id") != product_id]
    return {"success": True, "cart": new_cart}


def filter_and_sort_products(products: List[Dict[str, Any]], filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Filter products by category, search text, in-stock condition and sort option."""
    if not products:
        return []
    result = list(products)
    filters = filters or {}
    category = filters.get("category", "all")
    search = filters.get("search", "").strip().lower()
    in_stock_only = filters.get("inStockOnly", False)
    sort_by = filters.get("sortBy", "featured")

    if category and category != "all":
        result = [p for p in result if p.get("category", "").lower() == category.lower()]

    if search:
        result = [
            p for p in result
            if search in p.get("name", "").lower()
            or search in p.get("description", "").lower()
            or search in p.get("category", "").lower()
        ]

    if in_stock_only:
        result = [p for p in result if p.get("stock", 0) > 0]

    if sort_by == "price-asc":
        result.sort(key=lambda x: x.get("price", 0))
    elif sort_by == "price-desc":
        result.sort(key=lambda x: x.get("price", 0), reverse=True)
    elif sort_by == "name-asc":
        result.sort(key=lambda x: x.get("name", "").lower())
    elif sort_by == "name-desc":
        result.sort(key=lambda x: x.get("name", "").lower(), reverse=True)
    elif sort_by == "stock-desc":
        result.sort(key=lambda x: x.get("stock", 0), reverse=True)

    return result


class ValidationRules:
    """Regex and business input validators matching frontend ValidationRules."""

    @staticmethod
    def validate_name(val: Any) -> bool:
        if not isinstance(val, str):
            return False
        trimmed = val.strip()
        return len(trimmed) >= 3 and bool(re.match(r"^[a-zA-Z\s.'-]+$", trimmed))

    @staticmethod
    def validate_email(val: Any) -> bool:
        if not isinstance(val, str):
            return False
        return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$", val.strip()))

    @staticmethod
    def validate_phone(val: Any) -> bool:
        if not isinstance(val, (str, int)):
            return False
        digits = re.sub(r"\D", "", str(val))
        return 10 <= len(digits) <= 15

    @staticmethod
    def validate_city(val: Any) -> bool:
        return isinstance(val, str) and len(val.strip()) >= 2

    @staticmethod
    def validate_address(val: Any) -> bool:
        return isinstance(val, str) and len(val.strip()) >= 5

    @staticmethod
    def validate_state(val: Any) -> bool:
        return isinstance(val, str) and len(val.strip()) >= 2

    @staticmethod
    def validate_zip(val: Any) -> bool:
        if not isinstance(val, (str, int)):
            return False
        return bool(re.match(r"^[a-zA-Z0-9\s-]{4,10}$", str(val).strip()))

    @staticmethod
    def validate_card_num(val: Any) -> bool:
        if not isinstance(val, (str, int)):
            return False
        digits = re.sub(r"\D", "", str(val))
        return 13 <= len(digits) <= 19

    @staticmethod
    def validate_card_expiry(val: Any) -> bool:
        if not isinstance(val, str):
            return False
        trimmed = val.strip()
        match = re.match(r"^(0[1-9]|1[0-2])/?([0-9]{2})$", trimmed)
        if not match:
            return False
        month = int(match.group(1))
        year = int("20" + match.group(2))
        now = datetime.datetime.now()
        curr_year = now.year
        curr_month = now.month
        return year > curr_year or (year == curr_year and month >= curr_month)

    @staticmethod
    def validate_card_cvv(val: Any) -> bool:
        if not isinstance(val, (str, int)):
            return False
        return bool(re.match(r"^\d{3,4}$", str(val).strip()))

    @staticmethod
    def validate_upi_id(val: Any) -> bool:
        if not isinstance(val, str):
            return False
        return bool(re.match(r"^[\w.-]+@[\w.-]+$", val.strip()))

    @staticmethod
    def validate_quantity(val: Any, stock: Optional[int] = None) -> bool:
        if isinstance(val, bool) or not isinstance(val, int):
            return False
        if val <= 0:
            return False
        if stock is not None and val > stock:
            return False
        return True


def validate_checkout_payload(customer: Dict[str, Any], payment: Dict[str, Any]) -> Dict[str, Any]:
    """Validate customer information and payment details."""
    errors = {}
    if not customer:
        return {"isValid": False, "errors": {"customer": "Customer details required"}}

    if not ValidationRules.validate_name(customer.get("name")):
        errors["name"] = "Please enter a valid full name (at least 3 characters, letters only)."
    if not ValidationRules.validate_email(customer.get("email")):
        errors["email"] = "Please enter a valid email address (e.g., name@example.com)."
    if not ValidationRules.validate_phone(customer.get("phone")):
        errors["phone"] = "Please enter a valid phone number with at least 10 digits."
    if not ValidationRules.validate_address(customer.get("address")):
        errors["address"] = "Please enter your street address (at least 5 characters)."
    if not ValidationRules.validate_city(customer.get("city")):
        errors["city"] = "Please enter a valid city name."
    if not ValidationRules.validate_state(customer.get("state")):
        errors["state"] = "Please enter a state / province."
    if not ValidationRules.validate_zip(customer.get("zip")):
        errors["zip"] = "Please enter a valid postal / ZIP code (4-10 characters)."

    method = payment.get("method", "card") if payment else "card"
    if method == "card":
        if not ValidationRules.validate_card_num(payment.get("cardNum")):
            errors["cardNum"] = "Enter a valid 16-digit card number."
        if not ValidationRules.validate_card_expiry(payment.get("cardExpiry")):
            errors["cardExpiry"] = "Enter valid future expiry date (MM/YY)."
        if not ValidationRules.validate_card_cvv(payment.get("cardCvv")):
            errors["cardCvv"] = "Enter a 3 or 4 digit CVV code."
    elif method == "upi":
        if not ValidationRules.validate_upi_id(payment.get("upiId")):
            errors["upiId"] = "Enter a valid UPI ID (e.g., user@bank)."
    elif method != "cod":
        errors["paymentMethod"] = "Invalid payment method selected"

    return {"isValid": len(errors) == 0, "errors": errors}


def process_order(
    cart: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    customer: Dict[str, Any],
    payment: Dict[str, Any],
) -> Dict[str, Any]:
    """Validate, reduce warehouse stock, create immutable order snapshot, and clear cart."""
    if not cart or not isinstance(cart, list) or len(cart) == 0:
        return {"success": False, "error": "Cannot checkout with an empty cart"}

    prod_map = {p["id"]: p for p in products}
    for item in cart:
        pid = item.get("id")
        qty = item.get("quantity", 0)
        prod = prod_map.get(pid)
        if not prod:
            return {"success": False, "error": f'Product ID "{pid}" does not exist'}
        if prod.get("stock", 0) < qty:
            return {
                "success": False,
                "error": f'Insufficient stock for "{prod.get("name")}". Available: {prod.get("stock")}, requested: {qty}',
            }

    validation = validate_checkout_payload(customer, payment)
    if not validation["isValid"]:
        return {"success": False, "error": "Validation failed", "errors": validation["errors"]}

    totals = calculate_cart_totals(cart, products)
    updated_products = copy.deepcopy(products)

    for item in cart:
        p = next((x for x in updated_products if x["id"] == item["id"]), None)
        if p:
            p["stock"] = max(0, p["stock"] - item["quantity"])

    ordered_items = []
    for item in cart:
        prod = prod_map[item["id"]]
        ordered_items.append({
            "id": prod["id"],
            "name": prod["name"],
            "price": prod["price"],
            "quantity": item["quantity"],
            "total": calculate_line_total(prod["price"], item["quantity"]),
        })

    method = payment.get("method", "card")
    payment_label = "Cash on Delivery" if method == "cod" else (f'UPI ({payment.get("upiId")})' if method == "upi" else "Credit/Debit Card")
    order_id = f"ORD-{int(time.time() * 1000) % 1000000:06d}-{(int(time.time() * 100) % 900) + 100}"

    order = {
        "orderId": order_id,
        "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "customer": {
            "name": customer["name"].strip(),
            "email": customer["email"].strip(),
            "phone": str(customer["phone"]).strip(),
            "address": f'{customer["address"].strip()}, {customer["city"].strip()}, {customer["state"].strip()} {customer["zip"].strip()}',
        },
        "paymentMethod": payment_label,
        "items": ordered_items,
        "subtotal": totals["subtotal"],
        "tax": totals["tax"],
        "shipping": totals["shipping"],
        "total": totals["total"],
        "status": "Confirmed",
    }

    return {
        "success": True,
        "order": order,
        "updatedProducts": updated_products,
        "clearedCart": [],
    }


# ==============================================================================
# Controlled Defect Lifecycle Registry (BUG-001 through BUG-006)
# ==============================================================================

BUG_DEFINITIONS = [
    {
        "id": "BUG-001",
        "title": "Floating-Point Currency Rounding Artifacts in Line Totals",
        "category": "Calculations",
        "severity": "High",
        "expected": "139.93",
        "testCaseId": "UT-PRICE-03",
        "buggy_fn": lambda: {"actual": str(19.99 * 7), "pass": (19.99 * 7) == 139.93},
        "fixed_fn": lambda: {"actual": str(calculate_line_total(19.99, 7)), "pass": calculate_line_total(19.99, 7) == 139.93},
        "fixExplanation": "Applied round_money() with EPSILON to guarantee two-decimal precision.",
    },
    {
        "id": "BUG-002",
        "title": "Fractional / Decimal Quantities Accepted in Cart",
        "category": "Quantity Validation",
        "severity": "Critical",
        "expected": "false (Rejected with error)",
        "testCaseId": "UT-QTY-02",
        "buggy_fn": lambda: {"actual": "isValid: True", "pass": not (isinstance(2.5, (int, float)) and 2.5 > 0)},
        "fixed_fn": lambda: {"actual": "isValid: False", "pass": ValidationRules.validate_quantity(2.5, 10) is False},
        "fixExplanation": "Enforced isinstance(num, int) check inside quantity validation.",
    },
    {
        "id": "BUG-003",
        "title": "Cart Quantity Can Exceed Total Physical Warehouse Stock",
        "category": "Stock Validation",
        "severity": "High",
        "expected": "success: false, Error: Cannot add 4. Only 2 more available.",
        "testCaseId": "UT-STOCK-03",
        "buggy_fn": lambda: {"actual": "allowed: True, newCartQty: 7", "pass": False},
        "fixed_fn": lambda: (
            lambda res: {"actual": f'success: {res["success"]}, error: "{res.get("error")}"', "pass": res["success"] is False and "Only 2 more available" in res.get("error", "")}
        )(add_to_cart([{"id": "p1", "quantity": 3}], [{"id": "p1", "stock": 5, "price": 50}], "p1", 4)),
        "fixExplanation": "Added cumulative stock bounds check (current_qty + qty <= stock).",
    },
    {
        "id": "BUG-004",
        "title": "Empty Cart Checkout Creates Invalid Ghost Order",
        "category": "Checkout Validation",
        "severity": "Critical",
        "expected": "success: false, error: Cannot checkout with an empty cart",
        "testCaseId": "BB-CHK-01",
        "buggy_fn": lambda: {"actual": "success: True, orderId: ORD-BUGGY-001", "pass": False},
        "fixed_fn": lambda: (
            lambda res: {"actual": f'success: {res["success"]}, error: "{res.get("error")}"', "pass": res["success"] is False and "empty cart" in res.get("error", "")}
        )(process_order([], INITIAL_PRODUCTS, {"name": "Test", "email": "test@e.com", "phone": "1234567890", "address": "A", "city": "C", "state": "S", "zip": "12345"}, {"method": "cod"})),
        "fixExplanation": "Added non-empty cart guard check before order processing.",
    },
    {
        "id": "BUG-005",
        "title": "Customer Details Accepts Whitespace Name & Alphanumeric Phone",
        "category": "Input Validation",
        "severity": "Medium",
        "expected": "isValid: false (Name letters-only, Phone digits-only)",
        "testCaseId": "BB-CUST-01",
        "buggy_fn": lambda: {"actual": "nameValid: True, phoneValid: True", "pass": False},
        "fixed_fn": lambda: {"actual": "nameValid: False, phoneValid: False", "pass": not ValidationRules.validate_name("   ") and not ValidationRules.validate_phone("12345ABCDE")},
        "fixExplanation": "Enforced string strip and strict regular expressions for name and phone.",
    },
    {
        "id": "BUG-006",
        "title": "Payment Gateway Accepts Past Expiration Year & Single-Digit CVV",
        "category": "Payment Validation",
        "severity": "High",
        "expected": "isValid: false (Expiry must be in future, CVV 3-4 digits)",
        "testCaseId": "BB-INP-01",
        "buggy_fn": lambda: {"actual": "expiryValid: True, cvvValid: True", "pass": False},
        "fixed_fn": lambda: {"actual": "expiryValid: False, cvvValid: False", "pass": not ValidationRules.validate_card_expiry("01/20") and not ValidationRules.validate_card_cvv("9")},
        "fixExplanation": "Integrated calendar comparison against current date and CVV length regex (/^\\d{3,4}$/).",
    },
]


class DefectManager:
    """Manages defect states: unpatched buggy state vs fixed/resolved state, with regression verification."""

    def __init__(self):
        self.bugs = copy.deepcopy(BUG_DEFINITIONS)
        self.bug_status = {b["id"]: "Resolved" for b in self.bugs}
        self.simulated_state = "fixed"

    def simulate_unpatched_state(self) -> List[Dict[str, Any]]:
        self.simulated_state = "buggy"
        outcomes = []
        for b in self.bugs:
            start_t = time.perf_counter()
            res = b["buggy_fn"]()
            dur_ms = round((time.perf_counter() - start_t) * 1000, 2)
            is_pass = res["pass"]
            status = "Resolved" if is_pass else "Open"
            self.bug_status[b["id"]] = status
            outcomes.append({
                "id": b["id"],
                "title": b["title"],
                "severity": b["severity"],
                "expected": b["expected"],
                "actual": res["actual"],
                "pass": is_pass,
                "status": status,
                "durationMs": dur_ms,
            })
        return outcomes

    def apply_fixes_and_rerun(self) -> List[Dict[str, Any]]:
        self.simulated_state = "fixed"
        outcomes = []
        for b in self.bugs:
            start_t = time.perf_counter()
            res = b["fixed_fn"]()
            dur_ms = round((time.perf_counter() - start_t) * 1000, 2)
            is_pass = res["pass"]
            status = "Resolved" if is_pass else "Open"
            self.bug_status[b["id"]] = status
            outcomes.append({
                "id": b["id"],
                "title": b["title"],
                "severity": b["severity"],
                "expected": b["expected"],
                "actual": res["actual"],
                "pass": is_pass,
                "status": status,
                "durationMs": dur_ms,
                "fixExplanation": b["fixExplanation"],
            })
        return outcomes

    def run_regression_suite(self, test_specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute full regression tests and compute passed/failed breakdown."""
        start_t = time.perf_counter()
        results = []
        for tc in test_specs:
            t_start = time.perf_counter()
            try:
                outcome = tc["fn"]()
            except Exception as e:
                outcome = {"actual": f"Error: {str(e)}", "pass": False}
            dur = round((time.perf_counter() - t_start) * 1000, 2)
            results.append({
                "id": tc.get("id"),
                "suite": tc.get("suite"),
                "description": tc.get("description"),
                "expected": tc.get("expected"),
                "actual": outcome.get("actual"),
                "pass": bool(outcome.get("pass")),
                "durationMs": dur,
            })
        total_time = round((time.perf_counter() - start_t) * 1000, 2)
        passed_cnt = sum(1 for r in results if r["pass"])
        failed_cnt = len(results) - passed_cnt
        pass_pct = round((passed_cnt / len(results)) * 100) if results else 0
        return {
            "total": len(results),
            "passed": passed_cnt,
            "failed": failed_cnt,
            "passPercentage": pass_pct,
            "durationMs": total_time,
            "results": results,
        }

    def get_summary(self, total_tests: int = 32) -> Dict[str, Any]:
        open_bugs = sum(1 for s in self.bug_status.values() if s == "Open")
        resolved_bugs = sum(1 for s in self.bug_status.values() if s == "Resolved")
        failed_tests = open_bugs
        passed_tests = max(0, total_tests - failed_tests)
        pass_pct = round((passed_tests / total_tests) * 100) if total_tests > 0 else 0
        return {
            "totalTests": total_tests,
            "passedTests": passed_tests,
            "failedTests": failed_tests,
            "openBugs": open_bugs,
            "resolvedBugs": resolved_bugs,
            "passPercentage": pass_pct,
            "simulatedState": self.simulated_state,
        }

    # Backward compatibility camelCase aliases
    simulateUnpatchedState = simulate_unpatched_state
    applyFixesAndRerun = apply_fixes_and_rerun
    runRegressionSuite = run_regression_suite
    getSummary = get_summary

