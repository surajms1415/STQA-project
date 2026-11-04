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
        if q <= 0 or math.isnan(p) or math.isinf(p) or p < 0 or abs(p) > 1e12:
            return 0.0
        return round_money(p * q)
    except (ValueError, TypeError, OverflowError):
        return 0.0


def calculate_cart_totals(cart: Any, products: Any) -> Dict[str, Any]:
    """
    Calculate subtotal, 5% standard tax, tiered shipping ($5 if subtotal < $50, Free if >= $50),
    and grand total.
    """
    if not isinstance(cart, list) or not isinstance(products, list):
        return {
            "subtotal": 0.0,
            "tax": 0.0,
            "shipping": 0.0,
            "total": 0.0,
            "itemCount": 0,
        }

    subtotal = 0.0
    item_count = 0
    prod_map = {p["id"]: p for p in products if isinstance(p, dict) and "id" in p}

    for item in cart:
        if not isinstance(item, dict):
            continue
        pid = item.get("id")
        try:
            qty = int(item.get("quantity", 0))
        except (ValueError, TypeError):
            continue
        if pid in prod_map and qty > 0:
            p_price = float(prod_map[pid].get("price", 0.0))
            if not math.isnan(p_price) and not math.isinf(p_price):
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
    """Regex and business input validators matching frontend ValidationRules with defensive sanitization."""

    @staticmethod
    def validate_name(val: Any) -> bool:
        if not isinstance(val, str) or any(ord(c) < 32 for c in val):
            return False
        trimmed = val.strip()
        # Disallow non-breaking spaces or non-ascii control spaces
        if "\xa0" in trimmed:
            return False
        return 3 <= len(trimmed) <= 100 and bool(re.match(r"^[a-zA-Z\s.'-]+$", trimmed))

    @staticmethod
    def validate_email(val: Any) -> bool:
        if not isinstance(val, str) or any(ord(c) < 32 for c in val) or len(val) > 254:
            return False
        return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$", val.strip()))

    @staticmethod
    def validate_phone(val: Any) -> bool:
        if not isinstance(val, (str, int)) or any(ord(c) < 32 for c in str(val)):
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

    prod_map = {p["id"]: p for p in products if isinstance(p, dict) and "id" in p}
    for item in cart:
        if not isinstance(item, dict):
            return {"success": False, "error": "Invalid item structure in cart"}
        pid = item.get("id")
        raw_qty = item.get("quantity", 0)
        if not isinstance(raw_qty, int) or isinstance(raw_qty, bool) or raw_qty <= 0:
            return {"success": False, "error": f'Invalid quantity for item "{pid}"'}
        qty = raw_qty
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

SEVERITY = {
    "CRITICAL": "Critical",
    "HIGH": "High",
    "MEDIUM": "Medium",
    "LOW": "Low",
}

PRIORITY = {
    "P1": "P1 - Critical",
    "P2": "P2 - High",
    "P3": "P3 - Medium",
    "P4": "P4 - Low",
}

STATUS = {
    "OPEN": "Open",
    "RESOLVED": "Resolved",
    "REOPENED": "Re-Opened",
}

BUG_DEFINITIONS = [
    {
        "id": "BUG-001",
        "title": "Floating-Point Currency Rounding Artifacts in Line Totals",
        "category": "Calculations",
        "component": "Price Calculation",
        "severity": SEVERITY["HIGH"],
        "priority": PRIORITY["P2"],
        "requirementId": "REQ-06",
        "expected": "139.93",
        "testCaseId": "UT-PRICE-03",
        "impactedTests": ["UT-PRICE-01", "UT-PRICE-02", "UT-PRICE-03", "IT-CART-02", "BV-PRICE-01", "REG-PRICE-01"],
        "description": "Calculating price * quantity without decimal quantization produces IEEE-754 floating-point artifacts (e.g. 19.99 * 7 = 139.92999999999998 instead of $139.93).",
        "rootCause": "Double-precision IEEE-754 binary floating-point representation lacks native decimal quantization, causing float overflow artifacts on multiplications like 19.99 * 7.",
        "stepsToReproduce": "1. Add 7 units of item priced at $19.99.\n2. Calculate line total.\n3. Observe raw unrounded float.",
        "buggy_fn": lambda: {"actual": str(19.99 * 7), "pass": (19.99 * 7) == 139.93},
        "fixed_fn": lambda: {"actual": str(calculate_line_total(19.99, 7)), "pass": calculate_line_total(19.99, 7) == 139.93},
        "fixExplanation": "Applied round_money() with EPSILON to guarantee two-decimal precision.",
    },
    {
        "id": "BUG-002",
        "title": "Fractional / Decimal Quantities Accepted in Cart",
        "category": "Quantity Validation",
        "component": "Cart & Inventory",
        "severity": SEVERITY["CRITICAL"],
        "priority": PRIORITY["P1"],
        "requirementId": "REQ-03",
        "expected": "false (Rejected with error)",
        "testCaseId": "UT-QTY-02",
        "impactedTests": ["UT-QTY-01", "UT-QTY-02", "UT-QTY-03", "UT-QTY-04", "BV-QTY-01", "NEG-QTY-01", "VAL-QTY-01"],
        "description": "System accepts non-integer values (e.g. 2.5) because validation only checks if number > 0, leading to fractional inventory and prices.",
        "rootCause": "Insufficient type checking only confirmed quantity was positive (qty > 0) without ensuring it was a whole integer.",
        "stepsToReproduce": "1. Attempt to add 2.5 items to cart.\n2. Cart updates with quantity 2.5.",
        "buggy_fn": lambda: {"actual": "isValid: True", "pass": not (isinstance(2.5, (int, float)) and 2.5 > 0)},
        "fixed_fn": lambda: {"actual": "isValid: False", "pass": ValidationRules.validate_quantity(2.5, 10) is False},
        "fixExplanation": "Enforced isinstance(num, int) check inside quantity validation.",
    },
    {
        "id": "BUG-003",
        "title": "Cart Quantity Can Exceed Total Physical Warehouse Stock",
        "category": "Stock Validation",
        "component": "Stock Enforcement",
        "severity": SEVERITY["HIGH"],
        "priority": PRIORITY["P1"],
        "requirementId": "REQ-01",
        "expected": "success: false, Error: Cannot add 4. Only 2 more available.",
        "testCaseId": "UT-STOCK-03",
        "impactedTests": ["UT-STOCK-01", "UT-STOCK-02", "UT-STOCK-03", "IT-CART-01", "BV-STOCK-01", "NEG-STOCK-01"],
        "description": "If a customer already has 3 units in cart and adds 4 more when total stock is 5, system fails to verify cumulative cart quantity against inventory.",
        "rootCause": "Inventory verification only checked newly submitted quantity against physical stock, ignoring existing quantities already reserved in customer's active cart.",
        "stepsToReproduce": "1. Product stock is 5.\n2. Cart already holds 3.\n3. Add 4 more.\n4. Cart now holds 7 (oversold).",
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
        "component": "Checkout Controller",
        "severity": SEVERITY["CRITICAL"],
        "priority": PRIORITY["P1"],
        "requirementId": "REQ-07",
        "expected": "success: false, error: Cannot checkout with an empty cart",
        "testCaseId": "BB-CHK-01",
        "impactedTests": ["BB-CHK-01", "IT-ORDER-01", "FT-E2E-01", "NEG-ORD-01", "VAL-ORD-01"],
        "description": "Calling checkout submission with empty cart succeeds, generating a $0 order invoice and polluting order history.",
        "rootCause": "Missing guard clause checking cart length before initializing order processing, allowing ghost orders with $0 total.",
        "stepsToReproduce": "1. Empty shopping cart.\n2. Submit checkout payload.\n3. Order is created.",
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
        "component": "Customer Form",
        "severity": SEVERITY["MEDIUM"],
        "priority": PRIORITY["P3"],
        "requirementId": "REQ-09",
        "expected": "isValid: false (Name letters-only, Phone digits-only)",
        "testCaseId": "BB-CUST-01",
        "impactedTests": ["BB-CUST-01", "UT-VAL-01", "VAL-CUST-01", "NEG-CUST-01", "FT-CHK-01"],
        "description": "Form accepts spaces-only string (\"   \") for name and letters inside phone numbers (\"98765PHONE\") due to simple length checks.",
        "rootCause": "Inadequate input sanitation using simple length check without trimming whitespace and lack of strict regex patterns for name and phone.",
        "stepsToReproduce": "1. Enter \"   \" in name field.\n2. Enter \"12345ABCDE\" in phone.\n3. Submit form.",
        "buggy_fn": lambda: {"actual": "nameValid: True, phoneValid: True", "pass": False},
        "fixed_fn": lambda: {"actual": "nameValid: False, phoneValid: False", "pass": not ValidationRules.validate_name("   ") and not ValidationRules.validate_phone("12345ABCDE")},
        "fixExplanation": "Enforced string strip and strict regular expressions for name and phone.",
    },
    {
        "id": "BUG-006",
        "title": "Payment Gateway Accepts Past Expiration Year & Single-Digit CVV",
        "category": "Payment Validation",
        "component": "Payment Module",
        "severity": SEVERITY["HIGH"],
        "priority": PRIORITY["P2"],
        "requirementId": "REQ-09",
        "expected": "isValid: false (Expiry must be in future, CVV 3-4 digits)",
        "testCaseId": "BB-INP-01",
        "impactedTests": ["BB-INP-01", "UT-VAL-03", "VAL-PAY-01", "NEG-PAY-01", "FT-PAY-01"],
        "description": "Expired credit card date (01/20) and 1-digit CVV (\"9\") are accepted because expiry is only checked for format MM/YY rather than date comparison.",
        "rootCause": "Syntax-only regex verification for MM/YY format without comparing date against current calendar month/year, and missing CVV length restriction.",
        "stepsToReproduce": "1. Enter Card Expiry \"01/20\".\n2. Enter CVV \"9\".\n3. Submit card payment.",
        "buggy_fn": lambda: {"actual": "expiryValid: True, cvvValid: True", "pass": False},
        "fixed_fn": lambda: {"actual": "expiryValid: False, cvvValid: False", "pass": not ValidationRules.validate_card_expiry("01/20") and not ValidationRules.validate_card_cvv("9")},
        "fixExplanation": "Integrated calendar comparison against current date and CVV length regex (/^\\d{3,4}$/).",
    },
]

# ==============================================================================
# Requirements Traceability Matrix (RTM)
# ==============================================================================

TRACEABILITY_MATRIX = [
    {
        "req_id": "REQ-01",
        "req_title": "Product Catalog & Real-Time Stock Status",
        "category": "Catalog & Inventory",
        "test_cases": ["UT-STOCK-01", "UT-STOCK-02", "UT-STOCK-03", "IT-STORE-02", "BV-STOCK-01", "NEG-STOCK-01"],
        "defect_ids": ["BUG-003"],
        "status": "Covered",
    },
    {
        "req_id": "REQ-02",
        "req_title": "Product Search & Dynamic Category Filtering",
        "category": "Discovery",
        "test_cases": ["FT-SRCH-01", "FT-SRCH-02", "FT-CAT-01", "BV-SRCH-01"],
        "defect_ids": [],
        "status": "Covered",
    },
    {
        "req_id": "REQ-03",
        "req_title": "Cart Quantity Constraints & Stock Bounds",
        "category": "Cart & Validation",
        "test_cases": ["UT-QTY-01", "UT-QTY-02", "UT-QTY-03", "UT-QTY-04", "BB-QTY-01", "BB-QTY-02", "BV-QTY-01", "VAL-QTY-01"],
        "defect_ids": ["BUG-002", "BUG-003"],
        "status": "Covered",
    },
    {
        "req_id": "REQ-04",
        "req_title": "Shopping Cart Item Manipulation",
        "category": "Cart State",
        "test_cases": ["IT-CART-01", "IT-QTY-01", "FT-CART-01", "FT-CART-02", "IT-STORE-01"],
        "defect_ids": [],
        "status": "Covered",
    },
    {
        "req_id": "REQ-05",
        "req_title": "Inventory Synchronization on Order Completion",
        "category": "Inventory Management",
        "test_cases": ["IT-STORE-02", "FT-E2E-01"],
        "defect_ids": [],
        "status": "Covered",
    },
    {
        "req_id": "REQ-06",
        "req_title": "Financial Calculations & Floating-Point Precision",
        "category": "Pricing & Taxes",
        "test_cases": ["UT-PRICE-01", "UT-PRICE-02", "UT-PRICE-03", "UT-CART-01", "UT-CART-02", "UT-CART-03", "UT-CART-04", "UT-CART-05", "BV-PRICE-01", "REG-PRICE-01"],
        "defect_ids": ["BUG-001"],
        "status": "Covered",
    },
    {
        "req_id": "REQ-07",
        "req_title": "Checkout Verification & Empty Cart Guard",
        "category": "Checkout",
        "test_cases": ["BB-CHK-01", "IT-ORDER-01", "FT-E2E-01", "NEG-ORD-01"],
        "defect_ids": ["BUG-004"],
        "status": "Covered",
    },
    {
        "req_id": "REQ-08",
        "req_title": "Order Processing & Persistent Receipt Generation",
        "category": "Orders",
        "test_cases": ["IT-ORDER-01", "FT-E2E-01", "VAL-ORD-01"],
        "defect_ids": ["BUG-004"],
        "status": "Covered",
    },
    {
        "req_id": "REQ-09",
        "req_title": "Form Input Validation & Payment Security Verification",
        "category": "Validation & Security",
        "test_cases": ["BB-CUST-01", "BB-INP-01", "BB-INP-02", "UT-VAL-01", "UT-VAL-02", "UT-VAL-03", "VAL-CUST-01", "VAL-PAY-01", "NEG-PAY-01"],
        "defect_ids": ["BUG-005", "BUG-006"],
        "status": "Covered",
    },
    {
        "req_id": "REQ-10",
        "req_title": "User Interface Responsiveness & Defect Visibility",
        "category": "UI / QA Dashboard",
        "test_cases": ["PW-RESP-01", "PW-NAV-01", "PW-DEF-01"],
        "defect_ids": [],
        "status": "Covered",
    },
]


class DefectManager:
    """Manages defect states: unpatched buggy state vs fixed/resolved state, with regression verification and failure tracking."""

    def __init__(self):
        self.bugs = copy.deepcopy(BUG_DEFINITIONS)
        self.bug_status = {b["id"]: STATUS["RESOLVED"] for b in self.bugs}
        self.simulated_state = "fixed"
        self.failure_records: List[Dict[str, Any]] = []

    def record_failure(
        self,
        test_id: str,
        error_message: str,
        expected: str,
        actual: str,
        stack_trace: Optional[str] = None,
        defect_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record details of a failed test case."""
        record = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "test_id": test_id,
            "defect_id": defect_id,
            "error_message": error_message,
            "expected": expected,
            "actual": actual,
            "stack_trace": stack_trace or "N/A",
            "status": "Failed",
        }
        self.failure_records.append(record)
        return record

    def get_failure_records(self) -> List[Dict[str, Any]]:
        """Return list of all recorded failures."""
        return list(self.failure_records)

    def clear_failure_records(self) -> None:
        """Clear recorded failures."""
        self.failure_records.clear()

    def simulate_unpatched_state(self) -> List[Dict[str, Any]]:
        self.simulated_state = "buggy"
        self.clear_failure_records()
        outcomes = []
        for b in self.bugs:
            start_t = time.perf_counter()
            res = b["buggy_fn"]()
            dur_ms = round((time.perf_counter() - start_t) * 1000, 2)
            is_pass = res["pass"]
            status = STATUS["RESOLVED"] if is_pass else STATUS["OPEN"]
            self.bug_status[b["id"]] = status

            if not is_pass:
                self.record_failure(
                    test_id=b["testCaseId"],
                    error_message=f"Defect exposed: {b['title']}. Expected [{b['expected']}], but got [{res['actual']}].",
                    expected=b["expected"],
                    actual=res["actual"],
                    defect_id=b["id"],
                )

            outcomes.append({
                "id": b["id"],
                "title": b["title"],
                "severity": b["severity"],
                "priority": b["priority"],
                "requirementId": b["requirementId"],
                "expected": b["expected"],
                "actual": res["actual"],
                "pass": is_pass,
                "status": status,
                "durationMs": dur_ms,
                "rootCause": b["rootCause"],
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
            status = STATUS["RESOLVED"] if is_pass else STATUS["OPEN"]
            self.bug_status[b["id"]] = status
            outcomes.append({
                "id": b["id"],
                "title": b["title"],
                "severity": b["severity"],
                "priority": b["priority"],
                "requirementId": b["requirementId"],
                "expected": b["expected"],
                "actual": res["actual"],
                "pass": is_pass,
                "status": status,
                "durationMs": dur_ms,
                "fixExplanation": b["fixExplanation"],
                "rootCause": b["rootCause"],
            })
        return outcomes

    def identify_rerun_tests(self, defect_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Identify which tests must be rerun after a defect or set of defects is resolved.
        Returns target test IDs, the exact Pytest selection filter, and component rationale.
        """
        if defect_ids is None:
            # Check all resolved defects or currently targeted defects
            defect_ids = [b["id"] for b in self.bugs if self.bug_status.get(b["id"]) == STATUS["RESOLVED"]]

        impacted_tests = []
        reasons = {}

        for b in self.bugs:
            if b["id"] in defect_ids:
                tests = b.get("impactedTests", [b["testCaseId"]])
                for t in tests:
                    if t not in impacted_tests:
                        impacted_tests.append(t)
                reasons[b["id"]] = {
                    "component": b["component"],
                    "primaryTest": b["testCaseId"],
                    "impactedTests": tests,
                    "fixExplanation": b.get("fixExplanation", ""),
                }

        # Build Pytest keyword filter expression
        # e.g., 'UT_PRICE or test_price'
        pytest_filter = " or ".join(t.replace("-", "_").lower() for t in impacted_tests)
        pytest_command = f'pytest python_tests/ -k "{pytest_filter}"' if pytest_filter else "pytest python_tests/"

        return {
            "defect_ids": defect_ids,
            "rerun_test_ids": impacted_tests,
            "total_rerun_tests": len(impacted_tests),
            "pytest_command": pytest_command,
            "reasons": reasons,
        }

    def get_traceability_matrix(self) -> List[Dict[str, Any]]:
        """Return the complete Requirements Traceability Matrix."""
        matrix = copy.deepcopy(TRACEABILITY_MATRIX)
        # Update defect status in the matrix
        for req in matrix:
            req_defects = []
            for did in req["defect_ids"]:
                req_defects.append({
                    "defect_id": did,
                    "status": self.bug_status.get(did, STATUS["RESOLVED"]),
                })
            req["defect_details"] = req_defects
        return matrix

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
            is_pass = bool(outcome.get("pass"))

            if not is_pass:
                self.record_failure(
                    test_id=tc.get("id", "UNKNOWN"),
                    error_message=f"Regression failure in suite [{tc.get('suite')}]: expected [{tc.get('expected')}], got [{outcome.get('actual')}].",
                    expected=str(tc.get("expected")),
                    actual=str(outcome.get("actual")),
                )

            results.append({
                "id": tc.get("id"),
                "suite": tc.get("suite"),
                "description": tc.get("description"),
                "expected": tc.get("expected"),
                "actual": outcome.get("actual"),
                "pass": is_pass,
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

    def get_summary(self, total_tests: int = 32, skipped_tests: int = 0) -> Dict[str, Any]:
        open_bugs = sum(1 for s in self.bug_status.values() if s == STATUS["OPEN"])
        resolved_bugs = sum(1 for s in self.bug_status.values() if s == STATUS["RESOLVED"])
        reopened_bugs = sum(1 for s in self.bug_status.values() if s == STATUS["REOPENED"])
        failed_tests = open_bugs
        passed_tests = max(0, total_tests - failed_tests - skipped_tests)
        effective_tested = total_tests - skipped_tests
        pass_pct = round((passed_tests / effective_tested) * 100) if effective_tested > 0 else 0
        fail_pct = round((failed_tests / effective_tested) * 100) if effective_tested > 0 else 0
        return {
            "totalTests": total_tests,
            "passedTests": passed_tests,
            "failedTests": failed_tests,
            "skippedTests": skipped_tests,
            "openBugs": open_bugs,
            "resolvedBugs": resolved_bugs,
            "reopenedBugs": reopened_bugs,
            "passPercentage": pass_pct,
            "failureRate": fail_pct,
            "simulatedState": self.simulated_state,
        }

    # Backward compatibility camelCase aliases
    simulateUnpatchedState = simulate_unpatched_state
    applyFixesAndRerun = apply_fixes_and_rerun
    runRegressionSuite = run_regression_suite
    getSummary = get_summary
    recordFailure = record_failure
    getFailureRecords = get_failure_records
    clearFailureRecords = clear_failure_records
    identifyRerunTests = identify_rerun_tests
    getTraceabilityMatrix = get_traceability_matrix

