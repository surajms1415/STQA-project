"""
Defect Management & Regression Testing Suite for AuraMart E-Commerce Application.
Demonstrates controlled bug injection, root cause identification, fix verification,
and full automated regression testing.
"""

import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.defects
class TestDefectManagementAndRegression:
    """Defect lifecycle test suite covering BUG-001 through BUG-006."""

    def test_defect_01_controlled_scenarios_expose_bugs(self, defect_manager):
        """1. Controlled Scenarios Expose Bugs & Capture Defect Metadata."""
        print("\n--- EXPOSING BUGS IN CONTROLLED SCENARIOS ---")
        buggy_outcomes = defect_manager.simulate_unpatched_state()

        assert len(buggy_outcomes) == 6, "Should expose exactly 6 controlled bugs"

        for b in buggy_outcomes:
            print(f"[BUG DETECTED] {b['id']} | Severity: {b['severity']} | Status: {b['status']}")
            print(f"   Title:    {b['title']}")
            print(f"   Expected: {b['expected']}")
            print(f"   Actual:   {b['actual']} -> FAIL (Open)")
            assert b["pass"] is False, f"{b['id']} should fail in unpatched state"
            assert b["status"] == "Open", f"{b['id']} should be marked Open"

        summary = defect_manager.get_summary(32)
        print("\n[PRE-FIX QA METRICS]")
        print(f"   Total Tests: {summary['totalTests']} | Passed: {summary['passedTests']} | Failed: {summary['failedTests']}")
        print(f"   Open Bugs: {summary['openBugs']} | Resolved Bugs: {summary['resolvedBugs']} | Pass Rate: {summary['passPercentage']}%\n")

        assert summary["openBugs"] == 6, "Should have 6 open bugs"
        assert summary["failedTests"] == 6, "Should have 6 failed tests"

    def test_defect_02_fix_bugs_and_rerun_failed_tests(self, defect_manager):
        """2. Fix Identified Bugs & Rerun Failed Test Cases."""
        print("\n--- APPLYING FIXES & RERUNNING FAILED TEST CASES ---")
        fixed_outcomes = defect_manager.apply_fixes_and_rerun()

        for b in fixed_outcomes:
            print(f"[BUG RESOLVED] {b['id']} | Status: {b['status']} | Time: {b['durationMs']}ms")
            print(f"   Fix Applied: {b['fixExplanation']}")
            print(f"   Actual:      {b['actual']} -> PASS (Resolved)")
            assert b["pass"] is True, f"{b['id']} should pass in fixed state"
            assert b["status"] == "Resolved", f"{b['id']} should be marked Resolved"

        summary = defect_manager.get_summary(32)
        print("\n[POST-FIX QA METRICS]")
        print(f"   Total Tests: {summary['totalTests']} | Passed: {summary['passedTests']} | Failed: {summary['failedTests']}")
        print(f"   Open Bugs: {summary['openBugs']} | Resolved Bugs: {summary['resolvedBugs']} | Pass Rate: {summary['passPercentage']}%\n")

        assert summary["openBugs"] == 0, "All bugs should be resolved"
        assert summary["resolvedBugs"] == 6, "Resolved bugs should be 6"
        assert summary["passPercentage"] == 100, "Pass rate should be 100%"

    def test_defect_03_perform_full_regression_testing(self, defect_manager):
        """3. Perform Full Regression Testing Across All Core Test Cases."""
        print("\n--- PERFORMING FULL REGRESSION TESTING ---")
        full_test_specs = [
            {
                "id": "UT-PRICE-01",
                "suite": "Unit: Price",
                "description": "Price formatting",
                "expected": "$99.99",
                "fn": lambda: {"actual": Core.format_price(99.99), "pass": Core.format_price(99.99) == "$99.99"},
            },
            {
                "id": "UT-PRICE-02",
                "suite": "Unit: Price",
                "description": "Line total calculation",
                "expected": "149.97",
                "fn": lambda: {"actual": str(Core.calculate_line_total(49.99, 3)), "pass": Core.calculate_line_total(49.99, 3) == 149.97},
            },
            {
                "id": "UT-QTY-01",
                "suite": "Unit: Quantity",
                "description": "Integer qty check",
                "expected": "True",
                "fn": lambda: {"actual": "True", "pass": Core.ValidationRules.validate_quantity(3, 5)},
            },
            {
                "id": "UT-STOCK-01",
                "suite": "Unit: Stock",
                "description": "Stock availability",
                "expected": "True",
                "fn": lambda: {"actual": "True", "pass": Core.is_product_in_stock({"stock": 5})},
            },
            {
                "id": "FT-E2E-01",
                "suite": "Functional: E2E",
                "description": "End-to-End order workflow",
                "expected": "Confirmed",
                "fn": lambda: (
                    lambda res: {"actual": res.get("order", {}).get("status"), "pass": res["success"] is True}
                )(
                    Core.process_order(
                        [{"id": "p1", "quantity": 1}],
                        Core.INITIAL_PRODUCTS,
                        {
                            "name": "Regression Tester",
                            "email": "test@qa.org",
                            "phone": "9876543210",
                            "address": "123 QA St",
                            "city": "QA City",
                            "state": "ST",
                            "zip": "12345",
                        },
                        {"method": "cod"},
                    )
                ),
            },
        ]

        regression = defect_manager.run_regression_suite(full_test_specs)
        print(f"[REGRESSION RESULT] Total: {regression['total']} | Passed: {regression['passed']} | Failed: {regression['failed']} | Pass: {regression['passPercentage']}%")

        assert regression["failed"] == 0, "Regression suite should have zero failures"
        assert regression["passPercentage"] == 100, "Regression pass percentage should be 100%"
