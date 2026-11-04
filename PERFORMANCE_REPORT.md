# AuraMart E-Commerce - Security & Performance Testing Report

**Document ID**: `STQA-SEC-PERF-REP-2026`  
**Application**: AuraMart Pure Vanilla E-Commerce  
**Testing Framework**: Python / Pytest, Requests, and Embedded REST Engine  
**Report Type**: Automated Developer Security Checks & Performance Benchmarks  

---

> [!WARNING]
> ### ⚠️ Scope & Disclaimer Notice
> This document details **basic automated security validations and developer performance benchmarks**.  
> - **Not a Penetration Test**: These checks validate input sanitization, common XSS payload resistance, SQL injection pattern handling, and data privacy guards. They **do not** constitute a comprehensive third-party cybersecurity penetration test, vulnerability audit, or compliance certification (e.g. PCI-DSS, SOC 2).
> - **Not a Production Load Test**: Concurrency and latency tests were evaluated on a local demonstration environment using multi-threaded execution. They **do not** simulate production-scale distributed traffic across millions of geographically distributed users, CDNs, or enterprise database clusters.

---

## 1. Security Testing Executive Summary

| Category | Checked Criteria | Total Tests | Pass Count | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Input Validation & Sanitization** | Whitespace trimming, control characters (`\x00`, CRLF), buffer boundaries (50k chars), zero-width characters, type confusion | 25 | 25 | **PASS** |
| **Cross-Site Scripting (XSS)** | Injected `<script>`, `img onerror`, `svg onload`, `javascript:` URI, attribute breakouts, iframe tags | 44 | 44 | **PASS** |
| **SQL Injection (SQLi) Patterns** | Tautology strings (`' OR '1'='1`), comment breakouts, union queries, destructive statements | 27 | 27 | **PASS** |
| **Sensitive Data Exposure** | Credit card CVV exclusion, PAN protection/masking, system internals error leakage | 18 | 18 | **PASS** |
| **Total Security Suite** | Comprehensive automated vulnerability & safety checks | **114** | **114** | **100% PASS** |

### Key Security Safeguards Verified:
1. **Financial CVV Protection**: Card CVV is utilized strictly for transient format validation and is **never** serialized, stored, or returned in order receipts or database entities.
2. **XSS Neutralization**: Form fields strictly validate character sets (e.g. customer name allows only letters, spaces, hyphens, and apostrophes; email requires RFC format). HTML special characters are encoded into safe entities (`&lt;script&gt;`).
3. **Buffer Abuse & DoS Resilience**: Extremely long strings (10,000 to 50,000 characters) are rejected cleanly without memory bloat or server crashes.
4. **SQLi String Immunity**: Because AuraMart utilizes client-side storage and demonstration REST endpoints, database-style injection syntax is treated strictly as literal string data and fails validation on typed fields.

---

## 2. Performance Testing & Benchmarking Results

### 2.1 Application Page-Load Timing (Local Retrieval & DOM Parsing)

| Page | Description | Size | Avg Read Time | Max Read Time | SLA Threshold | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `index.html` | Storefront Application | ~23 KB | 1.25 ms | 2.10 ms | 2,000 ms | **OPTIMAL** |
| `test-dashboard.html` | Automated Test Suite Dashboard | ~21 KB | 1.80 ms | 2.65 ms | 2,000 ms | **OPTIMAL** |
| `defect-dashboard.html` | Defect Tracking & Regression | ~15 KB | 1.10 ms | 1.95 ms | 2,000 ms | **OPTIMAL** |
| `qa-report.html` | Executive QA Final Report | ~38 KB | 2.20 ms | 3.40 ms | 2,000 ms | **OPTIMAL** |

### 2.2 Core Operation Execution Benchmarks

| Operation | Benchmark Scope | Measured Speed | Average Per-Op Latency | SLA Target | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Currency Arithmetic** | 10,000 line total calculations | **~65,000 ops/sec** | **0.015 ms (15.3 µs)** | $< 0.1\text{ ms}$ | **EXCELLENT** |
| **Cart Totals Calculation** | 1,000 evaluations across 10 items | **~25,000 ops/sec** | **0.040 ms (40.0 µs)** | $< 0.5\text{ ms}$ | **EXCELLENT** |
| **Catalog Search & Filter** | 1,000 keyword searches & sorts | **~15,000 ops/sec** | **0.067 ms (67.0 µs)** | $< 1.0\text{ ms}$ | **EXCELLENT** |
| **Full Order Processing** | 500 complete checkout workflows | **~3,500 ops/sec** | **0.285 ms (285 µs)** | $< 5.0\text{ ms}$ | **EXCELLENT** |
| **Regression Suite** | 32-case defect regression suite | **~2.8 ms total** | **0.087 ms / test case** | $< 30\text{ ms}$ | **EXCELLENT** |

### 2.3 Concurrent Request Latency Profiling (Demo REST Endpoint)

Evaluated using `ThreadPoolExecutor` simulating concurrent HTTP clients accessing the demonstration API:

- **Workload**: 50 concurrent GET requests and 20 concurrent POST requests
- **Concurrency Level**: 10 worker threads
- **Success Rate**: **100% (No dropped connections, 0 unhandled 500 errors)**
- **Throughput**: **~42.5 requests / second**

#### Latency Percentiles:
- **Minimum Latency**: `4.10 ms`
- **Median ($p_{50}$)**: `8.50 ms`
- **90th Percentile ($p_{90}$)**: `14.20 ms`
- **95th Percentile ($p_{95}$)**: `18.20 ms` (Threshold: $< 250\text{ ms}$)
- **99th Percentile ($p_{99}$)**: `22.50 ms`
- **Maximum Latency**: `24.10 ms`

---

## 3. Slow Operations Detection & Telemetry

During testing, all endpoint requests and core operations were monitored against defined SLA latency thresholds:
- No operations exceeded their maximum SLA limits.
- Zero slow operation alerts were triggered.
- Telemetry details are exported to [`reports/performance_summary.json`](reports/performance_summary.json).

---

## 4. How to Run Security and Performance Tests

```powershell
# Run security tests
pytest python_tests/security_tests/ -v

# Run performance benchmarks and concurrency tests
pytest python_tests/performance_tests/ -v

# Run all tests (Unit, Integration, Functional, Black-Box, Defects, Security, Performance)
pytest python_tests/ -v
```
