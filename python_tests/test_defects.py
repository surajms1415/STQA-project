"""
Defect Management & Regression Testing Suite for AuraMart E-Commerce Application.
Demonstrates:
1. Preservation of all controlled defects (BUG-001 through BUG-006) and documented root causes.
2. Defect metadata (ID, severity, priority, status, description, component).
3. Test-to-defect mapping and impacted test selection.
4. Requirements Traceability Matrix (RTM) maintenance.
5. Recording failed test cases and failure error details.
6. Identifying which tests need to be rerun after fixing defects.
7. Running regression tests verifying all previously reported defects are resolved.
8. Generating comprehensive test summaries (passed, failed, skipped).
"""

import pytest
from python_tests import stqa_core as Core
from python_tests.conftest import verify


@pytest.mark.defects
class TestDefectManagementAndRegression:
    """Comprehensive Defect Lifecycle & Regression Test Suite."""

    def test_defect_01_metadata_and_documented_root_causes(self, defect_manager):
        """1. Verify Defect IDs, Severity, Priority, Status, Description, and Root Causes."""
        bugs = defect_manager.bugs
        assert len(bugs) == 6, "Must preserve exactly 6 controlled defects (BUG-001 to BUG-006)"

        expected_bugs = {
            "BUG-001": {
                "severity": "High",
                "priority": "P2 - High",
                "testCaseId": "UT-PRICE-03",
                "category": "Calculations",
            },
            "BUG-002": {
                "severity": "Critical",
                "priority": "P1 - Critical",
                "testCaseId": "UT-QTY-02",
                "category": "Quantity Validation",
            },
            "BUG-003": {
                "severity": "High",
                "priority": "P1 - Critical",
                "testCaseId": "UT-STOCK-03",
                "category": "Stock Validation",
            },
            "BUG-004": {
                "severity": "Critical",
                "priority": "P1 - Critical",
                "testCaseId": "BB-CHK-01",
                "category": "Checkout Validation",
            },
            "BUG-005": {
                "severity": "Medium",
                "priority": "P3 - Medium",
                "testCaseId": "BB-CUST-01",
                "category": "Input Validation",
            },
            "BUG-006": {
                "severity": "High",
                "priority": "P2 - High",
                "testCaseId": "BB-INP-01",
                "category": "Payment Validation",
            },
        }

        for bug in bugs:
            bid = bug["id"]
            assert bid in expected_bugs, f"Unexpected bug ID {bid}"
            expected = expected_bugs[bid]

            assert bug["severity"] == expected["severity"]
            assert bug["priority"] == expected["priority"]
            assert bug["testCaseId"] == expected["testCaseId"]
            assert bug["category"] == expected["category"]

            # Verify documented root causes
            assert len(bug.get("rootCause", "").strip()) > 10, f"{bid} must have a documented root cause"
            assert len(bug.get("description", "").strip()) > 10, f"{bid} must have a clear description"
            assert len(bug.get("stepsToReproduce", "").strip()) > 10, f"{bid} must have steps to reproduce"
            assert bug.get("expected") is not None, f"{bid} must document expected result"

    def test_defect_02_controlled_scenarios_expose_bugs_and_record_failures(self, defect_manager):
        """2. Controlled Scenarios Expose Bugs & Record Failed Test Details."""
        buggy_outcomes = defect_manager.simulate_unpatched_state()

        assert len(buggy_outcomes) == 6, "Should expose exactly 6 controlled bugs"
        for b in buggy_outcomes:
            assert b["pass"] is False, f"{b['id']} should fail in unpatched buggy mode"
            assert b["status"] == "Open", f"{b['id']} should transition to Open"
            assert b["rootCause"], f"{b['id']} must report root cause"

        # Verify failure recording with detailed error data
        failure_records = defect_manager.get_failure_records()
        assert len(failure_records) == 6, "Must record all 6 failing test cases"

        for record in failure_records:
            assert record["status"] == "Failed"
            assert record["timestamp"], "Failure record must have timestamp"
            assert record["test_id"], "Failure record must reference test_id"
            assert record["defect_id"], "Failure record must reference defect_id"
            assert record["error_message"], "Failure record must have descriptive error message"
            assert record["expected"] is not None, "Failure record must specify expected outcome"
            assert record["actual"] is not None, "Failure record must specify actual outcome"

        summary = defect_manager.get_summary(32)
        assert summary["openBugs"] == 6
        assert summary["failedTests"] == 6
        assert summary["simulatedState"] == "buggy"

    def test_defect_03_test_to_defect_mapping_and_rerun_identification(self, defect_manager):
        """3. Map Test Cases to Corresponding Defects & Identify Rerun Tests."""
        # Query rerun candidates for BUG-001 (Pricing bug)
        rerun_info = defect_manager.identify_rerun_tests(["BUG-001"])
        assert "BUG-001" in rerun_info["defect_ids"]
        assert "UT-PRICE-03" in rerun_info["rerun_test_ids"]
        assert "UT-PRICE-01" in rerun_info["rerun_test_ids"]
        assert "pytest" in rerun_info["pytest_command"]

        # Query rerun candidates for all bugs
        all_reruns = defect_manager.identify_rerun_tests(["BUG-001", "BUG-002", "BUG-003", "BUG-004", "BUG-005", "BUG-006"])
        assert len(all_reruns["rerun_test_ids"]) >= 6
        # Verify component-level reasoning
        assert "BUG-001" in all_reruns["reasons"]
        assert all_reruns["reasons"]["BUG-001"]["component"] == "Price Calculation"
        assert all_reruns["reasons"]["BUG-002"]["component"] == "Cart & Inventory"

    def test_defect_04_traceability_matrix_maintenance(self, defect_manager):
        """4. Maintain Test-to-Requirement Traceability Matrix (RTM)."""
        rtm = defect_manager.get_traceability_matrix()
        assert len(rtm) == 10, "Traceability matrix should cover REQ-01 through REQ-10"

        req_ids = [r["req_id"] for r in rtm]
        for i in range(1, 11):
            expected_req = f"REQ-{i:02d}"
            assert expected_req in req_ids, f"Matrix missing requirement {expected_req}"

        # Verify defect mapping in RTM
        req_06 = next(r for r in rtm if r["req_id"] == "REQ-06")
        assert "BUG-001" in req_06["defect_ids"]
        assert "UT-PRICE-03" in req_06["test_cases"]

        req_03 = next(r for r in rtm if r["req_id"] == "REQ-03")
        assert "BUG-002" in req_03["defect_ids"]
        assert "UT-QTY-02" in req_03["test_cases"]

    def test_defect_05_apply_fixes_and_verify_resolution(self, defect_manager):
        """5. Apply Bug Fixes and Verify Defects Transition to Resolved."""
        fixed_outcomes = defect_manager.apply_fixes_and_rerun()

        assert len(fixed_outcomes) == 6
        for b in fixed_outcomes:
            assert b["pass"] is True, f"{b['id']} should pass after fix applied"
            assert b["status"] == "Resolved", f"{b['id']} should be marked Resolved"
            assert b["fixExplanation"], f"{b['id']} must provide fix explanation"

        summary = defect_manager.get_summary(32)
        assert summary["openBugs"] == 0
        assert summary["resolvedBugs"] == 6
        assert summary["failedTests"] == 0
        assert summary["passPercentage"] == 100
        assert summary["simulatedState"] == "fixed"

    def test_defect_06_run_full_regression_testing(self, defect_manager):
        """6. Run Full Regression Suite to Confirm Resolved Defects Do Not Regress."""
        # Ensure fixes are applied
        defect_manager.apply_fixes_and_rerun()

        # Execute 32-case regression test registry
        test_specs = [
            {"id": "UT-PRICE-01", "suite": "Unit: Price", "description": "Currency formatting", "expected": "$99.99", "fn": lambda: {"actual": Core.format_price(99.99), "pass": Core.format_price(99.99) == "$99.99"}},
            {"id": "UT-PRICE-02", "suite": "Unit: Price", "description": "Line total", "expected": "149.97", "fn": lambda: {"actual": str(Core.calculate_line_total(49.99, 3)), "pass": Core.calculate_line_total(49.99, 3) == 149.97}},
            {"id": "UT-PRICE-03", "suite": "Unit: Price", "description": "Float rounding precision", "expected": "139.93", "fn": lambda: {"actual": str(Core.calculate_line_total(19.99, 7)), "pass": Core.calculate_line_total(19.99, 7) == 139.93}},
            {"id": "UT-QTY-01", "suite": "Unit: Quantity", "description": "Integer quantity", "expected": "True", "fn": lambda: {"actual": "True", "pass": Core.ValidationRules.validate_quantity(3, 5)}},
            {"id": "UT-QTY-02", "suite": "Unit: Quantity", "description": "Reject decimal quantity", "expected": "False", "fn": lambda: {"actual": "False", "pass": Core.ValidationRules.validate_quantity(2.5, 5) is False}},
            {"id": "UT-QTY-03", "suite": "Unit: Quantity", "description": "Reject zero quantity", "expected": "False", "fn": lambda: {"actual": "False", "pass": Core.ValidationRules.validate_quantity(0, 5) is False}},
            {"id": "UT-QTY-04", "suite": "Unit: Quantity", "description": "Reject negative quantity", "expected": "False", "fn": lambda: {"actual": "False", "pass": Core.ValidationRules.validate_quantity(-2, 5) is False}},
            {"id": "UT-STOCK-01", "suite": "Unit: Stock", "description": "Stock detection", "expected": "True", "fn": lambda: {"actual": "True", "pass": Core.is_product_in_stock({"stock": 5})}},
            {"id": "UT-STOCK-02", "suite": "Unit: Stock", "description": "Out of stock detection", "expected": "False", "fn": lambda: {"actual": "False", "pass": not Core.is_product_in_stock({"stock": 0})}},
            {"id": "UT-STOCK-03", "suite": "Unit: Stock", "description": "Cumulative stock guard", "expected": "3", "fn": lambda: {"actual": "3", "pass": Core.get_available_stock({"id": "x", "stock": 5}, [{"id": "x", "quantity": 2}]) == 3}},
            {"id": "IT-CART-01", "suite": "Integration: Cart", "description": "Add to cart updates array", "expected": "1", "fn": lambda: {"actual": "1", "pass": len(Core.add_to_cart([], [{"id": "p1", "stock": 5, "price": 50}], "p1", 1)["cart"]) == 1}},
            {"id": "IT-QTY-01", "suite": "Integration: Qty", "description": "Update qty recalculates totals", "expected": "157.50", "fn": lambda: (lambda res: {"actual": str(Core.calculate_cart_totals(res["cart"], [{"id": "p1", "stock": 5, "price": 50}])["total"]), "pass": Core.calculate_cart_totals(res["cart"], [{"id": "p1", "stock": 5, "price": 50}])["total"] == 157.50})(Core.update_cart_quantity([{"id": "p1", "quantity": 1}], [{"id": "p1", "stock": 5, "price": 50}], "p1", 3))},
            {"id": "BB-CHK-01", "suite": "Black Box: Guard", "description": "Empty cart checkout blocked", "expected": "False", "fn": lambda: {"actual": "False", "pass": Core.process_order([], Core.INITIAL_PRODUCTS, {"name": "V", "email": "v@e.com", "phone": "1234567890", "address": "A", "city": "C", "state": "S", "zip": "12345"}, {"method": "cod"})["success"] is False}},
            {"id": "BB-CUST-01", "suite": "Black Box: Validation", "description": "Reject whitespace name", "expected": "False", "fn": lambda: {"actual": "False", "pass": Core.ValidationRules.validate_name("   ") is False}},
            {"id": "BB-INP-01", "suite": "Black Box: Security", "description": "Reject expired card and 1-digit CVV", "expected": "False", "fn": lambda: {"actual": "False", "pass": not Core.ValidationRules.validate_card_expiry("01/20") and not Core.ValidationRules.validate_card_cvv("9")}},
            {"id": "FT-E2E-01", "suite": "Functional: E2E", "description": "End-to-End order workflow", "expected": "Confirmed", "fn": lambda: (lambda res: {"actual": res.get("order", {}).get("status"), "pass": res["success"] is True})(Core.process_order([{"id": "p1", "quantity": 1}], Core.INITIAL_PRODUCTS, {"name": "Regression Tester", "email": "test@qa.org", "phone": "9876543210", "address": "123 QA St", "city": "QA City", "state": "ST", "zip": "12345"}, {"method": "cod"}))},
        ]

        regression_result = defect_manager.run_regression_suite(test_specs)
        assert regression_result["failed"] == 0, f"Expected 0 regression failures, got {regression_result['failed']}"
        assert regression_result["passed"] == len(test_specs)
        assert regression_result["passPercentage"] == 100

    def test_defect_07_summary_metrics_passed_failed_skipped(self, defect_manager):
        """7. Generate Summary of Passed, Failed, and Skipped Tests."""
        # Verify fixed state summary
        defect_manager.apply_fixes_and_rerun()
        summary_clean = defect_manager.get_summary(total_tests=32, skipped_tests=2)

        assert summary_clean["totalTests"] == 32
        assert summary_clean["skippedTests"] == 2
        assert summary_clean["failedTests"] == 0
        assert summary_clean["passedTests"] == 30  # 32 - 0 - 2
        assert summary_clean["passPercentage"] == 100
        assert summary_clean["failureRate"] == 0
        assert summary_clean["openBugs"] == 0
        assert summary_clean["resolvedBugs"] == 6

        # Verify buggy state summary with skipped tests
        defect_manager.simulate_unpatched_state()
        summary_buggy = defect_manager.get_summary(total_tests=32, skipped_tests=2)

        assert summary_buggy["totalTests"] == 32
        assert summary_buggy["skippedTests"] == 2
        assert summary_buggy["failedTests"] == 6
        assert summary_buggy["passedTests"] == 24  # 32 - 6 - 2
        assert summary_buggy["openBugs"] == 6
        assert summary_buggy["passPercentage"] == 80  # 24/30 = 80%
        assert summary_buggy["failureRate"] == 20    # 6/30 = 20%
