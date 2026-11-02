/**
 * AuraMart E-Commerce Core Logic Engine
 * Universal Module (Node.js & Browser compatible)
 * 
 * Provides pure business logic, calculations, data management, and validation.
 */

(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    // Node.js / CommonJS
    module.exports = factory();
  } else {
    // Browser global
    root.ECommerceCore = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const STORAGE_KEYS = {
    PRODUCTS: 'auramart_products_v1',
    CART: 'auramart_cart_v1',
    ORDERS: 'auramart_orders_v1'
  };

  const INITIAL_PRODUCTS = [
    {
      id: 'p1',
      name: 'Aura Wireless Headphones',
      category: 'Audio',
      price: 99.99,
      stock: 8,
      description: 'Active noise-cancelling over-ear headphones with 40h battery life and deep bass.',
      icon: 'headphones'
    },
    {
      id: 'p2',
      name: 'Pro Mechanical Keyboard',
      category: 'Electronics',
      price: 129.50,
      stock: 5,
      description: 'Customizable RGB hot-swappable mechanical keyboard with tactile brown switches.',
      icon: 'keyboard'
    },
    {
      id: 'p3',
      name: 'Smart Fitness Watch',
      category: 'Wearables',
      price: 179.00,
      stock: 4,
      description: 'AMOLED fitness tracker with heart-rate monitor, SpO2 sensor, and built-in GPS.',
      icon: 'watch'
    },
    {
      id: 'p4',
      name: 'Ergonomic Wireless Mouse',
      category: 'Electronics',
      price: 49.99,
      stock: 12,
      description: 'Precision vertical optical mouse designed to reduce wrist strain during long sessions.',
      icon: 'mouse'
    },
    {
      id: 'p5',
      name: 'Minimalist Desk Lamp',
      category: 'Home',
      price: 38.50,
      stock: 6,
      description: 'Dimmable LED desk lamp with touch controls, 3 color temperatures, and USB charging.',
      icon: 'lamp'
    },
    {
      id: 'p6',
      name: 'Everyday Travel Backpack',
      category: 'Accessories',
      price: 64.99,
      stock: 3,
      description: 'Water-resistant 25L commuter backpack with padded 15.6" laptop compartment.',
      icon: 'backpack'
    },
    {
      id: 'p7',
      name: 'True Wireless Earbuds',
      category: 'Audio',
      price: 59.00,
      stock: 10,
      description: 'Compact Bluetooth 5.3 in-ear earbuds with crystal clear calls and IPX5 resistance.',
      icon: 'earbuds'
    },
    {
      id: 'p8',
      name: 'Ultra HD 4K Action Camera',
      category: 'Electronics',
      price: 219.99,
      stock: 2,
      description: 'Rugged waterproof 4K/60fps camera with dual screens and 6-axis gyro stabilization.',
      icon: 'camera'
    },
    {
      id: 'p9',
      name: 'Insulated Stainless Tumbler',
      category: 'Home',
      price: 24.50,
      stock: 15,
      description: 'Vacuum-insulated 750ml flask keeping drinks ice-cold for 24h or steaming hot for 12h.',
      icon: 'bottle'
    },
    {
      id: 'p10',
      name: 'Leather Tech Sleeve',
      category: 'Accessories',
      price: 34.00,
      stock: 0, // Deliberately out of stock for testing
      description: 'Premium vegan leather protective envelope sleeve with magnetic snap closure.',
      icon: 'sleeve'
    }
  ];

  /* ==========================================================================
     Validation Rules
     ========================================================================== */

  const ValidationRules = {
    name: {
      validate: function (val) {
        if (typeof val !== 'string') return false;
        const trimmed = val.trim();
        return trimmed.length >= 3 && /^[a-zA-Z\s.'-]+$/.test(trimmed);
      },
      error: 'Please enter a valid full name (at least 3 characters, letters only).'
    },
    email: {
      validate: function (val) {
        if (typeof val !== 'string') return false;
        return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val.trim());
      },
      error: 'Please enter a valid email address (e.g., name@example.com).'
    },
    phone: {
      validate: function (val) {
        if (typeof val !== 'string' && typeof val !== 'number') return false;
        const digits = String(val).replace(/\D/g, '');
        return digits.length >= 10 && digits.length <= 15;
      },
      error: 'Please enter a valid phone number with at least 10 digits.'
    },
    city: {
      validate: function (val) {
        if (typeof val !== 'string') return false;
        return val.trim().length >= 2;
      },
      error: 'Please enter a valid city name.'
    },
    address: {
      validate: function (val) {
        if (typeof val !== 'string') return false;
        return val.trim().length >= 5;
      },
      error: 'Please enter your street address (at least 5 characters).'
    },
    state: {
      validate: function (val) {
        if (typeof val !== 'string') return false;
        return val.trim().length >= 2;
      },
      error: 'Please enter a state / province.'
    },
    zip: {
      validate: function (val) {
        if (typeof val !== 'string' && typeof val !== 'number') return false;
        return /^[a-zA-Z0-9\s-]{4,10}$/.test(String(val).trim());
      },
      error: 'Please enter a valid postal / ZIP code (4-10 characters).'
    },
    cardNum: {
      validate: function (val) {
        if (typeof val !== 'string' && typeof val !== 'number') return false;
        const digits = String(val).replace(/\D/g, '');
        return digits.length >= 13 && digits.length <= 19;
      },
      error: 'Enter a valid 16-digit card number.'
    },
    cardExpiry: {
      validate: function (val) {
        if (typeof val !== 'string') return false;
        const trimmed = val.trim();
        if (!/^(0[1-9]|1[0-2])\/?([0-9]{2})$/.test(trimmed)) return false;
        const parts = trimmed.split('/');
        const month = parseInt(parts[0], 10);
        const year = parseInt('20' + parts[1], 10);
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth() + 1;
        return year > currentYear || (year === currentYear && month >= currentMonth);
      },
      error: 'Enter valid future expiry date (MM/YY).'
    },
    cardCvv: {
      validate: function (val) {
        if (typeof val !== 'string' && typeof val !== 'number') return false;
        return /^\d{3,4}$/.test(String(val).trim());
      },
      error: 'Enter a 3 or 4 digit CVV code.'
    },
    upiId: {
      validate: function (val) {
        if (typeof val !== 'string') return false;
        return /^[\w.-]+@[\w.-]+$/.test(val.trim());
      },
      error: 'Enter a valid UPI ID (e.g., user@bank).'
    },
    quantity: {
      validate: function (val, stock) {
        const num = Number(val);
        if (!Number.isInteger(num)) return false;
        if (num <= 0) return false;
        if (typeof stock === 'number' && num > stock) return false;
        return true;
      },
      error: 'Quantity must be a positive integer not exceeding available stock.'
    }
  };

  /* ==========================================================================
     Calculations & Formatters
     ========================================================================== */

  function formatPrice(val) {
    const num = Number(val);
    if (isNaN(num)) return '$0.00';
    return `$${num.toFixed(2)}`;
  }

  function roundMoney(val) {
    return Math.round((Number(val) + Number.EPSILON) * 100) / 100;
  }

  function calculateLineTotal(price, quantity) {
    const p = Number(price);
    const q = Number(quantity);
    if (isNaN(p) || isNaN(q) || q <= 0) return 0;
    return roundMoney(p * q);
  }

  function calculateCartTotals(cart, products) {
    let subtotal = 0;
    let itemCount = 0;

    if (Array.isArray(cart)) {
      cart.forEach(item => {
        const prod = (products || []).find(p => p.id === item.id);
        if (prod) {
          const qty = Number(item.quantity) || 0;
          subtotal += (Number(prod.price) || 0) * qty;
          itemCount += qty;
        }
      });
    }

    subtotal = roundMoney(subtotal);
    const tax = roundMoney(subtotal * 0.05); // 5% Standard Tax
    const shipping = subtotal >= 50 || subtotal === 0 ? 0 : 5.00; // Free on >= $50
    const total = roundMoney(subtotal + tax + shipping);

    return {
      subtotal,
      tax,
      shipping,
      total,
      itemCount
    };
  }

  /* ==========================================================================
     Stock & Cart Management Logic
     ========================================================================== */

  function isProductInStock(product) {
    if (!product) return false;
    return typeof product.stock === 'number' && product.stock > 0;
  }

  function getAvailableStock(product, cart) {
    if (!product) return 0;
    const cartItem = (cart || []).find(item => item.id === product.id);
    const inCart = cartItem ? cartItem.quantity : 0;
    return Math.max(0, product.stock - inCart);
  }

  function addToCart(cart, products, productId, quantityToAdd = 1) {
    const qty = Number(quantityToAdd);
    if (!Number.isInteger(qty) || qty <= 0) {
      return { success: false, error: 'Invalid quantity to add', cart };
    }

    const product = (products || []).find(p => p.id === productId);
    if (!product) {
      return { success: false, error: 'Product not found', cart };
    }

    if (product.stock <= 0) {
      return { success: false, error: 'Product is out of stock', cart };
    }

    const newCart = JSON.parse(JSON.stringify(cart || []));
    const cartItem = newCart.find(i => i.id === productId);
    const currentQty = cartItem ? cartItem.quantity : 0;

    if (currentQty + qty > product.stock) {
      return {
        success: false,
        error: `Cannot add ${qty}. Only ${product.stock - currentQty} more available.`,
        cart: newCart
      };
    }

    if (cartItem) {
      cartItem.quantity += qty;
    } else {
      newCart.push({ id: productId, quantity: qty });
    }

    return {
      success: true,
      cart: newCart,
      item: newCart.find(i => i.id === productId)
    };
  }

  function updateCartQuantity(cart, products, productId, newQuantity) {
    const qty = Number(newQuantity);
    const product = (products || []).find(p => p.id === productId);
    if (!product) {
      return { success: false, error: 'Product not found', cart };
    }

    const newCart = JSON.parse(JSON.stringify(cart || []));
    const index = newCart.findIndex(i => i.id === productId);

    if (index === -1) {
      return { success: false, error: 'Item not in cart', cart };
    }

    if (qty <= 0) {
      newCart.splice(index, 1);
      return { success: true, removed: true, cart: newCart };
    }

    if (!Number.isInteger(qty)) {
      return { success: false, error: 'Quantity must be an integer', cart: newCart };
    }

    if (qty > product.stock) {
      return {
        success: false,
        error: `Requested quantity (${qty}) exceeds stock (${product.stock})`,
        cart: newCart
      };
    }

    newCart[index].quantity = qty;
    return { success: true, cart: newCart, item: newCart[index] };
  }

  function removeFromCart(cart, productId) {
    const newCart = (cart || []).filter(item => item.id !== productId);
    return { success: true, cart: newCart };
  }

  /* ==========================================================================
     Search & Filtering Logic
     ========================================================================== */

  function filterAndSortProducts(products, filters) {
    if (!Array.isArray(products)) return [];
    let list = [...products];
    const { category = 'all', search = '', inStockOnly = false, sortBy = 'featured' } = (filters || {});

    // Filter by Category
    if (category && category !== 'all') {
      list = list.filter(p => p.category.toLowerCase() === category.toLowerCase());
    }

    // Filter by Search Query
    if (search && search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q)
      );
    }

    // Filter by In-Stock Only
    if (inStockOnly) {
      list = list.filter(p => p.stock > 0);
    }

    // Sorting
    switch (sortBy) {
      case 'price-asc':
        list.sort((a, b) => a.price - b.price);
        break;
      case 'price-desc':
        list.sort((a, b) => b.price - a.price);
        break;
      case 'name-asc':
        list.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'name-desc':
        list.sort((a, b) => b.name.localeCompare(a.name));
        break;
      case 'stock-desc':
        list.sort((a, b) => b.stock - a.stock);
        break;
      default:
        break;
    }

    return list;
  }

  /* ==========================================================================
     Checkout & Order Creation Logic
     ========================================================================== */

  function validateCheckoutPayload(customer, payment) {
    const errors = {};

    if (!customer) {
      return { isValid: false, errors: { customer: 'Customer details required' } };
    }

    if (!ValidationRules.name.validate(customer.name)) {
      errors.name = ValidationRules.name.error;
    }
    if (!ValidationRules.email.validate(customer.email)) {
      errors.email = ValidationRules.email.error;
    }
    if (!ValidationRules.phone.validate(customer.phone)) {
      errors.phone = ValidationRules.phone.error;
    }
    if (!ValidationRules.address.validate(customer.address)) {
      errors.address = ValidationRules.address.error;
    }
    if (!ValidationRules.city.validate(customer.city)) {
      errors.city = ValidationRules.city.error;
    }
    if (!ValidationRules.state.validate(customer.state)) {
      errors.state = ValidationRules.state.error;
    }
    if (!ValidationRules.zip.validate(customer.zip)) {
      errors.zip = ValidationRules.zip.error;
    }

    const method = payment ? payment.method : 'card';
    if (method === 'card') {
      if (!ValidationRules.cardNum.validate(payment.cardNum)) {
        errors.cardNum = ValidationRules.cardNum.error;
      }
      if (!ValidationRules.cardExpiry.validate(payment.cardExpiry)) {
        errors.cardExpiry = ValidationRules.cardExpiry.error;
      }
      if (!ValidationRules.cardCvv.validate(payment.cardCvv)) {
        errors.cardCvv = ValidationRules.cardCvv.error;
      }
    } else if (method === 'upi') {
      if (!ValidationRules.upiId.validate(payment.upiId)) {
        errors.upiId = ValidationRules.upiId.error;
      }
    } else if (method !== 'cod') {
      errors.paymentMethod = 'Invalid payment method selected';
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }

  function processOrder(cart, products, customer, payment) {
    if (!Array.isArray(cart) || cart.length === 0) {
      return { success: false, error: 'Cannot checkout with an empty cart' };
    }

    // Verify stock availability
    for (const item of cart) {
      const prod = (products || []).find(p => p.id === item.id);
      if (!prod) {
        return { success: false, error: `Product ID "${item.id}" does not exist` };
      }
      if (prod.stock < item.quantity) {
        return {
          success: false,
          error: `Insufficient stock for "${prod.name}". Available: ${prod.stock}, requested: ${item.quantity}`
        };
      }
    }

    // Validate inputs
    const validation = validateCheckoutPayload(customer, payment);
    if (!validation.isValid) {
      return { success: false, error: 'Validation failed', errors: validation.errors };
    }

    const totals = calculateCartTotals(cart, products);
    const updatedProducts = JSON.parse(JSON.stringify(products));

    // Decrement stock
    cart.forEach(item => {
      const prod = updatedProducts.find(p => p.id === item.id);
      if (prod) {
        prod.stock = Math.max(0, prod.stock - item.quantity);
      }
    });

    // Create order items snapshot
    const orderedItems = cart.map(item => {
      const prod = products.find(p => p.id === item.id);
      return {
        id: prod.id,
        name: prod.name,
        price: prod.price,
        quantity: item.quantity,
        total: calculateLineTotal(prod.price, item.quantity)
      };
    });

    const paymentLabel = payment.method === 'cod'
      ? 'Cash on Delivery'
      : payment.method === 'upi'
        ? `UPI (${payment.upiId})`
        : 'Credit/Debit Card';

    const orderId = `ORD-${Date.now().toString().slice(-6)}-${Math.floor(100 + Math.random() * 900)}`;

    const order = {
      orderId,
      date: new Date().toISOString(),
      customer: {
        name: customer.name.trim(),
        email: customer.email.trim(),
        phone: String(customer.phone).trim(),
        address: `${customer.address.trim()}, ${customer.city.trim()}, ${customer.state.trim()} ${customer.zip.trim()}`
      },
      paymentMethod: paymentLabel,
      items: orderedItems,
      subtotal: totals.subtotal,
      tax: totals.tax,
      shipping: totals.shipping,
      total: totals.total,
      status: 'Confirmed'
    };

    return {
      success: true,
      order,
      updatedProducts,
      clearedCart: []
    };
  }

  /* ==========================================================================
     Public Export API
     ========================================================================== */

  return {
    STORAGE_KEYS,
    INITIAL_PRODUCTS,
    ValidationRules,
    formatPrice,
    roundMoney,
    calculateLineTotal,
    calculateCartTotals,
    isProductInStock,
    getAvailableStock,
    addToCart,
    updateCartQuantity,
    removeFromCart,
    filterAndSortProducts,
    validateCheckoutPayload,
    processOrder
  };
});
