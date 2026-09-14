# Repo review — 2026-09-12 (multi-panel autonomous sweep)

**Method.** Four independent expert-review panels (Panel 1) swept the tree read-only across distinct
surfaces — Python correctness, shell + GitHub Actions security, references/manifest consistency, and
dead-code/tech-debt — each held to a strict evidence bar (file:line, observation-vs-inference, a
concrete failure scenario). A validation + tie-break pass (Panels 2/3) verified every high-value
finding against the filesystem and the repo's own gates before any change was made. Baseline was
healthy: `ci-preflight` 19/19 green, all JSON/shell/Python parse, prettier + ruff clean, branch even
with `origin/main`.

**Headline:** **0 P0, no CI-breaking defects.** This is a mature, heavily-gated repo. The real
findings are latent defects the gates don't catch: broken internal references from two file-move
sweeps, cross-platform robustness gaps in shipped scripts, and a **fail-open weakness in a required
CI gate**. The confirmed, safe, mechanical fixes are implemented in the accompanying PR (grouped by
priority). The items below **need a human decision** and were deliberately NOT auto-implemented.

---

## What was fixed in the PR (no design input needed)

| Priority | Fix | Files |
|---|---|---|
| P1 | 6 broken markdown links in shipped `plugins/ravenclaude-core/CLAUDE.md` (4 repointed to `docs/plans/archive/…`; 2 gitignored `.ravenclaude/runs/…` links de-linked) | `plugins/ravenclaude-core/CLAUDE.md` |
| P1 | Shipped SKILL `sources:` / body refs repointed to `archive/` | `probe-kit`, `refine-to-rubric`, `repo-build-studio` SKILL.md |
| P1/P2 | Archive-drift repoints across 20 files (shipped plugin + docs) — every one verified: non-archive missing **and** archive present | edtech + ravenclaude-core + `docs/**` |
| P2 | `encoding="utf-8"` added to 19 text-mode file-I/O sites in shipped finance scripts (byte-identity contract + non-UTF-8-host crash) | `plugins/finance/scripts/*.py` |
| P3 | `ghg_calc.py` stdin read forced to UTF-8 (guarded) | `plugins/esg-sustainability-reporting/scripts/ghg_calc.py` |
| P3 | `open-dashboard.sh` mktemp-failure fallback `/tmp/…$$` → `/dev/null` (a symlink-attack target that contradicted the block's own comment) | `scripts/open-dashboard.sh` |
| P3 | Stale-doc fixes: `architecture.md` plugin count 181→184; CHANGELOG `repo-guide.html` link → portal; dashboard-assets README (removed surface); release-checklist step 3 (removed version mirror); root CLAUDE.md auto-merge recommendation superseded-pointer; CLAUDE.md wrong `generate-copilot-hooks.py` prefix | various |

Plugins bumped: `finance` 0.18.6→0.18.7, `esg-sustainability-reporting` 0.2.2→0.2.3,
`ravenclaude-core` 0.321.6→0.321.7, `edtech-partner-success` 0.12.8→0.12.9 (catalog synced; copilot
package regenerated).

---

## Needs design input / human decision (NOT auto-implemented)

### 1. [P1] `check-md-links.py` — a *required* CI gate is failing open

**Observation (verified this session).** `scripts/check-md-links.py` runs in `validate-marketplace.yml`
(a required check) and reports green, yet 6 markdown links in `plugins/ravenclaude-core/CLAUDE.md`
were genuinely broken (targets verified absent on disk; the current gate reported 0 broken). Two
mechanisms hide broken links:

1. **Unclosed-fence truncation.** `strip_code()` (lines ~127-137) removes balanced ` ``` ` fences,
   then treats the *first residual* ` ``` ` as an unclosed fence and truncates everything to EOF.
   CLAUDE.md has an inline ` ``` ` mention in prose at line 1009 (not a real fence — all 10 fenced
   blocks are balanced, verified by a line-based fence-state trace), which trips the heuristic and
   drops ~4000 lines (L1009→EOF) from checking. Measured blast radius across the whole tree: exactly
   2 real broken links hidden (`.ravenclaude/runs/source-control-coordinator/{strategic,build}-plan.md`).
2. **Inline-code link-text handling.** `INLINE_CODE_RE.sub("")` is applied to the whole text and can
   strip `[`code`](path)` link syntax depending on surrounding backtick parity, so links whose visible
   text is an inline-code span can escape checking (this is what hid the 4 archive-moved `plan.md`
   links).

**Why this is design input, not an auto-fix.** A correct fix needs a real CommonMark parser: every
regex variant tried this session (line-based fence tracking; no-truncation; inline-span skipping)
surfaced a *different* unstable subset of the true broken set. Rewriting a required gate whose new
blast radius is unpredictable — it will surface an unknown number of currently-hidden broken links
that must all be fixed to keep CI green — should be a reviewed change, not an autonomous one.
**Recommendation:** replace `strip_code`'s regex fence/inline handling with a minimal CommonMark
block scanner (or a vendored `markdown-it-py`/`mistune` tokenizer), add a must-fail fixture for each
hidden shape (inline-fence-in-prose, `[`code`](broken)`), then fix whatever links it surfaces in the
same PR. The 6 links this session found are already fixed in the PR, so the rewrite starts clean.

### 2. [P2] 38 domain anti-pattern hooks miss new-file `Write` / `Edit` payloads

`plugins/*/hooks/check-*-anti-patterns.sh` do `[ ! -f "$file" ] && exit 0` then grep the **on-disk**
file — so a `PreToolUse` `Write` creating a new file (which does not exist yet) surfaces no warning,
and an `Edit` greps pre-edit content. The payload-reading pattern already exists in
`plugins/data-platform/hooks/flag-data-platform-smells.sh:28-42` (reads `.tool_input.content` /
`.new_string` / `.edits[]`). **Design input:** these are advisory (`exit 0`) unless `*_STRICT=1`; the
fix makes them *newly block* new-file writes under STRICT — a deliberate behavior change across 38
security-relevant hooks (aws-cloud, gcp-cloud, security-engineering, auth-identity, …). Recommend
templating the payload-reading pattern and regenerating, gated on a yes for the STRICT behavior change.

### 3. [P2] Copilot projection ships dangling relative cross-references

`generate-copilot-plugin.py` copies agent cross-references (`../skills/…`, `../rules/…`, `../CLAUDE.md`)
verbatim into `plugins/ravenclaude-core/copilot/agents/`. Positive control this session: the identical
path `../skills/webfetch-hardening/SKILL.md` **resolves** from canonical `agents/` but is **missing**
from `copilot/agents/` (the sibling dirs don't exist under `copilot/`). The copilot `--check`
freshness gate compares regenerated bytes, so it never validates link targets. **Design input:** the
fix is a generator change — rewrite cross-refs to plugin-relative, strip them, or project the
referenced dirs. Pick one.

### 4. [P2] `orchestrator_scope: all` relay-all `claude -p` egress path ships without its security sign-off

`plugins/ravenclaude-core/CLAUDE.md:1279,1299` state the relay-all path (which egresses *every* prompt
to a second processor) is "pending a fresh `security-reviewer` sign-off." Off by default
(`orchestrator_scope: team`), so blast radius is capped, but the owed review is real. **Recommend:**
dispatch the security-reviewer pass; the verdict may require code changes.

### 5. [P2] `source-control-coordinator` active-mode precondition patch is staged but unapplied

`docs/pending-guard-destructive-merge-patch.md` holds a `guard-destructive.sh` merge-deny patch + two
`deny_patterns` that CLAUDE.md (v0.321.0) says "must land, alone, before the rest of this feature is
safe to enable anywhere as `active`." The agent + `/coordinate` command ship; the knob defaults `off`.
**Design input / high-blast:** applying a `guard-destructive.sh` change is the high-blast class this
repo defers to a human. Recommend applying the staged PR-1 patch + its 3-case fixture in a dedicated,
reviewed change.

### 6. [P2] Python secret-scrub pattern ports are hand-copied with no drift gate

`thing-denial-kb.py:127` and `precompact-digest.py:71` carry Python ports of `hooks/_scrub.sh`'s
`_secret_patterns` ("keep this copy in sync"); `pseudonymize-brief.py` carries a third. Gate 50 tests
only the bash `_scrub.sh`. The sets are currently identical, but a future pattern added to `_scrub.sh`
would not propagate to these egress paths, silently under-scrubbing with green CI. **Recommend:** a
gate that extracts and compares the pattern sets (or generate the Python from the bash). Low-risk to
add, but it is a new gate (design choice on shape) — flagged rather than slipped in.

### 7. [P3] `precompact-digest.py` broken-delegate observability hole

Per CLAUDE.md v0.314.0 §F5, a broken/absent cheap-lane delegate yields *neither* a digest *nor* an
audit event — silently indistinguishable from a healthy quiet session. The named fix (an additive
`allow / precompact-delegate-unavailable` receipt) is a documented deferral on a security-egress path.
**Recommend:** implement the additive audit-event branch.

### 8. [P3] `.ravenclaude/runs/…` links in CLAUDE.md — de-linked; consider promoting instead

The two de-linked references (strategic-plan.md / build-plan.md) point at gitignored local run
artifacts absent from any clone, so promotion was impossible without the content. If you still have
those plans in a session, consider promoting them to `docs/plans/` (committed) and restoring proper
links; otherwise the de-link stands.

---

## Explicitly checked and clean (honest coverage note)

Required-check `paths:` filters (correct — none on the 3 required workflows); GitHub Actions SHA-pinning
(100%); no `pull_request_target` / script injection; least-privilege workflow permissions;
`guard-destructive.sh` / `enforce-layout.sh` / `worktree-clean.sh` hardening; manifest drift (184==184,
0 version mismatch); agent frontmatter (0/622 missing `tools:`/over-300-char/missing scenarios); layout
globs (0/9518 fail); generator determinism (`sorted()`, no bare `except`, no mutable defaults);
denominator guards across 68 calculators; `serve-dashboards.py` CSRF/DNS-rebind guards.
