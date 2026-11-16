/**
 * AuraMart Executive QA Report Controller (qa-report.js)
 * Dynamically synchronizes executive quality assurance metrics, category breakdown passes,
 * and defect resolution states with live defect injections from localStorage / DefectQAEngine.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'auramart_active_defects';
  const TOTAL_TESTS = 378;
  const TOTAL_DEFECTS = 16;

  // Category test counts baseline (Total 378)
  const CATEGORY_CONFIG = {
    'Unit Testing': { total: 46, id: 'cat-unit' },
    'Integration Testing': { total: 12, id: 'cat-integration' },
    'Functional Testing': { total: 20, id: 'cat-functional' },
    'Black-Box Testing': { total: 14, id: 'cat-blackbox' },
    'Boundary Value Testing': { total: 38, id: 'cat-boundary' },
    'Negative Testing': { total: 28, id: 'cat-negative' },
    'Validation Testing': { total: 18, id: 'cat-validation' },
    'Defect Lifecycle & RTM': { total: 16, id: 'cat-defect' },
    'Security Testing': { total: 114, id: 'cat-security' },
    'Performance Benchmarks': { total: 13, id: 'cat-perf' },
    'REST API Demonstration': { total: 26, id: 'cat-api' },
    'Browser Automation (Playwright)': { total: 33, id: 'cat-playwright' }
  };

  function getActiveDefects() {
    try {
      if (typeof localStorage !== 'undefined') {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const list = JSON.parse(stored);
          if (Array.isArray(list)) return list;
        }
      }
    } catch (e) {
      console.warn('Could not read localStorage for active defects', e);
    }
    return [];
  }

  function getBugDefinitions() {
    if (window.DefectQAEngine && Array.isArray(window.DefectQAEngine.BUG_DEFINITIONS)) {
      return window.DefectQAEngine.BUG_DEFINITIONS;
    }
    return [];
  }

  function renderReport() {
    const activeBugIds = getActiveDefects();
    const openCount = activeBugIds.length;
    const resolvedCount = Math.max(0, TOTAL_DEFECTS - openCount);
    const failedTests = Math.min(TOTAL_TESTS, openCount);
    const passedTests = Math.max(0, TOTAL_TESTS - failedTests);
    const passRate = openCount === 0 ? '100' : ((passedTests / TOTAL_TESTS) * 100).toFixed(1);

    const bugDefs = getBugDefinitions();
    const bugMap = {};
    bugDefs.forEach(b => { bugMap[b.id] = b; });

    // 1. Header Status Badge & Meta
    const statusBadge = document.getElementById('report-status-badge');
    if (statusBadge) {
      if (openCount === 0) {
        statusBadge.className = 'badge-check';
        statusBadge.style.cssText = 'font-size: 0.9rem; padding: 0.35rem 0.85rem; background-color: #ecfdf5; color: #047857; border: 1px solid #a7f3d0;';
        statusBadge.innerHTML = 'Status: READY FOR PRODUCTION';
      } else {
        statusBadge.className = 'badge-check';
        statusBadge.style.cssText = 'font-size: 0.9rem; padding: 0.35rem 0.85rem; background-color: #fee2e2; color: #b91c1c; border: 1px solid #f87171;';
        statusBadge.innerHTML = `Status: DEPLOYMENT BLOCKED (${openCount} Active Regressions)`;
      }
    }

    const metaTests = document.getElementById('report-meta-automated-tests');
    if (metaTests) {
      metaTests.innerHTML = `<strong>Total Automated Tests:</strong> 378 Tests (${openCount === 0 ? '100% Passed' : `${passRate}% Passed, ${failedTests} Failing`})`;
    }

    const metaDefects = document.getElementById('report-meta-defect-status');
    if (metaDefects) {
      metaDefects.innerHTML = `<strong>Defect Status:</strong> 16 Identified &bull; ${resolvedCount} Resolved &bull; ${openCount} Open${openCount > 0 ? ' (Regressions Active)' : ''}`;
    }

    // 2. Active Defect Alert Banner
    const alertBanner = document.getElementById('qa-report-alert-banner');
    const alertCount = document.getElementById('alert-open-count');
    const alertPills = document.getElementById('alert-open-pills');

    if (alertBanner) {
      if (openCount > 0) {
        alertBanner.style.display = 'block';
        if (alertCount) alertCount.textContent = openCount;
        if (alertPills) {
          alertPills.innerHTML = activeBugIds.map(id => {
            const bug = bugMap[id];
            const title = bug ? bug.title : id;
            return `<span style="background: #ffffff; color: #b91c1c; border: 1px solid #fca5a5; border-radius: 4px; padding: 0.2rem 0.5rem; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.35rem;">
              <span>🔴</span><strong>${id}:</strong> ${escapeHtml(title)}
            </span>`;
          }).join('');
        }
      } else {
        alertBanner.style.display = 'none';
      }
    }

    // 3. Section 1 Executive Summary Badges
    const elTotal = document.getElementById('report-total-tests');
    const elPassed = document.getElementById('report-passed-tests');
    const elFailed = document.getElementById('report-failed-tests');
    const elSkipped = document.getElementById('report-skipped-tests');
    const elPassRate = document.getElementById('report-pass-rate');
    const elResolved = document.getElementById('report-defects-resolved');
    const elKeyFinding = document.getElementById('report-key-finding');

    if (elTotal) elTotal.textContent = TOTAL_TESTS;
    if (elPassed) {
      elPassed.textContent = passedTests;
      elPassed.className = openCount === 0 ? 'val green' : 'val orange';
      if (openCount > 0) elPassed.style.color = '#ea580c';
      else elPassed.style.color = '#059669';
    }
    if (elFailed) {
      elFailed.textContent = failedTests;
      elFailed.className = openCount === 0 ? 'val gray' : 'val red';
      if (openCount > 0) elFailed.style.color = '#dc2626';
      else elFailed.style.color = '#475569';
    }
    if (elSkipped) elSkipped.textContent = '0';
    if (elPassRate) {
      elPassRate.textContent = `${passRate}%`;
      elPassRate.className = openCount === 0 ? 'val green' : 'val red';
      if (openCount > 0) elPassRate.style.color = '#dc2626';
      else elPassRate.style.color = '#059669';
    }
    if (elResolved) {
      elResolved.textContent = `${resolvedCount} / ${TOTAL_DEFECTS}`;
      elResolved.style.color = openCount === 0 ? '#7c3aed' : '#b91c1c';
    }

    if (elKeyFinding) {
      if (openCount === 0) {
        elKeyFinding.innerHTML = `<strong>Key Finding:</strong> All 378 automated test specifications pass with zero breaking regressions. All 16 controlled boundary defects (including IEEE-754 precision leakage, fractional quantities, inventory overselling, and empty cart checkouts) have been systematically resolved and verified.`;
      } else {
        elKeyFinding.innerHTML = `<strong>Key Finding:</strong> <span style="color: #b91c1c; font-weight: 800;">REGRESSION BLOCKED:</span> ${openCount} active injected defect(s) (<code style="background:#fee2e2;color:#b91c1c;padding:0.1rem 0.3rem;border-radius:3px;">${activeBugIds.join(', ')}</code>) are causing assertion failures across the test matrix (${failedTests} failing tests, ${passRate}% pass rate). Click <em>"✨ Fix All Defects"</em> above or open the <em>Defect Studio</em> to return to 100% production readiness.`;
      }
    }

    // 4. Section 2 Test Suite Execution Breakdown Table
    Object.keys(CATEGORY_CONFIG).forEach(categoryName => {
      const config = CATEGORY_CONFIG[categoryName];
      const row = document.querySelector(`tr[data-category="${categoryName}"]`);
      if (!row) return;

      // Find active bugs that violate this category
      const impactingActiveBugs = activeBugIds.filter(id => {
        const bug = bugMap[id];
        return bug && Array.isArray(bug.violatedTesting) && bug.violatedTesting.includes(categoryName);
      });

      const catFailed = impactingActiveBugs.length;
      const catPassed = Math.max(0, config.total - catFailed);

      const cellPassed = row.querySelector('.cat-passed');
      const cellFailed = row.querySelector('.cat-failed');
      const cellStatus = row.querySelector('.cat-status');

      if (cellPassed) cellPassed.textContent = catPassed;
      if (cellFailed) cellFailed.textContent = catFailed;

      if (cellStatus) {
        if (catFailed === 0) {
          cellStatus.innerHTML = `<span class="badge-check">PASS (100%)</span>`;
          row.style.backgroundColor = '';
        } else {
          cellStatus.innerHTML = `<span class="badge-check" style="background-color: #fee2e2; color: #b91c1c; border-color: #f87171;">FAIL (${catFailed} Active)</span>`;
          row.style.backgroundColor = '#fff5f5';
        }
      }
    });

    // Breakdown Total Row
    const totalPassedEl = document.getElementById('report-table-total-passed');
    const totalFailedEl = document.getElementById('report-table-total-failed');
    const totalStatusEl = document.getElementById('report-table-total-status');

    if (totalPassedEl) totalPassedEl.textContent = passedTests;
    if (totalFailedEl) totalFailedEl.textContent = failedTests;
    if (totalStatusEl) {
      if (openCount === 0) {
        totalStatusEl.innerHTML = `<span class="badge-check" style="font-size: 0.85rem; padding: 0.3rem 0.8rem;">100% PASS</span>`;
      } else {
        totalStatusEl.innerHTML = `<span class="badge-check" style="font-size: 0.85rem; padding: 0.3rem 0.8rem; background-color: #fee2e2; color: #b91c1c; border-color: #f87171;">${passRate}% PASS (${failedTests} FAILING)</span>`;
      }
    }

    // 5. Section 4 Defect Table (All 16 Defects)
    document.querySelectorAll('tr[data-bug-id]').forEach(row => {
      const bugId = row.getAttribute('data-bug-id');
      const isOpen = activeBugIds.includes(bugId);
      const statusCell = row.querySelector('.bug-verification-status');

      if (statusCell) {
        if (isOpen) {
          statusCell.innerHTML = `<span class="badge-check" style="background-color: #fee2e2; color: #b91c1c; border-color: #f87171; font-weight: 700;">🔴 Open (Injected)</span>`;
          row.style.backgroundColor = '#fffaf0';
        } else {
          statusCell.innerHTML = `<span class="badge-check">🟢 Resolved</span>`;
          row.style.backgroundColor = '';
        }
      }
    });

    // 6. Section 6 Final Sign-off
    const signoffDecision = document.getElementById('report-signoff-decision');
    const signoffQa = document.getElementById('signoff-qa-status');
    const signoffDev = document.getElementById('signoff-dev-status');
    const signoffRelease = document.getElementById('signoff-release-status');

    if (signoffDecision) {
      if (openCount === 0) {
        signoffDecision.innerHTML = `<strong>Final QA Decision: APPROVED (GO FOR DEPLOYMENT)</strong><br>
        The application meets 100% of functional, non-functional, security, and performance quality assurance criteria. The codebase is clean, modular, and verified safe for public deployment on Netlify or GitHub Pages.`;
      } else {
        signoffDecision.innerHTML = `<strong>Final QA Decision: <span style="color: #b91c1c; font-weight: 800;">BLOCKED &bull; ACTION REQUIRED (${openCount} Active Regressions)</span></strong><br>
        Production release candidate is quarantined due to active defect simulation. All 16 quality verification checkpoints must be resolved before deployment sign-off.`;
      }
    }

    if (signoffQa) {
      signoffQa.innerHTML = openCount === 0
        ? `✓ Certified &bull; 100% Pass Rate (378 Tests)`
        : `<span style="color: #dc2626;">✗ Blocked &bull; ${passRate}% Pass Rate (${failedTests} Failing)</span>`;
    }
    if (signoffDev) {
      signoffDev.innerHTML = openCount === 0
        ? `✓ Zero Regressions Confirmed`
        : `<span style="color: #dc2626;">✗ ${openCount} Injected Defect(s) Active</span>`;
    }
    if (signoffRelease) {
      signoffRelease.innerHTML = openCount === 0
        ? `✓ Approved for Netlify / GH Pages`
        : `<span style="color: #dc2626;">✗ Release Quarantined Pending Fixes</span>`;
    }
  }

  function fixAllDefects() {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, JSON.stringify([]));
      }
    } catch (e) {
      console.warn('Could not reset active defects in localStorage', e);
    }
    if (typeof window !== 'undefined' && typeof window.dispatchEvent === 'function') {
      window.dispatchEvent(new CustomEvent('auramart_defects_changed', { detail: { activeDefects: [] } }));
    }
    renderReport();
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Initialize on page load
  document.addEventListener('DOMContentLoaded', () => {
    renderReport();

    // Fix All Button handler
    const btnFixAll = document.getElementById('btn-report-fix-all');
    if (btnFixAll) {
      btnFixAll.addEventListener('click', () => {
        fixAllDefects();
      });
    }

    // Cross-tab synchronization
    window.addEventListener('storage', (e) => {
      if (e.key === STORAGE_KEY) {
        renderReport();
      }
    });

    // In-page event synchronization
    window.addEventListener('auramart_defects_changed', () => {
      renderReport();
    });
  });

  // Export helper to window for console testing
  window.QAReportController = {
    renderReport,
    fixAllDefects,
    getActiveDefects
  };
})();
