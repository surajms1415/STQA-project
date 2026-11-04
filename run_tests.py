#!/usr/bin/env python3
"""
AuraMart STQA - Master Python Test Runner CLI
Provides simple flags to execute individual test categories or the entire QA suite.

Usage Examples:
  python run_tests.py --all            # Run all automated tests (Unit, Integration, Security, Perf, API, Playwright)
  python run_tests.py --unit           # Run unit tests only
  python run_tests.py --integration    # Run integration tests only
  python run_tests.py --functional     # Run functional e-commerce tests
  python run_tests.py --blackbox       # Run black-box input/output tests
  python run_tests.py --defects        # Run defect lifecycle & regression tests
  python run_tests.py --security       # Run security tests (XSS, SQLi, Sanitization)
  python run_tests.py --performance    # Run performance benchmarks & latency tests
  python run_tests.py --api            # Run REST API demonstration tests
  python run_tests.py --browser        # Run Playwright browser automation tests
  python run_tests.py --report         # Run tests and generate self-contained HTML report
"""

import argparse
import os
import subprocess
import sys


def get_pytest_bin():
    """Locate pytest executable in current virtualenv or system PATH."""
    venv_bin = os.path.join(os.path.dirname(sys.executable), "pytest.exe" if os.name == "nt" else "pytest")
    if os.path.exists(venv_bin):
        return venv_bin
    return "pytest"


def run_command(cmd_list):
    """Execute command and return exit code."""
    print(f"\n[AuraMart STQA] Executing: {' '.join(cmd_list)}\n")
    return subprocess.call(cmd_list)


def main():
    parser = argparse.ArgumentParser(
        description="AuraMart E-Commerce STQA Test Runner CLI",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("--all", action="store_true", help="Execute entire test suite across all categories")
    parser.add_argument("--unit", action="store_true", help="Execute Unit Testing suite (Pricing, Qty, Stock, Cart)")
    parser.add_argument("--integration", action="store_true", help="Execute Integration Testing suite (Cart state, Orders, Storage)")
    parser.add_argument("--functional", action="store_true", help="Execute Functional Testing suite (Search, Filtering, E2E)")
    parser.add_argument("--blackbox", action="store_true", help="Execute Black-Box Testing suite (Boundaries, Guards, Validations)")
    parser.add_argument("--regression", action="store_true", help="Execute Regression Testing suite")
    parser.add_argument("--boundary", action="store_true", help="Execute Boundary Value Testing suite")
    parser.add_argument("--negative", action="store_true", help="Execute Negative Testing suite")
    parser.add_argument("--validation", action="store_true", help="Execute Validation Testing suite")
    parser.add_argument("--defects", action="store_true", help="Execute Defect Lifecycle (BUG-001..006) verification")
    parser.add_argument("--security", action="store_true", help="Execute Security Testing suite (Sanitization, XSS, SQLi, Exposure)")
    parser.add_argument("--performance", action="store_true", help="Execute Performance Benchmarks & Concurrency suite")
    parser.add_argument("--api", action="store_true", help="Execute REST API demonstration tests (Requests)")
    parser.add_argument("--browser", action="store_true", help="Execute Playwright End-to-End browser automation tests")
    parser.add_argument("--report", action="store_true", help="Generate self-contained HTML test report in reports/pytest_report.html")

    args, unknown = parser.parse_known_args()
    pytest_bin = get_pytest_bin()
    os.makedirs("reports", exist_ok=True)

    base_cmd = [pytest_bin, "-v", "--tb=short"]

    # Category mappings
    if args.unit:
        return run_command(base_cmd + ["python_tests/test_unit.py"] + unknown)
    elif args.integration:
        return run_command(base_cmd + ["python_tests/test_integration.py"] + unknown)
    elif args.functional:
        return run_command(base_cmd + ["python_tests/test_functional.py"] + unknown)
    elif args.blackbox:
        return run_command(base_cmd + ["python_tests/test_blackbox.py"] + unknown)
    elif args.regression:
        return run_command(base_cmd + ["python_tests/test_regression.py"] + unknown)
    elif args.boundary:
        return run_command(base_cmd + ["python_tests/test_boundary.py"] + unknown)
    elif args.negative:
        return run_command(base_cmd + ["python_tests/test_negative.py"] + unknown)
    elif args.validation:
        return run_command(base_cmd + ["python_tests/test_validation.py"] + unknown)
    elif args.defects:
        return run_command(base_cmd + ["python_tests/test_defects.py"] + unknown)
    elif args.security:
        return run_command(base_cmd + ["python_tests/security_tests/"] + unknown)
    elif args.performance:
        return run_command(base_cmd + ["python_tests/performance_tests/"] + unknown)
    elif args.api:
        return run_command(base_cmd + ["python_tests/api_tests/"] + unknown)
    elif args.browser:
        return run_command(base_cmd + ["python_tests/playwright_tests/"] + unknown)
    elif args.report:
        report_path = os.path.join("reports", "pytest_report.html")
        cmd = base_cmd + [
            "python_tests/",
            "--ignore=python_tests/playwright_tests",
            f"--html={report_path}",
            "--self-contained-html",
        ] + unknown
        code = run_command(cmd)
        print(f"\n[AuraMart STQA] HTML Report generated: {report_path}")
        return code
    elif args.all:
        report_path = os.path.join("reports", "pytest_report.html")
        cmd = base_cmd + [
            "python_tests/",
            f"--html={report_path}",
            "--self-contained-html",
        ] + unknown
        code = run_command(cmd)
        print(f"\n[AuraMart STQA] Full Suite HTML Report generated: {report_path}")
        return code
    else:
        # Default: run all core, security, performance, and defects suites with quick summary
        print("No category specified. Running all core, security, and performance test suites...")
        print("Tip: Use 'python run_tests.py --help' to inspect individual category options.\n")
        return run_command(base_cmd + [
            "python_tests/",
            "--ignore=python_tests/playwright_tests",
        ] + unknown)


if __name__ == "__main__":
    sys.exit(main())
