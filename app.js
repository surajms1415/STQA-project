/**
 * AuraMart - Pure Vanilla JavaScript E-Commerce Application
 * 
 * Modular Architecture:
 * 1. Storage & State Management
 * 2. Product Catalog & SVG Icons
 * 3. Product Grid & Filtering / Search
 * 4. Cart Management & Calculations
 * 5. Form Validation & Checkout
 * 6. Order Confirmation & History
 * 7. Toast Notifications & Event Listeners
 */

(function () {
  'use strict';

  /* ==========================================================================
     1. Initial Data & State Setup
     ========================================================================== */

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
      stock: 0, // Deliberately out-of-stock for demonstration
      description: 'Premium vegan leather protective envelope sleeve with magnetic snap closure.',
      icon: 'sleeve'
    }
  ];

  // Application State
  const AppState = {
    products: [],
    cart: [],
    orders: [],
    filter: {
      category: 'all',
      search: '',
      inStockOnly: false,
      sortBy: 'featured'
    }
  };

  /* ==========================================================================
     2. SVG Icon Library (Zero External Dependencies)
     ========================================================================== */

  const SvgIcons = {
    headphones: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 18v-6a9 9 0 0 1 18 0v6"></path>
        <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path>
      </svg>`,
    keyboard: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="4" width="20" height="16" rx="2" ry="2"></rect>
        <line x1="6" y1="8" x2="6" y2="8"></line>
        <line x1="10" y1="8" x2="10" y2="8"></line>
        <line x1="14" y1="8" x2="14" y2="8"></line>
        <line x1="18" y1="8" x2="18" y2="8"></line>
        <line x1="6" y1="12" x2="6" y2="12"></line>
        <line x1="10" y1="12" x2="10" y2="12"></line>
        <line x1="14" y1="12" x2="14" y2="12"></line>
        <line x1="18" y1="12" x2="18" y2="12"></line>
        <line x1="7" y1="16" x2="17" y2="16"></line>
      </svg>`,
    watch: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="7"></circle>
        <polyline points="12 9 12 12 13.5 13.5"></polyline>
        <path d="M16.51 17.35l-.35 3.83a2 2 0 0 1-2 1.82H9.83a2 2 0 0 1-2-1.82l-.35-3.83m.01-10.7l.35-3.83A2 2 0 0 1 9.83 1h4.35a2 2 0 0 1 2 1.82l.35 3.83"></path>
      </svg>`,
    mouse: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <rect x="5" y="2" width="14" height="20" rx="7"></rect>
        <line x1="12" y1="6" x2="12" y2="10"></line>
      </svg>`,
    lamp: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 18h6"></path>
        <path d="M10 22h4"></path>
        <path d="M12 2v4"></path>
        <path d="M12 6a7 7 0 0 0-5 6.9c0 2.2 1.3 4 3 5.1h4c1.7-1.1 3-2.9 3-5.1A7 7 0 0 0 12 6z"></path>
      </svg>`,
    backpack: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 10a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V10z"></path>
        <path d="M9 6V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"></path>
        <line x1="8" y1="14" x2="16" y2="14"></line>
        <line x1="8" y1="18" x2="16" y2="18"></line>
      </svg>`,
    earbuds: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="7" cy="8" r="4"></circle>
        <path d="M7 12v7a2 2 0 0 0 2 2h0"></path>
        <circle cx="17" cy="8" r="4"></circle>
        <path d="M17 12v7a2 2 0 0 1-2 2h0"></path>
      </svg>`,
    camera: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
        <circle cx="12" cy="13" r="4"></circle>
      </svg>`,
    bottle: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M8 2h8v3H8z"></path>
        <path d="M10 5v2a3 3 0 0 1-3 3v11a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V10a3 3 0 0 1-3-3V5"></path>
      </svg>`,
    sleeve: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="4" width="20" height="16" rx="2"></rect>
        <path d="M2 7l10 7 10-7"></path>
      </svg>`,
    default: `
      <svg class="product-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <rect x="2" y="3" width="20" height="18" rx="2"></rect>
        <circle cx="8.5" cy="8.5" r="1.5"></circle>
        <polyline points="21 15 16 10 5 21"></polyline>
      </svg>`
  };

  function getProductIcon(iconName) {
    return SvgIcons[iconName] || SvgIcons.default;
  }

  /* ==========================================================================
     3. LocalStorage Helpers
     ========================================================================== */

  function loadStorage(key, fallback) {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : fallback;
    } catch (err) {
      console.warn(`Error reading localStorage key "${key}":`, err);
      return fallback;
    }
  }

  function saveStorage(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (err) {
      console.error(`Error saving localStorage key "${key}":`, err);
      showToast('Could not save data to browser storage', 'error');
    }
  }

  /* ==========================================================================
     4. App State Initialization
     ========================================================================== */

  function initializeState() {
    // Products (preserve stock changes if previously saved)
    const storedProducts = loadStorage(STORAGE_KEYS.PRODUCTS, null);
    if (storedProducts && Array.isArray(storedProducts) && storedProducts.length > 0) {
      AppState.products = storedProducts;
    } else {
      AppState.products = JSON.parse(JSON.stringify(INITIAL_PRODUCTS));
      saveStorage(STORAGE_KEYS.PRODUCTS, AppState.products);
    }

    // Cart
    AppState.cart = loadStorage(STORAGE_KEYS.CART, []);

    // Orders History
    AppState.orders = loadStorage(STORAGE_KEYS.ORDERS, []);
  }

  /* ==========================================================================
     5. Formatting & Calculation Helpers
     ========================================================================== */

  function formatPrice(val) {
    return `$${Number(val).toFixed(2)}`;
  }

  function getProductById(id) {
    return AppState.products.find(p => p.id === id);
  }

  function getCartItemQuantity(productId) {
    const item = AppState.cart.find(c => c.id === productId);
    return item ? item.quantity : 0;
  }

  function calculateCartTotals() {
    let subtotal = 0;
    let itemCount = 0;

    AppState.cart.forEach(item => {
      const product = getProductById(item.id);
      if (product) {
        subtotal += product.price * item.quantity;
        itemCount += item.quantity;
      }
    });

    const tax = subtotal * 0.05; // 5% Standard Sales Tax
    const shipping = subtotal > 50 || subtotal === 0 ? 0 : 5.00; // Free shipping over $50
    const total = subtotal + tax + shipping;

    return {
      subtotal,
      tax,
      shipping,
      total,
      itemCount
    };
  }

  /* ==========================================================================
     6. Product Rendering & Filtering Logic
     ========================================================================== */

  function getFilteredAndSortedProducts() {
    let list = [...AppState.products];

    // Filter by category
    if (AppState.filter.category !== 'all') {
      list = list.filter(p => p.category.toLowerCase() === AppState.filter.category.toLowerCase());
    }

    // Filter by search query
    if (AppState.filter.search.trim()) {
      const q = AppState.filter.search.trim().toLowerCase();
      list = list.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q)
      );
    }

    // Filter by in-stock only
    if (AppState.filter.inStockOnly) {
      list = list.filter(p => p.stock > 0);
    }

    // Sorting
    switch (AppState.filter.sortBy) {
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
      default: // 'featured' (natural order)
        break;
    }

    return list;
  }

  function renderProducts() {
    const gridEl = document.getElementById('product-grid');
    const emptyStateEl = document.getElementById('no-products');
    const resultsCountEl = document.getElementById('results-count');
    const resetFiltersBtn = document.getElementById('reset-filters-btn');

    if (!gridEl) return;

    const filtered = getFilteredAndSortedProducts();

    // Check if any filter is active
    const hasActiveFilters =
      AppState.filter.category !== 'all' ||
      AppState.filter.search.trim() !== '' ||
      AppState.filter.inStockOnly;

    if (resetFiltersBtn) {
      resetFiltersBtn.classList.toggle('hidden', !hasActiveFilters);
    }

    if (resultsCountEl) {
      resultsCountEl.textContent = `Showing ${filtered.length} of ${AppState.products.length} products`;
    }

    if (filtered.length === 0) {
      gridEl.innerHTML = '';
      emptyStateEl.classList.remove('hidden');
      return;
    }

    emptyStateEl.classList.add('hidden');

    gridEl.innerHTML = filtered.map(product => {
      const cartQty = getCartItemQuantity(product.id);
      const remainingStock = product.stock - cartQty;
      const isOutOfStock = product.stock === 0;
      const isMaxInCart = remainingStock <= 0;

      let stockTagClass = 'in-stock';
      let stockTagText = `${product.stock} in stock`;

      if (isOutOfStock) {
        stockTagClass = 'out-stock';
        stockTagText = 'Out of Stock';
      } else if (product.stock <= 3) {
        stockTagClass = 'low-stock';
        stockTagText = `Only ${product.stock} left`;
      }

      let buttonText = 'Add to Cart';
      if (cartQty > 0) {
        buttonText = `Added (${cartQty})`;
      }
      if (isMaxInCart && !isOutOfStock) {
        buttonText = 'Max in Cart';
      }

      return `
        <article class="product-card ${isOutOfStock ? 'out-of-stock' : ''}" data-product-id="${product.id}">
          <div class="product-image-box">
            <span class="badge-tag">${escapeHtml(product.category)}</span>
            <span class="stock-tag ${stockTagClass}">${stockTagText}</span>
            ${getProductIcon(product.icon)}
          </div>
          <div class="product-body">
            <h3 class="product-title">${escapeHtml(product.name)}</h3>
            <p class="product-description">${escapeHtml(product.description)}</p>
            <div class="product-footer">
              <div class="product-price-box">
                <span class="price-currency">USD</span>
                <span class="product-price">${formatPrice(product.price)}</span>
              </div>
              <button 
                class="add-cart-btn ${cartQty > 0 ? 'added' : ''}" 
                data-action="add-to-cart" 
                data-id="${product.id}"
                ${isMaxInCart ? 'disabled' : ''}
                title="${isMaxInCart ? 'Stock limit reached' : 'Add to cart'}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 5v14M5 12h14"></path>
                </svg>
                <span>${buttonText}</span>
              </button>
            </div>
          </div>
        </article>
      `;
    }).join('');
  }

  /* ==========================================================================
     7. Cart Management
     ========================================================================== */

  function addToCart(productId) {
    const product = getProductById(productId);
    if (!product) return;

    if (product.stock <= 0) {
      showToast(`${product.name} is out of stock.`, 'warning');
      return;
    }

    const cartItem = AppState.cart.find(c => c.id === productId);

    if (cartItem) {
      if (cartItem.quantity >= product.stock) {
        showToast(`Cannot add more: only ${product.stock} items available in stock.`, 'warning');
        return;
      }
      cartItem.quantity += 1;
    } else {
      AppState.cart.push({ id: productId, quantity: 1 });
    }

    saveStorage(STORAGE_KEYS.CART, AppState.cart);
    updateCartUI();
    renderProducts(); // Update button badge / availability
    showToast(`Added "${product.name}" to cart!`, 'success');
  }

  function increaseCartQuantity(productId) {
    const product = getProductById(productId);
    const cartItem = AppState.cart.find(c => c.id === productId);

    if (!product || !cartItem) return;

    if (cartItem.quantity >= product.stock) {
      showToast(`Cannot increase: maximum stock of ${product.stock} reached.`, 'warning');
      return;
    }

    cartItem.quantity += 1;
    saveStorage(STORAGE_KEYS.CART, AppState.cart);
    updateCartUI();
    renderProducts();
  }

  function decreaseCartQuantity(productId) {
    const product = getProductById(productId);
    const cartItemIndex = AppState.cart.findIndex(c => c.id === productId);

    if (cartItemIndex === -1) return;

    if (AppState.cart[cartItemIndex].quantity > 1) {
      AppState.cart[cartItemIndex].quantity -= 1;
    } else {
      // If quantity is 1 and user decreases, remove item
      const removedName = product ? product.name : 'Item';
      AppState.cart.splice(cartItemIndex, 1);
      showToast(`Removed "${removedName}" from cart.`, 'info');
    }

    saveStorage(STORAGE_KEYS.CART, AppState.cart);
    updateCartUI();
    renderProducts();
  }

  function removeFromCart(productId) {
    const product = getProductById(productId);
    AppState.cart = AppState.cart.filter(c => c.id !== productId);
    saveStorage(STORAGE_KEYS.CART, AppState.cart);

    updateCartUI();
    renderProducts();
    showToast(`Removed "${product ? product.name : 'Item'}" from cart.`, 'info');
  }

  function clearCart(promptConfirm = true) {
    if (AppState.cart.length === 0) return;

    if (promptConfirm && !confirm('Are you sure you want to remove all items from your cart?')) {
      return;
    }

    AppState.cart = [];
    saveStorage(STORAGE_KEYS.CART, AppState.cart);
    updateCartUI();
    renderProducts();
    showToast('Your cart has been cleared.', 'info');
  }

  function updateCartUI() {
    const cartBadge = document.getElementById('cart-badge');
    const drawerCount = document.getElementById('cart-drawer-count');
    const cartContainer = document.getElementById('cart-items-container');
    const emptyCartView = document.getElementById('empty-cart-view');
    const cartFooter = document.getElementById('cart-footer');

    const subtotalEl = document.getElementById('cart-subtotal');
    const taxEl = document.getElementById('cart-tax');
    const shippingEl = document.getElementById('cart-shipping');
    const totalEl = document.getElementById('cart-total');
    const shippingNote = document.getElementById('shipping-note');

    const totals = calculateCartTotals();

    // Badges
    if (cartBadge) {
      cartBadge.textContent = totals.itemCount;
      cartBadge.classList.toggle('hidden', totals.itemCount === 0);
    }
    if (drawerCount) {
      drawerCount.textContent = `${totals.itemCount} item${totals.itemCount === 1 ? '' : 's'}`;
    }

    // Pricing Breakdown
    if (subtotalEl) subtotalEl.textContent = formatPrice(totals.subtotal);
    if (taxEl) taxEl.textContent = formatPrice(totals.tax);
    if (shippingEl) shippingEl.textContent = totals.shipping === 0 ? 'Free' : formatPrice(totals.shipping);
    if (totalEl) totalEl.textContent = formatPrice(totals.total);

    if (shippingNote) {
      if (totals.subtotal >= 50) {
        shippingNote.textContent = '(Free Shipping unlocked!)';
        shippingNote.style.color = 'var(--success)';
      } else {
        const remaining = 50 - totals.subtotal;
        shippingNote.textContent = `(Add ${formatPrice(remaining)} for Free Shipping)`;
        shippingNote.style.color = 'var(--text-muted)';
      }
    }

    // Toggle Empty State vs Items List
    if (AppState.cart.length === 0) {
      if (cartContainer) cartContainer.innerHTML = '';
      if (emptyCartView) emptyCartView.classList.remove('hidden');
      if (cartFooter) cartFooter.classList.add('hidden');
      return;
    }

    if (emptyCartView) emptyCartView.classList.add('hidden');
    if (cartFooter) cartFooter.classList.remove('hidden');

    // Render Cart Items
    if (cartContainer) {
      cartContainer.innerHTML = AppState.cart.map(item => {
        const product = getProductById(item.id);
        if (!product) return '';

        const itemTotal = product.price * item.quantity;
        const isMax = item.quantity >= product.stock;

        return `
          <div class="cart-item" data-cart-id="${product.id}">
            <div class="cart-item-thumb">
              ${getProductIcon(product.icon)}
            </div>
            <div class="cart-item-info">
              <span class="cart-item-name">${escapeHtml(product.name)}</span>
              <span class="cart-item-unit-price">${formatPrice(product.price)} each</span>
              <button class="remove-item-btn" data-action="remove-item" data-id="${product.id}">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
                Remove
              </button>
            </div>
            <div class="cart-item-actions">
              <span class="cart-item-total">${formatPrice(itemTotal)}</span>
              <div class="qty-control">
                <button 
                  class="qty-btn" 
                  data-action="dec-qty" 
                  data-id="${product.id}" 
                  title="Decrease quantity">&minus;</button>
                <span class="qty-display">${item.quantity}</span>
                <button 
                  class="qty-btn" 
                  data-action="inc-qty" 
                  data-id="${product.id}" 
                  ${isMax ? 'disabled' : ''} 
                  title="${isMax ? 'Maximum stock reached' : 'Increase quantity'}">&plus;</button>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  /* ==========================================================================
     8. Modal & Drawer Open / Close Controls
     ========================================================================== */

  function openCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    if (drawer && overlay) {
      overlay.classList.remove('hidden');
      drawer.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    if (drawer && overlay) {
      drawer.classList.remove('open');
      overlay.classList.add('hidden');
      document.body.style.overflow = '';
    }
  }

  function openCheckoutModal() {
    if (AppState.cart.length === 0) {
      showToast('Your cart is empty. Add items before checking out.', 'warning');
      return;
    }

    closeCartDrawer();
    populateCheckoutSummary();

    const modal = document.getElementById('checkout-modal');
    if (modal) {
      modal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      // Focus first input
      setTimeout(() => {
        const firstInput = document.getElementById('cust-name');
        if (firstInput) firstInput.focus();
      }, 100);
    }
  }

  function closeCheckoutModal() {
    const modal = document.getElementById('checkout-modal');
    if (modal) {
      modal.classList.add('hidden');
      document.body.style.overflow = '';
    }
  }

  function populateCheckoutSummary() {
    const itemsContainer = document.getElementById('checkout-items-list');
    const subtotalEl = document.getElementById('checkout-subtotal');
    const taxEl = document.getElementById('checkout-tax');
    const shippingEl = document.getElementById('checkout-shipping');
    const totalEl = document.getElementById('checkout-total');
    const placeOrderText = document.getElementById('place-order-text');

    const totals = calculateCartTotals();

    if (itemsContainer) {
      itemsContainer.innerHTML = AppState.cart.map(item => {
        const product = getProductById(item.id);
        if (!product) return '';
        return `
          <div class="checkout-item-row">
            <span class="checkout-item-title">${escapeHtml(product.name)}</span>
            <span class="checkout-item-qty">&times; ${item.quantity}</span>
            <span><strong>${formatPrice(product.price * item.quantity)}</strong></span>
          </div>
        `;
      }).join('');
    }

    if (subtotalEl) subtotalEl.textContent = formatPrice(totals.subtotal);
    if (taxEl) taxEl.textContent = formatPrice(totals.tax);
    if (shippingEl) shippingEl.textContent = totals.shipping === 0 ? 'Free' : formatPrice(totals.shipping);
    if (totalEl) totalEl.textContent = formatPrice(totals.total);
    if (placeOrderText) placeOrderText.textContent = `Place Order (${formatPrice(totals.total)})`;
  }

  /* ==========================================================================
     9. Form Validation & Checkout Submission
     ========================================================================== */

  const ValidationRules = {
    name: {
      validate: (val) => val.trim().length >= 3 && /^[a-zA-Z\s.'-]+$/.test(val.trim()),
      error: 'Please enter a valid full name (at least 3 characters, letters only).'
    },
    email: {
      validate: (val) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val.trim()),
      error: 'Please enter a valid email address (e.g., name@example.com).'
    },
    phone: {
      validate: (val) => {
        const digits = val.replace(/\D/g, '');
        return digits.length >= 10 && digits.length <= 15;
      },
      error: 'Please enter a valid phone number with at least 10 digits.'
    },
    city: {
      validate: (val) => val.trim().length >= 2,
      error: 'Please enter a valid city name.'
    },
    address: {
      validate: (val) => val.trim().length >= 5,
      error: 'Please enter your street address (at least 5 characters).'
    },
    state: {
      validate: (val) => val.trim().length >= 2,
      error: 'Please enter a state / province.'
    },
    zip: {
      validate: (val) => /^[a-zA-Z0-9\s-]{4,10}$/.test(val.trim()),
      error: 'Please enter a valid postal / ZIP code (4-10 characters).'
    },
    cardNum: {
      validate: (val) => {
        const digits = val.replace(/\D/g, '');
        return digits.length >= 13 && digits.length <= 19;
      },
      error: 'Enter a valid 16-digit card number.'
    },
    cardExpiry: {
      validate: (val) => {
        if (!/^(0[1-9]|1[0-2])\/?([0-9]{2})$/.test(val.trim())) return false;
        const [monthStr, yearStr] = val.split('/');
        const month = parseInt(monthStr, 10);
        const year = parseInt('20' + yearStr, 10);
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth() + 1;
        return year > currentYear || (year === currentYear && month >= currentMonth);
      },
      error: 'Enter valid future expiry date (MM/YY).'
    },
    cardCvv: {
      validate: (val) => /^\d{3,4}$/.test(val.trim()),
      error: 'Enter a 3 or 4 digit CVV code.'
    },
    upiId: {
      validate: (val) => /^[\w.-]+@[\w.-]+$/.test(val.trim()),
      error: 'Enter a valid UPI ID (e.g., user@bank).'
    }
  };

  function setFieldError(fieldId, errorMsg) {
    const inputEl = document.getElementById(fieldId);
    const errorEl = document.getElementById(`${fieldId}-error`);

    if (inputEl) {
      if (errorMsg) {
        inputEl.classList.add('invalid');
      } else {
        inputEl.classList.remove('invalid');
      }
    }

    if (errorEl) {
      errorEl.textContent = errorMsg || '';
    }
  }

  function validateCheckoutForm() {
    let isValid = true;

    // 1. Customer info fields
    const nameVal = document.getElementById('cust-name').value;
    if (!ValidationRules.name.validate(nameVal)) {
      setFieldError('cust-name', ValidationRules.name.error);
      isValid = false;
    } else {
      setFieldError('cust-name', '');
    }

    const emailVal = document.getElementById('cust-email').value;
    if (!ValidationRules.email.validate(emailVal)) {
      setFieldError('cust-email', ValidationRules.email.error);
      isValid = false;
    } else {
      setFieldError('cust-email', '');
    }

    const phoneVal = document.getElementById('cust-phone').value;
    if (!ValidationRules.phone.validate(phoneVal)) {
      setFieldError('cust-phone', ValidationRules.phone.error);
      isValid = false;
    } else {
      setFieldError('cust-phone', '');
    }

    const cityVal = document.getElementById('cust-city').value;
    if (!ValidationRules.city.validate(cityVal)) {
      setFieldError('cust-city', ValidationRules.city.error);
      isValid = false;
    } else {
      setFieldError('cust-city', '');
    }

    const addressVal = document.getElementById('cust-address').value;
    if (!ValidationRules.address.validate(addressVal)) {
      setFieldError('cust-address', ValidationRules.address.error);
      isValid = false;
    } else {
      setFieldError('cust-address', '');
    }

    const stateVal = document.getElementById('cust-state').value;
    if (!ValidationRules.state.validate(stateVal)) {
      setFieldError('cust-state', ValidationRules.state.error);
      isValid = false;
    } else {
      setFieldError('cust-state', '');
    }

    const zipVal = document.getElementById('cust-zip').value;
    if (!ValidationRules.zip.validate(zipVal)) {
      setFieldError('cust-zip', ValidationRules.zip.error);
      isValid = false;
    } else {
      setFieldError('cust-zip', '');
    }

    // 2. Payment Method Validation
    const paymentMethodEl = document.querySelector('input[name="paymentMethod"]:checked');
    const paymentMethod = paymentMethodEl ? paymentMethodEl.value : 'card';

    if (paymentMethod === 'card') {
      const cardNumVal = document.getElementById('card-num').value;
      if (!ValidationRules.cardNum.validate(cardNumVal)) {
        setFieldError('card-num', ValidationRules.cardNum.error);
        isValid = false;
      } else {
        setFieldError('card-num', '');
      }

      const cardExpiryVal = document.getElementById('card-expiry').value;
      if (!ValidationRules.cardExpiry.validate(cardExpiryVal)) {
        setFieldError('card-expiry', ValidationRules.cardExpiry.error);
        isValid = false;
      } else {
        setFieldError('card-expiry', '');
      }

      const cardCvvVal = document.getElementById('card-cvv').value;
      if (!ValidationRules.cardCvv.validate(cardCvvVal)) {
        setFieldError('card-cvv', ValidationRules.cardCvv.error);
        isValid = false;
      } else {
        setFieldError('card-cvv', '');
      }
    } else if (paymentMethod === 'upi') {
      const upiIdVal = document.getElementById('upi-id').value;
      if (!ValidationRules.upiId.validate(upiIdVal)) {
        setFieldError('upi-id', ValidationRules.upiId.error);
        isValid = false;
      } else {
        setFieldError('upi-id', '');
      }
    }

    return isValid;
  }

  function handleCheckoutSubmit(e) {
    e.preventDefault();

    if (AppState.cart.length === 0) {
      showToast('Your cart is empty!', 'warning');
      return;
    }

    // Verify current stock availability before submitting order
    for (const item of AppState.cart) {
      const prod = getProductById(item.id);
      if (!prod || prod.stock < item.quantity) {
        showToast(`Sorry, ${prod ? prod.name : 'an item'} only has ${prod ? prod.stock : 0} in stock. Please adjust your cart.`, 'error');
        return;
      }
    }

    // Validate inputs
    if (!validateCheckoutForm()) {
      showToast('Please fix the errors in the form before placing your order.', 'error');
      return;
    }

    // Collect Customer Data
    const name = document.getElementById('cust-name').value.trim();
    const email = document.getElementById('cust-email').value.trim();
    const phone = document.getElementById('cust-phone').value.trim();
    const address = document.getElementById('cust-address').value.trim();
    const city = document.getElementById('cust-city').value.trim();
    const state = document.getElementById('cust-state').value.trim();
    const zip = document.getElementById('cust-zip').value.trim();
    const paymentMethodEl = document.querySelector('input[name="paymentMethod"]:checked');
    const paymentMethod = paymentMethodEl ? paymentMethodEl.value : 'card';

    let paymentLabel = 'Credit/Debit Card';
    if (paymentMethod === 'cod') paymentLabel = 'Cash on Delivery';
    if (paymentMethod === 'upi') paymentLabel = `UPI (${document.getElementById('upi-id').value.trim()})`;

    const totals = calculateCartTotals();

    // Prepare Items snapshot
    const orderedItems = AppState.cart.map(item => {
      const product = getProductById(item.id);
      return {
        id: product.id,
        name: product.name,
        price: product.price,
        quantity: item.quantity,
        total: product.price * item.quantity
      };
    });

    // 1. Decrement Stock from Products in State & LocalStorage
    AppState.cart.forEach(cartItem => {
      const product = getProductById(cartItem.id);
      if (product) {
        product.stock = Math.max(0, product.stock - cartItem.quantity);
      }
    });
    saveStorage(STORAGE_KEYS.PRODUCTS, AppState.products);

    // 2. Generate Order Record
    const orderId = `ORD-${Date.now().toString().slice(-6)}-${Math.floor(100 + Math.random() * 900)}`;
    const newOrder = {
      orderId,
      date: new Date().toLocaleString('en-US', {
        dateStyle: 'medium',
        timeStyle: 'short'
      }),
      customer: {
        name,
        email,
        phone,
        address: `${address}, ${city}, ${state} ${zip}`
      },
      paymentMethod: paymentLabel,
      items: orderedItems,
      subtotal: totals.subtotal,
      tax: totals.tax,
      shipping: totals.shipping,
      total: totals.total
    };

    // 3. Save Order to History in LocalStorage
    AppState.orders.unshift(newOrder);
    saveStorage(STORAGE_KEYS.ORDERS, AppState.orders);

    // 4. Empty Cart
    AppState.cart = [];
    saveStorage(STORAGE_KEYS.CART, AppState.cart);

    // 5. Update UI
    updateCartUI();
    renderProducts();
    updateOrdersBadge();

    // 6. Close Checkout Modal & Display Order Confirmation Receipt
    closeCheckoutModal();
    displayOrderConfirmation(newOrder);

    // Reset Form
    document.getElementById('checkout-form').reset();
    togglePaymentFields();
  }

  /* ==========================================================================
     10. Order Confirmation & Receipt Display
     ========================================================================== */

  function displayOrderConfirmation(order) {
    document.getElementById('receipt-order-id').textContent = `#${order.orderId}`;
    document.getElementById('receipt-date').textContent = order.date;
    document.getElementById('receipt-name').textContent = order.customer.name;
    document.getElementById('receipt-email').textContent = order.customer.email;
    document.getElementById('receipt-phone').textContent = order.customer.phone;
    document.getElementById('receipt-payment').textContent = order.paymentMethod;
    document.getElementById('receipt-address').textContent = order.customer.address;

    // Items table
    const itemsTable = document.getElementById('receipt-items-table');
    itemsTable.innerHTML = order.items.map(item => `
      <div class="receipt-item-row">
        <span>${escapeHtml(item.name)} <small class="text-muted">(&times;${item.quantity})</small></span>
        <strong>${formatPrice(item.total)}</strong>
      </div>
    `).join('');

    // Totals table
    const totalsTable = document.getElementById('receipt-totals-table');
    totalsTable.innerHTML = `
      <div class="price-row">
        <span>Subtotal</span>
        <span>${formatPrice(order.subtotal)}</span>
      </div>
      <div class="price-row">
        <span>Sales Tax (5%)</span>
        <span>${formatPrice(order.tax)}</span>
      </div>
      <div class="price-row">
        <span>Shipping</span>
        <span>${order.shipping === 0 ? 'Free' : formatPrice(order.shipping)}</span>
      </div>
      <div class="price-row total-row">
        <span>Total Paid</span>
        <span>${formatPrice(order.total)}</span>
      </div>
    `;

    const successModal = document.getElementById('order-success-modal');
    if (successModal) {
      successModal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeOrderConfirmationModal() {
    const successModal = document.getElementById('order-success-modal');
    if (successModal) {
      successModal.classList.add('hidden');
      document.body.style.overflow = '';
    }
  }

  /* ==========================================================================
     11. Order History
     ========================================================================== */

  function updateOrdersBadge() {
    const badge = document.getElementById('orders-badge');
    if (!badge) return;
    const count = AppState.orders.length;
    badge.textContent = count;
    badge.classList.toggle('hidden', count === 0);
  }

  function openOrdersHistoryModal() {
    const modal = document.getElementById('orders-history-modal');
    const container = document.getElementById('orders-history-list');

    if (AppState.orders.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="padding: 2.5rem 1rem;">
          <div class="empty-icon">📦</div>
          <h3>No Orders Found</h3>
          <p>You haven't placed any orders yet. Once you complete a purchase, your order history will appear here.</p>
        </div>
      `;
    } else {
      container.innerHTML = AppState.orders.map(order => `
        <div class="history-order-item">
          <div class="history-order-header">
            <div>
              <span class="history-order-id">#${escapeHtml(order.orderId)}</span>
              <div class="history-order-date">${escapeHtml(order.date)}</div>
            </div>
            <div>
              <span class="history-badge">Confirmed</span>
            </div>
          </div>
          <div class="history-order-details">
            <div><strong>Items (${order.items.reduce((acc, i) => acc + i.quantity, 0)}):</strong> 
              ${order.items.map(i => `${escapeHtml(i.name)} (${i.quantity})`).join(', ')}
            </div>
            <div><strong>Shipped to:</strong> ${escapeHtml(order.customer.name)} - ${escapeHtml(order.customer.address)}</div>
            <div><strong>Payment:</strong> ${escapeHtml(order.paymentMethod)}</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: var(--text-main); margin-top: 0.35rem;">
              Total: ${formatPrice(order.total)}
            </div>
          </div>
        </div>
      `).join('');
    }

    if (modal) {
      modal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeOrdersHistoryModal() {
    const modal = document.getElementById('orders-history-modal');
    if (modal) {
      modal.classList.add('hidden');
      document.body.style.overflow = '';
    }
  }

  function clearOrderHistory() {
    if (AppState.orders.length === 0) return;
    if (!confirm('Are you sure you want to clear your entire order history?')) return;

    AppState.orders = [];
    saveStorage(STORAGE_KEYS.ORDERS, []);
    updateOrdersBadge();
    openOrdersHistoryModal(); // re-render empty state
    showToast('Order history cleared.', 'info');
  }

  /* ==========================================================================
     12. UI Toast Notifications
     ========================================================================== */

  function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let iconSvg = '';
    if (type === 'success') {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
    } else if (type === 'warning') {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>';
    } else if (type === 'error') {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';
    } else {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
    }

    toast.innerHTML = `${iconSvg}<span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      if (toast.parentNode === container) {
        container.removeChild(toast);
      }
    }, 3000);
  }

  /* ==========================================================================
     13. Utilities & Event Binding
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

  function togglePaymentFields() {
    const selectedMethod = document.querySelector('input[name="paymentMethod"]:checked')?.value;
    const cardGroup = document.getElementById('card-fields-group');
    const upiGroup = document.getElementById('upi-fields-group');

    if (cardGroup) {
      cardGroup.classList.toggle('hidden', selectedMethod !== 'card');
    }
    if (upiGroup) {
      upiGroup.classList.toggle('hidden', selectedMethod !== 'upi');
    }
  }

  function resetAllDemoData() {
    if (!confirm('This will reset product stock, cart, and order history back to fresh demo defaults. Proceed?')) {
      return;
    }

    localStorage.removeItem(STORAGE_KEYS.PRODUCTS);
    localStorage.removeItem(STORAGE_KEYS.CART);
    localStorage.removeItem(STORAGE_KEYS.ORDERS);

    AppState.products = JSON.parse(JSON.stringify(INITIAL_PRODUCTS));
    saveStorage(STORAGE_KEYS.PRODUCTS, AppState.products);
    AppState.cart = [];
    AppState.orders = [];

    // Reset filters
    AppState.filter = {
      category: 'all',
      search: '',
      inStockOnly: false,
      sortBy: 'featured'
    };

    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.value = '';
    const stockFilter = document.getElementById('stock-filter');
    if (stockFilter) stockFilter.checked = false;
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) sortSelect.value = 'featured';

    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.category === 'all');
    });

    renderProducts();
    updateCartUI();
    updateOrdersBadge();
    showToast('Demo data restored to original state!', 'success');
  }

  function setupEventListeners() {
    // Brand click: reset filters
    const brandLogo = document.getElementById('brand-logo');
    if (brandLogo) {
      brandLogo.addEventListener('click', () => {
        AppState.filter.category = 'all';
        AppState.filter.search = '';
        AppState.filter.inStockOnly = false;
        AppState.filter.sortBy = 'featured';

        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.value = '';
        const clearBtn = document.getElementById('clear-search-btn');
        if (clearBtn) clearBtn.classList.remove('visible');
        const stockFilter = document.getElementById('stock-filter');
        if (stockFilter) stockFilter.checked = false;
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) sortSelect.value = 'featured';

        document.querySelectorAll('.tab-btn').forEach(b => {
          b.classList.toggle('active', b.dataset.category === 'all');
        });

        renderProducts();
      });
    }

    // Search input
    const searchInput = document.getElementById('search-input');
    const clearSearchBtn = document.getElementById('clear-search-btn');

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        AppState.filter.search = e.target.value;
        if (clearSearchBtn) {
          clearSearchBtn.classList.toggle('visible', e.target.value.length > 0);
        }
        renderProducts();
      });
    }

    if (clearSearchBtn) {
      clearSearchBtn.addEventListener('click', () => {
        if (searchInput) {
          searchInput.value = '';
          AppState.filter.search = '';
          clearSearchBtn.classList.remove('visible');
          searchInput.focus();
          renderProducts();
        }
      });
    }

    // Category Tabs
    const categoryTabs = document.getElementById('category-tabs');
    if (categoryTabs) {
      categoryTabs.addEventListener('click', (e) => {
        const btn = e.target.closest('.tab-btn');
        if (!btn) return;

        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        AppState.filter.category = btn.dataset.category;
        renderProducts();
      });
    }

    // Stock Filter Toggle
    const stockFilter = document.getElementById('stock-filter');
    if (stockFilter) {
      stockFilter.addEventListener('change', (e) => {
        AppState.filter.inStockOnly = e.target.checked;
        renderProducts();
      });
    }

    // Sort Dropdown
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
      sortSelect.addEventListener('change', (e) => {
        AppState.filter.sortBy = e.target.value;
        renderProducts();
      });
    }

    // Reset Filters Buttons
    const resetFiltersBtn = document.getElementById('reset-filters-btn');
    const emptyResetBtn = document.getElementById('empty-reset-btn');
    const clearAllFilters = () => {
      AppState.filter.category = 'all';
      AppState.filter.search = '';
      AppState.filter.inStockOnly = false;

      if (searchInput) {
        searchInput.value = '';
        clearSearchBtn.classList.remove('visible');
      }
      if (stockFilter) {
        stockFilter.checked = false;
      }

      document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.category === 'all');
      });

      renderProducts();
    };

    if (resetFiltersBtn) resetFiltersBtn.addEventListener('click', clearAllFilters);
    if (emptyResetBtn) emptyResetBtn.addEventListener('click', clearAllFilters);

    // Cart Open / Close Buttons
    const cartBtn = document.getElementById('cart-btn');
    const closeCartBtn = document.getElementById('close-cart-btn');
    const cartOverlay = document.getElementById('cart-overlay');
    const continueShoppingBtn = document.getElementById('continue-shopping-btn');

    if (cartBtn) cartBtn.addEventListener('click', openCartDrawer);
    if (closeCartBtn) closeCartBtn.addEventListener('click', closeCartDrawer);
    if (cartOverlay) cartOverlay.addEventListener('click', closeCartDrawer);
    if (continueShoppingBtn) continueShoppingBtn.addEventListener('click', closeCartDrawer);

    // Cart Items Event Delegation (Add, Inc, Dec, Remove)
    document.addEventListener('click', (e) => {
      const target = e.target.closest('[data-action]');
      if (!target) return;

      const action = target.dataset.action;
      const productId = target.dataset.id;

      if (action === 'add-to-cart') {
        addToCart(productId);
      } else if (action === 'inc-qty') {
        increaseCartQuantity(productId);
      } else if (action === 'dec-qty') {
        decreaseCartQuantity(productId);
      } else if (action === 'remove-item') {
        removeFromCart(productId);
      }
    });

    // Clear Cart Button
    const clearCartBtn = document.getElementById('clear-cart-btn');
    if (clearCartBtn) {
      clearCartBtn.addEventListener('click', () => clearCart(true));
    }

    // Proceed to Checkout
    const proceedCheckoutBtn = document.getElementById('proceed-checkout-btn');
    if (proceedCheckoutBtn) {
      proceedCheckoutBtn.addEventListener('click', openCheckoutModal);
    }

    // Close Checkout Modal
    const closeCheckoutBtn = document.getElementById('close-checkout-btn');
    const backToCartBtn = document.getElementById('back-to-cart-btn');
    if (closeCheckoutBtn) closeCheckoutBtn.addEventListener('click', closeCheckoutModal);
    if (backToCartBtn) {
      backToCartBtn.addEventListener('click', () => {
        closeCheckoutModal();
        openCartDrawer();
      });
    }

    // Payment Radio Switcher
    document.querySelectorAll('input[name="paymentMethod"]').forEach(radio => {
      radio.addEventListener('change', togglePaymentFields);
    });

    // Realtime Input Form Validation on input/blur
    const inputsToValidate = [
      { id: 'cust-name', rule: ValidationRules.name },
      { id: 'cust-email', rule: ValidationRules.email },
      { id: 'cust-phone', rule: ValidationRules.phone },
      { id: 'cust-city', rule: ValidationRules.city },
      { id: 'cust-address', rule: ValidationRules.address },
      { id: 'cust-state', rule: ValidationRules.state },
      { id: 'cust-zip', rule: ValidationRules.zip }
    ];

    inputsToValidate.forEach(({ id, rule }) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('blur', () => {
          if (el.value.trim() !== '') {
            const isValid = rule.validate(el.value);
            setFieldError(id, isValid ? '' : rule.error);
          }
        });
        el.addEventListener('input', () => {
          if (el.classList.contains('invalid')) {
            const isValid = rule.validate(el.value);
            if (isValid) setFieldError(id, '');
          }
        });
      }
    });

    // Card Input Auto-formatting & Validation
    const cardNumInput = document.getElementById('card-num');
    if (cardNumInput) {
      cardNumInput.addEventListener('input', (e) => {
        let val = e.target.value.replace(/\D/g, '').substring(0, 16);
        let formatted = val.match(/.{1,4}/g)?.join(' ') || val;
        e.target.value = formatted;
        if (cardNumInput.classList.contains('invalid')) {
          if (ValidationRules.cardNum.validate(val)) setFieldError('card-num', '');
        }
      });
    }

    const cardExpiryInput = document.getElementById('card-expiry');
    if (cardExpiryInput) {
      cardExpiryInput.addEventListener('input', (e) => {
        let val = e.target.value.replace(/\D/g, '').substring(0, 4);
        if (val.length >= 3) {
          val = val.substring(0, 2) + '/' + val.substring(2);
        }
        e.target.value = val;
        if (cardExpiryInput.classList.contains('invalid')) {
          if (ValidationRules.cardExpiry.validate(val)) setFieldError('card-expiry', '');
        }
      });
    }

    // Checkout Form Submit
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
      checkoutForm.addEventListener('submit', handleCheckoutSubmit);
    }

    // Order Success Modal Actions
    const finishShoppingBtn = document.getElementById('finish-shopping-btn');
    if (finishShoppingBtn) {
      finishShoppingBtn.addEventListener('click', closeOrderConfirmationModal);
    }

    const printReceiptBtn = document.getElementById('print-receipt-btn');
    if (printReceiptBtn) {
      printReceiptBtn.addEventListener('click', () => {
        window.print();
      });
    }

    // Orders History Modal
    const ordersBtn = document.getElementById('orders-btn');
    const closeOrdersBtn = document.getElementById('close-orders-btn');
    const closeHistoryFooterBtn = document.getElementById('close-history-footer-btn');
    const clearOrdersBtn = document.getElementById('clear-orders-btn');

    if (ordersBtn) ordersBtn.addEventListener('click', openOrdersHistoryModal);
    if (closeOrdersBtn) closeOrdersBtn.addEventListener('click', closeOrdersHistoryModal);
    if (closeHistoryFooterBtn) closeHistoryFooterBtn.addEventListener('click', closeOrdersHistoryModal);
    if (clearOrdersBtn) clearOrdersBtn.addEventListener('click', clearOrderHistory);

    // Reset All Demo Data
    const resetAllBtn = document.getElementById('reset-all-demo-btn');
    if (resetAllBtn) resetAllBtn.addEventListener('click', resetAllDemoData);

    // Close Modals on Escape Key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeCartDrawer();
        closeCheckoutModal();
        closeOrderConfirmationModal();
        closeOrdersHistoryModal();
      }
    });
  }

  /* ==========================================================================
     14. App Bootstrap
     ========================================================================== */

  function initApp() {
    initializeState();
    setupEventListeners();
    renderProducts();
    updateCartUI();
    updateOrdersBadge();
    togglePaymentFields();
    console.log('AuraMart initialized successfully with vanilla JavaScript & localStorage.');
  }

  // Start when DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }

})();
