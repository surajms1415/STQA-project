# AuraMart E-Commerce - Test Case Specification Document

**Project**: AuraMart Pure Vanilla E-Commerce Application  
**QA Lead**: Software Testing & Quality Assurance (STQA) Engineering Team  
**Execution Environment**: Browser (Chromium / Firefox / WebKit) & Headless Node.js (v24.x)  
**Test Automation Framework**: Native Node.js Test Runner & Browser Execution Engine  
**Status**: 100% Passed (32 Automated + 6 Defect Verification Scenarios)  

---

## 1. Unit Testing Specifications (15 Test Cases)

### 1.1 Price Calculation Suite

| Test ID | Module | Precondition | Input / Test Data | Steps to Execute | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`UT-PRICE-01`** | Price Formatter | Core loaded | `99.99` (Number) | Call `Core.formatPrice(99.99)` | Returns string `"$99.99"` with 2 decimals | `"$99.99"` | **PASS** |
| **`UT-PRICE-02`** | Line Total | Core loaded | Price: `49.99`, Qty: `3` | Call `Core.calculateLineTotal(49.99, 3)` | Returns `149.97` | `149.97` | **PASS** |
| **`UT-PRICE-03`** | Precision Rounding | Core loaded | Price: `19.99`, Qty: `7` | Call `Core.calculateLineTotal(19.99, 7)` | Returns `139.93` (no float leakage `139.92999999999998`) | `139.93` | **PASS** |

### 1.2 Quantity Validation Suite

| Test ID | Module | Precondition | Input / Test Data | Steps to Execute | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`UT-QTY-01`** | Quantity Validator | In-stock product | Qty: `3`, Stock: `5` | Call `ValidationRules.quantity.validate(3, 5)` | Returns `true` | `true` | **PASS** |
| **`UT-QTY-02`** | Quantity Validator | Stock available | Qty: `2.5`, Stock: `5` | Call `ValidationRules.quantity.validate(2.5, 5)` | Returns `false` (rejection of decimals) | `false` | **PASS** |
| **`UT-QTY-03`** | Quantity Validator | Stock available | Qty: `0`, Stock: `5` | Call `ValidationRules.quantity.validate(0, 5)` | Returns `false` (zero rejected) | `false` | **PASS** |
| **`UT-QTY-04`** | Quantity Validator | Stock available | Qty: `-2`, Stock: `5` | Call `ValidationRules.quantity.validate(-2, 5)` | Returns `false` (negative rejected) | `false` | **PASS** |

### 1.3 Cart Calculations Suite

| Test ID | Module | Precondition | Input / Test Data | Steps to Execute | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`UT-CART-01`** | Subtotal Engine | Products in cart | 2x$100.00, 3x$20.00 | Call `Core.calculateCartTotals(cart, prods)` | Subtotal equals `$260.00` | `$260.00` | **PASS** |
| **`UT-CART-02`** | Tax Calculation | Cart subtotal $100 | Subtotal: `100.00` | Calculate 5% standard tax | Tax equals `$5.00` | `$5.00` | **PASS** |
| **`UT-CART-03`** | Standard Shipping | Cart subtotal < $50 | Subtotal: `40.00` | Evaluate shipping tier threshold | Shipping equals `$5.00` | `$5.00` | **PASS** |
| **`UT-CART-04`** | Free Shipping | Cart subtotal >= $50 | Subtotal: `100.00` | Evaluate shipping tier threshold | Shipping equals `$0.00` (Free Shipping) | `$0.00` | **PASS** |
| **`UT-CART-05`** | Grand Total | Subtotal, Tax, Ship | Subtotal $20, Tax $1, Ship $5 | Sum: `subtotal + tax + shipping` | Grand Total equals `$26.00` | `$26.00` | **PASS** |

### 1.4 Stock Validation Suite

| Test ID | Module | Precondition | Input / Test Data | Steps to Execute | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`UT-STOCK-01`** | Stock Checker | Product in catalog | `stock: 5` | Call `Core.isProductInStock(prod)` | Returns `true` | `true` | **PASS** |
| **`UT-STOCK-02`** | Stock Checker | Out-of-stock item | `stock: 0` | Call `Core.isProductInStock(prod)` | Returns `false` | `false` | **PASS** |
| **`UT-STOCK-03`** | Available Stock | Product stock: 5 | In Cart: `2` | Call `Core.getAvailableStock(prod, cart)` | Returns remaining `3` | `3` | **PASS** |

---

## 2. Integration Testing Specifications (5 Test Cases)

| Test ID | Module | Precondition | Input / Test Data | Steps to Execute | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`IT-CART-01`** | Cart Integration | Empty cart | Product `p1`, Qty `1` | `Core.addToCart(cart, prods, 'p1', 1)` | Cart length is 1, item quantity is 1 | `length: 1, qty: 1` | **PASS** |
| **`IT-QTY-01`** | Cart Integration | 1 item in cart | Update Qty to `3` | `Core.updateCartQuantity(cart, prods, 'p1', 3)` | Cart item qty is 3, total recalculated to `$126.00` | `qty: 3, total: 126.00` | **PASS** |
| **`IT-ORDER-01`** | Checkout Engine | Cart with 2 items | Valid Customer & COD | `Core.processOrder(cart, prods, cust, pay)` | Order created with `#ORD-` ID, cart emptied | `success: true, status: Confirmed` | **PASS** |
| **`IT-STORE-01`** | LocalStorage Sync | Storage available | Cart array `[{ id: 'p1', qty: 2 }]` | Set and get item from localStorage | Serialized JSON matches retrieved object | `p1 x 2 matched` | **PASS** |
| **`IT-STORE-02`** | Inventory Sync | Initial stock 5 | Order placed for 2 items | `Core.processOrder()`, save to storage | Product stock decremented to 3 in storage | `stock: 3` | **PASS** |

---

## 3. Black Box Testing Specifications (7 Test Cases)

| Test ID | Module | Precondition | Input / Test Data | Steps to Execute | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`BB-CHK-01`** | Boundary Checkout | Cart is empty (`[]`) | Valid customer info | Submit checkout request | Rejection with error: *"Cannot checkout with an empty cart"* | `success: false, empty cart` | **PASS** |
| **`BB-CUST-01`** | Form Validation | Form loaded | Name `"X"`, Email `"bad"`, Phone `"12"` | Submit customer form | Form marked invalid, errors flagged for name, email, phone | `isValid: false, 7 errors` | **PASS** |
| **`BB-QTY-01`** | Boundary Qty | Cart loaded | Qty `-3` | Attempt to add `-3` units to cart | Rejection with error: *"Invalid quantity to add"* | `success: false, invalid qty` | **PASS** |
| **`BB-QTY-02`** | Boundary Qty | 2 units in cart | Qty `0` | Update quantity to `0` | Item cleanly removed, cart length becomes 0 | `removed: true, length: 0` | **PASS** |
| **`BB-STOCK-01`** | Inventory Boundary | `p10` stock is 0 | Qty `1` | Attempt to add out-of-stock item | Rejection with error: *"Product is out of stock"* | `success: false, out of stock` | **PASS** |
| **`BB-INP-01`** | Payment Boundary | Card selected | Expiry `"01/20"`, CVV `"9"` | Submit expired card & 1-digit CVV | Rejection: Card expiry and CVV length flagged | `isValid: false, card errors` | **PASS** |
| **`BB-INP-02`** | Positive Validation | Form loaded | Complete valid customer & card payload | Submit form | Validation succeeds with 0 errors | `isValid: true, 0 errors` | **PASS** |

---

## 4. Functional Testing Specifications (5 Test Cases)

| Test ID | Module | Precondition | Input / Test Data | Steps to Execute | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`FT-SRCH-01`** | Catalog Search | 10 products | Query: `"Headphones"` | Filter products list | Returns 1+ items containing `"Headphones"` | `found 1 items` | **PASS** |
| **`FT-SRCH-02`** | Catalog Search | 10 products | Query: `"xyznonexistent987"` | Filter products list | Returns empty array (0 items) | `0 items` | **PASS** |
| **`FT-CART-01`** | Cart Lifecycle | Catalog loaded | Product `p1`, Qty `2` | Add product to cart | Item listed in cart with quantity 2 and line total | `qty: 2 in cart` | **PASS** |
| **`FT-CART-02`** | Cart Lifecycle | 2 items in cart | Delete button on `p1` | Remove `p1` from cart | `p1` removed, 1 item remaining in cart | `length: 1, hasP1: false` | **PASS** |
| **`FT-E2E-01`** | E2E Purchasing | Clean state | Search &rarr; Add &rarr; Checkout &rarr; Confirm | Complete end-to-end purchasing workflow | Order generated, stock decremented, cart emptied | `order: true, stockReduced: true, cartCleared: true` | **PASS** |

---

## 5. Traceability Matrix

| Requirement ID | Requirement Description | Test Case(s) | Defect ID (if applicable) | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | Display products with name, price, stock | `UT-PRICE-01`, `UT-STOCK-01`, `UT-STOCK-02` | `BUG-001` | **Verified** |
| **REQ-02** | Search and filter products | `FT-SRCH-01`, `FT-SRCH-02` | N/A | **Verified** |
| **REQ-03** | Add products to cart | `IT-CART-01`, `FT-CART-01` | `BUG-002`, `BUG-003` | **Verified** |
| **REQ-04** | Increase and decrease quantities | `UT-QTY-01`, `IT-QTY-01`, `BB-QTY-02` | `BUG-002`, `BUG-003` | **Verified** |
| **REQ-05** | Remove products from cart | `BB-QTY-02`, `FT-CART-02` | N/A | **Verified** |
| **REQ-06** | Calculate subtotal, tax, shipping, total | `UT-PRICE-02`, `UT-PRICE-03`, `UT-CART-01..05` | `BUG-001` | **Verified** |
| **REQ-07** | Checkout with customer details | `IT-ORDER-01`, `BB-INP-02`, `FT-E2E-01` | `BUG-004`, `BUG-005`, `BUG-006` | **Verified** |
| **REQ-08** | Display order confirmation & receipt | `IT-ORDER-01`, `FT-E2E-01` | `BUG-004` | **Verified** |
| **REQ-09** | Validate all user inputs | `BB-CUST-01`, `BB-INP-01`, `BB-INP-02` | `BUG-005`, `BUG-006` | **Verified** |
| **REQ-10** | LocalStorage state persistence | `IT-STORE-01`, `IT-STORE-02` | N/A | **Verified** |
