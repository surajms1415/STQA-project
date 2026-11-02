# AuraMart E-Commerce & STQA Framework - Deployment Guide

This project is a **100% static client-side web application** built using vanilla HTML5, CSS3, and JavaScript with zero backend runtime dependencies. It can be deployed to any static web hosting platform in seconds.

---

## 🚀 Option 1: Deploy to Netlify (Recommended)

### Method A: Manual Drag-and-Drop (Instant, No Git Required)
1. Go to [app.netlify.com/drop](https://app.netlify.com/drop) in your browser.
2. Sign in to your Netlify account (free).
3. Drag and drop the `STQA project/` folder directly into the upload area on Netlify.
4. Netlify will deploy your site in ~5 seconds and provide a live URL (e.g., `https://auramart-stqa.netlify.app`).

### Method B: Git-Connected Automated Deployment
1. Push this repository to GitHub or GitLab.
2. In Netlify, click **"Add new site"** &rarr; **"Import an existing project"**.
3. Select your repository.
4. Set the build settings:
   - **Build command**: *(leave empty)*
   - **Publish directory**: `.` (or root)
5. Click **"Deploy site"**.
   - The included `netlify.toml` and `_redirects` files automatically configure routing and security headers.

---

## 🐙 Option 2: Deploy to GitHub Pages

1. Initialize a git repository and commit your files:
   ```bash
   git init
   git add .
   git commit -m "Initial release of AuraMart E-Commerce STQA"
   ```
2. Create a new public repository on GitHub and push your code:
   ```bash
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git branch -M main
   git push -u origin main
   ```
3. In GitHub, go to your repository **Settings** &rarr; **Pages** (under Code and automation).
4. Under **Build and deployment**:
   - **Source**: Deploy from a branch
   - **Branch**: `main` / `root`
5. Click **Save**.
6. Within 1-2 minutes, GitHub Pages will publish your site at:
   `https://<your-username>.github.io/<repo-name>/`
   *(The included `.nojekyll` file prevents Jekyll from interfering with static files).*

---

## 💻 Option 3: Local Execution

### Double-Click Execution (Offline File Protocol)
Simply open any of the HTML pages directly in your browser:
- Storefront: `index.html`
- Test Suite: `test-dashboard.html`
- Defect QA: `defect-dashboard.html`
- QA Report: `qa-report.html`

### Local Static Server (Optional)
If you prefer running via a local HTTP server:
```bash
# Python 3
python -m http.server 8080

# Or Node.js npx
npx serve .
```
Then visit `http://localhost:8080`.

---

## 🔍 Pre-Deployment Verification Matrix

| Verification Item | Status | Result |
| :--- | :---: | :--- |
| **All Test Suites Passing** | `PASS` | 35/35 test suites pass in ~230 ms (`npm test`). |
| **Zero Backend Dependencies** | `PASS` | No Node server, Express, Python, or API endpoints required. |
| **Zero External CDN Assets** | `PASS` | Self-contained vector SVGs & native system fonts. |
| **Relative URL Paths** | `PASS` | Works seamlessly regardless of hosting subpath. |
| **LocalStorage Resiliency** | `PASS` | Fallback exception handling for restricted browser modes. |
| **Responsive UI** | `PASS` | Fully optimized across desktop, tablet, and mobile displays. |
