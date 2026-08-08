# Autonomous repository review — 2026-08-08

Scheduled multi-panel review of the RavenClaude marketplace. Method: five parallel
expert reviewers (Panel 1) over the executable code, adversarial validation of each
finding (Panel 2), and inline tie-break on ambiguous priorities (Panel 3). Scope was
deliberately the **executable logic** (Python scripts, shell hooks, `.mjs` gate checks)
— where gate-invisible bugs live — not the 7,300+ markdown content files.

## Repository health baseline (all green)

- `audit-gates.sh` meta-test: **690 pass, 0 fail, 0 skipped** (every gate bidirectionally verified).
- No plugin version drift across all 180 plugins; every `plugin.json` valid against its JSON schema; `marketplace.json` valid.
- Every standalone CI gate passes (frontmatter, layout, model-ids, marketplace-claims, storage-contract, host-support, md-links, generated-headers, grep-ere-pcre).

The reviewers found no defect in the CI infrastructure itself. All findings are logic/safety
bugs in the executable code that the gates do not (and mostly cannot) see.

## Implemented in the accompanying PR (non-substrate, safe to auto-apply)

Sorted by priority. All verified (self-tests / gate runs / functional runs pass).

| Pri | File | Fix |
|---|---|---|
| P2 | `scripts/check-model-ids.py` | Gate 134's `MODEL_RE` could not match legacy numeric-first ids (`claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`) — a stale legacy id in a governed file would pass unchecked. Widened the alternation to accept the numeric-first family shape and added both directions to `--self-test`. Full gate still clean against the tree. |
| P2 | `scripts/check-generated-headers.py` + `scripts/generate-feedback-report.py` | Gate 173's `GENERATED_PREFIXES` omitted two tracked generator outputs (`docs/concepts.md`, `feedback-report.html`), so its "all N generated files declare themselves" claim was false for them. `feedback-report.html`'s only marker was a footer (line 712), **outside** the gate's 1500-byte head window — so adding it naively would have *broken* the gate. Added a top-of-file generated marker in the generator, regenerated the report, then added both files to the prefix list. Gate now covers 38 files (was 36); teeth intact. |
| P3 | `scripts/eval-adaptive-classifier.py` | Five `Path.write_text()` calls (incl. the Unicode-bearing eval report) lacked `encoding="utf-8"`, risking `UnicodeEncodeError` on a non-UTF-8 host — inconsistent with the codebase's own portability discipline. Added the explicit encoding. Self-test passes. |
| P2 | `scripts/notify.sh` | On stock macOS (no GNU `timeout`) the no-arg stdin drain fell back to an **unbounded** `cat`, contradicting the script's own "must never block" invariant. Now sources the shared `_portable.sh` and uses `_rc_timeout` (timeout → gtimeout → perl alarm → unbounded), with a fail-safe stub if the helper is absent. Verified across arg / stdin / empty / no-`timeout`-on-PATH paths. |
| P2 | `scripts/check-checkout-fresh.sh` | Same door-2 gap: the `git fetch` ran unbounded where `timeout` is absent, contradicting the documented "must never block" guarantee. Now bounded via `_rc_timeout`. |
| P3 | `scripts/open-dashboard.sh` | The browser-open fallback ran a bare `timeout`, which on stock macOS is command-not-found and silently swallowed by `|| true` — the browser never opened, with no error. Now uses `_rc_timeout`. |

## BLOCKED — require maintainer action (Thing substrate; could not be auto-applied)

Every finding below is in the command-review tribunal's own **substrate**
(`plugins/ravenclaude-core/hooks/**`, `plugins/ravenclaude-core/scripts/**`, and
`scripts/generate-dashboards.py`). The `always_screen` self-protection guard denies any
Write/Edit to these paths **category-independently**, even with `command_review.enabled: false`.
The maintainer-substrate exemption did not fire this session because it requires the `gh`
CLI to confirm repo ownership and **`gh` is absent in this remote environment**.

**How to apply them:** a local dev session where `gh` is authenticated as the repo owner
(`mcorbett51090/RavenClaude`) activates `dev_repo_exempt` and permits these edits; or apply
them through the dashboard. Each is a verified, mostly-mechanical fix — the reviewers
reproduced each by executing the real code.

### P0

- **Gemini and Cursor hook adapters silently discard every JSON-based DENY.**
  `plugins/ravenclaude-core/hooks/gemini-hook-adapter.sh:120-127` and
  `plugins/ravenclaude-core/hooks/cursor-hook-adapter.sh:132-142` classify a wrapped hook's
  verdict by its **raw exit code only**, after redirecting the hook's stdout to `/dev/null`.
  But the command-review tribunal (`thing-orchestrator.sh`) and `route-decision-review.sh`
  signal *every* verdict — including deny — via `hookSpecificOutput.permissionDecision` JSON
  on stdout while exiting 0. So for any consumer running under Gemini CLI or Cursor with the
  tribunal toggled on, **every panel deny, every hard-rule deny (protected-branch force
  pushes, piped-installer commands), and the self-disable guard degrade to a silent ALLOW.**
  The first-use "ask" of the web-access guard degrades the same way.
  *Recommended fix (needs a design nod, pattern already exists):* mirror
  `copilot-hook-adapter.sh:164-174` — capture the wrapped hook's stdout, read
  `.hookSpecificOutput.permissionDecision`, and translate deny/ask into each host's real
  blocking mechanism instead of trusting the exit code. Cursor's stated "fail-open on
  malformed JSON" constraint means the deny translation must stay fixed-literal.

### P1

- **Classifier evades categorization for absolute-path-wrapped commands.**
  `plugins/ravenclaude-core/scripts/thing-decision.py:171-197` (`_normalize_lead`). The
  wrapper-stripping loop only matches a wrapper token when it is literally first; the
  absolute-path→basename resolution runs once *after* the loop, so a wrapper hidden behind an
  absolute path is never stripped. A privileged command invoked via its absolute path
  classifies as `None`, and per-category concern/panel review is skipped for that shape
  (the `always_screen` hard rules still fire). `thing-concerns.py`'s sibling `_normalize_for_match`
  has the same structural gap (lower impact — it unions the raw command with unanchored search).
  *Fix:* fold basename resolution into the wrapper-strip loop (or re-run the wrapper regexes
  after basename resolution). **This is a security control — run gates 14/15/22/24 after.**
- **Web-fetch sanitizer nested-decoy bypass on two of four paired patterns.**
  `plugins/ravenclaude-core/scripts/sanitize-webfetch-body.py:99` and `:104` still use a lazy
  `.*?` where the paired patterns 1 and 2 were deliberately changed to greedy `.*` to close a
  nested-decoy bypass. A nested `<important>…<important>…real payload…</important>…</important>`
  (and the fenced-`system` equivalent) leaves the real payload unwrapped in the output.
  *Fix:* change `.*?` → `.*` on both lines (same technique, same accepted trade-off already
  documented for patterns 1 and 2).
- **The unescaped-payload latent bug (Gate-invisible full-page corruption).**
  `scripts/generate-dashboards.py:250/264/275` (`learn_json`, `commands_json`, `trees_json`)
  and `:7958` (host-support payload) splice `json.dumps(...)` into
  `<script type="application/json">` blocks **without** the `.replace("<", "\\u003c")` escape
  that the four sibling payloads three lines later apply, and that the file's own comment
  mandates generically. Not broken today (no current content spells the closing-script
  sequence), but any concept SVG / knowledge string / best-practice preview that reaches these
  four payloads and contains a literal `</script>` will close the element early and turn the
  rest of `dashboard.html` / `index.html` into parsed markup. *Fix:* add
  `.replace("<", "\\u003c")` to the four sites, then regenerate `dashboard.html` + `index.html`.
  (`generate-dashboards.py` is substrate, which is why this could not be auto-applied.)

### P2

- **`apply-comfort-posture.py` raw traceback on a malformed `categories:` field.**
  `:562/:565`, `:682/:686-687`, `:734/:736` — `categories` is never validated as a mapping,
  so `categories: somestring` raises an unhandled `AttributeError` (every other malformed
  shape raises a clean `ValueError`). Reachable from the dashboard's Save & apply.
  *Fix:* add an `isinstance(categories, dict)` check → `ValueError` at the three sites.
- **`thing-denial-kb.py` collapses distinct non-Bash denials into one KB entry.**
  `:175-195` (`_event_from_command`, `:181`) assumes a `command` key, but non-Bash tool shapes
  carry `file_path` / `url` / `name`. All such denials collapse to the signature
  `<category>:<category>` and overwrite each other — defeating the KB for 6 of the 12 posture
  categories. *Fix:* extract the per-shape identifying field the way `saga_tool_input()` does.
- **`remind-tests.sh` undercounts changed source files.** `:19-22` parses `git status --porcelain`'s
  `$2` field, which breaks on paths with spaces and rename lines — the exact bug `dod-gate.sh`
  already fixed and documented. *Fix:* port `--porcelain=v1 -z | tr '\0' '\n' | grep -cE`.
- **`worktree-guard.sh` mutating-op classifier is a naive substring match.** `:290-306` — an
  unanchored, unnormalized substring test both false-negatives (extra whitespace/tab bypasses
  the block) and false-positives (a read-only command mentioning a git verb gets blocked).
  *Fix:* normalize whitespace and token-anchor, as `guard-destructive.sh` already does.
- **Stale fallback secret-pattern arrays.** `thing-seat.sh:86-101` and
  `claude-orchestrate.sh:128-143` carry inline fallback copies of `_scrub.sh`'s pattern set
  for use if the sourced helper is missing; both are stale (missing several newer secret
  shapes). If `_scrub.sh` ever fails to source, the egress backstop silently degrades.
  *Fix:* regenerate both from `_scrub.sh`, or fail closed rather than degrade.
- **`forge-worktree.sh` `_receipt()` emits unescaped JSON.** `:38-42`, `:199-239` — the
  free-form checkpoint label is only newline-stripped, never quote/backslash-escaped, so a
  label containing a quote produces malformed JSON. *Fix:* build the receipt with `jq -cn --arg`.

### P3

- **`agent-dispatch-evaluator.sh` uses an unsanitized session id in a filesystem path.**
  `:156-158` — every sibling hook sanitizes `CLAUDE_SESSION_ID` before using it as a path
  component; this one does not. Low reachability today. *Fix:* source `_emit-event.sh`'s
  `_ee_sanitize_session` (or duplicate the stub) and sanitize before building the path.
- **`guard-web-access.sh` host extraction breaks on bracketed IPv6-literal URLs with a port.**
  `:67-71` (mirrored in `mark-web-domain-seen.sh:76-80`) — the `%%:*` port-strip truncates a
  bracketed IPv6 literal to `[`, so such hosts silently bypass the allow/deny lists.
  *Fix (needs-design):* use an IPv6-aware URL parser (e.g. `urllib.parse.urlsplit`).

## Design-input / judgment items (not mechanical)

- **`audit-gates.sh --fix` residue restore** (`scripts/audit-gates.sh:1180-1205`, non-substrate
  but a judgment call): the per-file restore skips a file that was already dirty before the
  test, so a `--fix`-induced edit to that same file can be left in the working tree. True
  isolation would need hunk-level diffing or a worktree copy — a larger change than a one-liner.
  Left for a design decision.

## Notes

- Two low-severity items were observed but not filed: `reset-plugin-cache.py:180-183` leaves an
  orphaned snapshot dir on a failed initial copy; `capability-orientation.py:888-889` overshoots
  its truncation cap by ~19 chars (harmless).
- The reviewers read ~30 other Python gates, all 20 `.mjs` render gates, and the destructive
  git scripts in full and found them unusually well-hardened (bidirectional teeth, CSRF/traversal
  guards, SHA-guarded branch deletes) — no confirmed defects there.
