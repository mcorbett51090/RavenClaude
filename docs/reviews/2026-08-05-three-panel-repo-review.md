# Three-panel repository review — 2026-08-05

Autonomous whole-repo review run as a scheduled routine. Three expert panels
(find → adversarially verify → analyze → tie-break) swept the ~60K-line automation
code surface — `scripts/`, `plugins/ravenclaude-core/` code, `.github/workflows/`,
and root config. **32 findings raised, 31 confirmed** after adversarial verification;
24 had their priority set by a Panel-3 tie-breaker.

All automated CI gates were **green before and after** the review (JSON, shell,
frontmatter, version-drift, layout across 8924 files, markdown links, prettier, ruff,
and every specialized checker). The findings below are the semantic issues the gates
don't see.

## What was fixed in the accompanying PR

Every confirmed finding whose fix needs **no design decision** and does not require a
full portal regeneration was implemented and verified. Grouped by priority:

### P0 — security-critical (all fixed)

| Finding | File | Fix |
|---|---|---|
| Tribunal's category-independent hard-rule/self-disable screen never decoded base64, so an obfuscated `curl\|sh` / force-push / self-disable command classifying to `None`/an untoggled category bypassed the screen entirely | `plugins/ravenclaude-core/scripts/thing-concerns.py` | `screen_always()` now scans the base64-decoded forms of the command (shared `_iter_decoded_texts` generator; `evaluate()` path unchanged). Repro confirmed: base64'd `curl\|sh` now denied, benign untouched. |
| Binding decision-review verdicts never saw the AskUserQuestion `header`/option `description`, so a high-blast decision stating its stakes there (e.g. a `git push --force` in the header, bland "Continue?" question) could auto-resolve without the human ever being asked | `plugins/ravenclaude-core/hooks/route-decision-review.sh` | `header` + `description` now feed both the local high-blast grep and the engine `context` (size-capped). The §4a injection-echo hardener already treats them as untrusted, so the defense isn't weakened. |
| `guard-destructive.sh` had no deny for remote-branch deletion (`git push <remote> --delete <ref>` / `git push <remote> :<ref>`) — an always-on guard whose stated scope is "git history / branch destruction" | `plugins/ravenclaude-core/hooks/guard-destructive.sh` | New order-independent `_is_dangerous_git_push_delete` helper (flag + colon-refspec forms) + audit-gates fixtures. Sanctioned escape hatch (`archive-branch.sh`, run as a subprocess) is unaffected. |

### P1 — high (all non-design fixed)

- **`guard-destructive.sh`** — `git clean -d -f` (separated-token force flag) bypassed the contiguous-anchor regex. Replaced with order-independent `_is_dangerous_git_clean` + fixtures.
- **`capability-orientation.py`** — the SessionStart banner inlined raw `settings.json` permission-rule strings, so a committed rule containing a newline + `</ravenclaude-capabilities>` could break the untrusted-data frame. All rules now routed through `_sanitize_banner_field`.
- **`rc-deep-research.js`** (both byte-identical copies) — the Verify-phase adversarial `agent()` calls lacked the `.catch()` the search/fetch phases already carry, so one rejected verifier vote crashed the whole run. Guards added; the copied dispatch-evaluator block (Gate 52) is untouched.
- **`two-panel-plan-review.js`** — Panel 1 / Panel 2 lens fan-outs lacked per-agent `.catch()`; one failed lens aborted the whole review. Guards added.
- **`brand-extraction/extract_brand.py`** — fetched site title/`og:site_name`/URL written unescaped into the generated HTML report (stored XSS); font-family names written unescaped into CSS. Now `html.escape`d, and font names stripped of CSS-breakout chars.
- **`svg-report-lint/lint.py` + `declarative-visualization/lint.py`** — the remote-href "security floor" missed protocol-relative URLs (`//host/x.svg`) and control-char-split schemes (`jav&#9;ascript:`). Both patterns now flag `//` and strip tab/CR/LF before scheme-matching.
- **`visual-feedback-loop/driver.py`** — path guard used `abspath` (not `realpath`), diverging from the sandbox parity it claims with the layout linter, allowing a symlink escape. Now `realpath` on both sides; verified a symlink to an out-of-repo file is rejected.
- **`content-scan.py`** — `fetch_body_excerpt()` validated only the initial and final redirect hop, so an intermediate 3xx could land the fetch on a NEVER_FETCH host (LinkedIn/Reddit) or an internal SSRF target. Now a `_GuardedRedirectHandler` re-screens scheme + never-fetch + host-public on every hop.

### P2 / P3 — medium/low (non-design, fixed)

- **`generate-bi-report.py`** — HTML attribute-name injection via an unsanitized column `key`. Keys now constrained to a safe identifier grammar; all shipped keys already comply, so `report.html` output is byte-identical (freshness gate green).
- **`capability-orientation.py`** — the banner unioned project+local permission buckets without deny>ask>allow precedence, so a rule could show under both "allow" and "deny". Now reconciled to one effective bucket.
- **`check-lineup-citations.py`** — the context-window regex missed raw-digit token counts (`1,000,000 tokens`), silently passing uncited stale facts. Broadened; K/M forms kept, benign numbers (dates, versions, ports) not flagged.
- **`thing-seat.sh` + `claude-orchestrate.sh`** — the inline secret-scrub fallback arrays were stale vs canonical `_scrub.sh` (missing `rk_live_`/`npm_`/`hf_`/`AccountKey=`/embedded-cred-URL, loose JWT/`-p`). Re-synced byte-for-byte.
- **`pbir-layout-engine/lint.py`** — `check_column_alignment` ignored the caller's tolerance when grouping rows (hardcoded 1px). Now uses `max(tolerance, 1)` like the sibling `check_equal_gap`.
- **`.repo-layout.json`** — added the documented `task-scope.json` / `self-heal-setup.md` feature files (the hook was self-denying them in this repo); removed three redundant globs subsumed by broader parents.
- **`regenerate-artifacts.yml`** — the post-merge self-heal pushes to `main` with double `[skip ci]`, bypassing all layout/link CI. Step 4f now also runs a layout allow-list check (inline, covers untracked new artifacts) and `check-md-links.py`, aborting the push on failure.
- **`check-run-actions-argv.py`** — the gate never asserted `argv` length ≥ 2, but `serve-dashboards.py` indexes `argv[1]` unconditionally. Length check added.
- **`cleanup-branches.sh`** — the deletion loop never re-verified the branch tip against the safety verdict (TOCTOU). Now records the verdict-time tip and refuses to delete if the tip moved.
- **`content-scan.py`** — `search()` lacked the `JSONDecodeError` guard its sibling `reddit-scan.py` carries (a 2xx non-JSON body crashed with a raw traceback). Added.

---

## 👉 Needs your input — items deliberately NOT auto-merged

These are the confirmed findings the panels flagged `needs_design_input`, plus three
that would require regenerating large committed artifacts or a big test harness and
so warrant their own reviewed change. Each has a concrete recommendation.

### 1. `serve-dashboards.py` static handler serves the entire repo tree (P1 — security)

**File:** `plugins/ravenclaude-core/scripts/serve-dashboards.py` (~L1387; both server copies)
The dynamic `/__*` endpoints are Origin/Host/CSRF-guarded, but the fallthrough to
`SimpleHTTPRequestHandler` serves any path under the repo root **with directory
listing on** — including `.git/` (full history → any secret ever committed) and the
`.ravenclaude/*` config the `/__read` allow-list was built to restrict. Confirmed
live: `GET /.git/config` and `GET /.ravenclaude/comfort-posture.yaml` return 200.

**Why not auto-merged:** the default bind is `127.0.0.1` (loopback), so this is **not
exploitable in the default posture** — it requires an explicit `--bind 0.0.0.0` or a
Public Codespace port. And it changes the security boundary of a 2000-line server with
a byte-identical-parity gate across two copies — exactly the kind of structural
security change the repo's own `design_checkins` discipline says to surface.

**Recommended fix (I can apply on your go-ahead):** override `translate_path`
(or `list_directory`) to refuse `.git`, `.ravenclaude`, and dotfile prefixes and
disable directory listing — a strictly-safer floor that doesn't change legitimate
dashboard serving — mirrored byte-identically in both server copies, plus update the
printed security note to disclose the full-tree exposure when bound off-loopback.
**Decision needed:** denylist-in-`translate_path` (my recommendation) vs. routing all
static serving through the `_local_request_ok()` Origin/Host check.

### 2. Decision-tally Thor-convene guards Heimdall (injection seat) but not Forseti (risk seat) (P2)

**File:** `plugins/ravenclaude-core/scripts/thing-decide.py` (`_tally`, ~L579)
If exactly one seat abstains and it's **Forseti** (the sole risk/security seat), no
Thor convene is forced and a binding yes/no can return with zero risk-focused review.
The mirror-image Heimdall-abstain case *is* guarded.
**Recommendation:** compute `forseti_abstained` and add it to the Thor-convene
condition, extending Thor's brief to re-assess reversibility when standing in for
Forseti. **Design call:** whether Forseti-absence should force a *convene* or a
*defer* — the repo rated the symmetric Heimdall bug P2, so this is a genuine
preference about risk-seat integrity.

### 3. `_HIGH_BLAST_RE` misses common destructive verbs (P3)

**File:** `plugins/ravenclaude-core/scripts/thing-decide.py` (~L71) + shell twin
`route-decision-review.sh` (~L100)
The deterministic high-blast floor omits `overwrite`, `terminate`, `disable`,
`uninstall`, `downgrade`, `rollback`, `grant admin`, `elevate`. It can only *add* a
defer, so the gap is defense-in-depth (Forseti's LLM seat is the primary defense).
**Recommendation:** extend the alternation in both files. **Design call:** the exact
verb list is a judgment about false-positive tolerance vs. coverage.

### 4. `rc-deep-research.js` MAX_FETCH budget bypassed for all "high"-relevance results (P2)

**File:** `plugins/ravenclaude-core/skills/rc-deep-research/rc-deep-research.js` (~L921, both copies)
`if (fetchSlots <= 0 && relRank[r.relevance] >= 1)` never fires for `high`
(`relRank.high === 0`), so high-relevance sources always bypass the `MAX_FETCH`
budget — up to ~2× the configured cap. Cost/latency only, no correctness impact.
**Design call:** is preserving high-relevance sources over budget *intentional*? If
yes, cap the overflow explicitly (`fetchSlots > -N`) with a comment; if no, drop the
`relRank >= 1` carve-out. Either is a one-liner, but the intent is the design question.

### 5. `archive-branch.sh` — `--skip-push` + `--delete-remote` breaks the "recoverable forever" guarantee (P2)

**File:** `scripts/archive-branch.sh` (~L268)
Combining both flags creates the archive tag **locally only**, then deletes both the
local and remote branch — so a later clone loss permanently loses the work the tag was
meant to preserve.
**Recommendation:** refuse the flag combination, or force a tag push before any remote
delete regardless of `--skip-push`. **Design call:** hard-refuse vs. gate behind an
explicit `--yes-i-know-this-is-unrecoverable`.

### 6. Full "Plugins" tab rebuilt uncached per schema-bearing plugin (P3 — perf landmine)

**File:** `scripts/generate-dashboards.py` (`_page_kwargs`, ~L178)
`_render_plugins_category(_all_plugin_dirs())` walks all 164 plugins with no caching,
once per schema-bearing plugin. Only `ravenclaude-core` ships a dashboard schema today,
so cost is a one-time ~420KB embed — but a second schema-bearing plugin makes generator
cost and artifact size scale O(P·S) with no CI signal.
**Recommendation:** compute the plugins category once in `main()` and thread it through,
or `functools.lru_cache` on the sorted plugin-dir tuple. **Design call:** whether to
invest now (pre-emptive) or add a CI size-guard and defer until a second schema appears.

### Also deferred (mechanical, but out of scope for an auto-merge)

- **`_index_dashboard_template.py` esc()-into-`onclick` idiom (P3).** Not exploitable
  today (values are on-disk plugin dir names), but the wrong escaping primitive for a
  JS-string sink. Fixing it changes the generated 10 MB `index.html` and would need a
  full portal regeneration (mermaid/Chromium) + re-verification of the render/router
  gates — best done as its own change. **Recommendation:** migrate to the `data-*` +
  delegated-`addEventListener` pattern already used in `generate-dashboards.py`.
- **`audit-gates.sh` has no fixture coverage for `archive-branch.sh` / `cleanup-branches.sh` (P2).**
  These are the repo's only destructive-git scripts and two prior reviews found real
  data-loss bugs in them via manual review alone. Adding a fixture harness that safely
  exercises tag-then-delete / tip-matching against throwaway repos is a substantial
  test-authoring task worth its own PR. **Recommendation:** add
  `test-archive-branch.sh` / `test-cleanup-branches.sh` invoked from `audit-gates.sh`.
- **`regenerate-artifacts.yml` self-heal PR has no `add-paths` scoping (P3).** The
  self-heal legitimately touches a broad, partly-dynamic set (including README/CLAUDE
  count rewrites), so a hand-written `add-paths` list risks silently dropping real drift
  — worse than the current state. Step 4f now validates every changed file (JSON +
  prettier + layout + links), which covers the actual risk. Revisit if the artifact set
  is ever enumerated authoritatively.
