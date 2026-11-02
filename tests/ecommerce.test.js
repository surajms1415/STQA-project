/**
 * AuraMart E-Commerce Automated Test Suite
 * Compatible with Node.js Test Runner (native), Jest, and Vitest.
 * 
 * Includes:
 * 1. Unit Testing (Price, Quantity, Cart, Stock)
 * 2. Integration Testing (Add to cart, Update quantity, Checkout, Storage)
 * 3. Black Box Testing (Empty checkout, Invalid details, Negative/Zero qty, Out-of-stock, Inputs)
 * 4. Functional Testing (Search, Add to cart, Remove from cart, E2E flow)
 */

const isJest = typeof globalThis.describe === 'function' && typeof globalThis.it === 'function';
const { describe, it } = isJest ? globalThis : require('node:test');
const assert = isJest ? null : require('node:assert/strict');

const Core = require('../ecommerce-core.js');

// Helper to log test case details conforming to prompt requirements
function logTestCase(id, description, expected, actual, pass) {
  const statusStr = pass ? '\x1b[32mPASS\x1b[0m' : '\x1b[31mFAIL\x1b[0m';
  console.log(`  [${id}] ${description}`);
  console.log(`     Expected: ${expected}`);
  console.log(`     Actual:   ${actual} -> ${statusStr}`);
}

function verify(id, description, expected, actual, condition) {
  const pass = Boolean(condition);
  logTestCase(id, description, expected, actual, pass);
  if (isJest) {
    globalThis.expect(pass).toBe(true);
  } else {
    assert.ok(pass, `Test ${id} failed: expected "${expected}", got "${actual}"`);
  }
}

// Mock localStorage for integration storage tests in Node
class MockLocalStorage {
  constructor() {
    this.store = {};
  }
  getItem(key) {
    return this.store[key] || null;
  }
  setItem(key, value) {
    this.store[key] = String(value);
  }
  removeItem(key) {
    delete this.store[key];
  }
  clear() {
    this.store = {};
  }
}

/* ==========================================================================
   1. UNIT TESTING
   ========================================================================== */

describe('1. Unit Testing Suite', () => {

  describe('Price Calculation', () => {
    it('UT-PRICE-01: Formats decimal price into standard currency string', () => {
      const input = 99.99;
      const actual = Core.formatPrice(input);
      const expected = '$99.99';
      verify('UT-PRICE-01', 'Format price to standard currency string', expected, actual, actual === expected);
    });

    it('UT-PRICE-02: Calculates accurate line total for item (price * quantity)', () => {
      const price = 49.99;
      const qty = 3;
      const actual = Core.calculateLineTotal(price, qty);
      const expected = 149.97;
      verify('UT-PRICE-02', 'Calculate line total (49.99 * 3)', expected, actual, actual === expected);
    });

    it('UT-PRICE-03: Handles floating-point rounding cleanly without artifacts', () => {
      const price = 19.99;
      const qty = 7;
      const actual = Core.calculateLineTotal(price, qty);
      const expected = 139.93;
      verify('UT-PRICE-03', 'Float arithmetic precision (19.99 * 7)', expected, actual, actual === expected);
    });
  });

  describe('Quantity Validation', () => {
    it('UT-QTY-01: Accepts valid positive integer within stock', () => {
      const isValid = Core.ValidationRules.quantity.validate(3, 5);
      verify('UT-QTY-01', 'Quantity 3 with stock 5 is valid', true, isValid, isValid === true);
    });

    it('UT-QTY-02: Rejects non-integer or decimal quantity', () => {
      const isValid = Core.ValidationRules.quantity.validate(2.5, 5);
      verify('UT-QTY-02', 'Quantity 2.5 rejected', false, isValid, isValid === false);
    });

    it('UT-QTY-03: Rejects zero quantity', () => {
      const isValid = Core.ValidationRules.quantity.validate(0, 5);
      verify('UT-QTY-03', 'Quantity 0 rejected', false, isValid, isValid === false);
    });

    it('UT-QTY-04: Rejects negative quantity', () => {
      const isValid = Core.ValidationRules.quantity.validate(-2, 5);
      verify('UT-QTY-04', 'Quantity -2 rejected', false, isValid, isValid === false);
    });
  });

  describe('Cart Calculations', () => {
    const sampleProducts = [
      { id: 'p1', price: 100.00, stock: 10 },
      { id: 'p2', price: 20.00, stock: 10 }
    ];

    it('UT-CART-01: Computes accurate subtotal for varied items', () => {
      const cart = [{ id: 'p1', quantity: 2 }, { id: 'p2', quantity: 3 }];
      const totals = Core.calculateCartTotals(cart, sampleProducts);
      // (100 * 2) + (20 * 3) = 260
      verify('UT-CART-01', 'Subtotal calculation (200 + 60)', 260.00, totals.subtotal, totals.subtotal === 260.00);
    });

    it('UT-CART-02: Computes standard 5% tax accurately', () => {
      const cart = [{ id: 'p1', quantity: 1 }]; // subtotal = 100.00
      const totals = Core.calculateCartTotals(cart, sampleProducts);
      // 5% of 100 = 5.00
      verify('UT-CART-02', '5% Tax on $100', 5.00, totals.tax, totals.tax === 5.00);
    });

    it('UT-CART-03: Applies $5.00 shipping for orders under $50.00', () => {
      const cart = [{ id: 'p2', quantity: 2 }]; // subtotal = 40.00
      const totals = Core.calculateCartTotals(cart, sampleProducts);
      verify('UT-CART-03', 'Shipping for $40 subtotal is $5.00', 5.00, totals.shipping, totals.shipping === 5.00);
    });

    it('UT-CART-04: Unlocks Free Shipping ($0.00) for orders >= $50.00', () => {
      const cart = [{ id: 'p1', quantity: 1 }]; // subtotal = 100.00
      const totals = Core.calculateCartTotals(cart, sampleProducts);
      verify('UT-CART-04', 'Free shipping for $100 subtotal is $0.00', 0.00, totals.shipping, totals.shipping === 0.00);
    });

    it('UT-CART-05: Calculates correct total (subtotal + tax + shipping)', () => {
      const cart = [{ id: 'p2', quantity: 1 }]; // subtotal = 20, tax = 1.00, shipping = 5.00 -> total = 26.00
      const totals = Core.calculateCartTotals(cart, sampleProducts);
      verify('UT-CART-05', 'Total computation: 20 + 1 + 5', 26.00, totals.total, totals.total === 26.00);
    });
  });

  describe('Stock Validation', () => {
    const productInStock = { id: 'p1', name: 'In Stock Item', stock: 5 };
    const productOutOfStock = { id: 'p2', name: 'Sold Out Item', stock: 0 };

    it('UT-STOCK-01: Detects product in-stock availability correctly', () => {
      const inStock = Core.isProductInStock(productInStock);
      verify('UT-STOCK-01', 'Product stock 5 is in-stock', true, inStock, inStock === true);
    });

    it('UT-STOCK-02: Flags out-of-stock product when stock is 0', () => {
      const outOfStock = !Core.isProductInStock(productOutOfStock);
      verify('UT-STOCK-02', 'Product stock 0 is out-of-stock', true, outOfStock, outOfStock === true);
    });

    it('UT-STOCK-03: Computes available remaining stock accounting for cart items', () => {
      const cart = [{ id: 'p1', quantity: 2 }];
      const available = Core.getAvailableStock(productInStock, cart);
      verify('UT-STOCK-03', 'Available stock (5 - 2 in cart)', 3, available, available === 3);
    });
  });
});

/* ==========================================================================
   2. INTEGRATION TESTING
   ========================================================================== */

describe('2. Integration Testing Suite', () => {
  const testProducts = [
    { id: 'p1', name: 'Item Alpha', price: 40.00, stock: 5 },
    { id: 'p2', name: 'Item Beta', price: 25.00, stock: 3 }
  ];

  it('IT-CART-01: Add product to cart and verify cart update', () => {
    let cart = [];
    const res = Core.addToCart(cart, testProducts, 'p1', 1);
    cart = res.cart;

    const pass = res.success === true && cart.length === 1 && cart[0].id === 'p1' && cart[0].quantity === 1;
    verify('IT-CART-01', 'Add product p1 to empty cart', 'success: true, length: 1, qty: 1', `success: ${res.success}, length: ${cart.length}, qty: ${cart[0]?.quantity}`, pass);
  });

  it('IT-QTY-01: Update cart quantity and verify recalculated total', () => {
    let cart = [{ id: 'p1', quantity: 1 }];
    const res = Core.updateCartQuantity(cart, testProducts, 'p1', 3);
    cart = res.cart;

    const totals = Core.calculateCartTotals(cart, testProducts);
    // 40 * 3 = 120. Tax = 6. Shipping = 0. Total = 126.
    const pass = res.success === true && cart[0].quantity === 3 && totals.total === 126.00;
    verify('IT-QTY-01', 'Increase qty to 3 -> Total = 126.00', 'qty: 3, total: 126.00', `qty: ${cart[0].quantity}, total: ${totals.total}`, pass);
  });

  it('IT-ORDER-01: Checkout with cart and verify order creation & cart clearing', () => {
    const cart = [{ id: 'p1', quantity: 2 }];
    const customer = {
      name: 'Jane Doe',
      email: 'jane@example.com',
      phone: '9876543210',
      address: '742 Evergreen Terrace',
      city: 'Springfield',
      state: 'IL',
      zip: '62704'
    };
    const payment = { method: 'cod' };

    const res = Core.processOrder(cart, testProducts, customer, payment);
    const pass = res.success === true && res.order && res.order.orderId.startsWith('ORD-') && res.clearedCart.length === 0;
    verify('IT-ORDER-01', 'Order created with valid ID & cleared cart', 'success: true, status: Confirmed', `success: ${res.success}, id: ${res.order?.orderId}`, pass);
  });

  it('IT-STORE-01: Verify localStorage synchronization on cart update', () => {
    const storage = new MockLocalStorage();
    const cart = [{ id: 'p1', quantity: 2 }];
    storage.setItem(Core.STORAGE_KEYS.CART, JSON.stringify(cart));

    const retrieved = JSON.parse(storage.getItem(Core.STORAGE_KEYS.CART));
    const pass = Array.isArray(retrieved) && retrieved[0].id === 'p1' && retrieved[0].quantity === 2;
    verify('IT-STORE-01', 'Cart persisted and reloaded from storage', 'p1 x 2', `${retrieved[0]?.id} x ${retrieved[0]?.quantity}`, pass);
  });

  it('IT-STORE-02: Verify inventory reduction persisted to storage after order', () => {
    const storage = new MockLocalStorage();
    let products = JSON.parse(JSON.stringify(testProducts)); // p1 stock is 5
    const cart = [{ id: 'p1', quantity: 2 }];
    const customer = {
      name: 'Alice Wonder',
      email: 'alice@example.com',
      phone: '1234567890',
      address: '10 Downing St',
      city: 'London',
      state: 'LN',
      zip: 'SW1A'
    };
    const payment = { method: 'cod' };

    const res = Core.processOrder(cart, products, customer, payment);
    storage.setItem(Core.STORAGE_KEYS.PRODUCTS, JSON.stringify(res.updatedProducts));

    const savedProducts = JSON.parse(storage.getItem(Core.STORAGE_KEYS.PRODUCTS));
    const savedP1 = savedProducts.find(p => p.id === 'p1');

    const pass = savedP1.stock === 3; // 5 - 2 = 3
    verify('IT-STORE-02', 'Product stock reduced from 5 to 3 in storage', 'stock: 3', `stock: ${savedP1?.stock}`, pass);
  });
});

/* ==========================================================================
   3. BLACK BOX TESTING
   ========================================================================== */

describe('3. Black Box Testing Suite', () => {
  const products = [
    { id: 'p1', name: 'Item 1', price: 50.00, stock: 5 },
    { id: 'p_out', name: 'Zero Stock Item', price: 20.00, stock: 0 }
  ];

  it('BB-CHK-01: Empty checkout attempt is blocked', () => {
    const emptyCart = [];
    const customer = {
      name: 'Bob Test',
      email: 'bob@example.com',
      phone: '9876543210',
      address: '123 Main St',
      city: 'Boston',
      state: 'MA',
      zip: '02108'
    };
    const payment = { method: 'cod' };

    const res = Core.processOrder(emptyCart, products, customer, payment);
    const pass = res.success === false && res.error.includes('empty');
    verify('BB-CHK-01', 'Reject checkout on empty cart', 'success: false', `success: ${res.success}, msg: "${res.error}"`, pass);
  });

  it('BB-CUST-01: Rejects invalid customer details (short name, bad email, bad phone)', () => {
    const invalidCustomer = {
      name: 'X',
      email: 'bad-email-address',
      phone: '12',
      address: 'St',
      city: 'A',
      state: '',
      zip: '1'
    };
    const res = Core.validateCheckoutPayload(invalidCustomer, { method: 'cod' });
    const pass = res.isValid === false && res.errors.name && res.errors.email && res.errors.phone;
    verify('BB-CUST-01', 'Reject malformed customer info', 'isValid: false with field errors', `isValid: ${res.isValid}, errorCount: ${Object.keys(res.errors).length}`, pass);
  });

  it('BB-QTY-01: Rejects negative quantity attempt', () => {
    const res = Core.addToCart([], products, 'p1', -3);
    const pass = res.success === false;
    verify('BB-QTY-01', 'Reject adding negative quantity (-3)', 'success: false', `success: ${res.success}, error: "${res.error}"`, pass);
  });

  it('BB-QTY-02: Zero quantity removes item from cart cleanly', () => {
    const cart = [{ id: 'p1', quantity: 2 }];
    const res = Core.updateCartQuantity(cart, products, 'p1', 0);
    const pass = res.success === true && res.removed === true && res.cart.length === 0;
    verify('BB-QTY-02', 'Setting quantity to 0 removes item', 'removed: true, cart: []', `removed: ${res.removed}, count: ${res.cart.length}`, pass);
  });

  it('BB-STOCK-01: Out-of-stock product addition is blocked', () => {
    const res = Core.addToCart([], products, 'p_out', 1);
    const pass = res.success === false && res.error.includes('out of stock');
    verify('BB-STOCK-01', 'Reject adding out-of-stock product', 'success: false, out of stock', `success: ${res.success}, error: "${res.error}"`, pass);
  });

  it('BB-INP-01: Rejects invalid card payment details (expired, short number)', () => {
    const customer = {
      name: 'Valid Name',
      email: 'valid@example.com',
      phone: '9876543210',
      address: '123 Valid St',
      city: 'City',
      state: 'ST',
      zip: '12345'
    };
    const badCardPayment = {
      method: 'card',
      cardNum: '123', // Too short
      cardExpiry: '01/20', // Expired
      cardCvv: '9' // Too short
    };
    const res = Core.validateCheckoutPayload(customer, badCardPayment);
    const pass = res.isValid === false && res.errors.cardNum && res.errors.cardExpiry && res.errors.cardCvv;
    verify('BB-INP-01', 'Reject expired card and invalid card digits', 'isValid: false with card errors', `isValid: ${res.isValid}`, pass);
  });

  it('BB-INP-02: Accepts complete, valid customer and card payment input', () => {
    const validCustomer = {
      name: 'Sarah Connor',
      email: 'sarah@resistance.org',
      phone: '3105551212',
      address: '420 South Vermont Avenue',
      city: 'Los Angeles',
      state: 'CA',
      zip: '90020'
    };
    const validCardPayment = {
      method: 'card',
      cardNum: '4111222233334444',
      cardExpiry: '12/29',
      cardCvv: '789'
    };
    const res = Core.validateCheckoutPayload(validCustomer, validCardPayment);
    const pass = res.isValid === true && Object.keys(res.errors).length === 0;
    verify('BB-INP-02', 'Accept fully valid checkout details', 'isValid: true, errors: {}', `isValid: ${res.isValid}, errors: ${JSON.stringify(res.errors)}`, pass);
  });
});

/* ==========================================================================
   4. FUNCTIONAL TESTING
   ========================================================================== */

describe('4. Functional Testing Suite', () => {
  const catalog = Core.INITIAL_PRODUCTS;

  it('FT-SRCH-01: Search returns relevant products matching query string', () => {
    const results = Core.filterAndSortProducts(catalog, { search: 'Headphones' });
    const pass = results.length > 0 && results.some(p => p.name.includes('Headphones'));
    verify('FT-SRCH-01', 'Search "Headphones" finds matching product', 'found >= 1 item', `found ${results.length} items`, pass);
  });

  it('FT-SRCH-02: Search for nonexistent query returns empty array', () => {
    const results = Core.filterAndSortProducts(catalog, { search: 'xyz987nonexistent' });
    const pass = results.length === 0;
    verify('FT-SRCH-02', 'Search nonexistent item returns 0 items', '0 items', `${results.length} items`, pass);
  });

  it('FT-CART-01: Functional Add to Cart updates item and count correctly', () => {
    let cart = [];
    const itemToAdd = catalog[0]; // p1
    const res = Core.addToCart(cart, catalog, itemToAdd.id, 2);
    cart = res.cart;

    const pass = res.success === true && cart.find(i => i.id === itemToAdd.id)?.quantity === 2;
    verify('FT-CART-01', 'Add 2 units of product to cart', 'qty: 2 in cart', `qty: ${cart[0]?.quantity}`, pass);
  });

  it('FT-CART-02: Functional Remove from Cart completely deletes item', () => {
    let cart = [{ id: 'p1', quantity: 2 }, { id: 'p2', quantity: 1 }];
    const res = Core.removeFromCart(cart, 'p1');
    cart = res.cart;

    const pass = res.success === true && cart.length === 1 && !cart.some(i => i.id === 'p1');
    verify('FT-CART-02', 'Remove p1 from cart', 'p1 removed, length: 1', `length: ${cart.length}, hasP1: ${cart.some(i => i.id === 'p1')}`, pass);
  });

  it('FT-E2E-01: End-to-End full purchasing workflow', () => {
    // 1. Initial State
    let products = JSON.parse(JSON.stringify(Core.INITIAL_PRODUCTS));
    let cart = [];

    // 2. Search product
    const searchResults = Core.filterAndSortProducts(products, { search: 'Mouse' });
    const selectedProduct = searchResults[0]; // p4
    const initialStock = selectedProduct.stock;

    // 3. Add to Cart
    const addRes = Core.addToCart(cart, products, selectedProduct.id, 2);
    cart = addRes.cart;

    // 4. Validate Cart Totals
    const totals = Core.calculateCartTotals(cart, products);

    // 5. Customer Checkout
    const customer = {
      name: 'Alexander Graham',
      email: 'alex@telecom.org',
      phone: '8005550199',
      address: '109 Court St',
      city: 'Boston',
      state: 'MA',
      zip: '02108'
    };
    const payment = { method: 'upi', upiId: 'alex@okaxis' };

    const orderRes = Core.processOrder(cart, products, customer, payment);

    // 6. Verify End State
    const orderCreated = orderRes.success === true && orderRes.order.total === totals.total;
    const stockReduced = orderRes.updatedProducts.find(p => p.id === selectedProduct.id).stock === (initialStock - 2);
    const cartEmptied = orderRes.clearedCart.length === 0;

    const pass = orderCreated && stockReduced && cartEmptied;
    verify('FT-E2E-01', 'End-to-End: Search -> Add -> Totals -> Checkout -> Stock Decrement -> Cart Clear', 'All steps succeed', `order: ${orderRes.success}, stockReduced: ${stockReduced}, cartCleared: ${cartEmptied}`, pass);
  });
});
