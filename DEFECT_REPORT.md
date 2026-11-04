# AuraMart E-Commerce - Defect & Bug Tracking Report

**Document ID**: `STQA-DEF-REP-2026-V2`  
**Application**: AuraMart Pure Vanilla E-Commerce  
**Testing Framework**: Python / Pytest & JavaScript Dual Engine  
**Defect Management Lead**: QA & Defect Triage Engineering  
**Total Defects Tracked**: 6  
**Defects Resolved & Verified**: 6 (100%)  
**Active Open Defects**: 0  

---

## 1. Executive Defect Triage & Quality Metrics

### 1.1 Breakdown by Severity & Priority

| Defect ID | Title | Severity | Priority | Status | Requirement | Primary Test |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`BUG-001`** | Floating-Point Rounding Leakage | **High** | **P2 - High** | Resolved | `REQ-06` | `UT-PRICE-03` |
| **`BUG-002`** | Fractional / Decimal Quantities Accepted | **Critical** | **P1 - Critical** | Resolved | `REQ-03` | `UT-QTY-02` |
| **`BUG-003`** | Cart Exceeds Physical Stock Bounds | **High** | **P1 - Critical** | Resolved | `REQ-01` | `UT-STOCK-03` |
| **`BUG-004`** | Empty Cart Checkout Ghost Order | **Critical** | **P1 - Critical** | Resolved | `REQ-07` | `BB-CHK-01` |
| **`BUG-005`** | Whitespace Name & Alphanumeric Phone | **Medium** | **P3 - Medium** | Resolved | `REQ-09` | `BB-CUST-01` |
| **`BUG-006`** | Expired Credit Card & Short CVV | **High** | **P2 - High** | Resolved | `REQ-09` | `BB-INP-01` |

### 1.2 Severity Distribution

| Severity | Total Count | Resolved | Open | Resolution Rate |
| :--- | :---: | :---: | :---: | :---: |
| **Critical** | 2 | 2 | 0 | 100% |
| **High** | 3 | 3 | 0 | 100% |
| **Medium** | 1 | 1 | 0 | 100% |
| **Low** | 0 | 0 | 0 | N/A |
| **Total** | **6** | **6** | **0** | **100%** |

---

## 2. Comprehensive Defect Dossiers & Documented Root Causes

### Defect 1: `BUG-001`
- **Title**: Floating-Point Currency Rounding Artifacts in Line Totals
- **Severity**: **High**
- **Priority**: **P2 - High**
- **Status**: **Resolved**
- **Category**: Calculations
- **Component**: Price Calculation
- **Associated Requirement**: `REQ-06` (Financial Calculations & Precision)
- **Primary Test Case**: `UT-PRICE-03`
- **Impacted Tests to Rerun**: `UT-PRICE-01`, `UT-PRICE-02`, `UT-PRICE-03`, `IT-CART-02`, `BV-PRICE-01`, `REG-PRICE-01`
- **Description**: Standard binary float calculation (`price * quantity`) causes IEEE-754 precision leakage (e.g. `19.99 * 7 = 139.92999999999998`), cascading into inaccurate invoices and cart totals.
- **Documented Root Cause**: Double-precision IEEE-754 binary floating-point representation lacks native decimal quantization, causing float overflow artifacts on multiplications like `19.99 * 7`.
- **Steps to Reproduce**:
  1. Add 7 units of an item priced at $19.99.
  2. Inspect line total before string formatting.
  3. Observe precision artifact `139.92999999999998`.
- **Expected Result**: `139.93` (clean 2-decimal financial rounded number).
- **Actual Result (Defective)**: `139.92999999999998`.
- **Fix Applied**: Implemented dedicated financial rounding helper using `Number.EPSILON`:
  ```javascript
  function roundMoney(val) {
    return Math.round((Number(val) + Number.EPSILON) * 100) / 100;
  }
  ```
- **Verification**: Verified via Pytest (`python_tests/test_defects.py`) and browser runner &rarr; **PASS**.

---

### Defect 2: `BUG-002`
- **Title**: Fractional / Decimal Quantities Accepted into Cart
- **Severity**: **Critical**
- **Priority**: **P1 - Critical**
- **Status**: **Resolved**
- **Category**: Quantity Validation
- **Component**: Cart & Inventory
- **Associated Requirement**: `REQ-03` (Cart Quantity Constraints & Stock Bounds)
- **Primary Test Case**: `UT-QTY-02`
- **Impacted Tests to Rerun**: `UT-QTY-01`, `UT-QTY-02`, `UT-QTY-03`, `UT-QTY-04`, `BV-QTY-01`, `NEG-QTY-01`, `VAL-QTY-01`
- **Description**: Inputting non-integer quantities (e.g., `2.5` headphones) passes validation because the code only verified `qty > 0`.
- **Documented Root Cause**: Insufficient type checking only confirmed quantity was positive (`qty > 0`) without ensuring it was a whole integer (`Number.isInteger()` / `isinstance(qty, int)`).
- **Steps to Reproduce**:
  1. Submit quantity `2.5` to `addToCart()`.
  2. Cart records fractional quantity and prices items fractionally.
- **Expected Result**: Rejected with error `false (Rejected with error)`.
- **Actual Result (Defective)**: Quantity `2.5` accepted (`isValid: true`).
- **Fix Applied**: Added explicit integer guard using `Number.isInteger(num)`:
  ```javascript
  quantity: {
    validate: function (val, stock) {
      const num = Number(val);
      if (!Number.isInteger(num)) return false;
      if (num <= 0) return false;
      if (typeof stock === 'number' && num > stock) return false;
      return true;
    }
  }
  ```
- **Verification**: Verified via Pytest and browser runner &rarr; **PASS**.

---

### Defect 3: `BUG-003`
- **Title**: Cart Quantity Allowed to Exceed Total Physical Warehouse Stock
- **Severity**: **High**
- **Priority**: **P1 - Critical**
- **Status**: **Resolved**
- **Category**: Stock Validation
- **Component**: Stock Enforcement
- **Associated Requirement**: `REQ-01` (Product Catalog & Real-Time Stock Status)
- **Primary Test Case**: `UT-STOCK-03`
- **Impacted Tests to Rerun**: `UT-STOCK-01`, `UT-STOCK-02`, `UT-STOCK-03`, `IT-CART-01`, `BV-STOCK-01`, `NEG-STOCK-01`
- **Description**: If a customer already has 3 units in cart and adds 4 more when total stock is 5, system fails to verify cumulative cart quantity against inventory.
- **Documented Root Cause**: Inventory verification only checked newly submitted quantity against physical stock (`4 <= 5`), ignoring existing quantities already reserved in customer's active cart.
- **Steps to Reproduce**:
  1. Product stock is 5.
  2. Cart already holds 3 units.
  3. Add 4 more units.
  4. Cart now holds 7 units (overselling physical warehouse inventory).
- **Expected Result**: `success: false, Error: Cannot add 4. Only 2 more available.`
- **Actual Result (Defective)**: `allowed: true, newCartQty: 7`.
- **Fix Applied**: Enforced cumulative bounds verification in `addToCart()`:
  ```javascript
  const currentQty = cartItem ? cartItem.quantity : 0;
  if (currentQty + qty > product.stock) {
    return {
      success: false,
      error: `Cannot add ${qty}. Only ${product.stock - currentQty} more available.`
    };
  }
  ```
- **Verification**: Verified via Pytest and browser runner &rarr; **PASS**.

---

### Defect 4: `BUG-004`
- **Title**: Empty Cart Checkout Creates Invalid Ghost Order
- **Severity**: **Critical**
- **Priority**: **P1 - Critical**
- **Status**: **Resolved**
- **Category**: Checkout Validation
- **Component**: Checkout Controller
- **Associated Requirement**: `REQ-07` (Checkout Verification & Empty Cart Guard)
- **Primary Test Case**: `BB-CHK-01`
- **Impacted Tests to Rerun**: `BB-CHK-01`, `IT-ORDER-01`, `FT-E2E-01`, `NEG-ORD-01`, `VAL-ORD-01`
- **Description**: Submitting checkout with an empty cart succeeds, generating a $0 order invoice and polluting order history with empty item lists.
- **Documented Root Cause**: Missing guard clause checking cart length before initializing order processing, allowing ghost orders with $0 total.
- **Steps to Reproduce**:
  1. Empty shopping cart (`cart = []`).
  2. Call `processOrder()` with valid customer info.
  3. Order is generated and confirmed.
- **Expected Result**: `success: false, error: Cannot checkout with an empty cart`.
- **Actual Result (Defective)**: `success: true, orderId: ORD-BUGGY-001`.
- **Fix Applied**: Added guard clause at order processing entry point:
  ```javascript
  if (!Array.isArray(cart) || cart.length === 0) {
    return { success: false, error: 'Cannot checkout with an empty cart' };
  }
  ```
- **Verification**: Verified via Pytest and browser runner &rarr; **PASS**.

---

### Defect 5: `BUG-005`
- **Title**: Customer Details Accepts Whitespace-Only Name & Alphanumeric Phone
- **Severity**: **Medium**
- **Priority**: **P3 - Medium**
- **Status**: **Resolved**
- **Category**: Input Validation
- **Component**: Customer Form
- **Associated Requirement**: `REQ-09` (Form Input Validation & Payment Security)
- **Primary Test Case**: `BB-CUST-01`
- **Impacted Tests to Rerun**: `BB-CUST-01`, `UT-VAL-01`, `VAL-CUST-01`, `NEG-CUST-01`, `FT-CHK-01`
- **Description**: Passing `"   "` (spaces) for name and `"12345ABCDE"` for phone passed validation because check used raw `.length >= 3` without trimming or regex checks.
- **Documented Root Cause**: Inadequate input sanitation using simple length check without trimming whitespace and lack of strict regex patterns for name and phone.
- **Steps to Reproduce**:
  1. Enter `"   "` in name field.
  2. Enter `"12345ABCDE"` in phone.
  3. Submit checkout form.
- **Expected Result**: `isValid: false (Name letters-only, Phone digits-only)`.
- **Actual Result (Defective)**: `nameValid: true, phoneValid: true`.
- **Fix Applied**: Added string trimming and strict regular expressions:
  ```javascript
  name: {
    validate: (val) => val.trim().length >= 3 && /^[a-zA-Z\s.'-]+$/.test(val.trim())
  },
  phone: {
    validate: (val) => {
      const digits = String(val).replace(/\D/g, '');
      return digits.length >= 10 && digits.length <= 15;
    }
  }
  ```
- **Verification**: Verified via Pytest and browser runner &rarr; **PASS**.

---

### Defect 6: `BUG-006`
- **Title**: Payment Gateway Accepts Past Expiration Year & Single-Digit CVV
- **Severity**: **High**
- **Priority**: **P2 - High**
- **Status**: **Resolved**
- **Category**: Payment Validation
- **Component**: Payment Module
- **Associated Requirement**: `REQ-09` (Form Input Validation & Payment Security)
- **Primary Test Case**: `BB-INP-01`
- **Impacted Tests to Rerun**: `BB-INP-01`, `UT-VAL-03`, `VAL-PAY-01`, `NEG-PAY-01`, `FT-PAY-01`
- **Description**: Entering past expiration date (`01/20`) and 1-digit CVV (`"9"`) is processed without temporal card validation.
- **Documented Root Cause**: Syntax-only regex verification for MM/YY format without comparing date against current calendar month/year, and missing CVV length restriction.
- **Steps to Reproduce**:
  1. Enter Card Expiry `"01/20"`.
  2. Enter CVV `"9"`.
  3. Submit card payment.
- **Expected Result**: `isValid: false (Expiry must be in future, CVV 3-4 digits)`.
- **Actual Result (Defective)**: `expiryValid: true, cvvValid: true`.
- **Fix Applied**: Implemented temporal calendar comparison and strict 3-4 digit CVV check:
  ```javascript
  cardExpiry: {
    validate: function (val) {
      if (!/^(0[1-9]|1[0-2])\/?([0-9]{2})$/.test(val.trim())) return false;
      const [mStr, yStr] = val.split('/');
      const month = parseInt(mStr, 10);
      const year = parseInt('20' + yStr, 10);
      const now = new Date();
      return year > now.getFullYear() || (year === now.getFullYear() && month >= (now.getMonth() + 1));
    }
  },
  cardCvv: {
    validate: (val) => /^\d{3,4}$/.test(String(val).trim())
  }
  ```
- **Verification**: Verified via Pytest and browser runner &rarr; **PASS**.

---

## 3. Requirements Traceability Matrix (RTM)

The following matrix connects functional application requirements (`REQ-01` through `REQ-10`) to test cases and controlled defect IDs:

| Requirement ID | Requirement Scope | Category | Associated Test Cases | Mapped Defect(s) | Verification Status |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **`REQ-01`** | Product Catalog & Real-Time Stock Status | Catalog & Inventory | `UT-STOCK-01`, `UT-STOCK-02`, `UT-STOCK-03`, `IT-STORE-02`, `BV-STOCK-01`, `NEG-STOCK-01` | `BUG-003` | **Covered** |
| **`REQ-02`** | Product Search & Dynamic Category Filtering | Discovery | `FT-SRCH-01`, `FT-SRCH-02`, `FT-CAT-01`, `BV-SRCH-01` | None | **Covered** |
| **`REQ-03`** | Cart Quantity Constraints & Stock Bounds | Cart & Validation | `UT-QTY-01`, `UT-QTY-02`, `UT-QTY-03`, `UT-QTY-04`, `BB-QTY-01`, `BB-QTY-02`, `BV-QTY-01`, `VAL-QTY-01` | `BUG-002`, `BUG-003` | **Covered** |
| **`REQ-04`** | Shopping Cart Item Manipulation | Cart State | `IT-CART-01`, `IT-QTY-01`, `FT-CART-01`, `FT-CART-02`, `IT-STORE-01` | None | **Covered** |
| **`REQ-05`** | Inventory Synchronization on Order Completion | Inventory Management | `IT-STORE-02`, `FT-E2E-01` | None | **Covered** |
| **`REQ-06`** | Financial Calculations & Precision | Pricing & Taxes | `UT-PRICE-01`, `UT-PRICE-02`, `UT-PRICE-03`, `UT-CART-01`, `UT-CART-02`, `UT-CART-03`, `UT-CART-04`, `UT-CART-05`, `BV-PRICE-01`, `REG-PRICE-01` | `BUG-001` | **Covered** |
| **`REQ-07`** | Checkout Verification & Empty Cart Guard | Checkout | `BB-CHK-01`, `IT-ORDER-01`, `FT-E2E-01`, `NEG-ORD-01` | `BUG-004` | **Covered** |
| **`REQ-08`** | Order Processing & Persistent Receipt Generation | Orders | `IT-ORDER-01`, `FT-E2E-01`, `VAL-ORD-01` | `BUG-004` | **Covered** |
| **`REQ-09`** | Form Input Validation & Payment Security | Validation & Security | `BB-CUST-01`, `BB-INP-01`, `BB-INP-02`, `UT-VAL-01`, `UT-VAL-02`, `UT-VAL-03`, `VAL-CUST-01`, `VAL-PAY-01`, `NEG-PAY-01` | `BUG-005`, `BUG-006` | **Covered** |
| **`REQ-10`** | UI Responsiveness & Defect Visibility | UI / QA Dashboard | `PW-RESP-01`, `PW-NAV-01`, `PW-DEF-01` | None | **Covered** |

---

## 4. Test Rerun & Impact Analysis Engine

When a defect is resolved, the defect manager automatically inspects its component dependencies and calculates the exact targeted test set that must be rerun:

```python
# Automated rerun identification
impact_plan = defect_manager.identify_rerun_tests(["BUG-001", "BUG-002"])
# Output:
#   defect_ids: ['BUG-001', 'BUG-002']
#   rerun_test_ids: ['UT-PRICE-01', 'UT-PRICE-02', 'UT-PRICE-03', 'IT-CART-02', 'BV-PRICE-01', 'REG-PRICE-01', 'UT-QTY-01', 'UT-QTY-02', 'UT-QTY-03', 'UT-QTY-04', 'BV-QTY-01', 'NEG-QTY-01', 'VAL-QTY-01']
#   pytest_command: pytest python_tests/ -k "ut_price_01 or ut_price_02 or ut_price_03 or it_cart_02 or bv_price_01 or reg_price_01 or ut_qty_01 or ut_qty_02 or ut_qty_03 or ut_qty_04 or bv_qty_01 or neg_qty_01 or val_qty_01"
```

---

## 5. Failure Recording & Error Details Schema

When tests fail (such as during unpatched bug simulation or regression runs), every failure is logged with complete execution context:

| Field | Description | Example Value |
| :--- | :--- | :--- |
| `timestamp` | ISO-8601 UTC timestamp | `"2026-11-04T12:12:30.450Z"` |
| `test_id` | Unique test specification ID | `"UT-PRICE-03"` |
| `defect_id` | Linked defect identifier | `"BUG-001"` |
| `error_message` | Detailed failure explanation | `"Defect exposed: Floating-Point Currency Rounding Artifacts... Expected [139.93], but got [139.92999999999998]."` |
| `expected` | Expected test value | `"139.93"` |
| `actual` | Actual received value | `"139.92999999999998"` |
| `stack_trace` | Call stack or N/A | `"N/A"` |
| `status` | State of the failure record | `"Failed"` |

---

## 6. Summary of Passed, Failed, and Skipped Tests

| Metric | Simulated Unpatched State | Post-Fix Regression Suite | Full Python Pytest Suite |
| :--- | :---: | :---: | :---: |
| **Total Test Cases** | 32 | 32 | 192 |
| **Passed Tests** | 26 | 32 | 192 |
| **Failed Tests** | 6 | 0 | 0 |
| **Skipped Tests** | 0 | 0 | 0 |
| **Pass Percentage** | 81% | 100% | 100% |
| **Failure Rate** | 19% | 0% | 0% |
| **Open Defects** | 6 | 0 | 0 |
| **Resolved Defects** | 0 | 6 | 6 |
