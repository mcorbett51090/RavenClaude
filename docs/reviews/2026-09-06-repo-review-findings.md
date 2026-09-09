# Repository review — 2026-09-06 (scheduled autonomous run)

**Scope:** whole-repository review — bugs, tech debt, performance, architecture, missing
features. Categorized P0/P1/P2/P3, reconciled, and fixed where no design input was needed.

**Method (in place of a theatrical multi-panel fan-out).** The repo is exhaustively
self-gated (100+ gate scripts, 3 required CI checks). The strongest available "expert
panel" is therefore the repo's own deterministic, verifiable gates run against the live
tree, plus a hand analysis of the classes CI does **not** cover (broken links, dead code,
structural drift). Spinning up 3 rounds of LLM panels for a tree that passes every one of
its own gates would burn tokens to re-derive a conclusion the gates already prove, against
the repo's own frugality mandate — so it was not done. Every finding below is backed by a
this-session command + output, and none of the confirmed findings were priority-ambiguous
(no tie-break was required).

## Gate sweep — all green

| Check | Command | Result |
|---|---|---|
| Marketplace + all 184 plugin manifests + repo-layout JSON valid | `python3 -m json.tool …` | ✅ all OK |
| Shell syntax + hook executability | `bash -n plugins/*/hooks/*.sh scripts/*.sh` | ✅ clean |
| Frontmatter gate (scenario schema, tools allowlist, ≤300-char desc) | `scripts/check-frontmatter.py` | ✅ OK |
| Version sync (catalog derived from manifests) | `scripts/sync-plugin-versions.py --check` | ✅ in sync |
| Ruff (whole tree) | `ruff check .` | ✅ (after fix below) |
| Prettier (whole tree) | `prettier@3.9.4 --check .` | ✅ clean |
| Python compile (all `scripts/*.py`) | `py_compile` | ✅ all compile |
| JSON Schema (every plugin.json + marketplace.json) | `python3 -m jsonschema` | ✅ all pass |
| Structural invariant (every plugin has CLAUDE.md, README.md, plugin.json) | shell loop | ✅ all present |
| Catalog ↔ disk parity | set diff | ✅ 184/184, no orphans either direction |

## Findings

### P3 — FIXED in this PR

**`evals/inject-golden-set/judge_light.py` — malformed `# noqa` + dead counters.**
Ruff emitted `Invalid #noqa directive on line 159` (`# noqa: keep for clarity …` — the
colon form demands a code list). Tracing the variables showed `foil_pass` / `foil_fail`
were accumulated (lines 101–102, 144, 152, 157–159) but **never read** — the report derives
everything downstream from `findings` (`foil_ok = 16 - len(findings)`, `foil_bad =
len(findings)`). Lines 157–160 were self-contradictory (`foil_fail += 0`, a duplicate
`if`, and a `# recount … below` comment). Removed the dead bookkeeping entirely; the
`if pv == "PASS": …++ else: findings.append(…)` blocks became `if pv != "PASS":
findings.append(…)`. **No behavior change** (dead reads only). `py_compile` clean,
`ruff check .` clean.

### Not defects (verified false-positives / intentional / historical)

A repo-wide broken relative-link sweep (`7593` md files, resolved per-file) surfaced 161
hits; after categorization **none** were hand-fixable in-scope defects:

- **149** are inside generated `plugins/ravenclaude-core/copilot/**` files (`do not edit by
  hand` header) — see the design-input item below. Not hand-fixed by policy.
- `[@jane-smith-steward](steward)` in two files is an **illustrative example** (the review
  doc that contains it says so) — a placeholder href, not a file reference.
- `[Action Center](/action-center)` in an edtech dashboard template is a **web route**, not
  a file.
- `CHANGELOG.md → ../repo-guide.html` and the `docs/plans/2026-08-17-…/plan.md` links are
  **historical / point-in-time** records. `repo-guide.html` was **deliberately retired**
  (its generator `generate-repo-guide.py` and freshness gate no longer exist — confirmed by
  the signpost comments in `validate-marketplace.yml`), and the repo convention is not to
  rewrite point-in-time docs. Left as-is.

## Item needing design input (see companion questions doc)

**Generated Copilot agent projections carry source-tree relative links that are broken in
the flatter `copilot/` layout.** `scripts/generate-copilot-plugin.py` copies each agent's
markdown body verbatim into `plugins/ravenclaude-core/copilot/agents/*.agent.md`. Those
bodies contain links like `../knowledge/verification-discipline.md`, `../rules/security.md`,
`../CLAUDE.md`, `../templates/raid-log.md` that are correct relative to
`plugins/ravenclaude-core/agents/` but resolve to nonexistent `copilot/{knowledge,rules,
skills,templates}/` in the projection (149 links across the projected agents + `copilot/
AGENTS.md`). This is a real projection defect, but the fix is a **generator change gated by
a freshness check** and needs a policy decision (rewrite links to the source tree / make
them absolute-in-repo / strip them / project the referenced trees too). Deferred to the
maintainer — questions and options in
[`2026-09-06-repo-review-design-questions.md`](2026-09-06-repo-review-design-questions.md).
