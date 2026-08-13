# Repository review — 2026-08-05 (autonomous three-panel + implementation)

**Run shape:** Panel 1 (six partitioned `sonnet` finder agents, high effort) → Panel 2/3
(adversarial verification + priority validation by the `opus` orchestrator, each finding
re-read against the real code and, where a hook/regex was involved, empirically reproduced)
→ implementation of the confirmed non-design fixes on `claude/stoic-fermat-w2gcma`.

## Mechanical health (pre-review sweep) — all green

Every CI gate passed on the tree at `3a0106f` before the semantic review began, so all
findings below are logic/robustness defects the structural gates cannot catch:

- JSON validity (marketplace / all 166 `plugin.json` / repo-layout): OK
- `check-frontmatter.py`, `check-marketplace-claims.py`, `check-layout.py --all`,
  `check-md-links.py`, `check-mcp-attribution.py`, `check-grep-ere-pcre.py`,
  `check-hook-stdin-fallback.py`: OK
- `prettier@3.9.4 --check .` (whole tree): exit 0 · `ruff check .`: passed
- Version drift (166 marketplace entries vs `plugin.json`): none
- TODO/FIXME/HACK markers in code: all in vendored `mermaid.min.js`, test fixtures, or
  intentional anti-pattern grep strings — no real debt markers.

## Scope reviewed

~40 logic/safety scripts across six partitions: security/safety shell hooks, the tribunal
decision engine, comfort-posture + capability + web-sanitize, pseudonymize + streams, the
CI gate scripts, and the repo-root shell utilities. The ~11K-line generated dashboard,
vendored code, and per-plugin markdown were out of scope (generated/tested elsewhere).

## Confirmed findings & disposition

Panel 1 raised 25 candidate findings; Panel 2/3 confirmed 20 (5 were rejected as
false-positives — already-guarded paths, misread line numbers, or harmless). Of the 20
confirmed, **17 were mechanical and are fixed in this PR**; **3 need design input** and are
written up in [`2026-08-05-repo-review-design-questions.md`](2026-08-05-repo-review-design-questions.md).

### Fixed in this PR (grouped by priority)

**P1 — correctness / security / data-loss**

| # | File:line | Defect |
|---|---|---|
| 1 | `scripts/archive-branch.sh:268` | `--skip-push --delete-remote` deleted the remote branch while the archive tag was local-only (never pushed) → unrecoverable work when an ephemeral session is reclaimed. Now refused. |
| 2 | `plugins/ravenclaude-core/scripts/pseudonymize-brief.py:77` | IBAN regex matched only the compact form; a standard space-grouped IBAN leaked verbatim through the pseudonymizer (PII egress). Now tokenized; self-test fixture added. |
| 3 | `plugins/ravenclaude-core/scripts/capability-orientation.py:651` | `.claude/settings.json` permission-rule strings were echoed into the SessionStart banner **unsanitized**, so a hostile/cloned repo could break the untrusted-data frame and inject a fake `<system-reminder>`. Now frame-break sanitized like every other field. |
| 4 | `plugins/ravenclaude-core/scripts/capability-orientation.py:730` | `last_posture` (`ts` from `posture-events.jsonl`) inlined into the banner unsanitized — same frame-break class. Now sanitized. |
| 5 | `plugins/ravenclaude-core/scripts/thing-decide.py:437` | `_parse_seat` called `.strip()` on a non-string seat `result`, raising an uncaught `AttributeError` that crashes the panel (and fails **open** for decision-review). Now returns the fail-safe ABSTAIN. |
| 6 | `plugins/ravenclaude-core/hooks/guard-destructive.sh:359` | `rm -rf ../../` (and deeper) bypassed the guard — only a single `../` segment was matched. Now catches any multi-segment nav; scoped paths still allowed. |
| 7 | `plugins/ravenclaude-core/hooks/guard-destructive.sh:370` | `chmod -R 4777/2777/6777/1777` (setuid/setgid/sticky + world-writable) bypassed while `777` was caught. Now caught. |
| 8 | `plugins/ravenclaude-core/hooks/dod-gate.sh:122` | `sha256sum` is absent on stock macOS → every cmd hashed to the literal `"nohash"`, so one confirmation authorized any later (incl. swapped) command. Now falls back `sha256sum → shasum -a 256 → cksum`; Linux tokens unchanged. |
| 9 | `plugins/ravenclaude-core/hooks/guard-web-access.sh:107` | A multi-line YAML flow array (`deny: [\n …\n]`) parsed to zero entries → silently empties the blacklist (fail-open). Now accumulated across lines. |

**P2 — edge-case bugs / robustness**

| # | File:line | Defect |
|---|---|---|
| 10 | `scripts/check-frontmatter.py:168` | `tools in (None, "", [], {})` let `tools: false` / `tools: " "` bypass the least-privilege gate (`False`/whitespace ∉ the tuple). New `_is_blank()` helper used at all three sites (tools/audience/works_with/quickstart). |
| 11 | `plugins/ravenclaude-core/scripts/apply-comfort-posture.py:333` | `parse_yaml` returned a top-level list/scalar unchanged → raw `AttributeError` traceback downstream. Now raises a clean `ValueError`. |
| 12 | `plugins/ravenclaude-core/hooks/guard-web-access.sh:124` | A trailing `# comment` on a block-style deny entry corrupted the host string, silently disabling that entry. Now stripped. |
| 13 | `plugins/ravenclaude-core/scripts/stream-ops.py:166` | `read_registry` didn't validate each per-stream value is a dict; a malformed entry crashed every reader (`list_streams`/`get_centroids`/`append_event`), violating the "never raise" contract. Malformed entries now dropped. |
| 14 | `plugins/ravenclaude-core/scripts/pseudonymize.py:273` | Surrogate collision guard compared a multi-word candidate against a set of single words → the FM4 "surrogate ≠ any input word" guarantee never fired. Now checks each constituent word. |

**P3 — latent hardening**

| # | File:line | Defect |
|---|---|---|
| 15 | `scripts/check-frontmatter.py:134` | Flat-file skill/agent/command globs didn't exclude `README/CHANGELOG/NOTES` like the sibling `check-marketplace-claims.py` does — a roster README would hard-fail the gate. Now excluded. |
| 16 | `scripts/worktree-new.sh:49` | Unvalidated `BASE_REF` passed with no `--` separator; a flag-shaped ref (`--no-checkout`) silently produced an empty worktree. Now `--`-separated (rejected loudly). |
| 17 | `plugins/ravenclaude-core/scripts/capability-orientation.py` | No size cap on the repo-controlled `environment-context.md` / `run-config.json` read+scanned every SessionStart. Added a 256 KiB cap mirroring `_POSTURE_MAX_BYTES`. |

### Verification

Each hook/regex fix was empirically reproduced before and after (guard-destructive rm/chmod
tables, web-access parser on 4 config forms, dod-gate hash under a `sha256sum`-less PATH,
worktree `--` rejection). Python fixes carry unit checks (`_is_blank` matrix, `parse_yaml`
non-mapping, pseudonymize self-tests incl. the new IBAN fixture, stream-ops malformed
registry). Full local suite green: shell `bash -n`, `ruff`, `prettier --check .`,
`check-frontmatter/md-links/marketplace-claims/layout`, and `audit-gates.sh`.

## Secondary observation (no code change)

The two `docs/follow-ups/` parked-work items have **re-check dates now in the past**
(2026-06-18 and 2026-07-16, vs today 2026-08-05). They are multi-session design workflows,
not review findings — flagged for the maintainer to re-park or close.
