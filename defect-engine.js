/**
 * AuraMart Defect Management & QA Engine
 * Universal Module (Node.js & Browser compatible)
 * 
 * Manages:
 * 1. Controlled Buggy Implementations (for demonstration of exposed defects)
 * 2. Patched / Fixed Implementations
 * 3. Bug Registry with Severity, Steps, Expected vs Actual
 * 4. Dynamic Regression Test Runner
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

  // Status definitions
  const STATUS = {
    OPEN: 'Open',
    RESOLVED: 'Resolved',
    REOPENED: 'Re-Opened'
  };

  // 6 Controlled Bug Specifications
  const BUG_DEFINITIONS = [
    {
      id: 'BUG-001',
      title: 'Floating-Point Currency Rounding Artifacts in Line Totals',
      category: 'Calculations',
      severity: SEVERITY.HIGH,
      component: 'Price Calculation',
      description: 'Calculating price * quantity without decimal quantization produces IEEE-754 floating-point artifacts (e.g. 19.99 * 7 = 139.92999999999998 instead of $139.93).',
      stepsToReproduce: '1. Add 7 units of item priced at $19.99.\n2. Calculate line total.\n3. Observe raw unrounded float.',
      expected: '139.93',
      testCaseId: 'UT-PRICE-03',
      // The buggy implementation
      buggyFn: function () {
        const price = 19.99;
        const qty = 7;
        const raw = price * qty; // 139.92999999999998
        return {
          actual: String(raw),
          pass: raw === 139.93 // Fails!
        };
      },
      // The fixed implementation
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
      title: 'Fractional / Decimal Quantities Accepted in Cart',
      category: 'Quantity Validation',
      severity: SEVERITY.CRITICAL,
      component: 'Cart & Inventory',
      description: 'System accepts non-integer values (e.g. 2.5) because validation only checks if number > 0, leading to fractional inventory and prices.',
      stepsToReproduce: '1. Attempt to add 2.5 items to cart.\n2. Cart updates with quantity 2.5.',
      expected: 'false (Rejected with error)',
      testCaseId: 'UT-QTY-02',
      buggyFn: function () {
        // Buggy check: only num > 0
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
      title: 'Cart Quantity Can Exceed Total Physical Warehouse Stock',
      category: 'Stock Validation',
      severity: SEVERITY.HIGH,
      component: 'Stock Enforcement',
      description: 'If a customer already has 3 units in cart and adds 4 more when total stock is 5, system fails to verify cumulative cart quantity against inventory.',
      stepsToReproduce: '1. Product stock is 5.\n2. Cart already holds 3.\n3. Add 4 more.\n4. Cart now holds 7 (oversold).',
      expected: 'success: false, Error: Cannot add 4. Only 2 more available.',
      testCaseId: 'UT-STOCK-03',
      buggyFn: function () {
        const prod = { id: 'p1', stock: 5 };
        const cart = [{ id: 'p1', quantity: 3 }];
        const qtyToAdd = 4;
        // Buggy check: only checks if qtyToAdd <= prod.stock (4 <= 5), ignoring 3 in cart!
        const allowed = qtyToAdd <= prod.stock;
        const newTotalInCart = cart[0].quantity + qtyToAdd; // 7!
        return {
          actual: `allowed: ${allowed}, newCartQty: ${newTotalInCart}`,
          pass: allowed === false // Fails because allowed is true!
        };
      },
      fixedFn: function () {
        const prods = [{ id: 'p1', stock: 5, price: 50 }];
        const cart = [{ id: 'p1', quantity: 3 }];
        const res = Core.addToCart(cart, prods, 'p1', 4);
        return {
          actual: `success: ${res.success}, error: "${res.error}"`,
          pass: res.success === false && res.error.includes('Only 2 more available') // Passes!
        };
      },
      fixExplanation: 'Added cumulative stock bounds check (currentQty + qtyToAdd <= product.stock) before appending to cart.'
    },
    {
      id: 'BUG-004',
      title: 'Empty Cart Checkout Creates Invalid Ghost Order',
      category: 'Checkout Validation',
      severity: SEVERITY.CRITICAL,
      component: 'Checkout Controller',
      description: 'Calling checkout submission with empty cart succeeds, generating a $0 order invoice and polluting order history.',
      stepsToReproduce: '1. Empty shopping cart.\n2. Submit checkout payload.\n3. Order is created.',
      expected: 'success: false, error: Cannot checkout with an empty cart',
      testCaseId: 'BB-CHK-01',
      buggyFn: function () {
        // Buggy behavior: does not check cart.length
        const cart = [];
        const orderCreated = true;
        return {
          actual: `success: ${orderCreated}, orderId: ORD-BUGGY-001`,
          pass: orderCreated === false // Fails!
        };
      },
      fixedFn: function () {
        const cart = [];
        const customer = { name: 'Test', email: 'test@example.com', phone: '1234567890', address: 'Addr', city: 'City', state: 'ST', zip: '12345' };
        const res = Core.processOrder(cart, Core.INITIAL_PRODUCTS, customer, { method: 'cod' });
        return {
          actual: `success: ${res.success}, error: "${res.error}"`,
          pass: res.success === false && res.error.includes('empty cart') // Passes!
        };
      },
      fixExplanation: 'Added non-empty cart guard check: if (!cart || cart.length === 0) return { success: false, error: ... }.'
    },
    {
      id: 'BUG-005',
      title: 'Customer Details Accepts Whitespace Name & Alphanumeric Phone',
      category: 'Input Validation',
      severity: SEVERITY.MEDIUM,
      component: 'Customer Form',
      description: 'Form accepts spaces-only string ("   ") for name and letters inside phone numbers ("98765PHONE") due to simple length checks.',
      stepsToReproduce: '1. Enter "   " in name field.\n2. Enter "12345ABCDE" in phone.\n3. Submit form.',
      expected: 'isValid: false (Name letters-only, Phone digits-only)',
      testCaseId: 'BB-CUST-01',
      buggyFn: function () {
        const name = '   ';
        const phone = '12345ABCDE';
        // Buggy check: simple string length without trim or regex
        const isNameValid = name.length >= 3; // true!
        const isPhoneValid = phone.length >= 10; // true!
        return {
          actual: `nameValid: ${isNameValid}, phoneValid: ${isPhoneValid}`,
          pass: isNameValid === false && isPhoneValid === false // Fails!
        };
      },
      fixedFn: function () {
        const isNameValid = Core.ValidationRules.name.validate('   ');
        const isPhoneValid = Core.ValidationRules.phone.validate('12345ABCDE');
        return {
          actual: `nameValid: ${isNameValid}, phoneValid: ${isPhoneValid}`,
          pass: isNameValid === false && isPhoneValid === false // Passes!
        };
      },
      fixExplanation: 'Enforced trim and strict regex patterns: letters only for names, minimum 10 clean digits for phone numbers.'
    },
    {
      id: 'BUG-006',
      title: 'Payment Gateway Accepts Past Expiration Year & Single-Digit CVV',
      category: 'Payment Validation',
      severity: SEVERITY.HIGH,
      component: 'Payment Module',
      description: 'Expired credit card date (01/20) and 1-digit CVV ("9") are accepted because expiry is only checked for format MM/YY rather than date comparison.',
      stepsToReproduce: '1. Enter Card Expiry "01/20".\n2. Enter CVV "9".\n3. Submit card payment.',
      expected: 'isValid: false (Expiry must be in future, CVV 3-4 digits)',
      testCaseId: 'BB-INP-01',
      buggyFn: function () {
        const expiry = '01/20';
        const cvv = '9';
        // Buggy check: only regex format, no date comparison or CVV length
        const isFormatOk = /^\d{2}\/\d{2}$/.test(expiry); // true!
        const isCvvOk = cvv.length > 0; // true!
        return {
          actual: `expiryValid: ${isFormatOk}, cvvValid: ${isCvvOk}`,
          pass: isFormatOk === false && isCvvOk === false // Fails!
        };
      },
      fixedFn: function () {
        const isExpiryValid = Core.ValidationRules.cardExpiry.validate('01/20');
        const isCvvValid = Core.ValidationRules.cardCvv.validate('9');
        return {
          actual: `expiryValid: ${isExpiryValid}, cvvValid: ${isCvvValid}`,
          pass: isExpiryValid === false && isCvvValid === false // Passes!
        };
      },
      fixExplanation: 'Integrated temporal date comparison against current year/month and strict CVV digit length check (/^\\d{3,4}$/).'
    }
  ];

  // State
  class DefectManager {
    constructor() {
      this.bugs = JSON.parse(JSON.stringify(BUG_DEFINITIONS));
      this.bugStatusMap = new Map();
      this.simulatedState = 'fixed'; // 'buggy' or 'fixed'
      this.lastTestResults = [];
      this.initStatus();
    }

    initStatus() {
      this.bugs.forEach(b => {
        this.bugStatusMap.set(b.id, STATUS.RESOLVED);
      });
    }

    // Run controlled test scenario for a specific bug
    executeBugScenario(bugId, forceMode = null) {
      const bug = BUG_DEFINITIONS.find(b => b.id === bugId);
      if (!bug) return null;

      const mode = forceMode || this.simulatedState;
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

      // Update status
      const newStatus = isPass ? STATUS.RESOLVED : STATUS.OPEN;
      this.bugStatusMap.set(bug.id, newStatus);

      return {
        id: bug.id,
        title: bug.title,
        severity: bug.severity,
        component: bug.component,
        expected: bug.expected,
        actual: outcome.actual,
        pass: isPass,
        status: newStatus,
        mode,
        durationMs: duration,
        fixExplanation: bug.fixExplanation
      };
    }

    // Simulate pre-fix state to expose all common bugs
    simulateUnpatchedState() {
      this.simulatedState = 'buggy';
      const results = [];
      BUG_DEFINITIONS.forEach(b => {
        results.push(this.executeBugScenario(b.id, 'buggy'));
      });
      this.lastTestResults = results;
      return results;
    }

    // Apply bug fixes and rerun failed test cases
    applyFixesAndRerun() {
      this.simulatedState = 'fixed';
      const results = [];
      BUG_DEFINITIONS.forEach(b => {
        results.push(this.executeBugScenario(b.id, 'fixed'));
      });
      this.lastTestResults = results;
      return results;
    }

    // Run full regression testing against all 32 test cases in the test suite
    runRegressionSuite(testRegistry) {
      const results = [];
      const startTime = performance.now();

      testRegistry.forEach(tc => {
        const tStart = performance.now();
        let outcome = { actual: '', pass: false };
        try {
          outcome = tc.fn();
        } catch (e) {
          outcome = { actual: `Error: ${e.message}`, pass: false };
        }
        const dur = (performance.now() - tStart).toFixed(1);
        results.push({
          id: tc.id,
          suite: tc.suite,
          description: tc.description,
          expected: tc.expected,
          actual: outcome.actual,
          pass: Boolean(outcome.pass),
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
        passPercentage: Math.round((passedCount / results.length) * 100),
        durationMs: totalTime,
        results
      };
    }

    getSummary(testCount = 32) {
      let openBugs = 0;
      let resolvedBugs = 0;

      this.bugStatusMap.forEach(status => {
        if (status === STATUS.OPEN || status === STATUS.REOPENED) openBugs++;
        else if (status === STATUS.RESOLVED) resolvedBugs++;
      });

      const failedTests = openBugs; // in simulated buggy state, each bug fails a test
      const passedTests = Math.max(0, testCount - failedTests);
      const passPercentage = Math.round((passedTests / testCount) * 100);

      return {
        totalTests: testCount,
        passedTests,
        failedTests,
        openBugs,
        resolvedBugs,
        passPercentage,
        simulatedState: this.simulatedState
      };
    }
  }

  return {
    SEVERITY,
    STATUS,
    BUG_DEFINITIONS,
    DefectManager
  };
});
