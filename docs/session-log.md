# Session log — pick up where you left off

A rolling log of the **last 3 prompt/response pairs**, newest first. When a new
turn happens, the newest pair is prepended and the oldest is dropped so only 3
remain. Committed directly to `main` (no PR) so it survives Codespace rebuilds
and is always findable regardless of which branch work is happening on.

> Maintained by Claude each turn. "Response" is a concise summary of what was
> done plus the current state and next step — not a verbatim transcript.

---

## 1 — 2026-05-25 · Resume tribunal track → open PR #87 for T1

**Prompt:** "cont" (resume; then "cont" again to proceed).

**Response:** Oriented from a cold context — this session log was stale (covered
v0.19.0; the tribunal track had advanced two releases past it). Reconstructed
state from git + `docs/tribunal-review-feature-design.md`: **T0** merged (PR #84,
v0.21.0: guard-destructive fix + concern catalog); **T1** (read-only "Command
review (the Thing)" preview UI, **v0.22.0**) was committed + pushed on branch
`feat/ravenclaude-core-tribunal-t1` but had **no PR**. Verified the branch green
(JSON valid, hooks parse, dashboard regen → no diff so it's fresh, `prettier
--check .` exit 0; versions coherent at 0.22.0 in plugin.json + marketplace.json),
then opened **PR #87**. T1 is intentionally inert — a "Preview" panel + disabled
per-category toggles, no orchestrator, no behavior change.

**Current state / next step:** **PR #87 open**, CI running (layout gate passed,
manifests pending). After it merges: **T2 (single-seat orchestrator) is BLOCKED**
on the §B.5.1 hook-API substrate verification — the `permissionDecision` /
`updatedInput` claims contradict the repo's own
`knowledge/claude-code-permissions.md` and must be reconciled in **one standalone
PR** before any T2 code lands. That verification is the real next task, not
building T2.

---

## 2 — 2026-05-24 · Resume build → ship v0.19.0 + description cap

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

**Current state / next step:** **MERGED** as v0.19.0 (PR #82, squash `e7f703b`);
Matt confirmed the dashboard UI looks good. He has unspecified dashboard
**improvement ideas parked for a later session** — ask him to enumerate when raised.
Nothing else outstanding.

---

## 3 — 2026-05-24 · Running-log request

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

