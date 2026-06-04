# Dashboard visual regression — the shell comparison set

**What this is:** the manual visual-regression check for the unified dashboard shell ([plan](../plans/2026-06-04-unified-dashboard-shell/plan.md) §Phase 3), run 2026-06-04 with headless Chrome. **Result: PASS** — Phase 3 closed; the shell consolidation (index.html + dashboard + repo-guide) is fully done.

## The comparison set (re-run this if the shell or a payload changes visually)

| # | Surface A (baseline) | Surface B (compare) | What "fail" looks like |
|---|---|---|---|
| 1 | `dashboard.html` standalone — Overview / Settings / Heimdall / Bifröst tabs | `index.html#/dashboard`, same tabs | Tab color wrong, tokens wrong, layout broken, **Save & apply button absent** |
| 2 | `repo-guide.html` standalone — Overview + Plugins tabs | `index.html#/repo-guide`, same tabs | Same bar |
| 3 | `index.html#/home` before the change | After | Shell's own pages regressed |
| 4 | `index.html#/dashboard` at 390×844 mobile viewport | — | Collapsed iframe, true double scrollbar (RM4) |

Acceptable deltas: iframe border-radius/margin from the shell, scrollbar treatment, responsive reflow from the ~220px sidebar narrowing the iframe (e.g. Heimdall's 3-column grid reflows to 2 — that's the dashboard's own breakpoints working).

## 2026-06-04 result

- Surfaces 1–3: content-identical (tabs, gold tokens, Live banner, stat values, Save & apply button verified visible in-shell via DOM check: 330×74px).
- Surface 4: renders correctly; one noted nit — **65px of outer-page scroll on mobile** (shell header ≈92px + full-height iframe). Content fully reachable; within tolerance. Fix only if a user reports it: cap the iframe at `calc(100vh - <header>)` or set `overflow: hidden` on `#view` for iframe routes.

## How to re-run

Serve the repo (`python3 scripts/serve-dashboards.py --port 8001`), screenshot each surface pair with headless Chrome/puppeteer (hash routes address the dashboard tabs directly: `dashboard.html#/heimdall`), eyeball-compare.

**Gotcha (learned the hard way):** screenshot from a **clean tree** — `git worktree add /tmp/vr-main origin/main` — never the live working tree. A parallel session's in-progress merge left conflict markers in `dashboard.html` mid-capture, which render as literal `<<<<<<< HEAD` text and throw `SyntaxError: Unexpected token '<<'` in the payload JS.
