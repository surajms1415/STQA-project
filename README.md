# 🛒 AuraMart E-Commerce & STQA Testing Framework

[![Tests](https://img.shields.io/badge/Tests-35%20Passing-success?style=for-the-badge&logo=node.js)](tests/)
[![Pass Rate](https://img.shields.io/badge/Pass%20Rate-100%25-brightgreen?style=for-the-badge)](qa-report.html)
[![Defects](https://img.shields.io/badge/Defects-6%20Resolved%20%2F%200%20Open-blue?style=for-the-badge)](DEFECT_REPORT.md)
[![Architecture](https://img.shields.io/badge/Stack-Vanilla%20HTML%20%7C%20CSS%20%7C%20ES6-orange?style=for-the-badge)](index.html)
[![Deployment](https://img.shields.io/badge/Deployment-Netlify%20%26%20GitHub%20Pages-informational?style=for-the-badge)](DEPLOYMENT.md)

A comprehensive, production-ready E-Commerce web application paired with an end-to-end **Software Testing and Quality Assurance (STQA) Engineering Framework**. Built entirely using **pure semantic HTML5, modern CSS3, and vanilla JavaScript (ES6+)** with **zero external libraries, bundlers, backend servers, or external API dependencies**.

The application is completely self-contained, offline-resilient, and optimized for instant static web deployment to **GitHub Pages** or **Netlify**.

---

## 📑 Table of Contents

1. [Interactive Dashboards & Links](#-interactive-dashboards--links)
2. [Project Architecture & Design Patterns](#-project-architecture--design-patterns)
3. [Core Functions Reference & API Documentation](#-core-functions-reference--api-documentation)
4. [Testing Framework Architecture](#-testing-framework-architecture)
5. [Complete Test Suite Matrix (32 Test Cases)](#-complete-test-suite-matrix-32-test-cases)
6. [Interactive Browser Manual Testing Studio](#-interactive-browser-manual-testing-studio)
7. [Defect Management & QA Module (6 Common Bugs)](#-defect-management--qa-module-6-common-bugs)
8. [Requirement Traceability Matrix](#-requirement-traceability-matrix)
9. [Automated CLI Test Execution](#-automated-cli-test-execution)
10. [Static Web Deployment Guide](#-static-web-deployment-guide)
11. [Repository Structure](#-repository-structure)

---

## 🌐 Interactive Dashboards & Links

The system features unified cross-navigation across four dedicated views:

| View / Document | Target File | Description |
| :--- | :--- | :--- |
| **🛍️ E-Commerce Store** | [`index.html`](index.html) | Live storefront featuring product catalog, live search, category filtering, slide-over cart drawer, customer checkout modal, and printable invoice receipts. |
| **🧪 QA Test Suite Dashboard** | [`test-dashboard.html`](test-dashboard.html) | In-browser automated test runner executing 32 unit, integration, black-box, and functional tests with live metrics, plus an **Interactive Manual Testing Studio**. |
| **🐛 Defect Management Dashboard** | [`defect-dashboard.html`](defect-dashboard.html) | Demonstrable defect lifecycle simulator: expose 6 controlled bugs in unpatched mode, apply verified code fixes, retest failed cases, and run the 32-test regression suite. |
| **📑 Final QA Executive Report (HTML)** | [`qa-report.html`](qa-report.html) | Formally certified, print-ready Quality Assurance Executive Report with traceability matrix, sign-off blocks, and deployment readiness checklists. |
| **📋 Test Cases Specification** | [`TEST_CASES.md`](TEST_CASES.md) | Exhaustive test case documentation with preconditions, test data, steps, expected/actual results, and status. |
| **🐞 Defect Tracking Report** | [`DEFECT_REPORT.md`](DEFECT_REPORT.md) | Root-cause analysis, severity ratings, reproduction steps, code patches, and verification logs for all defects. |
| **📄 Final QA Report (Markdown)** | [`QA_REPORT.md`](QA_REPORT.md) | Formatted Markdown QA report for repository auditing and academic grading. |
| **🚀 Deployment Guide** | [`DEPLOYMENT.md`](DEPLOYMENT.md) | Step-by-step deployment guide for GitHub Pages, Netlify, and local static servers. |

---

## 🏛️ Project Architecture & Design Patterns

The codebase is organized into clean, decoupled architectural layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│   index.html (Semantic HTML5)  │  styles.css (CSS3 Variables & Animations)  │
│   app.js (DOM Controllers, Event Delegation, Cart Drawer & Modal Views)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ calls
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    UNIVERSAL BUSINESS DOMAIN ENGINE                         │
│                           ecommerce-core.js                                 │
│   - Financial Calculations (Subtotal, 5% Tax, Free Shipping Threshold)      │
│   - Financial Quantization & Rounding (Number.EPSILON Decimal Safety)       │
│   - Inventory Bounds, Stock Tracking & Real-Time Stock Availability         │
│   - Strict Regular Expression Validation (Name, Email, Phone, Card, CVV)   │
│   - Order Processing, Invoice Generation & LocalStorage Serialization       │
└──────────────────────┬───────────────────────────────┬──────────────────────┘
                       │ shared by                     │ shared by
┌──────────────────────▼───────────────┐ ┌─────────────▼──────────────────────┐
│       TEST AUTOMATION FRAMEWORK      │ │     DEFECT MANAGEMENT & QA ENGINE  │
│   - test-dashboard.html & test-runner│ │   - defect-dashboard.html & js     │
│   - Manual Test Execution Studio     │ │   - defect-engine.js (Bug Matrix)  │
│   - tests/ecommerce.test.js (CLI)    │ │   - tests/defects.test.js (CLI)    │
└──────────────────────────────────────┘ └────────────────────────────────────┘
```

### Universal Module Definition (UMD)
The business logic in [`ecommerce-core.js`](ecommerce-core.js) and defect engine in [`defect-engine.js`](defect-engine.js) use the Universal Module Definition pattern. They export cleanly to:
- **Browser Runtime**: Bound directly to `window.ECommerceCore` and `window.DefectQAEngine`.
- **Node.js Environment**: Exported via `module.exports` for headless automated CLI testing (`node --test` or `jest`).
- **Zero CORS / File Origin Constraints**: Operates without ES module import restrictions, enabling direct double-click opening via the `file:///` protocol.

---

## 📚 Core Functions Reference & API Documentation

All calculation, validation, and domain logic is encapsulated inside [`ecommerce-core.js`](ecommerce-core.js).

### 1. Calculation & Pricing Engine

#### `Core.formatPrice(val)`
- **Purpose**: Converts any raw numeric monetary value into a formatted currency string.
- **Parameters**: `val` *(number | string)* — Numeric value (e.g., `99.99`).
- **Returns**: `string` — Formatted price (e.g., `"$99.99"`). Handles `NaN` gracefully with fallback `"$0.00"`.

#### `Core.roundMoney(val)`
- **Purpose**: Quantizes floating-point arithmetic to exactly 2 decimal places using `Number.EPSILON` to eliminate IEEE-754 precision leakage.
- **Parameters**: `val` *(number)* — Raw computed floating-point value.
- **Returns**: `number` — Two-decimal rounded float (e.g., `19.99 * 7` &rarr; `139.93` instead of `139.92999999999998`).

#### `Core.calculateLineTotal(price, quantity)`
- **Purpose**: Calculates the total price for a line item based on unit price and quantity.
- **Parameters**: `price` *(number)*, `quantity` *(number)*.
- **Returns**: `number` — Line total rounded via `roundMoney()`.

#### `Core.calculateCartTotals(cart, products)`
- **Purpose**: Calculates the complete pricing breakdown for the active shopping cart.
- **Parameters**: 
  - `cart` *(Array<{id: string, quantity: number}>)*
  - `products` *(Array<Product>)*
- **Returns**: `Object`:
  ```javascript
  {
    subtotal: 260.00,  // Sum of (price * quantity)
    tax: 13.00,        // Exactly 5% standard sales tax
    shipping: 0.00,    // $5.00 flat fee; Free ($0.00) if subtotal >= $50.00
    total: 273.00,     // subtotal + tax + shipping
    itemCount: 5       // Total units across all items
  }
  ```

---

### 2. Stock & Cart Management API

#### `Core.isProductInStock(product)`
- **Parameters**: `product` *(Product)*.
- **Returns**: `boolean` — `true` if `product.stock > 0`, otherwise `false`.

#### `Core.getAvailableStock(product, cart)`
- **Parameters**: `product` *(Product)*, `cart` *(Array<CartItem>)*.
- **Returns**: `number` — Remaining available inventory accounting for units currently reserved in the customer's cart:
  $$\text{Available Stock} = \max(0, \text{product.stock} - \text{quantityInCart})$$

#### `Core.addToCart(cart, products, productId, quantityToAdd = 1)`
- **Purpose**: Adds or increments product quantity with stock boundary validation.
- **Validation**:
  1. Validates `quantityToAdd` is a positive integer (`Number.isInteger()`).
  2. Ensures product exists and has `stock > 0`.
  3. Verifies cumulative quantity: `currentCartQty + quantityToAdd <= product.stock`.
- **Returns**: `{ success: boolean, cart: Array, error?: string }`.

#### `Core.updateCartQuantity(cart, products, productId, newQuantity)`
- **Purpose**: Adjusts cart item quantity. If `newQuantity <= 0`, cleanly deletes the line item. If requested quantity exceeds stock, rejects the change.
- **Returns**: `{ success: boolean, removed?: boolean, cart: Array, error?: string }`.

#### `Core.removeFromCart(cart, productId)`
- **Purpose**: Removes a line item completely from the cart array.
- **Returns**: `{ success: true, cart: Array }`.

---

### 3. Search & Filtering Engine

#### `Core.filterAndSortProducts(products, filters)`
- **Parameters**:
  - `products` *(Array<Product>)*
  - `filters` *(Object)*:
    - `category`: `"all"` | `"Electronics"` | `"Audio"` | `"Wearables"` | `"Accessories"` | `"Home"`
    - `search`: Case-insensitive substring query matched against title, description, and category.
    - `inStockOnly`: `boolean` — Filters for items where `stock > 0`.
    - `sortBy`: `"featured"` | `"price-asc"` | `"price-desc"` | `"name-asc"` | `"name-desc"` | `"stock-desc"`.
- **Returns**: `Array<Product>` — Filtered and sorted product array.

---

### 4. Input Validation Rules & Regex Engine

Encapsulated in `Core.ValidationRules`:

| Rule Field | Validation Logic & Regex | Error Helper Prompt |
| :--- | :--- | :--- |
| `name` | `val.trim().length >= 3 && /^[a-zA-Z\s.'-]+$/.test(val.trim())` | *"Please enter a valid full name (at least 3 characters, letters only)."* |
| `email` | `/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val.trim())` | *"Please enter a valid email address (e.g., name@example.com)."* |
| `phone` | `val.replace(/\D/g, '').length >= 10 && <= 15` | *"Please enter a valid phone number with at least 10 digits."* |
| `city` | `val.trim().length >= 2` | *"Please enter a valid city name."* |
| `address` | `val.trim().length >= 5` | *"Please enter your street address (at least 5 characters)."* |
| `state` | `val.trim().length >= 2` | *"Please enter a state / province."* |
| `zip` | `/^[a-zA-Z0-9\s-]{4,10}$/.test(val.trim())` | *"Please enter a valid postal / ZIP code (4-10 characters)."* |
| `cardNum` | `digits.length >= 13 && digits.length <= 19` | *"Enter a valid 16-digit card number."* |
| `cardExpiry` | Future month/year comparison against `new Date()` | *"Enter valid future expiry date (MM/YY)."* |
| `cardCvv` | `/^\d{3,4}$/.test(val.trim())` | *"Enter a 3 or 4 digit CVV code."* |
| `upiId` | `/^[\w.-]+@[\w.-]+$/.test(val.trim())` | *"Enter a valid UPI ID (e.g., user@bank)."* |
| `quantity` | `Number.isInteger(num) && num > 0 && num <= stock` | *"Quantity must be a positive integer within available stock."* |

---

### 5. Checkout & Order Lifecycle API

#### `Core.validateCheckoutPayload(customer, payment)`
- **Purpose**: Executes real-time validation across all customer form fields and selected payment details.
- **Returns**: `{ isValid: boolean, errors: Record<string, string> }`.

#### `Core.processOrder(cart, products, customer, payment)`
- **Purpose**: Validates payload, verifies physical warehouse inventory, calculates totals, decrements product stock, records invoice snapshot, generates an immutable order reference ID, and empties the cart.
- **Returns**:
  ```javascript
  {
    success: true,
    order: {
      orderId: "ORD-849201-384",
      date: "2026-11-02T07:22:18.000Z",
      customer: { name, email, phone, address },
      paymentMethod: "Credit/Debit Card",
      items: [{ id, name, price, quantity, total }],
      subtotal: 199.98,
      tax: 10.00,
      shipping: 0.00,
      total: 209.98,
      status: "Confirmed"
    },
    updatedProducts: Array,
    clearedCart: []
  }
  ```

---

## 🧪 Testing Framework Architecture

The testing framework provides dual execution environments:

1. **In-Browser Test Runner (`test-dashboard.html`)**: Interactive UI with real-time metric counters, status filter tabs, individual re-run buttons, and the **Manual Testing Studio**.
2. **Automated CLI Runner (`node --test`)**: Zero-dependency headless runner reporting test results, assertions, and execution timings in terminal environments.

```
                              AuraMart Test Suite
                                       │
     ┌──────────────────┬──────────────┴─────┬──────────────────┐
     ▼                  ▼                    ▼                  ▼
1. Unit Tests     2. Integration       3. Black-Box       4. Functional
  (15 Tests)         (5 Tests)            (7 Tests)          (5 Tests)
  - Price Math       - Cart Lifecycle     - Empty Cart       - Catalog Search
  - Qty Constraints  - Quantity Recalc    - Bad Inputs       - Multi-Add
  - Tax & Shipping   - Order Placement    - Out-of-Stock     - Item Deletion
  - Stock Limits     - LocalStorage Sync  - Card Security    - E2E Checkout
```

---

## 📊 Complete Test Suite Matrix (32 Test Cases)

| Test ID | Suite | Target Module | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **`UT-PRICE-01`** | Unit | `formatPrice()` | `"$99.99"` | `"$99.99"` | **PASS** |
| **`UT-PRICE-02`** | Unit | `calculateLineTotal()` | `149.97` | `149.97` | **PASS** |
| **`UT-PRICE-03`** | Unit | `roundMoney()` Float Precision | `139.93` | `139.93` | **PASS** |
| **`UT-QTY-01`** | Unit | Positive integer quantity | `true` | `true` | **PASS** |
| **`UT-QTY-02`** | Unit | Rejection of decimal quantity (`2.5`) | `false` | `false` | **PASS** |
| **`UT-QTY-03`** | Unit | Rejection of zero quantity (`0`) | `false` | `false` | **PASS** |
| **`UT-QTY-04`** | Unit | Rejection of negative quantity (`-2`) | `false` | `false` | **PASS** |
| **`UT-CART-01`** | Unit | Multi-item subtotal calculation | `subtotal: 260.00` | `subtotal: 260.00` | **PASS** |
| **`UT-CART-02`** | Unit | Standard 5% sales tax calculation | `tax: 5.00` | `tax: 5.00` | **PASS** |
| **`UT-CART-03`** | Unit | $5.00 shipping for orders under $50 | `shipping: 5.00` | `shipping: 5.00` | **PASS** |
| **`UT-CART-04`** | Unit | Free shipping ($0.00) for orders $\ge \$50$ | `shipping: 0.00` | `shipping: 0.00` | **PASS** |
| **`UT-CART-05`** | Unit | Grand total (`subtotal + tax + shipping`) | `total: 26.00` | `total: 26.00` | **PASS** |
| **`UT-STOCK-01`** | Unit | In-stock product identification | `true` | `true` | **PASS** |
| **`UT-STOCK-02`** | Unit | Out-of-stock product identification | `false` | `false` | **PASS** |
| **`UT-STOCK-03`** | Unit | Remaining stock accounting for cart | `remaining: 4` | `remaining: 4` | **PASS** |
| **`IT-CART-01`** | Integration | Add product updates cart array | `length: 1, qty: 1` | `length: 1, qty: 1` | **PASS** |
| **`IT-QTY-01`** | Integration | Quantity update recalculates total | `qty: 3, total: 157.50` | `qty: 3, total: 157.50` | **PASS** |
| **`IT-ORDER-01`** | Integration | Checkout creates order & clears cart | `orderId: generated` | `orderId: generated` | **PASS** |
| **`IT-STORE-01`** | Integration | LocalStorage serialization & load | `stored: p1 x 2` | `stored: p1 x 2` | **PASS** |
| **`IT-STORE-02`** | Integration | Post-checkout stock decrement saved | `stock: 3` | `stock: 3` | **PASS** |
| **`BB-CHK-01`** | Black-Box | Rejection of empty cart checkout | `success: false` | `success: false` | **PASS** |
| **`BB-CUST-01`** | Black-Box | Malformed customer info flagged | `isValid: false` | `isValid: false` | **PASS** |
| **`BB-QTY-01`** | Black-Box | Rejection of negative quantity add | `success: false` | `success: false` | **PASS** |
| **`BB-QTY-02`** | Black-Box | Zero quantity removes line item | `removed: true` | `removed: true` | **PASS** |
| **`BB-STOCK-01`** | Black-Box | Rejection of out-of-stock product add | `success: false` | `success: false` | **PASS** |
| **`BB-INP-01`** | Black-Box | Rejection of expired card & short CVV | `isValid: false` | `isValid: false` | **PASS** |
| **`BB-INP-02`** | Black-Box | Acceptance of valid customer & card | `isValid: true` | `isValid: true` | **PASS** |
| **`FT-SRCH-01`** | Functional | Keyword search `"Headphones"` | `results >= 1` | `found 1 items` | **PASS** |
| **`FT-SRCH-02`** | Functional | Nonexistent search term handling | `found: 0 item(s)` | `found: 0 item(s)` | **PASS** |
| **`FT-CART-01`** | Functional | Add to cart updates badge & total | `qty: 2, subtotal: 199.98` | `qty: 2, subtotal: 199.98` | **PASS** |
| **`FT-CART-02`** | Functional | Remove from cart completely removes item | `remaining: 0` | `remaining: 0` | **PASS** |
| **`FT-E2E-01`** | Functional | End-to-end full purchasing workflow | `order: Confirmed` | `order: Confirmed` | **PASS** |

---

## 🔬 Interactive Browser Manual Testing Studio

Located in [`test-dashboard.html`](test-dashboard.html), the **Manual Testing Studio** allows quality assurance engineers to execute custom boundary values and verify execution traces in real time:

1. **Scenario Selection**:
   - `UT-PRICE`: Price Formatting & Precision Rounding
   - `UT-QTY`: Quantity Bounds & Warehouse Stock Availability
   - `UT-CART`: Subtotal, 5% Tax & Shipping Thresholds
   - `BB-CHK`: Empty Cart Checkout Prevention
   - `BB-CUST`: Customer Details & Regex Sanitization
   - `BB-INP`: Credit Card Calendar Expiry & CVV Length
2. **Custom Parameter Inputs**: Testers can enter arbitrary unit prices, stock limits, customer strings, card expiration dates, and CVVs.
3. **Preset Buttons**:
   - **Load Valid Sample**: Fills in compliant data vectors.
   - **Load Boundary Failure**: Fills in malicious or boundary edge cases (e.g., negative qty, expired cards, unrounded decimals).
4. **Live Execution Terminal**: Displays execution steps, raw function outputs, expected assertions, and dynamic `PASS`/`FAIL` badges.
5. **Observation Logger**: Allows manual testers to type observations for record-keeping and audit sign-offs.

---

## 🐛 Defect Management & QA Module (6 Common Bugs)

The Defect Management module in [`defect-dashboard.html`](defect-dashboard.html) provides a demonstrable Software Testing and Quality Assurance lifecycle workflow:

```
┌────────────────┐      ┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  BUG DETECTED  │ ───► │ STATUS: OPEN │ ───► │ CODE PATCHED │ ───► │  VERIFIED   │
│ (Unpatched Fn) │      │ (Test Fails) │      │ (Core Fix)   │      │ (Status: OK)│
└────────────────┘      └─────────────┘      └──────────────┘      └─────────────┘
```

### 1. Defect Catalog & Root Cause Analyses

| Bug ID | Severity | Module | Description & Defect Vector | Expected vs. Actual (Buggy State) | Fix Applied |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`BUG-001`** | **High** | Price Math | Float precision artifacts (`19.99 * 7 = 139.92999999999998`). | **Exp**: `139.93`<br>**Act**: `139.92999999999998` | Quantized arithmetic using `roundMoney()` with `Number.EPSILON`. |
| **`BUG-002`** | **Critical** | Quantity | Decimal quantities (`2.5` headphones) accepted due to simple `num > 0` check. | **Exp**: `false` (rejected)<br>**Act**: `true` (accepted) | Enforced strict `Number.isInteger(num)` guard. |
| **`BUG-003`** | **High** | Stock Limits | Cart allowed adding items exceeding warehouse stock (`3 in cart + 4 added > 5`). | **Exp**: `success: false`<br>**Act**: `success: true` (oversold) | Checked cumulative cart quantity: `currentCartQty + qtyToAdd <= stock`. |
| **`BUG-004`** | **Critical** | Checkout | Empty cart checkout allowed, creating $0 ghost orders. | **Exp**: `success: false`<br>**Act**: `success: true` | Added mandatory empty cart guard in `processOrder()`. |
| **`BUG-005`** | **Medium** | Customer Form | Whitespace-only names (`"   "`) and letters in phone numbers accepted. | **Exp**: `isValid: false`<br>**Act**: `isValid: true` | String trim and regex validation for names (`/^[a-zA-Z\s.'-]+$/`) and 10-digit phones. |
| **`BUG-006`** | **High** | Payment | Expired cards (`01/20`) and 1-digit CVV accepted without calendar comparison. | **Exp**: `isValid: false`<br>**Act**: `isValid: true` | Temporal date comparison against current year/month and strict `/^\d{3,4}$/` CVV check. |

### 2. Demonstrable Lifecycle Workflow

Testers can demonstrate the complete defect life cycle with three dedicated action buttons in [`defect-dashboard.html`](defect-dashboard.html):

1. **Step 1: Expose Common Bugs (Simulate Pre-Fix)**:
   - Executes the controlled unpatched code implementations.
   - Dynamic metrics shift to: **Passed: 26** &bull; **Failed: 6** &bull; **Open Bugs: 6** &bull; **Resolved: 0** &bull; **Pass Rate: 81%**.
   - Defect table displays red **`Open`** badges with actual defective outputs.
2. **Step 2: Apply Fixes & Rerun Failed Tests**:
   - Injects the validated patches into the execution pipeline.
   - Automatically reruns the failed test cases.
   - Dynamic metrics shift to: **Passed: 32** &bull; **Failed: 0** &bull; **Open Bugs: 0** &bull; **Resolved: 6** &bull; **Pass Rate: 100%**.
   - Status updates to green **`Resolved`** with code fix descriptions.
3. **Step 3: Run Full Regression Testing**:
   - Executes all 32 test cases across the system.
   - Confirms zero regressions in the dark Regression Console.

---

## 📋 Requirement Traceability Matrix

| Requirement | Description | Test Case(s) | Defect ID | Status |
| :--- | :--- | :--- | :--- | :---: |
| **REQ-01** | Display products with name, price, stock | `UT-PRICE-01`, `UT-STOCK-01`, `UT-STOCK-02` | `BUG-001` | **Verified** |
| **REQ-02** | Search and filter products by category | `FT-SRCH-01`, `FT-SRCH-02` | N/A | **Verified** |
| **REQ-03** | Add products to cart with stock validation | `IT-CART-01`, `FT-CART-01` | `BUG-002`, `BUG-003` | **Verified** |
| **REQ-04** | Increase/decrease quantities with boundary limits | `UT-QTY-01`, `IT-QTY-01`, `BB-QTY-02` | `BUG-002`, `BUG-003` | **Verified** |
| **REQ-05** | Remove products from cart & clear cart | `BB-QTY-02`, `FT-CART-02` | N/A | **Verified** |
| **REQ-06** | Subtotal, 5% tax, tiered shipping, total calculation | `UT-PRICE-02`, `UT-PRICE-03`, `UT-CART-01..05` | `BUG-001` | **Verified** |
| **REQ-07** | Checkout with validated customer details | `IT-ORDER-01`, `BB-INP-02`, `FT-E2E-01` | `BUG-004`, `BUG-005`, `BUG-006` | **Verified** |
| **REQ-08** | Order confirmation receipt & printable invoice | `IT-ORDER-01`, `FT-E2E-01` | `BUG-004` | **Verified** |
| **REQ-09** | Input sanitization & regex validation | `BB-CUST-01`, `BB-INP-01`, `BB-INP-02` | `BUG-005`, `BUG-006` | **Verified** |
| **REQ-10** | LocalStorage state synchronization | `IT-STORE-01`, `IT-STORE-02` | N/A | **Verified** |

---

## 💻 Automated CLI Test Execution

The automated test suite runs natively on **Node.js v18+** using the built-in `node:test` runner (zero external dependencies required):

```bash
# Run all test suites (35 tests: 32 functional + 3 defect lifecycle)
npm test

# Run only the 32 functional & unit tests
npm run test:unit

# Run only the defect lifecycle & regression suite
npm run test:defects

# Run with Jest or Vitest (if installed)
npm run test:jest
```

### CLI Output Preview:
```text
> node --test tests/*.test.js

--- EXPOSING BUGS IN CONTROLLED SCENARIOS ---
[BUG DETECTED] BUG-001 | Severity: High | Status: Open -> FAIL
[BUG DETECTED] BUG-002 | Severity: Critical | Status: Open -> FAIL
[BUG DETECTED] BUG-003 | Severity: High | Status: Open -> FAIL
[BUG DETECTED] BUG-004 | Severity: Critical | Status: Open -> FAIL
[BUG DETECTED] BUG-005 | Severity: Medium | Status: Open -> FAIL
[BUG DETECTED] BUG-006 | Severity: High | Status: Open -> FAIL
[PRE-FIX QA METRICS] Total: 32 | Passed: 26 | Failed: 6 | Pass Rate: 81%

--- APPLYING FIXES & RERUNNING FAILED TEST CASES ---
[BUG RESOLVED] BUG-001 | Status: Resolved -> PASS
[BUG RESOLVED] BUG-002 | Status: Resolved -> PASS
[BUG RESOLVED] BUG-003 | Status: Resolved -> PASS
[BUG RESOLVED] BUG-004 | Status: Resolved -> PASS
[BUG RESOLVED] BUG-005 | Status: Resolved -> PASS
[BUG RESOLVED] BUG-006 | Status: Resolved -> PASS
[POST-FIX QA METRICS] Total: 32 | Passed: 32 | Failed: 0 | Pass Rate: 100%

--- PERFORMING FULL REGRESSION TESTING ---
ℹ tests 35
ℹ suites 9
ℹ pass 35
ℹ fail 0
ℹ duration_ms 230.5ms
```

---

## 🚀 Static Web Deployment Guide

### Deploy to GitHub Pages (1-Click)
1. Push this repository to GitHub:
   ```bash
   git push -u origin main
   ```
2. In your GitHub repository, navigate to **Settings** &rarr; **Pages**.
3. Under **Build and deployment**:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main` / `/(root)`
4. Click **Save**. Your site will be live at:
   `https://<your-username>.github.io/<repo-name>/`
   *(The included `.nojekyll` file ensures all static assets and subfolders are published without interference).*

### Deploy to Netlify
1. Connect your repository to [Netlify](https://app.netlify.com).
2. Set **Publish directory** to `.` (root).
3. The included [`netlify.toml`](netlify.toml) and [`_redirects`](_redirects) files automatically handle routing and security headers.

### Run Locally (Offline)
Double-click [`index.html`](index.html), [`test-dashboard.html`](test-dashboard.html), or [`defect-dashboard.html`](defect-dashboard.html) to run directly in any browser without needing a web server.

---

## 📁 Repository Structure

```
STQA-project/
│
├── index.html              # Main E-Commerce store (catalog, cart drawer, checkout)
├── styles.css              # Main application styling (responsive grid, cards, modals)
├── app.js                  # Storefront DOM controller & event listeners
│
├── test-dashboard.html     # QA Test Suite Execution & Manual Testing Studio
├── test-dashboard.css      # Test Dashboard stylesheet
├── test-runner.js          # In-browser test runner engine & manual studio controller
│
├── defect-dashboard.html   # Defect Management & Bug Tracking Dashboard
├── defect-dashboard.css    # Defect Dashboard stylesheet
├── defect-dashboard.js     # Defect dashboard controller
├── defect-engine.js        # Defect engine (buggy vs fixed states & regression runner)
│
├── qa-report.html          # Final QA Executive Report (Printable HTML)
│
├── ecommerce-core.js       # Core business logic, validators & calculation algorithms (UMD)
│
├── tests/
│   ├── ecommerce.test.js   # 32 automated tests (Unit, Integration, Black Box, Functional)
│   └── defects.test.js     # Automated defect lifecycle & regression tests
│
├── package.json            # NPM test runner scripts
├── netlify.toml            # Netlify deployment configuration
├── _redirects              # Netlify SPA/clean routing rules
├── .nojekyll               # GitHub Pages static asset bypass
│
├── TEST_CASES.md           # Formal Test Case specifications & Traceability Matrix
├── DEFECT_REPORT.md        # Comprehensive Defect Tracking & Root-Cause Analysis
├── QA_REPORT.md            # Executive Quality Assurance Markdown Report
├── DEPLOYMENT.md           # Netlify & GitHub Pages Deployment Guide
└── README.md               # Complete project documentation & function reference
```

---

## 📜 License & Academic Integrity

This project is developed for the **Software Testing and Quality Assurance (STQA)** academic and engineering curriculum. Licensed under the [MIT License](LICENSE).
