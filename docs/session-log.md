# Session log — pick up where you left off

A rolling log of the **last 3 prompt/response pairs**, newest first. When a new
turn happens, the newest pair is prepended and the oldest is dropped so only 3
remain. Committed directly to `main` (no PR) so it survives Codespace rebuilds
and is always findable regardless of which branch work is happening on.

> Maintained by Claude each turn. "Response" is a concise summary of what was
> done plus the current state and next step — not a verbatim transcript.

---

## 1 — 2026-05-24 · Resume build → ship v0.19.0 + description cap

**Prompt:** "cont" (resume the in-progress build). Two decisions during the turn:
(a) collapse the posture scale from 5 levels to 3 (Deny/Ask/Allow); (b) do the
per-permission UI + the 3-level cleanup together in one PR. Mid-turn add: "make
it a hard rule that marketplace descriptions can only have 1024 characters."

**Response:** Finished the per-permission/per-layer feature and the 5→3 level
collapse end-to-end — schema, translator (old level names still accepted for
back-compat; emits identically), dashboard generator UI+JS (per-permission
User/Local/Project selectors → v5 `overrides:` map), set-posture skill,
pattern-explanations, README, live `comfort-posture.yaml`, plan-doc changelog.
Bumped ravenclaude-core to **v0.19.0**, regenerated dashboard.html + repo-guide,
**27/27 gates green**, opened **PR #82**. Then added the 1024-char description
cap as Check 3 in `check-marketplace-claims.py` + a Gate 12 fixture, trimmed all
8 over-cap descriptions, and folded it into PR #82 (same file as the version
bump). Updated PR conventions in `AGENTS.md` (docs-only changes commit straight
to main — which is why this log entry is a direct-to-main commit).

**Current state / next step:** PR #82 open and green, awaiting Matt's review/merge.
No follow-ups pending.

---

## 2 — 2026-05-24 · Running-log request

**Prompt:** "I need a running log of the last 3 prompts and responses so I can
always pick up my work where I left off. Do not run it through a PR. Just commit
it to main. It only needs to store the last 3, so when another prompt and
response happens then delete the oldest one."

**Response:** Created this file (`docs/session-log.md`) as a rolling 3-entry
continuity log and committed it straight to `main` (no PR). Each new turn
prepends a pair and drops the oldest beyond 3.

**Current state / next step:** Mid-build on branch
`feat/ravenclaude-core-per-permission-layers` — the dashboard per-permission /
per-layer feature (the 8-part plan Matt approved). Schema tooltip rewrite was
in progress when this request came in. Next: resume the build (schema → generator
→ translator → hook → regenerate → gates → PR).

---

## 3 — 2026-05-24 · "Go and then open a PR"

**Prompt:** "Go and then open a PR"

**Response:** Approved the 8-part dashboard plan. Created branch
`feat/ravenclaude-core-per-permission-layers`, set up a 9-item task list, and
explored the generator (`scripts/generate-dashboards.py`), schema
(`plugins/ravenclaude-core/dashboard-schema.json`), and translator
(`apply-comfort-posture.py`). Found that per-permission controls already exist in
the generator but were orphaned in v5, and all 112 permission tooltips already
exist. Began implementation.

**Current state / next step:** Building parts A–H; will open a PR when green.

---
