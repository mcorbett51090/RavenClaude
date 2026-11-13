# Phase 3b plan — thin `index.html` stub (single Pages entry)

**Date:** 2026-11-12  
**Status:** shipping  
**Predecessor:** Phase 3a merged (#1437)  
**Parent plan:** [`docs/plans/2026-11-12-phase3-single-artifact.md`](2026-11-12-phase3-single-artifact.md)

## Verdict

Replace fat marketplace `index.html` with a **thin redirect stub** → `plugins/ravenclaude-core/dashboard.html` (preserve hash/query). Keep lean consumer dashboard + `catalog-data.json`. **Deny** baking `#dt-store` / fat portal into the consumer ship (Gate 132 Δ0).

---

## Keep / Update / Deny

| Item | Decision | Why |
|---|---|---|
| Lean `dashboard.html` + Catalog hybrid | **Keep** | Canonical product |
| Consumer `DASH_PATH` | **Keep** | Already `/dashboard.html` |
| `#dt-store` / `__RC_DATA__` on dashboard | **Deny** | Gate 132 zero slack |
| One fat HTML as sole ship | **Deny** | Forces portal DOM onto consumers |
| Committed `index.html` → thin stub | **Update** | Pages `/` becomes one product |
| `generate-index-dashboard.py` default emit | **Update** | Stub + `catalog-data.json` (no fat portal) |
| Gate 97 | **Update** | Stub + catalog freshness |
| Gate 51 shell-router / router-execution | **Update** | Retire portal-only contract (no `NAV` on stub) |
| Gate 132 `INDEX` ratchet | **Update** | Drop index surface |
| Render must_fail halves on committed `index.html` | **Update** | Retarget → `dashboard.html` / `$DASH_HTML` |
| Gate 141 / 200 / committed-routes index half | **Update** | Drop or dashboard-only |
| Artifact byte budgets for fat index | **Update** | Drop / replace |

---

## Verification

```shell
python3 scripts/generate-index-dashboard.py --check
python3 scripts/check-artifact-freshness.py --check
python3 scripts/check-dom-budget.py --check   # dashboard only
# Pages-shaped: stub redirects
python3 - <<'PY'
from pathlib import Path
html = Path('index.html').read_text()
assert 'plugins/ravenclaude-core/dashboard.html' in html
assert 'dt-store' not in html
assert len(html) < 5000
print('stub ok', len(html))
PY
```
