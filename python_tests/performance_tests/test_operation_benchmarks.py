"""
Performance Testing - Core Domain Operation Execution Benchmarks.
Measures execution speed, throughput (operations/second), and algorithmic efficiency
for arithmetic, cart calculation, catalog search, order processing, and regression testing.
"""

import time
import pytest
from python_tests import stqa_core as Core


@pytest.mark.performance
class TestOperationBenchmarks:
    """Benchmark tests evaluating execution time for critical domain operations."""

    def test_perf_op_01_currency_calculation_throughput(self):
        """1. Benchmark Currency Rounding & Line Total Calculation (10,000 iterations)."""
        iterations = 10000
        start_t = time.perf_counter()

        for i in range(iterations):
            price = 19.99 + (i % 50)
            qty = (i % 10) + 1
            Core.calculate_line_total(price, qty)

        elapsed_sec = time.perf_counter() - start_t
        elapsed_ms = elapsed_sec * 1000.0
        ops_per_sec = iterations / elapsed_sec if elapsed_sec > 0 else float("inf")
        avg_ms_per_op = elapsed_ms / iterations

        print(f"\n  [BENCHMARK: Line Total] {iterations} ops in {elapsed_ms:.2f} ms")
        print(f"     Throughput: {ops_per_sec:,.0f} ops/sec")
        print(f"     Per-Op:     {avg_ms_per_op * 1000:.2f} microseconds")

        # Threshold: 10,000 iterations must complete in under 200ms
        assert elapsed_ms < 200.0, f"Calculation benchmark exceeded 200ms (took {elapsed_ms:.2f}ms)"
        assert ops_per_sec > 40000, f"Expected > 40,000 ops/sec, achieved {ops_per_sec:.0f}"

    def test_perf_op_02_cart_totals_calculation_latency(self):
        """2. Benchmark Cart Totals Calculation across Varied Items (1,000 iterations)."""
        cart = [{"id": f"p{i}", "quantity": (i % 3) + 1} for i in range(1, 10)]
        products = Core.INITIAL_PRODUCTS

        iterations = 1000
        start_t = time.perf_counter()

        for _ in range(iterations):
            Core.calculate_cart_totals(cart, products)

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        avg_ms = elapsed_ms / iterations

        print(f"\n  [BENCHMARK: Cart Totals] {iterations} ops in {elapsed_ms:.2f} ms")
        print(f"     Per-Op: {avg_ms:.4f} ms")

        # Threshold: 1,000 cart calculations under 100ms
        assert elapsed_ms < 100.0, f"Cart totals calculation exceeded 100ms (took {elapsed_ms:.2f}ms)"

    def test_perf_op_03_catalog_filtering_and_search_latency(self):
        """3. Benchmark Product Search & Category Filtering (1,000 iterations)."""
        search_terms = ["Headphones", "Keyboard", "Watch", "Mouse", "Desk", "Backpack", "Earbuds", "Nonexistent"]
        categories = ["all", "Audio", "Electronics", "Wearables", "Home", "Accessories"]

        iterations = 1000
        start_t = time.perf_counter()

        for i in range(iterations):
            search = search_terms[i % len(search_terms)]
            cat = categories[i % len(categories)]
            Core.filter_and_sort_products(Core.INITIAL_PRODUCTS, {"search": search, "category": cat, "sortBy": "price-asc"})

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        avg_ms = elapsed_ms / iterations

        print(f"\n  [BENCHMARK: Catalog Search] {iterations} ops in {elapsed_ms:.2f} ms")
        print(f"     Per-Op: {avg_ms:.4f} ms")

        # Threshold: 1,000 filter/sort iterations under 150ms
        assert elapsed_ms < 150.0, f"Search/filter benchmark exceeded 150ms (took {elapsed_ms:.2f}ms)"

    def test_perf_op_04_full_checkout_order_processing_latency(self, valid_customer):
        """4. Benchmark Full Order Processing & Inventory Decrement (500 iterations)."""
        iterations = 500
        cart = [{"id": "p1", "quantity": 1}]
        payment = {"method": "cod"}

        start_t = time.perf_counter()

        for _ in range(iterations):
            Core.process_order(cart, Core.INITIAL_PRODUCTS, valid_customer, payment)

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        avg_ms = elapsed_ms / iterations

        print(f"\n  [BENCHMARK: Order Processing] {iterations} ops in {elapsed_ms:.2f} ms")
        print(f"     Per-Op: {avg_ms:.4f} ms")

        # Threshold: 500 complete order validations under 250ms
        assert elapsed_ms < 250.0, f"Order processing benchmark exceeded 250ms (took {elapsed_ms:.2f}ms)"

    def test_perf_op_05_defect_regression_suite_execution_speed(self, defect_manager):
        """5. Benchmark 32-Case Regression Suite Execution Time (< 30ms)."""
        test_specs = [
            {"id": f"REG-{i:02d}", "suite": "Regression", "description": f"Test {i}", "expected": "$99.99", "fn": lambda: {"actual": "$99.99", "pass": True}}
            for i in range(1, 33)
        ]

        start_t = time.perf_counter()
        result = defect_manager.run_regression_suite(test_specs)
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        print(f"\n  [BENCHMARK: Regression Suite] 32 test cases evaluated in {elapsed_ms:.2f} ms")
        assert result["total"] == 32
        assert result["failed"] == 0
        assert elapsed_ms < 30.0, f"Regression suite exceeded 30ms threshold (took {elapsed_ms:.2f}ms)"
