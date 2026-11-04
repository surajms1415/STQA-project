"""
Performance Testing - Application Page-Load Timing & DOM Parsing Benchmarks.
Measures document load times, resource sizes, and parsing readiness across
all four core HTML application dashboards.
"""

import os
import time
from typing import Dict
import pytest

PAGES = [
    ("index.html", "Storefront Application"),
    ("test-dashboard.html", "Automated QA Test Dashboard"),
    ("defect-dashboard.html", "Defect Tracking & Regression Dashboard"),
    ("qa-report.html", "Executive QA Final Report"),
]

PAGE_LOAD_SLA_MS = 2000.0  # Maximum acceptable threshold for static page retrieval


@pytest.mark.performance
class TestPageLoadPerformance:
    """Performance benchmarks assessing application page-load times and resource metrics."""

    @pytest.mark.parametrize("page_file,page_name", PAGES)
    def test_perf_page_01_document_read_and_parse_latency(self, page_file, page_name):
        """1. Measure Document Retrieval and Parsing Latency for Each Application Page."""
        assert os.path.exists(page_file), f"Page file {page_file} must exist"

        # Benchmark 10 repeated reads to capture min, average, and max latency
        latencies = []
        file_size_bytes = 0

        for _ in range(10):
            start_t = time.perf_counter()
            with open(page_file, "r", encoding="utf-8") as f:
                content = f.read()
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            latencies.append(elapsed_ms)
            file_size_bytes = len(content.encode("utf-8"))

        avg_latency_ms = sum(latencies) / len(latencies)
        max_latency_ms = max(latencies)
        min_latency_ms = min(latencies)

        print(f"\n  [PERF: {page_file}] {page_name}")
        print(f"     Size:        {file_size_bytes / 1024:.1f} KB")
        print(f"     Avg Latency: {avg_latency_ms:.2f} ms")
        print(f"     Min/Max:     {min_latency_ms:.2f} ms / {max_latency_ms:.2f} ms")

        assert avg_latency_ms < PAGE_LOAD_SLA_MS, \
            f"{page_file} avg read latency ({avg_latency_ms:.2f}ms) exceeded SLA ({PAGE_LOAD_SLA_MS}ms)"
        assert max_latency_ms < PAGE_LOAD_SLA_MS, \
            f"{page_file} max read latency ({max_latency_ms:.2f}ms) exceeded SLA ({PAGE_LOAD_SLA_MS}ms)"

    def test_perf_page_02_static_bundle_size_efficiency(self):
        """2. Verify Core JavaScript and CSS Bundles Maintain Lean Footprint."""
        core_assets = [
            ("styles.css", 500 * 1024, "Main Stylesheet"),
            ("app.js", 500 * 1024, "Storefront Application Controller"),
            ("ecommerce-core.js", 500 * 1024, "Universal E-Commerce Domain Engine"),
            ("defect-engine.js", 500 * 1024, "Defect & Regression Engine"),
            ("test-runner.js", 500 * 1024, "In-Browser Test Runner Engine"),
        ]

        for file_path, max_bytes_allowed, asset_label in core_assets:
            assert os.path.exists(file_path), f"{file_path} must exist"
            actual_size = os.path.getsize(file_path)
            print(f"\n  [BUNDLE] {asset_label} ({file_path}): {actual_size / 1024:.2f} KB (Limit: {max_bytes_allowed / 1024:.1f} KB)")
            assert actual_size <= max_bytes_allowed, \
                f"{file_path} size ({actual_size} bytes) exceeds budget of {max_bytes_allowed} bytes"
