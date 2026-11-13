# Phase 3 plan — single artifact (entry first, then collapse)

**Date:** 2026-11-12  
**Status:** shipping (3a)  
**Decision:** [`docs/decisions/2026-11-12-one-product-portal-dashboard.md`](../decisions/2026-11-12-one-product-portal-dashboard.md) Phase 3  
**Predecessor:** Phase 2 Catalog hybrid on `main` (#1436)

## Verdict

Split Phase 3 into **3a (entry unification)** and **3b (artifact collapse)**. Ship 3a first: marketplace local home becomes the same artifact consumers already use (`dashboard.html` + `catalog-data.json` hybrid). Keep fat `index.html` for GitHub Pages + Gates 97/51 until 3b. Gate 132 Δ0.

---

## Measured anchors (post–Phase 2)

| Surface | Gate 132 | Bytes (approx) |
|---|---|---|
| `plugins/ravenclaude-core/dashboard.html` | 6,408 / 6,408 | ~11.0 MB |
| `index.html` | 7,294 / 7,294 | ~9.6 MB |
| `catalog-data.json` | n/a | ~615 KB |

`#dt-store` (~799 stubs) is the dominant index-only DOM cost. Baking it into the consumer ship is **Deny**.

---

## Phase 3a — entry unification (this PR)

### Keep / Update / Deny

| Item | Decision | Why |
|---|---|---|
| Consumer `DASH_PATH = "/dashboard.html"` | **Keep** | Already canonical (`rc dashboard`) |
| Lean `dashboard.html` + runtime Browse | **Keep** | Phase 2; Gate 132 zero slack |
| Root `dash_path` → `/plugins/ravenclaude-core/dashboard.html` | **Update** | Same product + Save; Catalog via `/catalog-data.json` |
| `scripts/open-dashboard.sh` open + liveness probes | **Update** | Must match `dash_path` |
| Audit C2 readiness curls (`/index.html`) | **Update** | Point at new path |
| Fat `index.html` for Pages + Gate 97/51 | **Keep** (3a) | Avoid blast radius |
| Kill / redirect `index.html` | **Deny** for 3a → 3b | Pages root + shell-router |
| `#dt-store` on consumer ship | **Deny** | Gate 132 |

### Files

- `scripts/serve-dashboards.py` — `dash_path` + comments  
- `scripts/open-dashboard.sh` — URL + curl probes  
- `scripts/audit-gates.sh` — C2 / C2b readiness curls  
- Decision + this plan status notes  

### Out of scope for 3a

- Gate 97/51/132 retarget  
- Generator collapse  
- Pages redirect stub  
- Consumer `DASH_PATH` change  

---

## Phase 3b — true single artifact (follow-up)

1. Thin `index.html` redirect stub → dashboard path **or** one fat HTML from `generate-dashboards.py` pipeline.  
2. Retarget Gate 97 (dashboard freshness + `catalog-data.json`) and Gate 51 (drop shell-router or rewrite for one surface).  
3. Gate 132: drop `INDEX` ratchet once fat index is gone.  
4. Pages host follows (legacy `main` `/` publish).

---

## Verification (3a)

```shell
python3 scripts/serve-dashboards.py --port 8767 --no-open &
# expect 302 / → /plugins/ravenclaude-core/dashboard.html
curl -sI http://127.0.0.1:8767/ | head -5
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8767/plugins/ravenclaude-core/dashboard.html
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8767/catalog-data.json
python3 scripts/check-dom-budget.py --check   # unchanged 6408 / 7294
```
