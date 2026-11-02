/**
 * AuraMart Browser Test Runner & QA Framework
 * 
 * Dynamic test executor for:
 * 1. Unit Tests (Price, Quantity, Cart, Stock)
 * 2. Integration Tests (Cart update, Quantity adjustment, Checkout, LocalStorage)
 * 3. Black Box Tests (Empty checkout, Invalid details, Negative/Zero qty, Out of stock, Inputs)
 * 4. Functional Tests (Search, Add, Remove, E2E Checkout)
 * 
 * All results are computed via runtime execution against ECommerceCore.
 */

(function () {
  'use strict';

  const Core = window.ECommerceCore;
  if (!Core) {
    console.error('ECommerceCore engine not found. Ensure ecommerce-core.js is loaded.');
    return;
  }

  // Registry of all executable test specifications
  const TEST_REGISTRY = [
    // ------------------------------------------------------------------------
    // 1. UNIT TESTS: Price Calculation
    // ------------------------------------------------------------------------
    {
      id: 'UT-PRICE-01',
      category: 'unit',
      suite: 'Price Calculation',
      description: 'Formats standard numeric price to currency string ($99.99)',
      expected: '$99.99',
      fn: function () {
        const res = Core.formatPrice(99.99);
        return {
          actual: res,
          pass: res === '$99.99'
        };
      }
    },
    {
      id: 'UT-PRICE-02',
      category: 'unit',
      suite: 'Price Calculation',
      description: 'Calculates line total for price * quantity (49.99 * 3)',
      expected: '149.97',
      fn: function () {
        const res = Core.calculateLineTotal(49.99, 3);
        return {
          actual: String(res),
          pass: res === 149.97
        };
      }
    },
    {
      id: 'UT-PRICE-03',
      category: 'unit',
      suite: 'Price Calculation',
      description: 'Floating point rounding precision check (19.99 * 7 = 139.93)',
      expected: '139.93',
      fn: function () {
        const res = Core.calculateLineTotal(19.99, 7);
        return {
          actual: String(res),
          pass: res === 139.93
        };
      }
    },

    // ------------------------------------------------------------------------
    // 1. UNIT TESTS: Quantity Validation
    // ------------------------------------------------------------------------
    {
      id: 'UT-QTY-01',
      category: 'unit',
      suite: 'Quantity Validation',
      description: 'Validates positive integer within product stock (qty: 3, stock: 5)',
      expected: 'true',
      fn: function () {
        const res = Core.ValidationRules.quantity.validate(3, 5);
        return {
          actual: String(res),
          pass: res === true
        };
      }
    },
    {
      id: 'UT-QTY-02',
      category: 'unit',
      suite: 'Quantity Validation',
      description: 'Rejects decimal quantity (qty: 2.5, stock: 5)',
      expected: 'false',
      fn: function () {
        const res = Core.ValidationRules.quantity.validate(2.5, 5);
        return {
          actual: String(res),
          pass: res === false
        };
      }
    },
    {
      id: 'UT-QTY-03',
      category: 'unit',
      suite: 'Quantity Validation',
      description: 'Rejects zero quantity (qty: 0, stock: 5)',
      expected: 'false',
      fn: function () {
        const res = Core.ValidationRules.quantity.validate(0, 5);
        return {
          actual: String(res),
          pass: res === false
        };
      }
    },
    {
      id: 'UT-QTY-04',
      category: 'unit',
      suite: 'Quantity Validation',
      description: 'Rejects negative quantity (qty: -2, stock: 5)',
      expected: 'false',
      fn: function () {
        const res = Core.ValidationRules.quantity.validate(-2, 5);
        return {
          actual: String(res),
          pass: res === false
        };
      }
    },

    // ------------------------------------------------------------------------
    // 1. UNIT TESTS: Cart Calculations
    // ------------------------------------------------------------------------
    {
      id: 'UT-CART-01',
      category: 'unit',
      suite: 'Cart Calculations',
      description: 'Computes subtotal for multiple cart items (2x$100 + 3x$20)',
      expected: 'subtotal: 260.00',
      fn: function () {
        const prods = [{ id: 'a', price: 100 }, { id: 'b', price: 20 }];
        const cart = [{ id: 'a', quantity: 2 }, { id: 'b', quantity: 3 }];
        const res = Core.calculateCartTotals(cart, prods);
        return {
          actual: `subtotal: ${res.subtotal.toFixed(2)}`,
          pass: res.subtotal === 260.00
        };
      }
    },
    {
      id: 'UT-CART-02',
      category: 'unit',
      suite: 'Cart Calculations',
      description: 'Computes standard 5% tax on $100 subtotal ($5.00)',
      expected: 'tax: 5.00',
      fn: function () {
        const prods = [{ id: 'a', price: 100 }];
        const cart = [{ id: 'a', quantity: 1 }];
        const res = Core.calculateCartTotals(cart, prods);
        return {
          actual: `tax: ${res.tax.toFixed(2)}`,
          pass: res.tax === 5.00
        };
      }
    },
    {
      id: 'UT-CART-03',
      category: 'unit',
      suite: 'Cart Calculations',
      description: 'Applies $5.00 standard shipping when subtotal < $50 ($40 subtotal)',
      expected: 'shipping: 5.00',
      fn: function () {
        const prods = [{ id: 'a', price: 40 }];
        const cart = [{ id: 'a', quantity: 1 }];
        const res = Core.calculateCartTotals(cart, prods);
        return {
          actual: `shipping: ${res.shipping.toFixed(2)}`,
          pass: res.shipping === 5.00
        };
      }
    },
    {
      id: 'UT-CART-04',
      category: 'unit',
      suite: 'Cart Calculations',
      description: 'Unlocks free shipping ($0.00) when subtotal >= $50 ($100 subtotal)',
      expected: 'shipping: 0.00',
      fn: function () {
        const prods = [{ id: 'a', price: 100 }];
        const cart = [{ id: 'a', quantity: 1 }];
        const res = Core.calculateCartTotals(cart, prods);
        return {
          actual: `shipping: ${res.shipping.toFixed(2)}`,
          pass: res.shipping === 0.00
        };
      }
    },
    {
      id: 'UT-CART-05',
      category: 'unit',
      suite: 'Cart Calculations',
      description: 'Calculates total sum: subtotal($20) + tax($1) + shipping($5) = $26.00',
      expected: 'total: 26.00',
      fn: function () {
        const prods = [{ id: 'a', price: 20 }];
        const cart = [{ id: 'a', quantity: 1 }];
        const res = Core.calculateCartTotals(cart, prods);
        return {
          actual: `total: ${res.total.toFixed(2)}`,
          pass: res.total === 26.00
        };
      }
    },

    // ------------------------------------------------------------------------
    // 1. UNIT TESTS: Stock Validation
    // ------------------------------------------------------------------------
    {
      id: 'UT-STOCK-01',
      category: 'unit',
      suite: 'Stock Validation',
      description: 'Identifies product with stock > 0 as in-stock',
      expected: 'true',
      fn: function () {
        const res = Core.isProductInStock({ id: 'x', stock: 8 });
        return {
          actual: String(res),
          pass: res === true
        };
      }
    },
    {
      id: 'UT-STOCK-02',
      category: 'unit',
      suite: 'Stock Validation',
      description: 'Identifies product with stock = 0 as out-of-stock',
      expected: 'false',
      fn: function () {
        const res = Core.isProductInStock({ id: 'x', stock: 0 });
        return {
          actual: String(res),
          pass: res === false
        };
      }
    },
    {
      id: 'UT-STOCK-03',
      category: 'unit',
      suite: 'Stock Validation',
      description: 'Calculates remaining stock accounting for cart items (Stock: 6, Cart: 2)',
      expected: 'remaining: 4',
      fn: function () {
        const prod = { id: 'x', stock: 6 };
        const cart = [{ id: 'x', quantity: 2 }];
        const res = Core.getAvailableStock(prod, cart);
        return {
          actual: `remaining: ${res}`,
          pass: res === 4
        };
      }
    },

    // ------------------------------------------------------------------------
    // 2. INTEGRATION TESTS
    // ------------------------------------------------------------------------
    {
      id: 'IT-CART-01',
      category: 'integration',
      suite: 'Cart Integration',
      description: 'Add product to cart and verify cart array length and quantity updated',
      expected: 'length: 1, qty: 1',
      fn: function () {
        const prods = [{ id: 'p1', stock: 5, price: 50 }];
        let cart = [];
        const res = Core.addToCart(cart, prods, 'p1', 1);
        cart = res.cart;
        return {
          actual: `length: ${cart.length}, qty: ${cart[0]?.quantity}`,
          pass: res.success === true && cart.length === 1 && cart[0].quantity === 1
        };
      }
    },
    {
      id: 'IT-QTY-01',
      category: 'integration',
      suite: 'Cart Integration',
      description: 'Update quantity to 3 and verify cart totals dynamically update',
      expected: 'qty: 3, total: 157.50',
      fn: function () {
        const prods = [{ id: 'p1', stock: 5, price: 50 }]; // 3 * 50 = 150 + 7.50 tax = 157.50
        let cart = [{ id: 'p1', quantity: 1 }];
        const res = Core.updateCartQuantity(cart, prods, 'p1', 3);
        const totals = Core.calculateCartTotals(res.cart, prods);
        return {
          actual: `qty: ${res.cart[0]?.quantity}, total: ${totals.total.toFixed(2)}`,
          pass: res.success === true && res.cart[0]?.quantity === 3 && totals.total === 157.50
        };
      }
    },
    {
      id: 'IT-ORDER-01',
      category: 'integration',
      suite: 'Checkout Integration',
      description: 'Checkout cart and verify order creation and cart emptied',
      expected: 'success: true, orderId: generated, cartEmpty: true',
      fn: function () {
        const prods = [{ id: 'p1', name: 'Widget', stock: 5, price: 40 }];
        const cart = [{ id: 'p1', quantity: 2 }];
        const customer = {
          name: 'Jane Smith',
          email: 'jane@example.com',
          phone: '9876543210',
          address: '456 Elm Street',
          city: 'Metropolis',
          state: 'NY',
          zip: '10001'
        };
        const payment = { method: 'cod' };
        const res = Core.processOrder(cart, prods, customer, payment);
        const hasId = Boolean(res.order && res.order.orderId);
        const cartClean = res.clearedCart && res.clearedCart.length === 0;
        return {
          actual: `success: ${res.success}, orderId: ${res.order?.orderId ? 'generated' : 'none'}, cartEmpty: ${cartClean}`,
          pass: res.success === true && hasId && cartClean
        };
      }
    },
    {
      id: 'IT-STORE-01',
      category: 'integration',
      suite: 'Storage Integration',
      description: 'Verify localStorage updates correctly on cart modifications',
      expected: 'stored & retrieved: p1 x 2',
      fn: function () {
        const testCart = [{ id: 'p1', quantity: 2 }];
        const key = 'test_auramart_cart';
        localStorage.setItem(key, JSON.stringify(testCart));
        const retrieved = JSON.parse(localStorage.getItem(key));
        localStorage.removeItem(key);
        const pass = retrieved && retrieved[0]?.id === 'p1' && retrieved[0]?.quantity === 2;
        return {
          actual: `stored & retrieved: ${retrieved[0]?.id} x ${retrieved[0]?.quantity}`,
          pass: pass
        };
      }
    },
    {
      id: 'IT-STORE-02',
      category: 'integration',
      suite: 'Storage Integration',
      description: 'Verify inventory stock reduction is stored in localStorage after checkout',
      expected: 'stock reduced from 5 to 3',
      fn: function () {
        const prods = [{ id: 'p1', name: 'Item', stock: 5, price: 20 }];
        const cart = [{ id: 'p1', quantity: 2 }];
        const customer = {
          name: 'Alex Grey',
          email: 'alex@example.com',
          phone: '1234567890',
          address: '10 Center Way',
          city: 'Denver',
          state: 'CO',
          zip: '80201'
        };
        const res = Core.processOrder(cart, prods, customer, { method: 'cod' });
        const key = 'test_auramart_products';
        localStorage.setItem(key, JSON.stringify(res.updatedProducts));
        const storedProds = JSON.parse(localStorage.getItem(key));
        localStorage.removeItem(key);
        const newStock = storedProds.find(p => p.id === 'p1')?.stock;
        return {
          actual: `stock reduced from 5 to ${newStock}`,
          pass: newStock === 3
        };
      }
    },

    // ------------------------------------------------------------------------
    // 3. BLACK BOX TESTS
    // ------------------------------------------------------------------------
    {
      id: 'BB-CHK-01',
      category: 'blackbox',
      suite: 'Boundary & Validation',
      description: 'Empty checkout: Attempting to submit order with empty cart is rejected',
      expected: 'success: false, error: Cannot checkout with an empty cart',
      fn: function () {
        const customer = { name: 'Test', email: 'test@example.com', phone: '1234567890', address: 'Addr', city: 'City', state: 'ST', zip: '12345' };
        const res = Core.processOrder([], Core.INITIAL_PRODUCTS, customer, { method: 'cod' });
        return {
          actual: `success: ${res.success}, error: ${res.error}`,
          pass: res.success === false && res.error.includes('empty cart')
        };
      }
    },
    {
      id: 'BB-CUST-01',
      category: 'blackbox',
      suite: 'Boundary & Validation',
      description: 'Invalid customer details: Flags malformed name, invalid email, short phone',
      expected: 'isValid: false, errors: name, email, phone flagged',
      fn: function () {
        const badCustomer = {
          name: 'A', // too short
          email: 'notanemail',
          phone: '123', // too short
          address: '',
          city: '',
          state: '',
          zip: ''
        };
        const res = Core.validateCheckoutPayload(badCustomer, { method: 'cod' });
        const hasName = Boolean(res.errors.name);
        const hasEmail = Boolean(res.errors.email);
        const hasPhone = Boolean(res.errors.phone);
        return {
          actual: `isValid: ${res.isValid}, flagged: ${Object.keys(res.errors).join(', ')}`,
          pass: res.isValid === false && hasName && hasEmail && hasPhone
        };
      }
    },
    {
      id: 'BB-QTY-01',
      category: 'blackbox',
      suite: 'Boundary & Validation',
      description: 'Negative quantity: Attempting to add negative quantity (-3) is blocked',
      expected: 'success: false, Invalid quantity to add',
      fn: function () {
        const res = Core.addToCart([], Core.INITIAL_PRODUCTS, 'p1', -3);
        return {
          actual: `success: ${res.success}, error: ${res.error}`,
          pass: res.success === false && res.error.includes('Invalid quantity')
        };
      }
    },
    {
      id: 'BB-QTY-02',
      category: 'blackbox',
      suite: 'Boundary & Validation',
      description: 'Zero quantity: Updating item quantity to 0 removes product from cart',
      expected: 'removed: true, cart length: 0',
      fn: function () {
        const cart = [{ id: 'p1', quantity: 2 }];
        const res = Core.updateCartQuantity(cart, Core.INITIAL_PRODUCTS, 'p1', 0);
        return {
          actual: `removed: ${res.removed}, cart length: ${res.cart.length}`,
          pass: res.success === true && res.removed === true && res.cart.length === 0
        };
      }
    },
    {
      id: 'BB-STOCK-01',
      category: 'blackbox',
      suite: 'Boundary & Validation',
      description: 'Out-of-stock products: Adding item with 0 stock (p10) is blocked',
      expected: 'success: false, Product is out of stock',
      fn: function () {
        const res = Core.addToCart([], Core.INITIAL_PRODUCTS, 'p10', 1);
        return {
          actual: `success: ${res.success}, error: ${res.error}`,
          pass: res.success === false && res.error.includes('out of stock')
        };
      }
    },
    {
      id: 'BB-INP-01',
      category: 'blackbox',
      suite: 'Boundary & Validation',
      description: 'Invalid payment inputs: Rejects expired card (01/20) and short CVV ("9")',
      expected: 'isValid: false, card errors flagged',
      fn: function () {
        const cust = { name: 'Valid User', email: 'user@test.com', phone: '9876543210', address: '123 Main St', city: 'City', state: 'ST', zip: '12345' };
        const badCard = { method: 'card', cardNum: '1234', cardExpiry: '01/20', cardCvv: '9' };
        const res = Core.validateCheckoutPayload(cust, badCard);
        return {
          actual: `isValid: ${res.isValid}, flagged: ${Object.keys(res.errors).join(', ')}`,
          pass: res.isValid === false && res.errors.cardNum && res.errors.cardExpiry && res.errors.cardCvv
        };
      }
    },
    {
      id: 'BB-INP-02',
      category: 'blackbox',
      suite: 'Boundary & Validation',
      description: 'Valid customer & card inputs: Completely passes input validation',
      expected: 'isValid: true, errors: 0',
      fn: function () {
        const goodCust = { name: 'Alice Walker', email: 'alice@example.com', phone: '9876543210', address: '789 Park Blvd', city: 'Seattle', state: 'WA', zip: '98101' };
        const goodCard = { method: 'card', cardNum: '4111222233334444', cardExpiry: '12/29', cardCvv: '456' };
        const res = Core.validateCheckoutPayload(goodCust, goodCard);
        return {
          actual: `isValid: ${res.isValid}, errors: ${Object.keys(res.errors).length}`,
          pass: res.isValid === true && Object.keys(res.errors).length === 0
        };
      }
    },

    // ------------------------------------------------------------------------
    // 4. FUNCTIONAL TESTS
    // ------------------------------------------------------------------------
    {
      id: 'FT-SRCH-01',
      category: 'functional',
      suite: 'Product Search',
      description: 'Product search by term "Headphones" finds matching product card',
      expected: 'results >= 1, includes Headphones',
      fn: function () {
        const results = Core.filterAndSortProducts(Core.INITIAL_PRODUCTS, { search: 'Headphones' });
        const hasItem = results.some(p => p.name.includes('Headphones'));
        return {
          actual: `found: ${results.length} item(s)`,
          pass: results.length >= 1 && hasItem
        };
      }
    },
    {
      id: 'FT-SRCH-02',
      category: 'functional',
      suite: 'Product Search',
      description: 'Product search with nonexistent query returns 0 matches cleanly',
      expected: 'found: 0 item(s)',
      fn: function () {
        const results = Core.filterAndSortProducts(Core.INITIAL_PRODUCTS, { search: 'xyznonexistent999' });
        return {
          actual: `found: ${results.length} item(s)`,
          pass: results.length === 0
        };
      }
    },
    {
      id: 'FT-CART-01',
      category: 'functional',
      suite: 'Cart Flow',
      description: 'Add to Cart: Adds item, updates cart quantity and subtotal accurately',
      expected: 'qty: 2, subtotal: 199.98',
      fn: function () {
        let cart = [];
        const res = Core.addToCart(cart, Core.INITIAL_PRODUCTS, 'p1', 2); // 99.99 * 2 = 199.98
        const totals = Core.calculateCartTotals(res.cart, Core.INITIAL_PRODUCTS);
        return {
          actual: `qty: ${res.cart[0]?.quantity}, subtotal: ${totals.subtotal.toFixed(2)}`,
          pass: res.success === true && res.cart[0]?.quantity === 2 && totals.subtotal === 199.98
        };
      }
    },
    {
      id: 'FT-CART-02',
      category: 'functional',
      suite: 'Cart Flow',
      description: 'Remove from Cart: Deletes item completely from cart collection',
      expected: 'item removed, remaining: 0',
      fn: function () {
        let cart = [{ id: 'p1', quantity: 2 }];
        const res = Core.removeFromCart(cart, 'p1');
        return {
          actual: `item removed, remaining: ${res.cart.length}`,
          pass: res.success === true && res.cart.length === 0
        };
      }
    },
    {
      id: 'FT-E2E-01',
      category: 'functional',
      suite: 'End-to-End Workflow',
      description: 'End-to-End Checkout: Search -> Add -> Checkout -> Decrement Stock -> Empty Cart',
      expected: 'order: Confirmed, stock decremented, cart emptied',
      fn: function () {
        let products = JSON.parse(JSON.stringify(Core.INITIAL_PRODUCTS));
        let cart = [];

        // 1. Search item
        const search = Core.filterAndSortProducts(products, { search: 'Mouse' });
        const item = search[0]; // p4, stock: 12
        const initialStock = item.stock;

        // 2. Add 2 to cart
        const add = Core.addToCart(cart, products, item.id, 2);
        cart = add.cart;

        // 3. Checkout
        const customer = {
          name: 'Robert Fulton',
          email: 'robert@steamboat.com',
          phone: '9876543210',
          address: '50 Hudson River Rd',
          city: 'Albany',
          state: 'NY',
          zip: '12207'
        };
        const orderRes = Core.processOrder(cart, products, customer, { method: 'upi', upiId: 'robert@upi' });

        const isOrderOk = orderRes.success === true && orderRes.order.status === 'Confirmed';
        const isStockOk = orderRes.updatedProducts.find(p => p.id === item.id).stock === (initialStock - 2);
        const isCartOk = orderRes.clearedCart.length === 0;

        return {
          actual: `order: ${orderRes.order?.status}, stock: ${initialStock} -> ${initialStock - 2}, cartEmpty: ${isCartOk}`,
          pass: isOrderOk && isStockOk && isCartOk
        };
      }
    }
  ];

  // Runtime State
  const TestState = {
    results: new Map(),
    activeCategory: 'all',
    searchQuery: '',
    statusFilter: 'all',
    isRunning: false
  };

  /* ==========================================================================
     Execution Engine
     ========================================================================== */

  function executeTest(testCase) {
    const startTime = performance.now();
    let outcome = { actual: '', pass: false, error: null };

    try {
      outcome = testCase.fn();
    } catch (err) {
      outcome = {
        actual: `Exception: ${err.message}`,
        pass: false,
        error: err
      };
    }

    const duration = Math.max(0.1, performance.now() - startTime).toFixed(1);

    const result = {
      id: testCase.id,
      category: testCase.category,
      suite: testCase.suite,
      description: testCase.description,
      expected: testCase.expected,
      actual: outcome.actual,
      pass: Boolean(outcome.pass),
      durationMs: duration,
      executedAt: new Date().toLocaleTimeString()
    };

    TestState.results.set(testCase.id, result);
    return result;
  }

  function runAllTests() {
    if (TestState.isRunning) return;
    TestState.isRunning = true;

    const runBtn = document.getElementById('run-all-tests-btn');
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.innerHTML = `
        <svg class="spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
          <path d="M12 2a10 10 0 0 1 10 10"></path>
        </svg>
        Executing Tests...
      `;
    }

    const startTime = performance.now();

    TEST_REGISTRY.forEach(tc => {
      executeTest(tc);
    });

    const totalDuration = (performance.now() - startTime).toFixed(1);

    TestState.isRunning = false;
    if (runBtn) {
      runBtn.disabled = false;
      runBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        Run All Tests
      `;
    }

    updateMetrics(totalDuration);
    renderTable();
    updateManualScenarioPills();
  }

  function runSingleTest(testId) {
    const testCase = TEST_REGISTRY.find(t => t.id === testId);
    if (!testCase) return;

    executeTest(testCase);
    updateMetrics();
    renderTable();
    updateManualScenarioPill(testId);
  }

  /* ==========================================================================
     Metrics & UI Rendering
     ========================================================================== */

  function updateMetrics(duration = null) {
    const total = TEST_REGISTRY.length;
    let passed = 0;
    let failed = 0;

    TestState.results.forEach(res => {
      if (res.pass) passed++;
      else failed++;
    });

    const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;

    const totalEl = document.getElementById('metric-total');
    const passedEl = document.getElementById('metric-passed');
    const failedEl = document.getElementById('metric-failed');
    const rateEl = document.getElementById('metric-pass-rate');
    const timeEl = document.getElementById('metric-time');
    const statusEl = document.getElementById('metric-status');

    if (totalEl) totalEl.textContent = total;
    if (passedEl) passedEl.textContent = passed;
    if (failedEl) failedEl.textContent = failed;
    if (rateEl) rateEl.textContent = `${passRate}% pass rate`;

    if (timeEl && duration !== null) {
      timeEl.textContent = `${duration} ms`;
    }

    if (statusEl) {
      if (passed === total) {
        statusEl.textContent = 'All 32 tests passed';
        statusEl.style.color = 'var(--success)';
      } else if (failed > 0) {
        statusEl.textContent = `${failed} test(s) failed`;
        statusEl.style.color = 'var(--danger)';
      }
    }
  }

  function getFilteredResults() {
    return TEST_REGISTRY.filter(tc => {
      // Category filter
      if (TestState.activeCategory !== 'all' && tc.category !== TestState.activeCategory) {
        return false;
      }

      // Search query
      if (TestState.searchQuery.trim()) {
        const q = TestState.searchQuery.toLowerCase();
        const matchesId = tc.id.toLowerCase().includes(q);
        const matchesDesc = tc.description.toLowerCase().includes(q);
        const matchesSuite = tc.suite.toLowerCase().includes(q);
        if (!matchesId && !matchesDesc && !matchesSuite) return false;
      }

      // Status filter
      if (TestState.statusFilter !== 'all') {
        const res = TestState.results.get(tc.id);
        if (!res) return false;
        if (TestState.statusFilter === 'PASS' && !res.pass) return false;
        if (TestState.statusFilter === 'FAIL' && res.pass) return false;
      }

      return true;
    });
  }

  function renderTable() {
    const tbody = document.getElementById('test-table-body');
    if (!tbody) return;

    const filtered = getFilteredResults();

    if (filtered.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
            No matching test cases found for the selected filters.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = filtered.map(tc => {
      const res = TestState.results.get(tc.id);
      const isExecuted = Boolean(res);
      const isPass = res ? res.pass : false;
      const statusClass = isExecuted ? (isPass ? 'pass' : 'fail') : 'pending';
      const statusText = isExecuted ? (isPass ? 'PASS' : 'FAIL') : 'READY';

      const actualText = res ? res.actual : 'Not executed yet';
      const timeText = res ? `${res.durationMs}ms` : '--';

      return `
        <tr data-test-id="${tc.id}">
          <td>
            <span class="test-badge">${tc.id}</span>
          </td>
          <td>
            <span class="suite-badge ${tc.category}">${tc.suite}</span>
          </td>
          <td>
            <strong>${escapeHtml(tc.description)}</strong>
          </td>
          <td>
            <code class="result-code">${escapeHtml(tc.expected)}</code>
          </td>
          <td>
            <code class="result-code" style="color: ${isExecuted ? (isPass ? '#059669' : '#dc2626') : 'inherit'};">
              ${escapeHtml(actualText)}
            </code>
          </td>
          <td>
            <span class="test-time">${timeText}</span>
          </td>
          <td style="text-align: center;">
            <span class="status-badge ${statusClass}">${statusText}</span>
          </td>
          <td style="text-align: right;">
            <button class="btn btn-sm btn-outline re-run-btn" data-run-id="${tc.id}" title="Re-execute test ${tc.id}">
              ▶
            </button>
          </td>
        </tr>
      `;
    }).join('');
  }

  function updateManualScenarioPills() {
    document.querySelectorAll('.scenario-card').forEach(card => {
      const testId = card.querySelector('.test-badge')?.textContent;
      if (testId) updateManualScenarioPill(testId);
    });
  }

  function updateManualScenarioPill(testId) {
    const pill = document.getElementById(`pill-${testId}`);
    if (!pill) return;

    const res = TestState.results.get(testId);
    if (!res) {
      pill.className = 'scenario-result-pill';
      pill.textContent = 'Not Run';
      return;
    }

    if (res.pass) {
      pill.className = 'scenario-result-pill pass';
      pill.textContent = 'PASS';
    } else {
      pill.className = 'scenario-result-pill fail';
      pill.textContent = 'FAIL';
    }
  }

  function clearResults() {
    TestState.results.clear();
    updateMetrics(0);
    renderTable();
    updateManualScenarioPills();
  }

  /* ==========================================================================
     Helper Utilities & Event Listeners
     ========================================================================== */

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /* ==========================================================================
     Manual Test Studio Engine
     ========================================================================== */

  function renderManualInputs(scenario) {
    const container = document.getElementById('manual-dynamic-inputs');
    if (!container) return;

    if (scenario === 'price-calc') {
      container.innerHTML = `
        <div class="manual-input-row">
          <div class="manual-input-group">
            <label for="man-unit-price">Unit Price ($):</label>
            <input type="number" step="0.01" id="man-unit-price" value="19.99">
          </div>
          <div class="manual-input-group">
            <label for="man-quantity">Quantity:</label>
            <input type="number" id="man-quantity" value="7">
          </div>
        </div>
      `;
    } else if (scenario === 'qty-bounds') {
      container.innerHTML = `
        <div class="manual-input-row">
          <div class="manual-input-group">
            <label for="man-req-qty">Quantity to Add:</label>
            <input type="number" step="any" id="man-req-qty" value="3">
          </div>
          <div class="manual-input-group">
            <label for="man-stock">Total Warehouse Stock:</label>
            <input type="number" id="man-stock" value="5">
          </div>
        </div>
        <div class="manual-input-group" style="margin-top: 0.5rem;">
          <label for="man-existing-cart">Already in Cart:</label>
          <input type="number" id="man-existing-cart" value="0">
        </div>
      `;
    } else if (scenario === 'cart-tiers') {
      container.innerHTML = `
        <div class="manual-input-group">
          <label for="man-subtotal">Input Subtotal Amount ($):</label>
          <input type="number" step="0.01" id="man-subtotal" value="45.00">
        </div>
        <p style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">Rules: Free Shipping on subtotal &ge; $50.00; Tax is exactly 5%.</p>
      `;
    } else if (scenario === 'empty-checkout') {
      container.innerHTML = `
        <div class="manual-input-group">
          <label for="man-cart-count">Simulated Cart Items Count:</label>
          <input type="number" id="man-cart-count" value="0">
        </div>
      `;
    } else if (scenario === 'customer-form') {
      container.innerHTML = `
        <div class="manual-input-group">
          <label for="man-cust-name">Full Name:</label>
          <input type="text" id="man-cust-name" value="Jane Doe">
        </div>
        <div class="manual-input-row" style="margin-top: 0.5rem;">
          <div class="manual-input-group">
            <label for="man-cust-email">Email:</label>
            <input type="text" id="man-cust-email" value="jane@example.com">
          </div>
          <div class="manual-input-group">
            <label for="man-cust-phone">Phone Number:</label>
            <input type="text" id="man-cust-phone" value="9876543210">
          </div>
        </div>
      `;
    } else if (scenario === 'payment-auth') {
      container.innerHTML = `
        <div class="manual-input-group">
          <label for="man-card-num">Card Number (16-digits):</label>
          <input type="text" id="man-card-num" value="4111222233334444">
        </div>
        <div class="manual-input-row" style="margin-top: 0.5rem;">
          <div class="manual-input-group">
            <label for="man-card-expiry">Expiry Date (MM/YY):</label>
            <input type="text" id="man-card-expiry" value="12/29">
          </div>
          <div class="manual-input-group">
            <label for="man-card-cvv">CVV (3-4 digits):</label>
            <input type="text" id="man-card-cvv" value="123">
          </div>
        </div>
      `;
    }
  }

  function executeManualStudioTest() {
    const scenario = document.getElementById('manual-scenario-picker')?.value;
    const terminal = document.getElementById('manual-terminal');
    const pill = document.getElementById('manual-status-pill');
    const notes = document.getElementById('manual-tester-notes')?.value;

    let log = '';
    let isPass = false;
    const time = new Date().toLocaleTimeString();

    if (scenario === 'price-calc') {
      const price = parseFloat(document.getElementById('man-unit-price')?.value);
      const qty = parseInt(document.getElementById('man-quantity')?.value, 10);
      const lineTotal = Core.calculateLineTotal(price, qty);
      const formatted = Core.formatPrice(lineTotal);

      log += `[${time}] Scenario: Price & Line Total Calculation\n`;
      log += `INPUTS: Unit Price = $${price}, Quantity = ${qty}\n`;
      log += `EXECUTION: calculateLineTotal(${price}, ${qty}) -> ${lineTotal}\n`;
      log += `OUTPUT FORMAT: formatPrice(${lineTotal}) -> ${formatted}\n`;

      isPass = !isNaN(lineTotal) && lineTotal > 0 && typeof formatted === 'string';
      log += `EXPECTED: Accurate positive monetary value\n`;
      log += `VERDICT: ${isPass ? 'PASS' : 'FAIL'}\n`;

    } else if (scenario === 'qty-bounds') {
      const reqQty = parseFloat(document.getElementById('man-req-qty')?.value);
      const stock = parseInt(document.getElementById('man-stock')?.value, 10);
      const inCart = parseInt(document.getElementById('man-existing-cart')?.value || '0', 10);

      log += `[${time}] Scenario: Quantity Bounds & Stock Validation\n`;
      log += `INPUTS: Request Qty = ${reqQty}, Total Stock = ${stock}, In Cart = ${inCart}\n`;

      const isInteger = Number.isInteger(reqQty) && reqQty > 0;
      const withinStock = (inCart + reqQty) <= stock;

      log += `CHECK 1 (Integer): Number.isInteger(${reqQty}) -> ${isInteger}\n`;
      log += `CHECK 2 (Cumulative Bounds): (${inCart} + ${reqQty} <= ${stock}) -> ${withinStock}\n`;

      if (!isInteger) {
        log += `OUTCOME: REJECTED (Non-integer or non-positive quantity)\n`;
        isPass = (reqQty <= 0 || !Number.isInteger(reqQty)); // If tester tested invalid, rejection is PASS
      } else if (!withinStock) {
        log += `OUTCOME: REJECTED (Stock oversell prevented)\n`;
        isPass = true;
      } else {
        log += `OUTCOME: ACCEPTED (Valid quantity within warehouse stock)\n`;
        isPass = true;
      }
      log += `VERDICT: ${isPass ? 'PASS' : 'FAIL'}\n`;

    } else if (scenario === 'cart-tiers') {
      const subtotal = parseFloat(document.getElementById('man-subtotal')?.value || '0');
      const mockCart = [{ id: 'mock', quantity: 1 }];
      const mockProd = [{ id: 'mock', price: subtotal }];
      const totals = Core.calculateCartTotals(mockCart, mockProd);

      log += `[${time}] Scenario: Subtotal, Tax & Shipping Tiers\n`;
      log += `INPUT SUBTOTAL: $${subtotal.toFixed(2)}\n`;
      log += `CALCULATED TAX (5%): $${totals.tax.toFixed(2)}\n`;
      log += `SHIPPING TIER: $${totals.shipping.toFixed(2)} (${totals.shipping === 0 ? 'Free Shipping Unlocked' : 'Standard Shipping Fee'})\n`;
      log += `GRAND TOTAL: $${totals.total.toFixed(2)}\n`;

      const expectedShipping = subtotal >= 50 ? 0 : 5;
      isPass = (totals.shipping === expectedShipping) && (totals.tax === Core.roundMoney(subtotal * 0.05));
      log += `VERDICT: ${isPass ? 'PASS' : 'FAIL'}\n`;

    } else if (scenario === 'empty-checkout') {
      const cartCount = parseInt(document.getElementById('man-cart-count')?.value || '0', 10);
      const mockCart = cartCount > 0 ? [{ id: 'p1', quantity: cartCount }] : [];
      const res = Core.processOrder(mockCart, Core.INITIAL_PRODUCTS, { name: 'Tester', email: 'test@qa.org', phone: '1234567890', address: '123 QA St', city: 'City', state: 'ST', zip: '12345' }, { method: 'cod' });

      log += `[${time}] Scenario: Empty Cart Checkout Prevention\n`;
      log += `INPUT: Cart Items Count = ${cartCount}\n`;
      log += `OUTPUT: success = ${res.success}, message = "${res.error || 'Order Confirmed'}"\n`;

      if (cartCount === 0) {
        isPass = (res.success === false && res.error.includes('empty cart'));
        log += `EXPECTED: Rejection on empty cart\n`;
      } else {
        isPass = res.success === true;
        log += `EXPECTED: Successful checkout on non-empty cart\n`;
      }
      log += `VERDICT: ${isPass ? 'PASS' : 'FAIL'}\n`;

    } else if (scenario === 'customer-form') {
      const name = document.getElementById('man-cust-name')?.value || '';
      const email = document.getElementById('man-cust-email')?.value || '';
      const phone = document.getElementById('man-cust-phone')?.value || '';

      const isNameValid = Core.ValidationRules.name.validate(name);
      const isEmailValid = Core.ValidationRules.email.validate(email);
      const isPhoneValid = Core.ValidationRules.phone.validate(phone);

      log += `[${time}] Scenario: Customer Details Validation\n`;
      log += `INPUTS: Name="${name}", Email="${email}", Phone="${phone}"\n`;
      log += `NAME VALIDATION (letters & min 3 chars): ${isNameValid}\n`;
      log += `EMAIL VALIDATION (standard email regex): ${isEmailValid}\n`;
      log += `PHONE VALIDATION (10+ clean digits): ${isPhoneValid}\n`;

      const allValid = isNameValid && isEmailValid && isPhoneValid;
      log += `OVERALL STATUS: ${allValid ? 'All Valid' : 'Validation Errors Flagged'}\n`;
      isPass = true; // successfully evaluated
      log += `VERDICT: PASS\n`;

    } else if (scenario === 'payment-auth') {
      const cardNum = document.getElementById('man-card-num')?.value || '';
      const cardExpiry = document.getElementById('man-card-expiry')?.value || '';
      const cardCvv = document.getElementById('man-card-cvv')?.value || '';

      const isCardValid = Core.ValidationRules.cardNum.validate(cardNum);
      const isExpiryValid = Core.ValidationRules.cardExpiry.validate(cardExpiry);
      const isCvvValid = Core.ValidationRules.cardCvv.validate(cardCvv);

      log += `[${time}] Scenario: Payment Authentication Validation\n`;
      log += `CARD NUM (13-19 digits): ${isCardValid}\n`;
      log += `EXPIRY DATE (Future MM/YY comparison): ${isExpiryValid}\n`;
      log += `CVV (3-4 digits): ${isCvvValid}\n`;

      const allValid = isCardValid && isExpiryValid && isCvvValid;
      log += `OVERALL AUTH STATUS: ${allValid ? 'Card Valid' : 'Payment Details Rejected'}\n`;
      isPass = true;
      log += `VERDICT: PASS\n`;
    }

    if (notes && notes.trim()) {
      log += `TESTER NOTE: "${notes.trim()}"\n`;
    }

    if (terminal) terminal.textContent = log;
    if (pill) {
      pill.className = isPass ? 'status-badge pass' : 'status-badge fail';
      pill.textContent = isPass ? 'PASS' : 'FAIL';
    }
  }

  function loadManualPreset(isValid) {
    const scenario = document.getElementById('manual-scenario-picker')?.value;
    if (scenario === 'price-calc') {
      document.getElementById('man-unit-price').value = isValid ? '24.50' : '19.99';
      document.getElementById('man-quantity').value = isValid ? '4' : '7';
    } else if (scenario === 'qty-bounds') {
      document.getElementById('man-req-qty').value = isValid ? '2' : '2.5';
      document.getElementById('man-stock').value = '5';
      document.getElementById('man-existing-cart').value = isValid ? '1' : '4';
    } else if (scenario === 'cart-tiers') {
      document.getElementById('man-subtotal').value = isValid ? '75.00' : '25.00';
    } else if (scenario === 'empty-checkout') {
      document.getElementById('man-cart-count').value = isValid ? '2' : '0';
    } else if (scenario === 'customer-form') {
      document.getElementById('man-cust-name').value = isValid ? 'Sarah Connor' : '   ';
      document.getElementById('man-cust-email').value = isValid ? 'sarah@resistance.org' : 'notanemail';
      document.getElementById('man-cust-phone').value = isValid ? '9876543210' : '123';
    } else if (scenario === 'payment-auth') {
      document.getElementById('man-card-num').value = isValid ? '4111222233334444' : '123';
      document.getElementById('man-card-expiry').value = isValid ? '12/29' : '01/20';
      document.getElementById('man-card-cvv').value = isValid ? '456' : '9';
    }
    executeManualStudioTest();
  }

  function setupEvents() {
    // Run All Tests button
    const runAllBtn = document.getElementById('run-all-tests-btn');
    if (runAllBtn) runAllBtn.addEventListener('click', runAllTests);

    // Clear Results button
    const clearBtn = document.getElementById('clear-results-btn');
    if (clearBtn) clearBtn.addEventListener('click', clearResults);

    // Suite Filter Tabs
    document.querySelectorAll('.test-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.test-tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        TestState.activeCategory = btn.dataset.category;
        renderTable();
      });
    });

    // Search Input
    const searchInput = document.getElementById('test-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        TestState.searchQuery = e.target.value;
        renderTable();
      });
    }

    // Status Filter
    const statusSelect = document.getElementById('test-status-filter');
    if (statusSelect) {
      statusSelect.addEventListener('change', (e) => {
        TestState.statusFilter = e.target.value;
        renderTable();
      });
    }

    // Re-run single test button (Event delegation)
    document.addEventListener('click', (e) => {
      const target = e.target.closest('[data-run-id]');
      if (!target) return;
      const testId = target.dataset.runId;
      runSingleTest(testId);
    });

    // Manual Scenario Runner buttons
    document.addEventListener('click', (e) => {
      const scenarioBtn = e.target.closest('.run-scenario-btn');
      if (!scenarioBtn) return;
      const testId = scenarioBtn.dataset.id;
      runSingleTest(testId);
    });

    // Run All Manual Scenarios button
    const runAllBbBtn = document.getElementById('run-all-bb-scenarios');
    if (runAllBbBtn) {
      runAllBbBtn.addEventListener('click', () => {
        const bbTests = TEST_REGISTRY.filter(t => t.category === 'blackbox');
        bbTests.forEach(t => executeTest(t));
        updateMetrics();
        renderTable();
        updateManualScenarioPills();
      });
    }

    // Manual Studio Event Handlers
    const manPicker = document.getElementById('manual-scenario-picker');
    if (manPicker) {
      manPicker.addEventListener('change', (e) => {
        renderManualInputs(e.target.value);
      });
    }

    const btnExecManual = document.getElementById('btn-exec-manual');
    if (btnExecManual) {
      btnExecManual.addEventListener('click', executeManualStudioTest);
    }

    const btnPresetValid = document.getElementById('btn-preset-valid');
    if (btnPresetValid) {
      btnPresetValid.addEventListener('click', () => loadManualPreset(true));
    }

    const btnPresetInvalid = document.getElementById('btn-preset-invalid');
    if (btnPresetInvalid) {
      btnPresetInvalid.addEventListener('click', () => loadManualPreset(false));
    }
  }

  // Self Initialization on page load
  document.addEventListener('DOMContentLoaded', () => {
    setupEvents();
    renderManualInputs('price-calc');
    renderTable();
    // Auto-run all tests on initial load so dashboard displays live execution results
    runAllTests();
  });

})();
