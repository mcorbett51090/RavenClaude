# Repository review — 2026-06-09 (three-panel + autonomous fixes)

**Reviewer:** Claude Code (Opus 4.8), branch `claude/stoic-fermat-hh3vnv`
**Scope:** full repository — 98 plugins, 134 Python files, 136 shell scripts, 268 JSON manifests, ~5,400 markdown files.
**Method:** ran the repo's own objective gates (the source of truth per `AGENTS.md` house-rule 4), then three review passes — Panel 1 (expert fan-out: 3 independent read-only sweeps over Python, shell, and docs/consistency), Panel 2 (each finding re-verified against disk by the lead), Panel 3 (tie-break — not needed; see below). Lighter models drove the fan-out sweeps; the lead validated and implemented.

---

## Headline

**The codebase is in excellent shape.** Every objective gate passes; the shell and Python are clean. The only concrete defect class found was **stale per-plugin counts in `README.md`** — a documentation-accuracy issue, already fixed in this PR. Two improvement opportunities need a decision and are written up below.

---

## What was checked (all green)

| Check | Result |
|---|---|
| All tracked JSON valid (`python3 -m json.tool`) | ✅ (the 2 devcontainer files are intentional JSONC) |
| All shell parses (`bash -n`) | ✅ 136/136 |
| All Python compiles (`py_compile`) | ✅ 134/134 |
| Plugin hooks executable | ✅ |
| Version drift (plugin.json ↔ marketplace.json) | ✅ none — 98/98 in sync |
| `prettier --check .` (whole tree) | ✅ exit 0 |
| `check-frontmatter.py` | ✅ |
| `check-marketplace-claims.py` | ✅ |
| `check-md-links.py` | ✅ all relative links resolve |
| `check-layout.py --all` | ✅ 6,903 files, all match allow-list |
| `check-run-actions-argv` / `check-lineup-citations` / `check-mcp-attribution` / `check-ragnarok` / `check-dashboard-server-parity` | ✅ |
| `audit-gates.sh` (meta-test) | ✅ 420/420 once `jsonschema` is installed (see P3-1) |
| Python deep bug-sweep (logic/leaks/injection/off-by-one) | ✅ no bugs |
| Shell deep bug-sweep (quoting/`set -e`/fail-closed hooks) | ✅ no bugs; every hook fails **safe** |

---

## Findings by priority

### P0 (critical) — none
### P1 (high) — none

### P2 (medium) — README per-plugin counts had drifted — **FIXED in this PR**

`README.md` hand-maintains per-plugin component counts in two places (the top summary bullets and the per-plugin detail tables). **29 of them had drifted** as plugins gained skills/agents/hooks/commands without the README being updated. Each was verified against disk before editing.

Representative corrections (full set in the diff — 38 lines, all in `README.md`):

| Plugin | Claim | Actual |
|---|---|---|
| `ravenclaude-core` | 22–23 skills, 13 hooks, 4 rules, 4 commands | **38 skills, 16 hooks, 5 rules, 7 commands** |
| `regulatory-compliance` | 6 specialists, 9 skills | **12 specialists** (6 function + 6 jurisdiction), **10 skills** |
| `power-platform` | 18 skills | 20 |
| `web-design` | 10 skills | 11 |
| `edtech-partner-success` | 12 skills | 16 |
| `data-platform` | 11 skills | 13 |
| `customer-success-analytics`, `team-portfolio` | 2 skills | 5 each |
| 20× engineering plugins (`devops-cicd`, `observability-sre`, `aws-cloud`, `backend-engineering`, `data-streaming-engineering`, …) | 3–4 skills | now correct (typically +1/+2; data-streaming 3→7) |

After the fix, a grounded re-scan reports **0 remaining mismatches**. The `regulatory-compliance` summary was also corrected to surface the 6 jurisdiction specialists (BMA, CIMA Cayman, Bahamas, Channel Islands, UK PRA, US) that were previously invisible to README readers.

### P3 (low)

**P3-1 — `audit-gates.sh` Gate 47 has a `jsonschema`-absent blind spot.** When the `jsonschema` Python module is not installed, `python3 -m jsonschema` exits non-zero, which makes the two **good-fixture** sub-gates fail (confusingly: "expected zero, got 1") **and** makes the two **bad-fixture** `must_fail` sub-gates pass *for the wrong reason* (a missing module is indistinguishable from "schema correctly rejected bad input") — a silent false-green on a gate that should have teeth. CI installs `jsonschema` first so this never bites in CI, but a local `audit-gates.sh` run without it produces a misleading 2-fail report (observed this session before `pip install jsonschema`). See `scripts/audit-gates.sh` Gate 47 (≈ line 2715) and `.github/workflows/validate-schemas.yml`. **This is not a product bug** — flagged because the repo explicitly values "a skip is not a pass" and gates-with-teeth (`docs/best-practices/ci-gate-audit.md`).

---

## Tie-breaking (Panel 3)

No severity was ambiguous, so no tie-break panel was convened. The single substantive finding (README count drift) is unambiguously a P2 documentation-accuracy issue, and the fix is rule-derivable (count files on disk) — no genuine-preference call. Per `CLAUDE.md`'s decision-review posture, rule-derivable fixes do not interrupt the maintainer.

---

## Open questions / recommendations needing your input

These were **not** implemented autonomously because each involves a design choice or touches a sensitive surface (the CI meta-test).

### Q1 — Gate the README's per-plugin prose counts so they can't drift again (root cause of P2)

`check-marketplace-claims.py` already validates the "N skills" / "N agents" claims in each plugin's **`plugin.json` description** and its **`marketplace.json` entry** (see `scripts/check-marketplace-claims.py:10–18`, `SKILLS_RE`/`AGENTS_RE`). But it does **not** look at `README.md`'s *separate* per-plugin bullets and detail tables — which is exactly why those drifted while CI stayed green. The same `--fix` self-healing pattern that rewrites `plugin.json` counts could be extended to the README.

- **Recommendation:** extend `check-marketplace-claims.py` to also parse and gate the README's per-plugin skill/agent counts (bullets + detail tables), reusing the existing `actual_skill_count` / `actual_agent_count` helpers. This would have caught all 29 drifts.
- **Decisions for you:**
  1. **Which kinds to gate?** Skills and agents are unambiguous. Hooks/rules/commands are trickier — "hooks" can mean *registered* hooks (16, from `hooks.json`) vs. *`.sh` files* (19, incl. sourced `_`-prefixed helpers + the Copilot adapter). I used **16 (registered)** in this PR; should the gate enforce that definition?
  2. **Match semantics for illustrative parentheticals** — e.g. `5 skills (incl. health-tier-design, renewal-workflow-design)`. Gate only the leading number, or also that the listed names exist?
  3. **Extend `--fix` to the README?** Regex-rewriting prose counts is riskier than rewriting JSON; worth it, or check-only?

### Q2 — Harden Gate 47 against a missing `jsonschema` (the P3-1 blind spot)

- **Recommendation:** add a presence guard at the top of Gate 47 — `python3 -c 'import jsonschema'` — and, if absent, **LOUD-skip** locally (matching the Gate 10 / actionlint pattern already in `audit-gates.sh`: "THIS IS NOT A PASS") while treating an unrunnable gate as a hard failure in CI. This removes the false-green on the bad fixtures.
- **Why not done autonomously:** `audit-gates.sh` is the meta-test that guards every other gate; editing it warrants a human eye, and "loud-skip vs hard-fail when the tool is absent" is a small policy choice the maintainer should confirm.

---

## Confirmation

Apart from the README count drift (fixed) and the two recommendations above, **no bugs, no broken references, no missing required files, no version drift, and no failing gates were found.** All 98 plugins carry their three required files; all relative links resolve; the whole tree is prettier-clean.
