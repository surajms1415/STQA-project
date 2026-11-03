"""
Playwright Browser Fixtures & Test Failure Screenshot Capture Hook.
Provides isolated browser contexts, clean page states, and automated artifact capture.
"""

import os
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INDEX_HTML_PATH = (PROJECT_ROOT / "index.html").resolve()
INDEX_FILE_URL = INDEX_HTML_PATH.as_uri()
SCREENSHOTS_DIR = PROJECT_ROOT / "reports" / "screenshots"


@pytest.fixture(scope="session")
def project_file_urls():
    """Provides file URIs for all frontend HTML files."""
    return {
        "store": INDEX_FILE_URL,
        "test_dashboard": (PROJECT_ROOT / "test-dashboard.html").resolve().as_uri(),
        "defect_dashboard": (PROJECT_ROOT / "defect-dashboard.html").resolve().as_uri(),
        "qa_report": (PROJECT_ROOT / "qa-report.html").resolve().as_uri(),
    }


@pytest.fixture(scope="session")
def playwright_instance():
    """Session-scoped Playwright runtime instance."""
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance) -> Browser:
    """Session-scoped Chromium browser instance."""
    browser_instance = playwright_instance.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ],
    )
    yield browser_instance
    browser_instance.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    """Isolated browser context with standard desktop viewport."""
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        device_scale_factor=1,
    )
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext, request) -> Page:
    """Fresh browser page attached to the test request for screenshot capture."""
    p = context.new_page()
    request.node.playwright_page = p
    yield p
    if not p.is_closed():
        p.close()


@pytest.fixture(scope="function")
def app_page(page: Page) -> Page:
    """
    Ready-to-use application page with reset localStorage ensuring pristine test state.
    """
    page.goto(INDEX_FILE_URL)
    # Clear localStorage to avoid cross-test contamination
    page.evaluate("() => { try { localStorage.clear(); } catch (e) {} }")
    page.reload()
    page.wait_for_selector("#product-grid .product-card", state="visible", timeout=10000)
    return page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Captures full-page screenshots automatically whenever a test fails,
    saving the PNG file to reports/screenshots/ and attaching it to reports.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        p: Page = getattr(item, "playwright_page", None)
        if p and not p.is_closed():
            try:
                SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
                clean_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in item.name)
                screenshot_path = SCREENSHOTS_DIR / f"{clean_name}.png"
                p.screenshot(path=str(screenshot_path), full_page=True)
                print(f"\n[SCREENSHOT CAPTURED] Saved failure screenshot to: {screenshot_path}")

                # Attach to pytest-html if available
                pytest_html = item.config.pluginmanager.getplugin("html")
                if pytest_html is not None:
                    if hasattr(report, "extras"):
                        report.extras.append(pytest_html.extras.image(str(screenshot_path)))
                    else:
                        extra = getattr(report, "extra", [])
                        extra.append(pytest_html.extras.image(str(screenshot_path)))
                        report.extra = extra

            except Exception as e:
                print(f"\n[SCREENSHOT ERROR] Could not capture screenshot: {e}")
