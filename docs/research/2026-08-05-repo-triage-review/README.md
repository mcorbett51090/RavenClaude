# Repository triage review — findings needing your decision (2026-08-05)

Automated three-panel expert review of the whole repo (scheduled routine). Panel 1 (5 parallel
finders, sonnet) scanned the real code surfaces; Panels 2–3 (verification + tie-break, opus) ran in
the main session, verifying each finding directly against the code.

**Every deterministic gate is green** — prettier, ruff, JSON-schema, layout (all 9,575 files),
frontmatter, model-id, md-links, marketplace-claims, and the **686-assertion `audit-gates.sh`
meta-test (0 fail, 0 skipped)**. So there are no format/lint/manifest defects. The findings below are
logic/consistency issues the gates structurally cannot see.

## What was already fixed autonomously (see the paired PR)

Mechanical, gate-safe fixes that touch **non-substrate** files were implemented and are in the PR:

| # | File | Fix |
|---|------|-----|
| HW1 | `scripts/ravenclaude` | Gemini install now **merges** hooks (preserves the user's own `hooks`, model, theme) instead of clobbering the whole `hooks` key. Verified with a synthetic-config test. |
| HW2 | `scripts/ravenclaude` | Codex/Cursor hook writes now disclose the overwrite (matching the Aider lane). |
| HW3 | `scripts/install-copilot-mcp.py` | Skip an already-configured MCP server instead of overwriting the user's hand-tuning (mirrors `install-codex-mcp.py`). |
| HW4 | `scripts/ravenclaude` | The suggested `alias rc=…` now quotes embedded paths, so a marketplace path with spaces survives paste. |
| AA2 | `README.md` | Corrected the stale `ravenclaude-core` component table (agents 14→15, skills 40→50, hooks 16→26, commands 7→8, added `/stream`). |
| AA3 | `scripts/rc-artifacts.py` | `--base` explicitness now tracked via `default=None` (the `== Path.cwd()` test silently ignored an explicit `--base "$PWD"`). |

> **Deliberately excluded from this PR:** the `README.md` fix (AA2) is a marketplace-meta doc, not a
> versioned plugin package, so no version bump. The one fix I prepared but did **not** include is **AA4**
> (`plugins/ravenclaude-core/bin/rc`) — it lives inside the versioned `ravenclaude-core` package, so
> shipping it warrants a semver bump + the generated-artifact regen cascade, disproportionate for a
> help-text fix in an unattended run. Ready patch below.

## Why the highest-value fixes are NOT in the PR — the Thing blocked them (correctly)

The tribunal's self-protection guard (`xc.tribunal-self-disable`) **hard-denies any edit to its own
substrate**: `plugins/ravenclaude-core/hooks/**`, `plugins/ravenclaude-core/scripts/**`,
`knowledge/concerns-catalog.md`, `scripts/generate-dashboards.py`, and `.ravenclaude/thing.yaml`.
Every fix below lives in that substrate. As an **unattended scheduled routine, I deliberately did not
disable or `dev_repo_exempt`-bypass a security control** to route around the guard — that is exactly
the action the guard exists to prevent an agent from taking, and it is a high-blast change that needs
your authorization.

**To apply the patches below yourself:** either edit the files directly, or set
`command_review.dev_repo_exempt: true` in `.ravenclaude/comfort-posture.yaml` (owner-gated; see the
v0.60.0 milestone in the plugin CLAUDE.md) for the session, then apply and turn it back off.

---

## P0/P1 — decision-review tribunal can bind a high-blast decision (patch ready)

**Finding DE1.** `plugins/ravenclaude-core/hooks/route-decision-review.sh:102-120`. The `header` and
option `description` fields are extracted (`:102-103`) but used **only** by the injection hardener
(`:181`). They are **not** folded into the deterministic high-blast scan (`hb`, `:113`) nor the
`context` sent to the engine (`:120`) — so both the shell high-blast belt-and-suspenders **and** the
engine's own `_screen_high_blast(question, context)` and every seat are blind to danger text that
lives only in `header`/`description`. The repo's own `skills/decision-review/SKILL.md` tells authors
to put the *consequence* in the option description — so a real `AskUserQuestion` (question "Proceed?",
options "Yes"/"No", danger in the description) can receive a **binding** yes/no, defeating the
documented "high-blast / irreversible decisions never auto-resolve" invariant.

- **Impact:** a security-relevant invariant bypass. Gated behind `decision_review: binding` (opt-in;
  this repo has it on) and a confident panel vote.
- **Effort:** S. The fix strictly *widens* what's treated as high-blast (more defers, never fewer
  allows) — it cannot make anything less safe. Verified gate-safe against Gate 31 (its fixtures carry
  no header/description and assert nothing on the `hb`/context values).
- **Recommendation:** apply. Ready patch:

```diff
 # --- 3. high-blast heuristic (engine also guards; belt + suspenders) ---
 hb=false
-if printf '%s %s %s' "$qtext" "$opt0" "$opt1" | grep -Eiq 'force[- ]?push|...'; then hb=true; fi
+if printf '%s %s %s %s %s' "$qtext" "$opt0" "$opt1" "${header:-}" "${description:-}" | grep -Eiq 'force[- ]?push|...'; then hb=true; fi
```
```diff
-req="$(jq -nc --arg q "$qtext" --arg c "Binary user prompt intercepted by route-decision-review. Options: [$opt0 | $opt1]. Auto-resolve only if rule/fact-derivable." --argjson hb "$hb" '{question:$q,context:$c,high_blast:$hb}' 2>/dev/null || echo '')"
+req="$(jq -nc --arg q "$qtext" --arg c "Binary user prompt intercepted by route-decision-review. Options: [$opt0 | $opt1]. Header: ${header:-}. Option details: ${description:-}. Auto-resolve only if rule/fact-derivable." --argjson hb "$hb" '{question:$q,context:$c,high_blast:$hb}' 2>/dev/null || echo '')"
```

---

## P1 — decision-review seats run sequentially but the caller budgets 80s (needs your call)

**Finding DE2.** `plugins/ravenclaude-core/scripts/thing-decide.py:666-672`. `decide()` runs the 3 (+1
tie-break) seats **sequentially**, each with a 45s (90s under `THING_HOST=copilot`) subprocess cap,
while the real-time caller `route-decision-review.sh:123` wraps the whole call in a fixed **80s**
timeout. Worst case (3×45=135s, or 180s with Thor; a single 90s seat under Copilot) exceeds 80s, so
every binding auto-resolution silently degrades to "ask the human" (the *safe* direction, but it
defeats the feature's purpose with no diagnostic).

- **Open question:** run the seats **concurrently** (ThreadPoolExecutor, bounded under the hook's 90s
  ceiling — mirrors `thing-orchestrator.sh`'s existing parallel fan-out), or have
  `route-decision-review.sh` derive its outer timeout from the resolved
  `seat_timeout_seconds`/`panel_deadline_seconds`? Concurrency is the real fix but changes the engine's
  execution model in a security-sensitive path.
- **Effort:** M. **Recommendation:** concurrent seats, matching the command-review orchestrator; needs
  a security-reviewer pass since it changes tribunal execution.

## P2 — thing-decide.py has no top-level contract guard (patch ready)

**Finding DE3.** `plugins/ravenclaude-core/scripts/thing-decide.py:804-811`. The docstring promises
"always exit 0 / one JSON object", and `main()` wraps stdin parsing — but the `decide(...)` call at
`:804` and the `__main__` dispatch have **no** surrounding try/except (unlike the sibling
`thing-denial-kb.py`). An unexpected exception inside `decide()` surfaces as a bare traceback + nonzero
exit; the `decision-review` skill's documented direct invocation has no `2>/dev/null || echo ''`
wrapper to catch it.

- **Effort:** S. **Recommendation:** apply. Wrap the `__main__` dispatch to print the standard defer
  JSON (`{"verdict":"defer","reasoning":"internal error: <class>","mode":"off","binding":false,"seats":[],"saga_log":null}`)
  and return 0 on any exception, exactly like `thing-denial-kb.py`'s guard.

## P3 — resolve_category can raise an uncaught TypeError (patch ready)

**Finding DE4.** `plugins/ravenclaude-core/scripts/apply-comfort-posture.py:517-520`. When a category
is a dict without a `default` key, `default = cat_value.get("default", global_default)` falls back to
the unvalidated `global_default`, then `if default not in VALID_LEVELS:` (a `set`) raises
`TypeError: unhashable type` if `global_default` is a YAML list/mapping (e.g. `global_default: [ask,
allow]`). `main()` only catches `ValueError`, so this crashes with a raw traceback instead of the
graceful "invalid comfort-posture" message.

- **Effort:** S. **Recommendation:** apply — `if not isinstance(default, str) or default not in
  VALID_LEVELS:` routes malformed input through the existing `ValueError` path.

---

## P1 — guard-destructive.sh RCE-guard gaps (security review needed)

Three findings in `plugins/ravenclaude-core/hooks/guard-destructive.sh`. All add/extend **deny**
patterns in the security floor — I've deliberately **not** auto-applied them: a false positive blocks
legitimate work and a false negative is a security gap, so a maintainer + `security-reviewer` should
own the exact regexes and confirm the gate fixtures.

- **GH1 (P1)** `:447,:453` — the curl/wget-pipe-to-interpreter deny alternation
  `([a-z]*sh|python[0-9.]*|perl|ruby|node)` is **narrower** than the file's own `_INTERP_BASE`
  (`:159-161`), which includes `php|tclsh|lua|Rscript|busybox`. So `curl … | php`, `curl … | lua`,
  `curl … | busybox sh` sail through. Also `curl … | xargs sh` (a token between the pipe and the
  interpreter) evades both. **Recommendation:** extend the alternation to match `_INTERP_BASE`.
- **GH2 (P1)** `:437-464` — no coverage for **download-then-execute** via `-o`/`-O` + `&&`/`;`
  (`curl -o /tmp/a.sh URL && bash /tmp/a.sh`). Only the pipe and heredoc forms are guarded.
  **Recommendation:** add a structural `_is_download_then_execute` check (finder supplied a draft
  regex) — but validate false positives (`curl -o out.json … && cat out.json` must stay allowed).
- **GH3 (P2)** `:415-432` — remote git-branch deletion (`git push origin --delete`, `-d`, `:branch`)
  is unguarded while the local `git branch -D` equivalent is thoroughly caught. **Recommendation:** add
  `_is_dangerous_git_push_delete` mirroring the existing local-delete check.

**Open question for all three:** confirm these are in-scope for the destructive-command floor (vs.
best-effort), then land them with matching `must_pass`/`must_fail` gate fixtures.

## P2 — worktree-guard block mode only treats git subcommands as mutating (needs your call)

**Finding GH4.** `plugins/ravenclaude-core/hooks/worktree-guard.sh:276-291` (`_wg_is_mutating`). In
`block` mode a raw Bash mutation (`rm -rf …`, `sed -i …`, `echo x > file`, `npm install`) is classified
**not mutating** and allowed, even though block mode exists to prevent tree collisions. Only the opt-in
`block` mode is affected (default is `warn`).

- **Open question (finder flagged `needs_design_input`):** should this collision-avoidance guard flag
  raw-Bash mutations (reusing `runaway-brake.sh`'s `is_read_only` allowlist), or is that left to
  `guard-destructive.sh` by design? Scope decision, not mechanical.

## P3 — guard-web-access.sh silently degrades when jq is absent (patch ready)

**Finding GH5.** `plugins/ravenclaude-core/hooks/guard-web-access.sh:56-64`. `tool`/`url` are extracted
via `jq -r` with no fallback; if `jq` is missing, `tool` stays empty, the hook `exit 0`s, and the
blacklist is never consulted — with no signal (unlike `guard-destructive.sh`, hardened to warn on this
exact case). **Recommendation:** mirror `guard-destructive.sh:71-73` — one stderr line noting the
web-access blacklist is degraded for this call. Observability only; no allow/deny decision changes.

---

## P1 — dashboard stat counts contradict the lists they label (needs your call)

Two findings in `scripts/generate-index-dashboard.py` (editable — NOT substrate — but routed here
because the fix embeds a product judgment and requires regenerating the freshness-gated
`index.html`/`dashboard.html`).

- **GEN1 (P1)** `:766` — `counts["templates"]` is a **recursive** file count (`_count_dir(…, "files")`)
  while the rendered Templates list (`_scan_templates`) is **top-level only**, so the same plugin shows
  e.g. `web-commerce` "64 templates" on the Resources page and 4 rows in its Templates tab (16×).
- **GEN2 (P2)** `:764` — `counts["hooks"]` globs every `*.sh` (33 for rc-core) including `_`-helpers and
  other-host adapters, while the hooks index counts only `hooks.json`-registered entries (26). Inflates
  the homepage "Active Hooks" tile (144→151 repo-wide).

- **Open question:** which number is canonical — align the **stat** to the rendered index
  (`len(templates_idx)` / `len(hooks_idx)`, the finder's recommendation, matching what the user can
  click), or keep the recursive count and expand the **rendered list**? Either resolves the
  contradiction; the first is a 2-line generator change + a full `index.html`/`dashboard.html` regen.
- **Recommendation:** align the stat to the rendered index (least surprising — the badge should match
  the list beside it), then regenerate and let the freshness gates confirm.

## P1 — Agentic Work-Streams classifier is permanently dead (needs your call)

**Finding AA1.** `plugins/ravenclaude-core/scripts/stream-*.py` + `hooks/stream-prompt-attribute.sh`.
Stream centroids are initialized `{}` and **never trained on any live path** — `set_centroid` /
`update_centroid` are called only from their own definitions and the gate scripts (which build
centroids synthetically). Every real `classify()` reads empty centroids → `_cosine` short-circuits to
`0.0` → `confident` is always `False`. So the SessionStart "SUGGESTED stream" line and `stream_classify:
auto` **can never fire for a real user**, contradicting the documented P2 milestone. Invisible to Gates
110/111/112 because they seed centroids synthetically and never drive the real hook chain end-to-end.

- **Open question (finder flagged `needs_design_input`):** wire centroid training into the live
  attribution path (`stream-prompt-attribute.sh` sticky + auto branches: after `append_event`, fold the
  prompt into the stream's centroid via `update_centroid` and persist with `set_centroid`), plus a new
  **end-to-end** gate that drives the real hook N times and asserts a subsequent confident classify.
  This is feature-completion work in a security-reviewed no-egress path (centroid persistence must keep
  the derived-features-only / no-raw-prompt invariant Gate 110 enforces), so it warrants your sign-off
  on the approach before build.

## P3 — bin/rc usage text malformed (patch ready — held for a version bump)

**Finding AA4.** `plugins/ravenclaude-core/bin/rc:43`. The `rc artifacts list|new <id>   where work
files go, across CLIs` line is wedged in the middle of the `rc streams` usage block, breaking the
grouping/alignment, and it is the only place `rc artifacts` is documented despite being a real verb.
Held out of the PR only because `bin/rc` is inside the versioned plugin package (see note above).

- **Effort:** S. **Recommendation:** move the `rc artifacts` line out of the streams block into its own
  entry and pad its description column, e.g. after `rc streams get-active`:
  `rc artifacts list|new <id>            Where work files go, across CLIs (list both tiers; new stamps a run dir).`

## Summary

- **In the PR (applied + verified):** HW1, HW2, HW3, HW4, AA2, AA3 — all gate-checked (686-assertion
  `audit-gates.sh` green, prettier, ruff, md-links, marketplace-claims).
- **Ready patches, need you to apply** (substrate-blocked by the Thing, or held for a version bump):
  DE1 (P0/P1), DE3 (P2), DE4 (P3), GH5 (P3), AA4 (P3).
- **Need a design decision before build:** DE2 (P1), GH1/GH2/GH3 (P1/P1/P2, security review),
  GH4 (P2), GEN1/GEN2 (P1/P2), AA1 (P1).

---

*Generated by the scheduled repository-triage routine. Auto-fixes are in the paired PR; the items above
need a human decision or are blocked by the tribunal's substrate self-protection.*
