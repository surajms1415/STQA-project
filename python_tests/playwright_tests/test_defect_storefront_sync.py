"""
End-to-End Playwright Automation Test:
Verifies live synchronization of defect injections between Defect Management Studio
and the live E-Commerce website storefront (index.html).
"""

import os
import json
import pytest
from playwright.sync_api import Page, expect

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORE_URL = f"file:///{os.path.join(BASE_DIR, 'index.html').replace('\\', '/')}"
STUDIO_URL = f"file:///{os.path.join(BASE_DIR, 'defect-dashboard.html').replace('\\', '/')}"


@pytest.mark.playwright
class TestDefectStorefrontSynchronization:
    """Verifies that defects injected in Defect Studio actively manifest on the live storefront."""

    def test_e2e_defect_injection_and_live_storefront_manifestation(self, page: Page, project_file_urls):
        studio_url = project_file_urls["defect_dashboard"]
        store_url = project_file_urls["store"]

        # 1. Start at Defect Studio
        page.goto(studio_url)
        page.wait_for_load_state("domcontentloaded")

        # Ensure starting in a clean fixed state
        fix_all_btn = page.locator("#btn-fix-all-top")
        fix_all_btn.click()
        page.wait_for_timeout(300)

        pass_rate = page.locator("#qa-pass-rate")
        expect(pass_rate).to_have_text("100%")

        # 2. Inject BUG-001 (Floating-Point Currency Rounding Artifact)
        bug_001_row = page.locator("tr[data-bug-id='BUG-001']")
        toggle_001_btn = bug_001_row.locator(".toggle-single-bug")
        toggle_001_btn.click()
        page.wait_for_timeout(300)

        # Confirm BUG-001 is now OPEN in studio
        status_001 = bug_001_row.locator(".status-badge")
        expect(status_001).to_contain_text("Open")

        # 3. Navigate to live E-Commerce Storefront (index.html)
        page.goto(store_url)
        page.wait_for_load_state("domcontentloaded")

        # 4. Verify Defect Alert Banner is VISIBLE on index.html
        defect_banner = page.locator("#defect-alert-banner")
        expect(defect_banner).to_be_visible()
        expect(defect_banner).to_contain_text("BUG-001")

        # 5. Add 7 units of $19.99 item or calculate total in cart
        float_outcome = page.evaluate("""() => {
            const raw = window.ECommerceCore.calculateLineTotal(19.99, 7);
            const formatted = window.ECommerceCore.formatPrice(raw);
            return { raw, formatted };
        }""")
        assert "139.92999999999998" in str(float_outcome["raw"]) or "139.92999999999998" in str(float_outcome["formatted"]), \
            f"Expected float leakage in BUG-001 buggy state, got: {float_outcome}"

        # 6. Inject BUG-011 (Out-of-stock item addition allowed)
        page.goto(studio_url)
        page.wait_for_load_state("domcontentloaded")
        bug_011_row = page.locator("tr[data-bug-id='BUG-011']")
        bug_011_row.locator(".toggle-single-bug").click()
        page.wait_for_timeout(300)

        # 7. Check index.html with BUG-011 active
        page.goto(store_url)
        page.wait_for_load_state("domcontentloaded")

        # Banner should now show BUG-001 and BUG-011
        expect(defect_banner).to_be_visible()
        expect(defect_banner).to_contain_text("BUG-001")
        expect(defect_banner).to_contain_text("BUG-011")

        # Product p10 (Leather Tech Sleeve, stock 0) should now have an active button
        p10_card = page.locator("article[data-product-id='p10']")
        p10_btn = p10_card.locator(".add-cart-btn")
        expect(p10_btn).not_to_be_disabled()

        # Click Add to Cart for the out-of-stock item
        p10_btn.click()
        page.wait_for_timeout(300)

        # Cart count should have incremented to 1
        cart_badge = page.locator("#cart-badge")
        expect(cart_badge).to_have_text("1")

        # 8. Test the 1-Click Fix All / Reset Button on the Storefront Banner
        reset_btn = page.locator("#defect-alert-reset-btn")
        reset_btn.click()
        page.wait_for_timeout(400)

        # Banner should now be HIDDEN
        expect(defect_banner).to_have_class("defect-alert-banner hidden")

        # Out-of-stock item button should now be disabled again
        expect(p10_btn).to_be_disabled()

        # 9. Verify studio also reflects the clean state
        page.goto(studio_url)
        page.wait_for_load_state("domcontentloaded")
        expect(pass_rate).to_have_text("100%")
        open_bugs_count = page.locator("#qa-open-bugs")
        expect(open_bugs_count).to_have_text("0")
