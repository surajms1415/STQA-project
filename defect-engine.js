/**
 * AuraMart Defect Management & QA Engine
 * Universal Module (Node.js & Browser compatible)
 * 
 * Manages:
 * 1. Controlled Buggy Implementations (for demonstration of exposed defects)
 * 2. Patched / Fixed Implementations
 * 3. Bug Registry with Severity, Priority, Section, Testing Category Violations, and Documented Root Causes
 * 4. Interactive Section & Defect Injection
 * 5. Failure Detail Recording & Error Tracking
 * 6. Automated Rerun & Impact Test Identification
 * 7. Requirements Traceability Matrix (RTM)
 * 8. Dynamic Regression Test Runner with Passed, Failed, and Skipped Metrics
 */

(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory(require('./ecommerce-core.js'));
  } else {
    root.DefectQAEngine = factory(root.ECommerceCore);
  }
})(typeof self !== 'undefined' ? self : this, function (Core) {
  'use strict';

  // Severity definitions
  const SEVERITY = {
    CRITICAL: 'Critical',
    HIGH: 'High',
    MEDIUM: 'Medium',
    LOW: 'Low'
  };

  // Priority definitions
  const PRIORITY = {
    P1: 'P1 - Critical',
    P2: 'P2 - High',
    P3: 'P3 - Medium',
    P4: 'P4 - Low'
  };

  // Status definitions
  const STATUS = {
    OPEN: 'Open',
    RESOLVED: 'Resolved',
    REOPENED: 'Re-Opened'
  };

  // Sections
  const SECTIONS = [
    'Pricing & Calculations',
    'Cart & Inventory Operations',
    'Checkout & Order Processing',
    'Customer Form Validation',
    'Payment Security & Data Privacy',
    'Product Discovery & Search'
  ];

  const STORAGE_KEY_DEFECTS = 'auramart_active_defects';

  function isDefectActive(bugId) {
    try {
      if (typeof localStorage !== 'undefined') {
        const stored = localStorage.getItem(STORAGE_KEY_DEFECTS);
        if (stored) {
          const list = JSON.parse(stored);
          return Array.isArray(list) && list.includes(bugId);
        }
      }
    } catch (e) {
      // fallback
    }
    return false;
  }

  // Comprehensive 16 Controlled Bug Specifications across all E-Commerce & QA Sections
  const BUG_DEFINITIONS = [
    {
      id: 'BUG-001',
      section: 'Pricing & Calculations',
      title: 'Floating-Point Currency Rounding Artifacts in Line Totals',
      category: 'Calculations',
      severity: SEVERITY.HIGH,
      priority: PRIORITY.P2,
      requirementId: 'REQ-06',
      component: 'Price Calculation',
      violatedTesting: ['Unit Testing', 'Boundary Value Testing'],
      description: 'Calculating price * quantity without decimal quantization produces IEEE-754 floating-point artifacts (e.g. 19.99 * 7 = 139.92999999999998 instead of $139.93).',
      rootCause: 'Double-precision IEEE-754 binary floating-point representation lacks native decimal quantization, causing float overflow artifacts on multiplications like 19.99 * 7.',
      stepsToReproduce: '1. Add 7 units of item priced at $19.99.\n2. Calculate line total.\n3. Observe raw unrounded float: 139.92999999999998.',
      expected: '139.93',
      testCaseId: 'UT-PRICE-03',
      impactedTests: ['UT-PRICE-01', 'UT-PRICE-02', 'UT-PRICE-03', 'IT-CART-02', 'BV-PRICE-01', 'REG-PRICE-01'],
      buggyFn: function () {
        const price = 19.99;
        const qty = 7;
        const raw = price * qty; // 139.92999999999998
        return {
          actual: String(raw),
          pass: raw === 139.93 // Fails!
        };
      },
      fixedFn: function () {
        const price = 19.99;
        const qty = 7;
        const fixed = Core.calculateLineTotal(price, qty); // 139.93
        return {
          actual: String(fixed),
          pass: fixed === 139.93 // Passes!
        };
      },
      fixExplanation: 'Applied roundMoney() with Number.EPSILON to guarantee two-decimal precision without float leakage.'
    },
    {
      id: 'BUG-002',
      section: 'Cart & Inventory Operations',
      title: 'Fractional / Decimal Quantities Accepted in Cart',
      category: 'Quantity Validation',
      severity: SEVERITY.CRITICAL,
      priority: PRIORITY.P1,
      requirementId: 'REQ-03',
      component: 'Cart & Inventory',
      violatedTesting: ['Unit Testing', 'Negative Testing', 'Validation Testing'],
      description: 'System accepts non-integer values (e.g. 2.5) because validation only checks if number > 0, leading to fractional inventory and prices.',
      rootCause: 'Insufficient type checking only confirmed quantity was positive (qty > 0) without ensuring it was a whole integer.',
      stepsToReproduce: '1. Attempt to add 2.5 items to cart.\n2. Cart updates with quantity 2.5 without error.',
      expected: 'false (Rejected with error)',
      testCaseId: 'UT-QTY-02',
      impactedTests: ['UT-QTY-01', 'UT-QTY-02', 'UT-QTY-03', 'UT-QTY-04', 'BV-QTY-01', 'NEG-QTY-01', 'VAL-QTY-01'],
      buggyFn: function () {
        const qty = 2.5;
        const isValid = (typeof qty === 'number' && qty > 0); // accepts 2.5!
        return {
          actual: `isValid: ${isValid}`,
          pass: isValid === false // Fails because isValid is true!
        };
      },
      fixedFn: function () {
        const qty = 2.5;
        const isValid = Core.ValidationRules.quantity.validate(qty, 10);
        return {
          actual: `isValid: ${isValid}`,
          pass: isValid === false // Passes!
        };
      },
      fixExplanation: 'Enforced Number.isInteger(num) check inside ValidationRules.quantity.'
    },
    {
      id: 'BUG-003',
      section: 'Cart & Inventory Operations',
      title: 'Cart Quantity Can Exceed Total Physical Warehouse Stock',
      category: 'Stock Validation',
      severity: SEVERITY.HIGH,
      priority: PRIORITY.P1,
      requirementId: 'REQ-01',
      component: 'Stock Enforcement',
      violatedTesting: ['Unit Testing', 'Boundary Value Testing', 'Integration Testing'],
      description: 'If a customer already has 3 units in cart and adds 4 more when total stock is 5, system fails to verify cumulative cart quantity against inventory.',
      rootCause: 'Inventory verification only checked newly submitted quantity against physical stock, ignoring existing quantities already reserved in customer\'s active cart.',
      stepsToReproduce: '1. Product stock is 5.\n2. Cart already holds 3.\n3. Add 4 more.\n4. Cart now holds 7 (oversold).',
      expected: 'success: false, Error: Cannot add 4. Only 2 more available.',
      testCaseId: 'UT-STOCK-03',
      impactedTests: ['UT-STOCK-01', 'UT-STOCK-02', 'UT-STOCK-03', 'IT-CART-01', 'BV-STOCK-01', 'NEG-STOCK-01'],
      buggyFn: function () {
        const prod = { id: 'p1', stock: 5 };
        const cart = [{ id: 'p1', quantity: 3 }];
        const qtyToAdd = 4;
        const allowed = qtyToAdd <= prod.stock;
        const newTotalInCart = cart[0].quantity + qtyToAdd;
        return {
          actual: `allowed: ${allowed}, newCartQty: ${newTotalInCart}`,
          pass: allowed === false
        };
      },
      fixedFn: function () {
        const prods = [{ id: 'p1', stock: 5, price: 50 }];
        const cart = [{ id: 'p1', quantity: 3 }];
        const res = Core.addToCart(cart, prods, 'p1', 4);
        return {
          actual: `success: ${res.success}, error: "${res.error}"`,
          pass: res.success === false && res.error.includes('Only 2 more available')
        };
      },
      fixExplanation: 'Added cumulative stock bounds check (currentQty + qtyToAdd <= product.stock) before appending to cart.'
    },
    {
      id: 'BUG-004',
      section: 'Checkout & Order Processing',
      title: 'Empty Cart Checkout Creates Invalid Ghost Order',
      category: 'Checkout Validation',
      severity: SEVERITY.CRITICAL,
      priority: PRIORITY.P1,
      requirementId: 'REQ-07',
      component: 'Checkout Controller',
      violatedTesting: ['Black-Box Testing', 'Integration Testing', 'Functional Testing'],
      description: 'Calling checkout submission with empty cart succeeds, generating a $0 order invoice and polluting order history.',
      rootCause: 'Missing guard clause checking cart length before initializing order processing, allowing ghost orders with $0 total.',
      stepsToReproduce: '1. Empty shopping cart.\n2. Submit checkout payload.\n3. Order is created.',
      expected: 'success: false, error: Cannot checkout with an empty cart',
      testCaseId: 'BB-CHK-01',
      impactedTests: ['BB-CHK-01', 'IT-ORDER-01', 'FT-E2E-01', 'NEG-ORD-01', 'VAL-ORD-01'],
      buggyFn: function () {
        const cart = [];
        const orderCreated = true;
        return {
          actual: `success: ${orderCreated}, orderId: ORD-BUGGY-001`,
          pass: orderCreated === false
        };
      },
      fixedFn: function () {
        const cart = [];
        const customer = { name: 'Test', email: 'test@example.com', phone: '1234567890', address: 'Addr', city: 'City', state: 'ST', zip: '12345' };
        const res = Core.processOrder(cart, Core.INITIAL_PRODUCTS, customer, { method: 'cod' });
        return {
          actual: `success: ${res.success}, error: "${res.error}"`,
          pass: res.success === false && res.error.includes('empty cart')
        };
      },
      fixExplanation: 'Added non-empty cart guard check: if (!cart || cart.length === 0) return { success: false, error: ... }.'
    },
    {
      id: 'BUG-005',
      section: 'Customer Form Validation',
      title: 'Customer Details Accepts Whitespace Name & Alphanumeric Phone',
      category: 'Input Validation',
      severity: SEVERITY.MEDIUM,
      priority: PRIORITY.P3,
      requirementId: 'REQ-09',
      component: 'Customer Form',
      violatedTesting: ['Black-Box Testing', 'Validation Testing'],
      description: 'Form accepts spaces-only string ("   ") for name and letters inside phone numbers ("98765PHONE") due to simple length checks.',
      rootCause: 'Inadequate input sanitation using simple length check without trimming whitespace and lack of strict regex patterns for name and phone.',
      stepsToReproduce: '1. Enter "   " in name field.\n2. Enter "12345ABCDE" in phone.\n3. Submit form.',
      expected: 'isValid: false (Name letters-only, Phone digits-only)',
      testCaseId: 'BB-CUST-01',
      impactedTests: ['BB-CUST-01', 'UT-VAL-01', 'VAL-CUST-01', 'NEG-CUST-01', 'FT-CHK-01'],
      buggyFn: function () {
        const name = '   ';
        const phone = '12345ABCDE';
        const isNameValid = name.length >= 3;
        const isPhoneValid = phone.length >= 10;
        return {
          actual: `nameValid: ${isNameValid}, phoneValid: ${isPhoneValid}`,
          pass: isNameValid === false && isPhoneValid === false
        };
      },
      fixedFn: function () {
        const isNameValid = Core.ValidationRules.name.validate('   ');
        const isPhoneValid = Core.ValidationRules.phone.validate('12345ABCDE');
        return {
          actual: `nameValid: ${isNameValid}, phoneValid: ${isPhoneValid}`,
          pass: isNameValid === false && isPhoneValid === false
        };
      },
      fixExplanation: 'Enforced trim and strict regex patterns: letters only for names, minimum 10 clean digits for phone numbers.'
    },
    {
      id: 'BUG-006',
      section: 'Payment Security & Data Privacy',
      title: 'Payment Gateway Accepts Past Expiration Year & Single-Digit CVV',
      category: 'Payment Validation',
      severity: SEVERITY.HIGH,
      priority: PRIORITY.P2,
      requirementId: 'REQ-09',
      component: 'Payment Module',
      violatedTesting: ['Security Testing', 'Black-Box Testing', 'Validation Testing'],
      description: 'Expired credit card date (01/20) and 1-digit CVV ("9") are accepted because expiry is only checked for format MM/YY rather than date comparison.',
      rootCause: 'Syntax-only regex verification for MM/YY format without comparing date against current calendar month/year, and missing CVV length restriction.',
      stepsToReproduce: '1. Enter Card Expiry "01/20".\n2. Enter CVV "9".\n3. Submit card payment.',
      expected: 'isValid: false (Expiry must be in future, CVV 3-4 digits)',
      testCaseId: 'BB-INP-01',
      impactedTests: ['BB-INP-01', 'UT-VAL-03', 'VAL-PAY-01', 'NEG-PAY-01', 'FT-PAY-01'],
      buggyFn: function () {
        const expiry = '01/20';
        const cvv = '9';
        const isFormatOk = /^\d{2}\/\d{2}$/.test(expiry);
        const isCvvOk = cvv.length > 0;
        return {
          actual: `expiryValid: ${isFormatOk}, cvvValid: ${isCvvOk}`,
          pass: isFormatOk === false && isCvvOk === false
        };
      },
      fixedFn: function () {
        const isExpiryValid = Core.ValidationRules.cardExpiry.validate('01/20');
        const isCvvValid = Core.ValidationRules.cardCvv.validate('9');
        return {
          actual: `expiryValid: ${isExpiryValid}, cvvValid: ${isCvvValid}`,
          pass: isExpiryValid === false && isCvvValid === false
        };
      },
      fixExplanation: 'Integrated temporal date comparison against current year/month and strict CVV digit length check (/^\\d{3,4}$/).'
    },
    {
      id: 'BUG-007',
      section: 'Pricing & Calculations',
      title: 'Free Shipping Threshold Boundary Flaw on Exactly $50.00 Order',
      category: 'Shipping Calculation',
      severity: SEVERITY.MEDIUM,
      priority: PRIORITY.P2,
      requirementId: 'REQ-06',
      component: 'Price Calculation',
      violatedTesting: ['Boundary Value Testing', 'Unit Testing'],
      description: 'Inequality operator `subtotal > 50` charges $5.00 shipping on orders of exactly $50.00 instead of granting free shipping per requirement.',
      rootCause: 'Off-by-one operator error: strictly greater-than (`>`) was used instead of greater-than-or-equal-to (`>=`).',
      stepsToReproduce: '1. Add items totaling exactly $50.00 to cart.\n2. Observe shipping fee is $5.00 instead of $0.00.',
      expected: 'shipping: 0.00',
      testCaseId: 'UT-CART-04',
      impactedTests: ['UT-CART-03', 'UT-CART-04', 'BV-PRICE-01', 'REG-PRICE-01'],
      buggyFn: function () {
        const subtotal = 50.00;
        const shipping = subtotal > 50.00 ? 0 : 5.00; // Buggy: evaluates to 5.00!
        return {
          actual: `shipping: ${shipping.toFixed(2)}`,
          pass: shipping === 0
        };
      },
      fixedFn: function () {
        const totals = Core.calculateCartTotals([{ id: 'p1', quantity: 1 }], [{ id: 'p1', price: 50.00 }]);
        return {
          actual: `shipping: ${totals.shipping.toFixed(2)}`,
          pass: totals.shipping === 0
        };
      },
      fixExplanation: 'Corrected boundary inequality comparison from `subtotal > 50` to `subtotal >= 50.00`.'
    },
    {
      id: 'BUG-008',
      section: 'Pricing & Calculations',
      title: '5% Standard Sales Tax Omission (Zero Tax Calculated)',
      category: 'Tax Calculation',
      severity: SEVERITY.HIGH,
      priority: PRIORITY.P2,
      requirementId: 'REQ-06',
      component: 'Price Calculation',
      violatedTesting: ['Unit Testing', 'Integration Testing'],
      description: 'Tax rate omitted or defaulted to 0, producing $0.00 sales tax on taxable merchandise and generating non-compliant financial totals.',
      rootCause: 'Omission of 0.05 standard tax multiplier in the cart summation routine.',
      stepsToReproduce: '1. Add $100.00 product to cart.\n2. Check tax computation.\n3. Tax evaluates to $0.00.',
      expected: 'tax: 5.00',
      testCaseId: 'UT-CART-02',
      impactedTests: ['UT-CART-02', 'UT-CART-05', 'IT-QTY-01', 'FT-E2E-01'],
      buggyFn: function () {
        const subtotal = 100.00;
        const tax = 0.00; // Buggy: zero tax
        return {
          actual: `tax: ${tax.toFixed(2)}`,
          pass: tax === 5.00
        };
      },
      fixedFn: function () {
        const totals = Core.calculateCartTotals([{ id: 'p1', quantity: 1 }], [{ id: 'p1', price: 100.00 }]);
        return {
          actual: `tax: ${totals.tax.toFixed(2)}`,
          pass: totals.tax === 5.00
        };
      },
      fixExplanation: 'Enforced roundMoney(subtotal * 0.05) to compute exact 5% sales tax.'
    },
    {
      id: 'BUG-009',
      section: 'Cart & Inventory Operations',
      title: 'Negative Quantity Input Allowed (Cart Subtotal Manipulation)',
      category: 'Quantity Validation',
      severity: SEVERITY.CRITICAL,
      priority: PRIORITY.P1,
      requirementId: 'REQ-03',
      component: 'Cart Controller',
      violatedTesting: ['Negative Testing', 'Black-Box Testing'],
      description: 'Negative quantities (e.g. -3) are accepted, artificially subtracting from cart subtotal and resulting in negative payable balances.',
      rootCause: 'Missing lower boundary check `qty <= 0` in cart addition controller.',
      stepsToReproduce: '1. Attempt to add -3 units of product to cart.\n2. Cart subtotal decrements.',
      expected: 'success: false, error: Quantity must be positive',
      testCaseId: 'BB-QTY-01',
      impactedTests: ['UT-QTY-04', 'BB-QTY-01', 'NEG-QTY-01'],
      buggyFn: function () {
        const qty = -3;
        const accepted = true; // Buggy: accepted!
        return {
          actual: `accepted: ${accepted}, qty: ${qty}`,
          pass: accepted === false
        };
      },
      fixedFn: function () {
        const res = Core.addToCart([], Core.INITIAL_PRODUCTS, 'p1', -3);
        return {
          actual: `success: ${res.success}, error: "${res.error}"`,
          pass: res.success === false
        };
      },
      fixExplanation: 'Added strict positive integer check: `if (quantity <= 0) return { success: false, error: ... }`.'
    },
    {
      id: 'BUG-010',
      section: 'Cart & Inventory Operations',
      title: 'Setting Quantity to Zero Leaves Phantom Item in Cart',
      category: 'Cart State',
      severity: SEVERITY.MEDIUM,
      priority: PRIORITY.P3,
      requirementId: 'REQ-04',
      component: 'Cart State Management',
      violatedTesting: ['Boundary Value Testing', 'Black-Box Testing'],
      description: 'Updating item quantity to 0 sets quantity property to 0 but fails to remove the product object from the cart array.',
      rootCause: 'Update logic lacked an automatic removal filter when quantity becomes 0.',
      stepsToReproduce: '1. Have 2 items in cart.\n2. Update quantity to 0.\n3. Cart length remains 1 with 0 qty.',
      expected: 'cartLength: 0 (Item removed)',
      testCaseId: 'BB-QTY-02',
      impactedTests: ['BB-QTY-02', 'FT-CART-02', 'BV-QTY-01'],
      buggyFn: function () {
        let cart = [{ id: 'p1', quantity: 2 }];
        cart[0].quantity = 0; // Buggy: item stays in cart with qty: 0
        return {
          actual: `cartLength: ${cart.length}, qty: ${cart[0].quantity}`,
          pass: cart.length === 0
        };
      },
      fixedFn: function () {
        const res = Core.updateCartQuantity([{ id: 'p1', quantity: 2 }], Core.INITIAL_PRODUCTS, 'p1', 0);
        return {
          actual: `cartLength: ${res.cart.length}`,
          pass: res.cart.length === 0
        };
      },
      fixExplanation: 'Integrated automatic array filtering: `cart = cart.filter(item => item.id !== productId)` when quantity is 0.'
    },
    {
      id: 'BUG-011',
      section: 'Cart & Inventory Operations',
      title: 'Out-of-Stock Product Addition Allowed to Shopping Cart',
      category: 'Stock Validation',
      severity: SEVERITY.HIGH,
      priority: PRIORITY.P1,
      requirementId: 'REQ-01',
      component: 'Inventory Controller',
      violatedTesting: ['Integration Testing', 'Black-Box Testing'],
      description: 'Products with inventory stock = 0 can still be added to shopping cart because add-to-cart lacks an initial zero stock check.',
      rootCause: 'Omission of `if (product.stock <= 0)` guard clause at top of `addToCart()` function.',
      stepsToReproduce: '1. Select product p10 (stock: 0).\n2. Click Add to Cart.\n3. Item is added.',
      expected: 'success: false, error: Product is out of stock',
      testCaseId: 'BB-STOCK-01',
      impactedTests: ['UT-STOCK-02', 'BB-STOCK-01', 'NEG-STOCK-01'],
      buggyFn: function () {
        const prod = { id: 'p10', stock: 0 };
        const added = true; // Buggy: added regardless of 0 stock
        return {
          actual: `added: ${added}, stock: ${prod.stock}`,
          pass: added === false
        };
      },
      fixedFn: function () {
        const res = Core.addToCart([], Core.INITIAL_PRODUCTS, 'p10', 1);
        return {
          actual: `success: ${res.success}, error: "${res.error}"`,
          pass: res.success === false && res.error.includes('out of stock')
        };
      },
      fixExplanation: 'Enforced guard `if (product.stock <= 0) return { success: false, error: "Product is out of stock" }`.'
    },
    {
      id: 'BUG-012',
      section: 'Customer Form Validation',
      title: 'Malformed Email Accepted Without Domain or @ Symbol',
      category: 'Email Validation',
      severity: SEVERITY.MEDIUM,
      priority: PRIORITY.P3,
      requirementId: 'REQ-09',
      component: 'Customer Form',
      violatedTesting: ['Validation Testing', 'Negative Testing'],
      description: 'Form allows plain strings like "invalidemail" without an "@" sign or valid top-level domain.',
      rootCause: 'Simple string length check `email.length > 5` instead of standard RFC-5322 regex validation.',
      stepsToReproduce: '1. Enter "bademail" into email field.\n2. Submit checkout form.\n3. Form accepts input.',
      expected: 'isValid: false (Requires valid email address)',
      testCaseId: 'BB-CUST-01',
      impactedTests: ['BB-CUST-01', 'VAL-CUST-01', 'NEG-CUST-01'],
      buggyFn: function () {
        const email = 'bademail';
        const isValid = email.length > 5; // Buggy: true!
        return {
          actual: `isValid: ${isValid}`,
          pass: isValid === false
        };
      },
      fixedFn: function () {
        const isValid = Core.ValidationRules.email.validate('bademail');
        return {
          actual: `isValid: ${isValid}`,
          pass: isValid === false
        };
      },
      fixExplanation: 'Enforced RFC-5322 regex pattern `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`.'
    },
    {
      id: 'BUG-013',
      section: 'Customer Form Validation',
      title: 'Postal Zip Code Accepts Letters & Invalid Short Lengths',
      category: 'Zip Code Validation',
      severity: SEVERITY.LOW,
      priority: PRIORITY.P4,
      requirementId: 'REQ-09',
      component: 'Customer Form',
      violatedTesting: ['Boundary Value Testing', 'Validation Testing'],
      description: 'Zip code field accepts non-numeric characters (e.g. "ABC") and 2-digit numbers without validating standard 5-digit postal format.',
      rootCause: 'Missing numeric pattern and length constraint check for zip code field.',
      stepsToReproduce: '1. Enter "12" or "ABC" in Zip field.\n2. Submit checkout.\n3. Form validates.',
      expected: 'isValid: false (Requires 5-digit postal zip code)',
      testCaseId: 'BB-CUST-01',
      impactedTests: ['BB-CUST-01', 'VAL-CUST-01', 'BV-QTY-01'],
      buggyFn: function () {
        const zip = '12';
        const isValid = zip.length > 0; // Buggy: true!
        return {
          actual: `isValid: ${isValid}`,
          pass: isValid === false
        };
      },
      fixedFn: function () {
        const isValid = Core.ValidationRules.zip.validate('12');
        return {
          actual: `isValid: ${isValid}`,
          pass: isValid === false
        };
      },
      fixExplanation: 'Applied strict 5-digit regex pattern `/^\\d{5}(-\\d{4})?$/`.'
    },
    {
      id: 'BUG-014',
      section: 'Payment Security & Data Privacy',
      title: 'Sensitive Plaintext Credit Card CVV Stored in Confirmed Order',
      category: 'Data Privacy',
      severity: SEVERITY.CRITICAL,
      priority: PRIORITY.P1,
      requirementId: 'REQ-09',
      component: 'Payment Module',
      violatedTesting: ['Security Testing', 'Negative Testing'],
      description: 'Checkout engine saves full credit card CVV in plaintext within the order record stored in browser localStorage.',
      rootCause: 'Direct object shallow copying copied sensitive card details including CVV into persistent records.',
      stepsToReproduce: '1. Complete order with card CVV "456".\n2. Inspect saved order in localStorage.\n3. CVV is stored in plaintext.',
      expected: 'order.payment.cvv: undefined (CVV stripped)',
      testCaseId: 'BB-INP-01',
      impactedTests: ['BB-INP-01', 'SEC-EXPO-01', 'NEG-PAY-01'],
      buggyFn: function () {
        const payment = { method: 'card', cardNum: '4111222233334444', cvv: '456' };
        const storedOrder = { id: 'ORD-001', payment: { ...payment } }; // Buggy: CVV stored!
        const hasCvv = 'cvv' in storedOrder.payment;
        return {
          actual: `hasCvvStored: ${hasCvv}, cvvVal: "${storedOrder.payment.cvv}"`,
          pass: hasCvv === false
        };
      },
      fixedFn: function () {
        const customer = { name: 'Alice Walker', email: 'a@e.com', phone: '9876543210', address: '123 Main St', city: 'New York', state: 'NY', zip: '10001' };
        const payment = { method: 'card', cardNum: '4111222233334444', cardExpiry: '12/29', cardCvv: '456' };
        const res = Core.processOrder([{ id: 'p1', quantity: 1 }], Core.INITIAL_PRODUCTS, customer, payment);
        const orderStr = JSON.stringify(res.order || {});
        const hasCvv = orderStr.includes('456');
        return {
          actual: `hasCvvStored: ${hasCvv}`,
          pass: res.success === true && hasCvv === false
        };
      },
      fixExplanation: 'Explicitly omitted CVV and masked PAN before serializing order to persistent storage.'
    },
    {
      id: 'BUG-015',
      section: 'Payment Security & Data Privacy',
      title: 'Cross-Site Scripting (XSS) Payload Accepted in Customer Name',
      category: 'XSS Prevention',
      severity: SEVERITY.HIGH,
      priority: PRIORITY.P1,
      requirementId: 'REQ-09',
      component: 'Security Sanitization',
      violatedTesting: ['Security Testing', 'Negative Testing'],
      description: 'Form accepts raw `<script>alert(1)</script>` or `<img onerror=...>` inside customer name field without sanitization.',
      rootCause: 'Missing HTML entity encoding and failure to restrict input characters in name validator.',
      stepsToReproduce: '1. Enter "<script>alert(1)</script>" as customer name.\n2. Form validates successfully.\n3. Script payload saved.',
      expected: 'isValid: false (Scripts rejected or escaped)',
      testCaseId: 'BB-CUST-01',
      impactedTests: ['BB-CUST-01', 'SEC-XSS-01', 'VAL-CUST-01'],
      buggyFn: function () {
        const payload = '<script>alert(1)</script>';
        const isAccepted = payload.length > 3; // Buggy: true!
        return {
          actual: `isAccepted: ${isAccepted}`,
          pass: isAccepted === false
        };
      },
      fixedFn: function () {
        const payload = '<script>alert(1)</script>';
        const isValid = Core.ValidationRules.name.validate(payload);
        return {
          actual: `isValid: ${isValid}`,
          pass: isValid === false
        };
      },
      fixExplanation: 'Enforced strict letter/space name regex and HTML entity encoding rejecting script tags.'
    },
    {
      id: 'BUG-016',
      section: 'Product Discovery & Search',
      title: 'Product Search Case Sensitivity Glitch (Uppercase Fails)',
      category: 'Catalog Search',
      severity: SEVERITY.MEDIUM,
      priority: PRIORITY.P3,
      requirementId: 'REQ-02',
      component: 'Search & Discovery',
      violatedTesting: ['Functional Testing', 'Black-Box Testing'],
      description: 'Search comparison `product.name.includes(query)` without case-folding causes searches like "HEADPHONES" to return 0 items.',
      rootCause: 'Missing `.toLowerCase()` conversion on both search target and user query.',
      stepsToReproduce: '1. Search for "HEADPHONES" in product search.\n2. 0 products found despite Headphones being in catalog.',
      expected: 'matches >= 1 (Case-insensitive matching)',
      testCaseId: 'FT-SRCH-01',
      impactedTests: ['FT-SRCH-01', 'FT-SRCH-02', 'BV-SRCH-01'],
      buggyFn: function () {
        const query = 'HEADPHONES';
        const prod = { name: 'Wireless Headphones' };
        const matches = prod.name.includes(query); // Buggy: false because case differs!
        return {
          actual: `matches: ${matches}`,
          pass: matches === true
        };
      },
      fixedFn: function () {
        const res = Core.filterAndSortProducts(Core.INITIAL_PRODUCTS, { search: 'HEADPHONES' });
        return {
          actual: `found: ${res.length} item(s)`,
          pass: res.length >= 1
        };
      },
      fixExplanation: 'Standardized query and catalog strings with `.toLowerCase().trim()` before substring evaluation.'
    }
  ];

  // Requirements Traceability Matrix (RTM)
  const TRACEABILITY_MATRIX = [
    {
      req_id: 'REQ-01',
      req_title: 'Product Catalog & Real-Time Stock Status',
      category: 'Catalog & Inventory',
      test_cases: ['UT-STOCK-01', 'UT-STOCK-02', 'UT-STOCK-03', 'IT-STORE-02', 'BV-STOCK-01', 'NEG-STOCK-01'],
      defect_ids: ['BUG-003', 'BUG-011'],
      status: 'Covered'
    },
    {
      req_id: 'REQ-02',
      req_title: 'Product Search & Dynamic Category Filtering',
      category: 'Discovery',
      test_cases: ['FT-SRCH-01', 'FT-SRCH-02', 'FT-CAT-01', 'BV-SRCH-01'],
      defect_ids: ['BUG-016'],
      status: 'Covered'
    },
    {
      req_id: 'REQ-03',
      req_title: 'Cart Quantity Constraints & Stock Bounds',
      category: 'Cart & Validation',
      test_cases: ['UT-QTY-01', 'UT-QTY-02', 'UT-QTY-03', 'UT-QTY-04', 'BB-QTY-01', 'BB-QTY-02', 'BV-QTY-01', 'VAL-QTY-01'],
      defect_ids: ['BUG-002', 'BUG-003', 'BUG-009'],
      status: 'Covered'
    },
    {
      req_id: 'REQ-04',
      req_title: 'Shopping Cart Item Manipulation',
      category: 'Cart State',
      test_cases: ['IT-CART-01', 'IT-QTY-01', 'FT-CART-01', 'FT-CART-02', 'IT-STORE-01'],
      defect_ids: ['BUG-010'],
      status: 'Covered'
    },
    {
      req_id: 'REQ-05',
      req_title: 'Inventory Synchronization on Order Completion',
      category: 'Inventory Management',
      test_cases: ['IT-STORE-02', 'FT-E2E-01'],
      defect_ids: [],
      status: 'Covered'
    },
    {
      req_id: 'REQ-06',
      req_title: 'Financial Calculations & Floating-Point Precision',
      category: 'Pricing & Taxes',
      test_cases: ['UT-PRICE-01', 'UT-PRICE-02', 'UT-PRICE-03', 'UT-CART-01', 'UT-CART-02', 'UT-CART-03', 'UT-CART-04', 'UT-CART-05', 'BV-PRICE-01', 'REG-PRICE-01'],
      defect_ids: ['BUG-001', 'BUG-007', 'BUG-008'],
      status: 'Covered'
    },
    {
      req_id: 'REQ-07',
      req_title: 'Checkout Verification & Empty Cart Guard',
      category: 'Checkout',
      test_cases: ['BB-CHK-01', 'IT-ORDER-01', 'FT-E2E-01', 'NEG-ORD-01'],
      defect_ids: ['BUG-004'],
      status: 'Covered'
    },
    {
      req_id: 'REQ-08',
      req_title: 'Order Processing & Persistent Receipt Generation',
      category: 'Orders',
      test_cases: ['IT-ORDER-01', 'FT-E2E-01', 'VAL-ORD-01'],
      defect_ids: ['BUG-004'],
      status: 'Covered'
    },
    {
      req_id: 'REQ-09',
      req_title: 'Form Input Validation & Payment Security Verification',
      category: 'Validation & Security',
      test_cases: ['BB-CUST-01', 'BB-INP-01', 'BB-INP-02', 'UT-VAL-01', 'UT-VAL-02', 'UT-VAL-03', 'VAL-CUST-01', 'VAL-PAY-01', 'NEG-PAY-01'],
      defect_ids: ['BUG-005', 'BUG-006', 'BUG-012', 'BUG-013', 'BUG-014', 'BUG-015'],
      status: 'Covered'
    },
    {
      req_id: 'REQ-10',
      req_title: 'User Interface Responsiveness & Defect Visibility',
      category: 'UI / QA Dashboard',
      test_cases: ['PW-RESP-01', 'PW-NAV-01', 'PW-DEF-01'],
      defect_ids: [],
      status: 'Covered'
    }
  ];

  // Defect Manager Class
  class DefectManager {
    constructor() {
      this.bugs = JSON.parse(JSON.stringify(BUG_DEFINITIONS));
      this.bugStatusMap = new Map();
      this.simulatedState = 'fixed'; // 'buggy' or 'fixed'
      this.lastTestResults = [];
      this.failureRecords = [];
      this.initStatus();
      this.loadFromStorage();
    }

    initStatus() {
      BUG_DEFINITIONS.forEach(b => {
        this.bugStatusMap.set(b.id, STATUS.RESOLVED);
      });
    }

    loadFromStorage() {
      try {
        if (typeof localStorage !== 'undefined') {
          const raw = localStorage.getItem(STORAGE_KEY_DEFECTS);
          if (raw) {
            const activeIds = JSON.parse(raw);
            if (Array.isArray(activeIds)) {
              BUG_DEFINITIONS.forEach(b => {
                if (activeIds.includes(b.id)) {
                  this.bugStatusMap.set(b.id, STATUS.OPEN);
                } else {
                  this.bugStatusMap.set(b.id, STATUS.RESOLVED);
                }
              });
              this.simulatedState = activeIds.length > 0 ? 'buggy' : 'fixed';
            }
          }
        }
      } catch (e) {
        // fallback
      }
    }

    saveToStorage() {
      try {
        if (typeof localStorage !== 'undefined') {
          const activeIds = [];
          this.bugStatusMap.forEach((status, bugId) => {
            if (status === STATUS.OPEN) {
              activeIds.push(bugId);
            }
          });
          localStorage.setItem(STORAGE_KEY_DEFECTS, JSON.stringify(activeIds));
          if (typeof window !== 'undefined' && typeof window.dispatchEvent === 'function') {
            window.dispatchEvent(new CustomEvent('auramart_defects_changed', { detail: { activeDefects: activeIds } }));
          }
        }
      } catch (e) {
        // fallback
      }
    }

    getActiveBugs() {
      const active = [];
      this.bugStatusMap.forEach((status, bugId) => {
        if (status === STATUS.OPEN) {
          const bug = BUG_DEFINITIONS.find(b => b.id === bugId);
          if (bug) active.push(bug);
        }
      });
      return active;
    }

    recordFailure(testId, errorMessage, expected, actual, stackTrace = null, defectId = null) {
      const record = {
        timestamp: new Date().toISOString(),
        testId: testId,
        defectId: defectId,
        errorMessage: errorMessage,
        expected: String(expected),
        actual: String(actual),
        stackTrace: stackTrace || 'N/A',
        status: 'Failed'
      };
      this.failureRecords.push(record);
      return record;
    }

    getFailureRecords() {
      return [...this.failureRecords];
    }

    clearFailureRecords() {
      this.failureRecords = [];
    }

    isBugOpen(bugId) {
      return this.bugStatusMap.get(bugId) === STATUS.OPEN;
    }

    // Run controlled test scenario for a specific bug
    executeBugScenario(bugId, forceMode = null) {
      const bug = BUG_DEFINITIONS.find(b => b.id === bugId);
      if (!bug) return null;

      const mode = forceMode || (this.isBugOpen(bugId) ? 'buggy' : 'fixed');

      // Pre-set status and storage to the target mode before invoking fn()
      // so that Core runtime methods see the intended defect active/inactive state
      const targetStatus = mode === 'buggy' ? STATUS.OPEN : STATUS.RESOLVED;
      this.bugStatusMap.set(bug.id, targetStatus);
      this.saveToStorage();

      const fn = mode === 'buggy' ? bug.buggyFn : bug.fixedFn;
      const startTime = performance.now();
      let outcome = { actual: '', pass: false };

      try {
        outcome = fn();
      } catch (e) {
        outcome = { actual: `Error: ${e.message}`, pass: false };
      }

      const duration = (performance.now() - startTime).toFixed(1);
      const isPass = Boolean(outcome.pass);

      // Confirm status based on verification outcome
      const newStatus = (mode === 'fixed')
        ? (isPass ? STATUS.RESOLVED : STATUS.OPEN)
        : STATUS.OPEN;

      this.bugStatusMap.set(bug.id, newStatus);
      this.saveToStorage();

      if (!isPass && mode === 'buggy') {
        this.recordFailure(
          bug.testCaseId,
          `Defect exposed: ${bug.title}. Expected [${bug.expected}], got [${outcome.actual}].`,
          bug.expected,
          outcome.actual,
          null,
          bug.id
        );
      } else if (newStatus === STATUS.RESOLVED) {
        this.failureRecords = this.failureRecords.filter(f => f.bugId !== bug.id);
      }

      const resObj = {
        id: bug.id,
        section: bug.section,
        title: bug.title,
        severity: bug.severity,
        priority: bug.priority,
        requirementId: bug.requirementId,
        component: bug.component,
        violatedTesting: bug.violatedTesting,
        expected: bug.expected,
        actual: outcome.actual,
        pass: isPass,
        status: newStatus,
        mode,
        durationMs: duration,
        fixExplanation: bug.fixExplanation,
        rootCause: bug.rootCause
      };

      const existingIdx = this.lastTestResults.findIndex(r => r.id === bug.id);
      if (existingIdx >= 0) {
        this.lastTestResults[existingIdx] = resObj;
      } else {
        this.lastTestResults.push(resObj);
      }

      return resObj;
    }

    // Inject a single error
    injectError(bugId) {
      this.bugStatusMap.set(bugId, STATUS.OPEN);
      this.saveToStorage();
      return this.executeBugScenario(bugId, 'buggy');
    }

    // Fix a single error
    fixError(bugId) {
      this.bugStatusMap.set(bugId, STATUS.RESOLVED);
      this.saveToStorage();
      return this.executeBugScenario(bugId, 'fixed');
    }

    // Inject all errors in a specific section
    injectSectionErrors(sectionName) {
      const results = [];
      BUG_DEFINITIONS.forEach(b => {
        if (!sectionName || sectionName === 'all' || b.section === sectionName) {
          results.push(this.executeBugScenario(b.id, 'buggy'));
        }
      });
      return results;
    }

    // Fix all errors in a specific section
    fixSectionErrors(sectionName) {
      const results = [];
      BUG_DEFINITIONS.forEach(b => {
        if (!sectionName || sectionName === 'all' || b.section === sectionName) {
          results.push(this.executeBugScenario(b.id, 'fixed'));
        }
      });
      return results;
    }

    // Simulate pre-fix state to expose all 16 bugs
    simulateUnpatchedState() {
      this.simulatedState = 'buggy';
      this.clearFailureRecords();
      const results = [];
      BUG_DEFINITIONS.forEach(b => {
        results.push(this.executeBugScenario(b.id, 'buggy'));
      });
      this.lastTestResults = results;
      return results;
    }

    // Apply bug fixes to all 16 bugs and rerun failed test cases
    applyFixesAndRerun() {
      this.simulatedState = 'fixed';
      this.clearFailureRecords();
      BUG_DEFINITIONS.forEach(b => {
        this.bugStatusMap.set(b.id, STATUS.RESOLVED);
      });
      this.saveToStorage();
      const results = [];
      BUG_DEFINITIONS.forEach(b => {
        results.push(this.executeBugScenario(b.id, 'fixed'));
      });
      this.lastTestResults = results;
      return results;
    }

    // Identify which tests need to be rerun after fixing defects
    identifyRerunTests(defectIds = null) {
      const targetBugs = defectIds
        ? BUG_DEFINITIONS.filter(b => defectIds.includes(b.id))
        : BUG_DEFINITIONS.filter(b => this.bugStatusMap.get(b.id) === STATUS.RESOLVED);

      const impacted = [];
      const reasons = {};

      targetBugs.forEach(b => {
        const tests = b.impactedTests || [b.testCaseId];
        tests.forEach(t => {
          if (!impacted.includes(t)) impacted.push(t);
        });
        reasons[b.id] = {
          component: b.component,
          primaryTest: b.testCaseId,
          impactedTests: tests,
          fixExplanation: b.fixExplanation
        };
      });

      return {
        defectIds: targetBugs.map(b => b.id),
        rerunTestIds: impacted,
        totalRerunTests: impacted.length,
        pytestFilter: impacted.map(t => t.replace(/-/g, '_').toLowerCase()).join(' or '),
        reasons
      };
    }

    getTraceabilityMatrix() {
      return TRACEABILITY_MATRIX.map(req => ({
        ...req,
        defectDetails: req.defect_ids.map(did => ({
          defectId: did,
          status: this.bugStatusMap.get(did) || STATUS.RESOLVED
        }))
      }));
    }

    // Run full regression testing against test cases
    runRegressionSuite(testRegistry) {
      const results = [];
      const startTime = performance.now();

      testRegistry.forEach(tc => {
        const tStart = performance.now();
        let outcome = { actual: '', pass: false };
        try {
          // If a corresponding bug is currently open, fail this regression spec
          outcome = tc.fn(this);
        } catch (e) {
          outcome = { actual: `Error: ${e.message}`, pass: false };
        }
        const dur = (performance.now() - tStart).toFixed(1);
        const isPass = Boolean(outcome.pass);

        if (!isPass) {
          this.recordFailure(
            tc.id || 'UNKNOWN',
            `Regression failure: Expected [${tc.expected || 'Pass'}], got [${outcome.actual}].`,
            tc.expected || 'Pass',
            outcome.actual
          );
        }

        results.push({
          id: tc.id,
          suite: tc.suite,
          description: tc.description,
          expected: tc.expected || 'Pass',
          actual: outcome.actual,
          pass: isPass,
          durationMs: dur
        });
      });

      const totalTime = (performance.now() - startTime).toFixed(1);
      const passedCount = results.filter(r => r.pass).length;
      const failedCount = results.length - passedCount;

      return {
        total: results.length,
        passed: passedCount,
        failed: failedCount,
        passPercentage: results.length > 0 ? Math.round((passedCount / results.length) * 100) : 100,
        durationMs: totalTime,
        results
      };
    }

    getSummary(testCount = 32, skippedTests = 0) {
      let openBugs = 0;
      let resolvedBugs = 0;
      let reopenedBugs = 0;

      this.bugStatusMap.forEach(status => {
        if (status === STATUS.OPEN) openBugs++;
        else if (status === STATUS.RESOLVED) resolvedBugs++;
        else if (status === STATUS.REOPENED) reopenedBugs++;
      });

      const failedTests = Math.min(testCount, openBugs);
      const passedTests = Math.max(0, testCount - failedTests - skippedTests);
      const effectiveTested = testCount - skippedTests;
      const passPercentage = effectiveTested > 0 ? Math.round((passedTests / effectiveTested) * 100) : 0;
      const failureRate = effectiveTested > 0 ? Math.round((failedTests / effectiveTested) * 100) : 0;

      return {
        totalTests: testCount,
        passedTests,
        failedTests,
        skippedTests,
        totalBugs: BUG_DEFINITIONS.length,
        openBugs,
        resolvedBugs,
        reopenedBugs,
        passPercentage,
        failureRate,
        simulatedState: openBugs > 0 ? 'buggy' : 'fixed'
      };
    }
  }

  return {
    SEVERITY,
    PRIORITY,
    STATUS,
    SECTIONS,
    BUG_DEFINITIONS,
    TRACEABILITY_MATRIX,
    DefectManager,
    isDefectActive,
    STORAGE_KEY_DEFECTS
  };
});
