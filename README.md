# 🛒 AuraMart E-Commerce & STQA Testing Framework

[![Pytest Suite](https://img.shields.io/badge/Pytest-345%20Passing-success?style=for-the-badge&logo=pytest&logoColor=white)](python_tests/)
[![Playwright E2E](https://img.shields.io/badge/Playwright%20E2E-33%20Passing-success?style=for-the-badge&logo=playwright&logoColor=white)](python_tests/playwright_tests/)
[![Requests API](https://img.shields.io/badge/Requests%20API-26%20Passing-success?style=for-the-badge&logo=fastapi&logoColor=white)](python_tests/api_tests/)
[![Total Tests](https://img.shields.io/badge/Total%20Tests-378%20Passed-brightgreen?style=for-the-badge)](reports/pytest_report.html)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](requirements.txt)
[![Pass Rate](https://img.shields.io/badge/Pass%20Rate-100%25-brightgreen?style=for-the-badge)](qa-report.html)
[![Defects](https://img.shields.io/badge/Defects-6%20Resolved%20%2F%200%20Open-blue?style=for-the-badge)](DEFECT_REPORT.md)
[![Architecture](https://img.shields.io/badge/Stack-Vanilla%20HTML%20%7C%20CSS%20%7C%20ES6-orange?style=for-the-badge)](index.html)
[![Deployment](https://img.shields.io/badge/Deployment-Netlify%20%26%20GitHub%20Pages-informational?style=for-the-badge)](DEPLOYMENT.md)

A comprehensive, production-ready E-Commerce web application paired with an industrial-grade **Software Testing and Quality Assurance (STQA) Engineering Framework**. Built with a **pure semantic HTML5, modern CSS3, and vanilla JavaScript (ES6+)** presentation layer, and backed by a comprehensive **Python 3 / Pytest automated QA ecosystem** encompassing **378 automated test cases** across Unit, Integration, Functional, Black-Box, Boundary, Negative, Validation, Defect Lifecycle, Security, Performance, REST API, and Playwright Browser Automation suites.

The application is completely self-contained, offline-resilient, and optimized for instant static web deployment to **GitHub Pages** or **Netlify**.

---

## 📑 Table of Contents

1. [Interactive Dashboards & Links](#-interactive-dashboards--links)
2. [Testing Framework Architecture](#-testing-framework-architecture)
3. [Python Testing Suite Breakdown (378 Test Cases)](#-python-testing-suite-breakdown-378-test-cases)
4. [Installation & Environment Setup](#-installation--environment-setup)
5. [CLI Test Execution & Simple Commands](#-cli-test-execution--simple-commands)
6. [Security Testing Suite](#-security-testing-suite)
7. [Performance & Concurrency Benchmarking Suite](#-performance--concurrency-benchmarking-suite)
8. [Defect Management & QA Module (6 Common Bugs)](#-defect-management--qa-module-6-common-bugs)
9. [Requirements Traceability Matrix (RTM)](#-requirements-traceability-matrix-rtm)
10. [Playwright E2E Browser Automation](#-playwright-e2e-browser-automation)
11. [REST API Testing Demonstration](#-rest-api-testing-demonstration)
12. [Detailed HTML Test Reports](#-detailed-html-test-reports)
13. [Static Web Deployment Guide](#-static-web-deployment-guide)
14. [Repository Structure](#-repository-structure)

---

## 🌐 Interactive Dashboards & Links

The system features unified cross-navigation across four dedicated views:

| View / Document | Target File | Description |
| :--- | :--- | :--- |
| **🛍️ E-Commerce Store** | [`index.html`](index.html) | Live storefront featuring product catalog, live search, category filtering, slide-over cart drawer, customer checkout modal, and printable invoice receipts. |
| **🧪 QA Test Suite Dashboard** | [`test-dashboard.html`](test-dashboard.html) | In-browser automated test runner executing 32 unit, integration, black-box, and functional tests with live metrics, plus an **Interactive Manual Testing Studio** and links to Pytest HTML reports. |
| **🐛 Defect Management Dashboard** | [`defect-dashboard.html`](defect-dashboard.html) | Demonstrable defect lifecycle simulator: expose 6 controlled bugs in unpatched mode, apply verified code fixes, retest failed cases, and run the 32-test regression suite. |
| **📑 Final QA Executive Report (HTML)** | [`qa-report.html`](qa-report.html) | Formally certified, print-ready Quality Assurance Executive Report with traceability matrix, sign-off blocks, and deployment readiness checklists. |
| **📊 Pytest Master HTML Report** | [`reports/pytest_report.html`](reports/pytest_report.html) | Self-contained, interactive HTML test execution report covering 345 Python tests with pass/fail metrics and execution timings. |
| **🎭 Playwright E2E Browser Report** | [`reports/playwright_report.html`](reports/playwright_report.html) | Automated Chromium browser test execution report with failure screenshot capture. |
| **⚡ REST API Test Report** | [`reports/api_report.html`](reports/api_report.html) | HTTP status codes, CRUD operations, and SLA verification results using Python Requests. |
| **📋 Test Cases Specification** | [`TEST_CASES.md`](TEST_CASES.md) | Exhaustive test case documentation with preconditions, test data, steps, expected/actual results, and status. |
| **🐞 Defect Tracking Report** | [`DEFECT_REPORT.md`](DEFECT_REPORT.md) | Root-cause analysis, severity ratings, reproduction steps, code patches, and verification logs for all defects. |
| **⚡ Performance Report** | [`PERFORMANCE_REPORT.md`](PERFORMANCE_REPORT.md) | Latency distributions ($p_{50}, p_{95}$), concurrency profiling, operation throughput, and scope disclaimers. |
| **📄 Final QA Report (Markdown)** | [`QA_REPORT.md`](QA_REPORT.md) | Formatted Markdown QA report for repository auditing and academic grading. |
| **🚀 Deployment Guide** | [`DEPLOYMENT.md`](DEPLOYMENT.md) | Step-by-step deployment guide for GitHub Pages, Netlify, and local static servers. |

---

## 🏛️ Testing Framework Architecture

The system decouples the client-side presentation, domain engine, and comprehensive Python QA automation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│   index.html (Semantic HTML5)  │  styles.css (CSS3 Variables & Animations)  │
│   app.js (DOM Controllers, Event Delegation, Cart Drawer & Modal Views)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ calls
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    UNIVERSAL BUSINESS DOMAIN ENGINE                         │
│                    ecommerce-core.js  │  defect-engine.js                   │
│   - Financial Calculations (Subtotal, 5% Tax, Free Shipping Threshold)      │
│   - Financial Quantization & Rounding (Number.EPSILON Decimal Safety)       │
│   - Inventory Bounds, Stock Tracking & Real-Time Stock Availability         │
│   - Strict Regular Expression Validation (Name, Email, Phone, Card, CVV)   │
│   - Order Processing, Invoice Generation & LocalStorage Serialization       │
│   - Controlled Defect Injection (BUG-001..006) & Dynamic Regression Runner  │
└──────────────────────┬───────────────────────────────┬──────────────────────┘
                       │ shared by                     │ verified by
┌──────────────────────▼───────────────┐ ┌─────────────▼──────────────────────┐
│       IN-BROWSER MANUAL QA STUDIO    │ │  🐍 PYTHON / PYTEST AUTOMATION     │
│   - test-dashboard.html & test-runner│ │   - python_tests/ (378 Tests)      │
│   - Interactive Scenario Playground  │ │   - run_tests.py (Master CLI)      │
│   - defect-dashboard.html & js       │ │   - pytest.ini (Category Markers)  │
└──────────────────────────────────────┘ └────────────────────────────────────┘
```

---

## 📊 Python Testing Suite Breakdown (378 Test Cases)

| Category | Folder / File | Tests | Pass % | Scope & Coverage |
| :--- | :--- | :---: | :---: | :--- |
| **1. Unit Testing** | [`test_unit.py`](python_tests/test_unit.py) | 46 | 100% | Price formatting, line total multiplication, floating-point precision, quantity bounds, subtotal, 5% sales tax, tiered shipping, stock remaining. |
| **2. Integration Testing** | [`test_integration.py`](python_tests/test_integration.py) | 12 | 100% | Product selection, cart state modifications, quantity updates, order generation, inventory decrement synchronization, and storage serialization. |
| **3. Functional Testing** | [`test_functional.py`](python_tests/test_functional.py) | 20 | 100% | Multi-keyword search, category tab filtering, price/stock sorting, cart drawer addition/removal, and full End-to-End order placement. |
| **4. Black-Box Testing** | [`test_blackbox.py`](python_tests/test_blackbox.py) | 14 | 100% | Specification and contract verification: empty checkout guard, invalid customer fields, zero quantity removal, out-of-stock rejection, and payment validation. |
| **5. Boundary Value Testing** | [`test_boundary.py`](python_tests/test_boundary.py) | 38 | 100% | Min/max quantities, boundary inventory limits, exact $50 shipping threshold ($49.99 vs $50.00), customer field lengths (name, zip, phone, card, CVV). |
| **6. Negative Testing** | [`test_negative.py`](python_tests/test_negative.py) | 28 | 100% | Rejection of negative quantities, zero quantities, fractional values, malformed emails, non-digit cards, expired dates, and invalid payment methods. |
| **7. Validation Testing** | [`test_validation.py`](python_tests/test_validation.py) | 18 | 100% | Product catalog schema constraints, ID uniqueness, field regex patterns (Name, Email, Phone, Zip, Card, Expiry, CVV, UPI ID), and structured errors. |
| **8. Defect Lifecycle & RTM** | [`test_defects.py`](python_tests/test_defects.py) | 7 | 100% | Controlled bug simulation (BUG-001..006), failure detail recording, patch verification, rerun test candidate selection, and RTM traceability. |
| **9. Security Testing** | [`security_tests/`](python_tests/security_tests/) | 114 | 100% | Whitespace trimming, control characters (`\x00`, CRLF), 11 XSS payload vectors, SQL injection string immunity, CVV/PAN data exposure protection. |
| **10. Performance Benchmarks** | [`performance_tests/`](python_tests/performance_tests/) | 13 | 100% | Document retrieval and parsing times, calculation throughput (65,000 ops/s), 10-thread concurrency profiling, and latency percentiles ($p_{50}, p_{95}$). |
| **11. REST API Demonstration** | [`api_tests/`](python_tests/api_tests/) | 26 | 100% | GET, POST, PUT, DELETE operations against embedded REST server, HTTP status codes (200, 201, 400, 404), schema validation, and latency SLA. |
| **12. Browser E2E Automation** | [`playwright_tests/`](python_tests/playwright_tests/) | 33 | 100% | Automated Chromium browser scenarios: Homepage loading, navigation routing, cart drawer, modal checkout, form validation, and responsive layouts. |
| **TOTAL AUTOMATED SUITE** | `python_tests/` | **378** | **100%** | **Complete Software Testing and Quality Assurance Suite** |

---

## 🛠️ Installation & Environment Setup

### Prerequisites
- **Python 3.10 or higher** (Python 3.10, 3.11, 3.12, 3.13, 3.14 verified)
- Modern web browser (Chrome, Edge, Firefox, or Safari)

### 1. Set Up Python Virtual Environment
```powershell
# Clone repository
git clone https://github.com/surajms1415/STQA-project.git
cd STQA-project

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\.venv\Scripts\activate.bat
# On Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```powershell
# Upgrade pip and install testing dependencies
pip install -r requirements.txt

# Install Playwright browser binaries (for E2E browser tests)
playwright install chromium
```

---

## ⚡ CLI Test Execution & Simple Commands

The project includes a unified CLI runner [`run_tests.py`](run_tests.py) providing simple, intuitive flags to run any test category or the entire suite:

### Category Execution Commands

| Category | Simple CLI Command | Direct Pytest Command |
| :--- | :--- | :--- |
| **Run All Tests** | `python run_tests.py --all` | `pytest python_tests/ -v` |
| **Unit Testing** | `python run_tests.py --unit` | `pytest python_tests/test_unit.py -v` |
| **Integration Testing** | `python run_tests.py --integration` | `pytest python_tests/test_integration.py -v` |
| **Functional Testing** | `python run_tests.py --functional` | `pytest python_tests/test_functional.py -v` |
| **Black-Box Testing** | `python run_tests.py --blackbox` | `pytest python_tests/test_blackbox.py -v` |
| **Regression Testing** | `python run_tests.py --regression` | `pytest python_tests/test_regression.py -v` |
| **Boundary Value Testing** | `python run_tests.py --boundary` | `pytest python_tests/test_boundary.py -v` |
| **Negative Testing** | `python run_tests.py --negative` | `pytest python_tests/test_negative.py -v` |
| **Validation Testing** | `python run_tests.py --validation` | `pytest python_tests/test_validation.py -v` |
| **Defect Lifecycle** | `python run_tests.py --defects` | `pytest python_tests/test_defects.py -v` |
| **Security Testing** | `python run_tests.py --security` | `pytest python_tests/security_tests/ -v` |
| **Performance Benchmarks**| `python run_tests.py --performance` | `pytest python_tests/performance_tests/ -v` |
| **REST API Demonstration** | `python run_tests.py --api` | `pytest python_tests/api_tests/ -v` |
| **Browser Automation (E2E)**| `python run_tests.py --browser` | `pytest python_tests/playwright_tests/ -v` |
| **Generate HTML Report** | `python run_tests.py --report` | `pytest python_tests/ --html=reports/pytest_report.html --self-contained-html` |

---

## 🔒 Security Testing Suite

Located in [`python_tests/security_tests/`](python_tests/security_tests/), this suite implements 114 automated security and data sanitization checks:

- **Input Sanitization** ([`test_input_sanitization.py`](python_tests/security_tests/test_input_sanitization.py)):
  - Whitespace trimming on text fields.
  - Rejection of control characters (`\x00` null byte, CRLF `\r\n`, ANSI escape codes, backspaces).
  - Buffer overflow and DoS length resiliency (testing 10,000 to 50,000 character inputs).
  - Zero-width non-printing characters (`\u200b`, `\ufeff`, non-breaking spaces).
  - Type confusion attacks (booleans, lists, dictionaries passed to string or number fields).
  - Mathematical extremes (`NaN`, `Infinity`, `-Infinity`, overflow numbers).
- **XSS Prevention** ([`test_xss_prevention.py`](python_tests/security_tests/test_xss_prevention.py)):
  - Tested against 11 standard XSS vectors (`<script>`, uppercase script, `img onerror`, `svg onload`, `javascript:` URI, attribute breakouts, `iframe`, `body onload`, autofocus).
  - Verifies rejection by form validators, literal string treatment in search filters, and HTML entity encoding (`&lt;script&gt;`).
- **SQL Injection Patterns** ([`test_sqli_patterns.py`](python_tests/security_tests/test_sqli_patterns.py)):
  - Tested SQL injection patterns: `' OR '1'='1`, comments (`--`, `#`), union queries, and destructive statements (`'; DROP TABLE; --`).
  - Verifies that injection syntax is treated strictly as literal strings and rejected by typed format validators.
- **Sensitive Data Privacy** ([`test_sensitive_data_exposure.py`](python_tests/security_tests/test_sensitive_data_exposure.py)):
  - Verified that credit card CVV is **never** serialized, stored, or returned in confirmed order records.
  - Full 16-digit card numbers (PAN) are unexposed/masked.
  - System errors do not leak filesystem paths, stack traces, or environment secrets.

---

## ⚡ Performance & Concurrency Benchmarking Suite

Located in [`python_tests/performance_tests/`](python_tests/performance_tests/), this suite evaluates execution timing, throughput, and latency distributions:

- **Page-Load Latency** ([`test_page_load_performance.py`](python_tests/performance_tests/test_page_load_performance.py)):
  - Measures document retrieval & parse latency for `index.html`, `test-dashboard.html`, `defect-dashboard.html`, and `qa-report.html`.
  - All pages load in **1.10 ms to 2.20 ms** (far exceeding the 2,000 ms SLA).
- **Core Operation Throughput** ([`test_operation_benchmarks.py`](python_tests/performance_tests/test_operation_benchmarks.py)):
  - Currency Arithmetic: **~65,000 ops/second** (0.015 ms per op).
  - Cart Calculations (10 items): **~25,000 ops/second** (0.040 ms per op).
  - Catalog Search & Filter: **~15,000 ops/second** (0.067 ms per op).
  - Full Order Checkout: **~3,500 ops/second** (0.285 ms per op).
  - Defect Regression Suite: **~2.8 ms** for all 32 test cases.
- **Concurrency & Latency Profiling** ([`test_concurrency_and_latency.py`](python_tests/performance_tests/test_concurrency_and_latency.py)):
  - Evaluated using `ThreadPoolExecutor` simulating concurrent HTTP clients accessing the demonstration REST API.
  - Workload: 50 concurrent GET requests and 20 concurrent POST orders at 10 worker threads.
  - **100% Success Rate** (No dropped connections, 0 unhandled 500 errors).
  - Median ($p_{50}$) latency: **8.50 ms**; 95th percentile ($p_{95}$): **18.20 ms**; Maximum: **24.10 ms**.
  - Structured telemetry exported to [`reports/performance_summary.json`](reports/performance_summary.json).

> [!NOTE]
> Detailed findings and scope disclaimers are documented in [`PERFORMANCE_REPORT.md`](PERFORMANCE_REPORT.md).

---

## 🐛 Defect Management & QA Module (6 Common Bugs)

The Defect Management module provides a demonstrable Software Testing and Quality Assurance lifecycle workflow:

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ BUG DETECTED │ ───► │ STATUS: OPEN │ ───► │ CODE PATCHED │ ───► │   VERIFIED   │
│ (Unpatched)  │      │ (Test Fails) │      │  (Core Fix)  │      │ (Status: OK) │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

### 1. Defect Catalog & Root Cause Analyses

| Bug ID | Title | Severity | Priority | Component | Primary Test | Documented Root Cause |
| :--- | :--- | :---: | :---: | :--- | :---: | :--- |
| **`BUG-001`** | Floating-Point Currency Rounding Leakage | **High** | **P2 - High** | Price Calculation | `UT-PRICE-03` | IEEE-754 double-precision arithmetic produces float leakage on operations like `19.99 * 7 = 139.92999999999998`. Fixed with quantized `roundMoney()` using `Number.EPSILON`. |
| **`BUG-002`** | Fractional / Decimal Quantities Accepted | **Critical** | **P1 - Critical** | Cart & Inventory | `UT-QTY-02` | Loose validation only verified `qty > 0` without checking for whole integers. Fixed using strict `Number.isInteger()` guard. |
| **`BUG-003`** | Cart Quantity Exceeds Physical Stock | **High** | **P1 - Critical** | Stock Enforcement | `UT-STOCK-03` | Validation checked newly added delta against stock without accounting for existing items already in cart. Fixed with cumulative bounds check `(currentQty + qty) <= stock`. |
| **`BUG-004`** | Empty Cart Checkout Ghost Order | **Critical** | **P1 - Critical** | Checkout Controller | `BB-CHK-01` | Missing empty array guard clause at order entry point, generating $0 invoices. Fixed with non-empty cart guard check. |
| **`BUG-005`** | Whitespace Name & Alphanumeric Phone | **Medium** | **P3 - Medium** | Customer Form | `BB-CUST-01` | Simple length check without trimming or regex character pattern validation. Fixed with trim and strict letter/digit regex. |
| **`BUG-006`** | Expired Credit Card & 1-Digit CVV | **High** | **P2 - High** | Payment Module | `BB-INP-01` | Format-only MM/YY check without temporal calendar comparison, and missing CVV length restriction. Fixed with calendar comparison and `^\d{3,4}$` CVV check. |

---

## 📋 Requirements Traceability Matrix (RTM)

| Requirement ID | Requirement Scope | Category | Associated Test Cases | Mapped Defect(s) | Status |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **`REQ-01`** | Product Catalog & Stock Status | Catalog & Inventory | `UT-STOCK-01`, `UT-STOCK-02`, `UT-STOCK-03`, `IT-STORE-02`, `BV-STOCK-01`, `NEG-STOCK-01` | `BUG-003` | **Covered** |
| **`REQ-02`** | Product Search & Category Filtering | Discovery | `FT-SRCH-01`, `FT-SRCH-02`, `FT-CAT-01`, `BV-SRCH-01` | None | **Covered** |
| **`REQ-03`** | Cart Quantity Limits & Validation | Cart & Validation | `UT-QTY-01`, `UT-QTY-02`, `UT-QTY-03`, `UT-QTY-04`, `BB-QTY-01`, `BB-QTY-02`, `BV-QTY-01`, `VAL-QTY-01` | `BUG-002`, `BUG-003` | **Covered** |
| **`REQ-04`** | Shopping Cart Manipulation | Cart State | `IT-CART-01`, `IT-QTY-01`, `FT-CART-01`, `FT-CART-02`, `IT-STORE-01` | None | **Covered** |
| **`REQ-05`** | Inventory Synchronization | Inventory Management | `IT-STORE-02`, `FT-E2E-01` | None | **Covered** |
| **`REQ-06`** | Financial Calculations & Precision | Pricing & Taxes | `UT-PRICE-01`, `UT-PRICE-02`, `UT-PRICE-03`, `UT-CART-01`, `UT-CART-02`, `UT-CART-03`, `UT-CART-04`, `UT-CART-05`, `BV-PRICE-01`, `REG-PRICE-01` | `BUG-001` | **Covered** |
| **`REQ-07`** | Checkout & Empty Cart Guard | Checkout | `BB-CHK-01`, `IT-ORDER-01`, `FT-E2E-01`, `NEG-ORD-01` | `BUG-004` | **Covered** |
| **`REQ-08`** | Order Processing & Receipt Generation | Orders | `IT-ORDER-01`, `FT-E2E-01`, `VAL-ORD-01` | `BUG-004` | **Covered** |
| **`REQ-09`** | Input Validation & Payment Security | Validation & Security | `BB-CUST-01`, `BB-INP-01`, `BB-INP-02`, `UT-VAL-01`, `UT-VAL-02`, `UT-VAL-03`, `VAL-CUST-01`, `VAL-PAY-01`, `NEG-PAY-01` | `BUG-005`, `BUG-006` | **Covered** |
| **`REQ-10`** | UI Responsiveness & Defect Visibility | UI / QA Dashboard | `PW-RESP-01`, `PW-NAV-01`, `PW-DEF-01` | None | **Covered** |

---

## 🎭 Playwright E2E Browser Automation

Located in [`python_tests/playwright_tests/`](python_tests/playwright_tests/), this suite automates Chromium browser interactions against the live storefront:

```powershell
# Run Playwright E2E tests
pytest python_tests/playwright_tests/ -v

# Generate self-contained Playwright HTML report
pytest python_tests/playwright_tests/ --html=reports/playwright_report.html --self-contained-html
```

- **33 Test Cases** covering homepage navigation, search filtering, cart drawer slide-overs, quantity adjustments, modal checkout validations, order confirmation receipts, and cross-device responsive viewports (Desktop 1280x800, Tablet 768x1024, Mobile 375x667).
- Automatic failure screenshot capture integrated in `conftest.py`.

---

## 🌐 REST API Testing Demonstration

Located in [`python_tests/api_tests/`](python_tests/api_tests/), demonstrating industrial API testing using **Python Requests** and **Pytest**:

```powershell
# Run REST API test suite
pytest python_tests/api_tests/ -v

# Generate self-contained API HTML report
pytest python_tests/api_tests/ --html=reports/api_report.html --self-contained-html
```

- **26 Test Cases** validating HTTP status codes (200, 201, 400, 404), CRUD verbs (GET, POST, PUT, DELETE), JSON schema structures, missing/invalid input handling, and latency thresholds.
- Configurable endpoint via `--api-base-url` or `AURAMART_API_BASE_URL` (defaults to embedded demonstration server).

---

## 📑 Detailed HTML Test Reports

The project automatically generates rich, self-contained HTML reports:

| Report | File Path | Scope |
| :--- | :--- | :--- |
| **Pytest Full Suite HTML Report** | [`reports/pytest_report.html`](reports/pytest_report.html) | Complete interactive test run log covering all 345 Python tests with pass/fail breakdown and execution times. |
| **Playwright Browser Report** | [`reports/playwright_report.html`](reports/playwright_report.html) | E2E browser scenario results with automated screenshot attachments. |
| **REST API Demonstration Report** | [`reports/api_report.html`](reports/api_report.html) | Endpoint responses, status code verifications, and latency benchmarks. |
| **Defect QA Telemetry** | [`reports/defect_qa_summary.json`](reports/defect_qa_summary.json) | Machine-readable defect states, failure records, impacted test rerun selectors, and RTM matrix. |
| **Performance Telemetry** | [`reports/performance_summary.json`](reports/performance_summary.json) | Latency percentiles ($p_{50}, p_{95}$), concurrency profiling, and operation throughput. |

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
├── ecommerce-core.js       # Core business logic, validators & calculation algorithms (UMD)
│
├── run_tests.py            # 🚀 Unified Master CLI Test Runner (--all, --unit, --browser, etc.)
├── generate_qa_summary.py  # Automated Defect Tracking & RTM Telemetry Exporter
├── pytest.ini              # Pytest configuration & category marker definitions
├── requirements.txt        # Python dependencies (pytest, pytest-html, playwright, requests)
│
├── python_tests/           # 🐍 Comprehensive Python / Pytest Automated Test Suite (378 Tests)
│   ├── __init__.py         # Package marker
│   ├── stqa_core.py        # Python business logic & defect simulation engine
│   ├── conftest.py         # Shared Pytest fixtures, mock storage & verification helpers
│   ├── test_unit.py        # 1. Unit Testing (Pricing, Calculations, Quantity, Stock)
│   ├── test_integration.py # 2. Integration Testing (Cart workflow, Orders, Storage sync)
│   ├── test_functional.py  # 3. Functional Testing (Search, Categories, Sort, E2E)
│   ├── test_blackbox.py    # 4. Black-Box Testing (Contract & specification validation)
│   ├── test_regression.py  # 5. Regression Testing (BUG-001..06 fix stability, idempotency)
│   ├── test_boundary.py    # 6. Boundary Value Testing (Min, Max, Limits, Length thresholds)
│   ├── test_negative.py    # 7. Negative Testing (Malformed data, Missing fields, XSS payloads)
│   ├── test_validation.py  # 8. Validation Testing (Schema constraints, Field regex, Payment)
│   ├── test_defects.py     # 8. Defect Lifecycle & RTM verification (BUG-001..006)
│   │
│   ├── security_tests/     # 🔒 Security Testing Suite (114 Tests)
│   │   ├── __init__.py     # Package marker
│   │   ├── test_input_sanitization.py        # Whitespace, control chars, buffer bounds, types
│   │   ├── test_xss_prevention.py            # 11 XSS payload vectors, entity encoding
│   │   ├── test_sqli_patterns.py             # SQL injection strings, tautologies, auth bypass
│   │   └── test_sensitive_data_exposure.py   # CVV/PAN protection, error leakage guards
│   │
│   ├── performance_tests/  # ⚡ Performance & Concurrency Suite (13 Tests)
│   │   ├── __init__.py     # Package marker
│   │   ├── test_page_load_performance.py     # Document retrieval and parse times
│   │   ├── test_operation_benchmarks.py      # Calculations throughput (65k ops/s)
│   │   └── test_concurrency_and_latency.py   # 10-thread concurrency, p50/p95 latency
│   │
│   ├── api_tests/          # 🌐 REST API Demonstration Suite (26 Tests)
│   │   ├── __init__.py     # Package marker
│   │   ├── demo_api_server.py                # Lightweight embedded REST server (GET, POST, PUT, DELETE)
│   │   ├── conftest.py                       # Configurable endpoint fixture (--api-base-url) & client
│   │   ├── test_api_get_operations.py        # GET listing, filtering, schema & 404 validation
│   │   ├── test_api_post_operations.py       # POST product & order creation, 400 validation
│   │   ├── test_api_put_operations.py        # PUT resource update, 404 & 400 validation
│   │   ├── test_api_delete_operations.py     # DELETE resource removal & 404 verification
│   │   └── test_api_error_handling_and_performance.py # Malformed JSON (400), SLAs & headers
│   │
│   └── playwright_tests/   # 🎭 Playwright Python End-to-End Browser Automation Suite (33 Tests)
│       ├── __init__.py     # Package marker
│       ├── conftest.py     # Playwright fixtures (browser, page, failure screenshot hook)
│       ├── test_homepage_navigation.py       # Homepage loading, brand, navbar routing
│       ├── test_product_catalog.py           # 10-item grid, stock tags, search & filters
│       ├── test_cart_operations.py           # Drawer slide-over, qty +/- & pricing
│       ├── test_checkout_and_validation.py   # Modal checkout, inline errors, receipt
│       └── test_responsive_ui.py             # Desktop, Tablet, and Mobile viewports
│
├── reports/                # 📊 Test Execution Reports & Machine-Readable Telemetry
│   ├── pytest_report.html  # Pytest Master HTML Test Report (345 Tests)
│   ├── playwright_report.html # Playwright Browser Automation Report (33 Tests)
│   ├── api_report.html     # REST API Test Report (26 Tests)
│   ├── defect_qa_summary.json # Defect Lifecycle & RTM Telemetry JSON
│   └── performance_summary.json # Performance, Concurrency & Latency Telemetry JSON
│
├── netlify.toml            # Netlify deployment configuration
├── _redirects              # Netlify SPA/clean routing rules
├── .nojekyll               # GitHub Pages static asset bypass
│
├── TEST_CASES.md           # Formal Test Case specifications & Traceability Matrix
├── DEFECT_REPORT.md        # Comprehensive Defect Tracking & Root-Cause Analysis
├── PERFORMANCE_REPORT.md   # Security & Performance Benchmarking Report
├── QA_REPORT.md            # Executive Quality Assurance Markdown Report
├── DEPLOYMENT.md           # Netlify & GitHub Pages Deployment Guide
└── README.md               # Complete project documentation & function reference
```

---

## 📜 License & Academic Integrity

This project is developed for the **Software Testing and Quality Assurance (STQA)** academic and engineering curriculum. Licensed under the [MIT License](LICENSE).
