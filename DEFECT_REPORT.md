# AuraMart E-Commerce - Defect & Bug Tracking Report

**Document Version**: 1.0  
**Project**: AuraMart Software Testing & Quality Assurance (STQA)  
**Defect Management Lead**: QA & Defect Triage Engineering  
**Total Defects Identified**: 6  
**Defects Resolved & Verified**: 6 (100%)  
**Open Defects**: 0  

---

## 1. Defect Summary by Severity & Category

| Severity | Count | Resolved | Open | Percentage |
| :--- | :---: | :---: | :---: | :---: |
| **Critical** | 2 | 2 | 0 | 100% |
| **High** | 3 | 3 | 0 | 100% |
| **Medium** | 1 | 1 | 0 | 100% |
| **Low** | 0 | 0 | 0 | 100% |
| **Total** | **6** | **6** | **0** | **100%** |

---

## 2. Individual Defect Details

### Defect 1: `BUG-001`
- **Title**: Floating-Point Currency Rounding Artifacts in Line Totals
- **Severity**: **High**
- **Priority**: High
- **Category**: Price Calculation / Arithmetic Precision
- **Associated Test Case**: `UT-PRICE-03`
- **Environment**: All Browsers & Node.js
- **Description**: Standard binary float calculation (`price * quantity`) causes IEEE-754 precision leakage (e.g. `19.99 * 7 = 139.92999999999998`), which cascades into inaccurate invoice totals.
- **Steps to Reproduce**:
  1. Add 7 units of an item priced at $19.99.
  2. Inspect line total before string formatting.
  3. Observe precision artifact `139.92999999999998`.
- **Expected Result**: `$139.93` (clean 2-decimal rounded number).
- **Actual Result (Defective)**: `139.92999999999998`.
- **Root Cause**: JavaScript standard numbers are double-precision 64-bit binary floats without native decimal quantization.
- **Fix Applied**: Implemented dedicated financial rounding helper `roundMoney(val)`:
  ```javascript
  function roundMoney(val) {
    return Math.round((Number(val) + Number.EPSILON) * 100) / 100;
  }
  ```
- **Verification**: Retested under `UT-PRICE-03` &rarr; **Verified Fixed (PASS)**.

---

### Defect 2: `BUG-002`
- **Title**: Fractional / Decimal Quantities Accepted into Cart
- **Severity**: **Critical**
- **Priority**: Immediate
- **Category**: Cart & Quantity Validation
- **Associated Test Case**: `UT-QTY-02`
- **Description**: Inputting non-integer quantities (such as `2.5` headphones) passes validation because the code only verified `qty > 0`.
- **Steps to Reproduce**:
  1. Submit quantity `2.5` to `addToCart()`.
  2. Cart records fractional quantity and prices items fractionally.
- **Expected Result**: Validation fails; rejected with error *"Quantity must be an integer"*.
- **Actual Result (Defective)**: Quantity `2.5` accepted (`isValid: true`).
- **Root Cause**: Missing integer type check before accepting input payload.
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
- **Verification**: Retested under `UT-QTY-02` &rarr; **Verified Fixed (PASS)**.

---

### Defect 3: `BUG-003`
- **Title**: Cart Quantity Allowed to Exceed Total Physical Warehouse Stock
- **Severity**: **High**
- **Priority**: High
- **Category**: Stock Enforcement
- **Associated Test Case**: `UT-STOCK-03`
- **Description**: If a user already has 3 units in their cart and attempts to add 4 more when total stock is 5, the addition succeeded because the validation only checked the newly added quantity against total stock (`4 <= 5`), neglecting the units already in the cart.
- **Steps to Reproduce**:
  1. Product has stock = 5.
  2. Add 3 units to cart.
  3. Add 4 more units to cart.
  4. Cart now contains 7 units (overselling physical stock).
- **Expected Result**: Rejection with error *"Cannot add 4. Only 2 more available."*
- **Actual Result (Defective)**: Succeeded, cart quantity becomes 7.
- **Root Cause**: Validation checked single-event addition (`qty <= stock`) instead of cumulative cart quantity (`currentCartQty + qty <= stock`).
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
- **Verification**: Retested under `UT-STOCK-03` &rarr; **Verified Fixed (PASS)**.

---

### Defect 4: `BUG-004`
- **Title**: Empty Cart Checkout Creates Invalid Ghost Order
- **Severity**: **Critical**
- **Priority**: Immediate
- **Category**: Checkout Validation
- **Associated Test Case**: `BB-CHK-01`
- **Description**: Submitting an order when cart is empty creates an order invoice of $0.00 with empty items table in database/localStorage.
- **Steps to Reproduce**:
  1. Empty shopping cart (`cart = []`).
  2. Call `processOrder()` with valid customer info.
  3. Order is generated and confirmed.
- **Expected Result**: Rejection with error *"Cannot checkout with an empty cart"*.
- **Actual Result (Defective)**: Order confirmed with empty items array.
- **Root Cause**: Missing guard clause at the start of `processOrder()`.
- **Fix Applied**: Added guard clause:
  ```javascript
  if (!Array.isArray(cart) || cart.length === 0) {
    return { success: false, error: 'Cannot checkout with an empty cart' };
  }
  ```
- **Verification**: Retested under `BB-CHK-01` &rarr; **Verified Fixed (PASS)**.

---

### Defect 5: `BUG-005`
- **Title**: Customer Details Accepts Whitespace-Only Name & Alphanumeric Phone
- **Severity**: **Medium**
- **Priority**: Medium
- **Category**: Customer Input Validation
- **Associated Test Case**: `BB-CUST-01`
- **Description**: Passing `"   "` (spaces) for name and `"12345ABCDE"` for phone passed validation because check used raw `.length >= 3` without trimming or regex checks.
- **Steps to Reproduce**:
  1. Input `"   "` in customer name.
  2. Input `"12345ABCDE"` in customer phone.
  3. Submit checkout form.
- **Expected Result**: Validation fails; error prompts for valid letters-only name and 10-digit phone.
- **Actual Result (Defective)**: Accepted as valid strings.
- **Root Cause**: Inadequate string sanitization and absent character constraints.
- **Fix Applied**: Added string trim and strict regex patterns:
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
- **Verification**: Retested under `BB-CUST-01` &rarr; **Verified Fixed (PASS)**.

---

### Defect 6: `BUG-006`
- **Title**: Expired Credit Card Date & Single-Digit CVV Accepted
- **Severity**: **High**
- **Priority**: High
- **Category**: Payment Security & Validation
- **Associated Test Case**: `BB-INP-01`
- **Description**: Entering past expiration date (`01/20`) and 1-digit CVV (`"9"`) is processed without temporal card validation.
- **Steps to Reproduce**:
  1. Select Credit/Debit card payment.
  2. Enter Card Expiry `"01/20"`.
  3. Enter CVV `"9"`.
  4. Submit form.
- **Expected Result**: Validation fails; errors flagged for expired date and CVV length.
- **Actual Result (Defective)**: Accepted as valid payment.
- **Root Cause**: Only verified syntax pattern `/^\d{2}\/\d{2}$/` without comparing year and month against `new Date()`.
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
- **Verification**: Retested under `BB-INP-01` &rarr; **Verified Fixed (PASS)**.
