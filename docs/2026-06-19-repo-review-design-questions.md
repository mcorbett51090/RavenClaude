# Repository review — issues needing design input (2026-06-19)

A comprehensive three-panel repository review ran on 2026-06-19 (expert review →
priority validation → tie-break). All standard CI gates were green; the deeper
review found a small set of genuine issues. The **autonomously-implementable**
fixes shipped in the accompanying PR (decision-review option-polarity guard,
`archive-branch.sh` base-branch resolution, the two-panel lens-label fix, the
broadened high-blast heuristic, the `check-md-links.py` read guard, and the
stale `feedback-report.html` regeneration — see `plugins/ravenclaude-core/CHANGELOG.md`
`0.157.1`).

This document captures the issues that were **deliberately not** implemented
autonomously because they involve a security/UX trade-off, an engine-contract
change, or a substrate decision that wants your call. Each has a recommendation.

---

## 1. `guard-web-access.sh` — "seen" marker written before consent (P2, security UX)

**Code:** [`plugins/ravenclaude-core/hooks/guard-web-access.sh:141-156`](../plugins/ravenclaude-core/hooks/guard-web-access.sh)

**The bug.** On the first WebFetch to a YAML-whitelisted domain the hook `touch`es
the per-session `seen_file` **before** it emits `permissionDecision: ask`. The
seen-file is the only "already prompted this session" gate. If the user answers
the `ask` with **deny/no**, the fetch is blocked — but the seen-file now exists,
so the **next** WebFetch to the same domain hits the silent-allow branch and
proceeds **without any prompt**. This inverts the control the comment at lines
107-111 says it exists for ("a hostile YAML edit … silently auto-allow
exfiltration"). A PreToolUse hook structurally cannot see the user's answer, so
recording "seen" before the answer is the wrong order.

**Why it's deferred.** The fix is a genuine product trade-off, not a mechanical
correction:

- **Option A — re-prompt every time** (drop the pre-`touch` and the silent-allow).
  Strictly fail-safe, but it removes the "ask once per session" ergonomic that is
  the feature's whole point — every fetch to a whitelisted-but-unconfirmed domain
  re-prompts.
- **Option B — record consent in a PostToolUse hook** that fires only when the
  fetch actually proceeded. Preserves "ask once," correctly gated on a real
  allow, but adds a new hook registration in all three wiring paths
  (`hooks.json`, the dev-mirror `.claude/settings.json`, and the Copilot adapter).

**Recommendation:** Option B — it keeps the ergonomic and closes the hole, at the
cost of one new (small) PostToolUse hook. If you'd rather not add a hook, Option A
is the safe interim. Either way this is the fail-safe direction (re-ask), so the
current behavior is "too permissive," never "too strict."

---

## 2. Engine-level deterministic high-blast floor (P2, engine contract)

**Code:** heuristic at
[`route-decision-review.sh` §3](../plugins/ravenclaude-core/hooks/route-decision-review.sh)
feeding [`thing-decide.py` `decide()`](../plugins/ravenclaude-core/scripts/thing-decide.py)

**The gap.** For the AskUserQuestion decision-review path, `high_blast` is set
**only** by the hook's keyword heuristic. `thing-decide.py`'s `decide()` defers on
high-blast **only when the caller passes `high_blast=true`** — it has no
deterministic high-blast screen of its own; absent the flag it relies entirely on
the LLM seats. The PR broadened the hook regex (force-with-lease/truncate/wipe/
revoke/purge), which narrows the gap, but the invariant "high-blast / irreversible
never auto-resolves" is still, at the engine layer, an LLM judgment call rather
than a deterministic floor. A destructive phrasing that dodges the hook regex
reaches the engine with `high_blast=false`.

**Why it's deferred.** Adding a deterministic high-blast screen *inside* `decide()`
changes the engine's contract and is shared by every caller (the `decision-review`
skill and the hook). It should reuse the existing destructive-pattern vocabulary
already maintained for the command tribunal
([`knowledge/concerns-catalog.md`](../plugins/ravenclaude-core/knowledge/concerns-catalog.md)
/ `guard-destructive.sh`) rather than inventing a third ad-hoc list — which is a
design decision about where that vocabulary lives and how the two tribunals share
it.

**Recommendation:** Add a deterministic high-blast screen to `decide()` sourced
from the concerns-catalog destructive vocabulary, keeping the hook heuristic as
belt-and-suspenders. Purely additive (it can only *add* defers), so it's
low-risk once the shared-vocabulary question is answered. Gate it with a new
audit-gates fixture proving a catalog-listed destructive verb defers even with
`high_blast=false`.

---

## 3. `route-decision-review.sh` — nested `decision_review` form not parsed (P3, low)

**Code:** hook parse at
[`route-decision-review.sh:52`](../plugins/ravenclaude-core/hooks/route-decision-review.sh)
vs engine at
[`thing-decide.py` `_decision_mode` (~:90)](../plugins/ravenclaude-core/scripts/thing-decide.py)

**The mismatch.** The Python engine accepts both the flat
(`decision_review: binding`) and nested (`decision_review: {mode: binding}`) posture
forms. The hook's `grep|sed` mode extraction only parses the **flat** form; for the
nested form it extracts an empty string and falls through to `emit_allow`. It is
**fail-safe in direction** (nested-form posture → the hook always asks the human,
never auto-denies), so there is no safety violation — but a user who configures the
documented nested form gets a hook that silently never auto-resolves, an
undocumented behavioral mismatch between the two layers that share the config key.

**Why it's deferred.** Low value (fails safe) and parsing nested YAML in
`grep|sed` is fiddly enough to risk introducing a new bug in a security-sensitive
hook. Not worth an autonomous change.

**Recommendation:** Either teach the hook's parser the nested `mode:` sub-key, or
canonicalize on the flat form and document that the hook only honors the flat
form. Pick one and make the two layers agree. Defer until you touch this hook for
another reason.

---

## 4. `rc-deep-research.js` — Heimdall latency-trip event not wired (P3, substrate)

**Code:** [`plugins/ravenclaude-core/skills/rc-deep-research/rc-deep-research.js:336`](../plugins/ravenclaude-core/skills/rc-deep-research/rc-deep-research.js)

**The TODO.** A documented deferral: emit a Heimdall amber
`evaluator-latency-trip` event when the latency circuit-breaker trips. The
breaker itself works and logs; only the dashboard amber-event emission is
missing, so a trip is observable in logs but not surfaced on the Heimdall card.
The surrounding comment explains it's deferred because the `_emit-event.sh`
shell-sourcing path is substrate-specific.

**Recommendation:** Wire the fire-and-forget `agent()` shell-helper call described
in the comment, or downgrade to a plain log if dashboard surfacing isn't wanted.
This is a "do we want it on the Heimdall card?" product call, not a bug — low
priority.

---

## What the review confirmed is healthy (no action)

The standard surfaces are in strong shape and were **not** the source of findings:

- All JSON manifests valid; **no** marketplace↔plugin version drift; every one of
  the 101 plugins has the required `plugin.json` / `README.md` / `CLAUDE.md`.
- All 444 audit-gates pass; frontmatter, markdown-link, layout, marketplace-claims,
  MCP-attribution, and run-actions-argv gates green.
- The Python `scripts/` surface is unusually defensive (no `shell=True`/`eval`/
  `pickle`; list-form `subprocess` with timeouts; the dashboard server fails closed
  on CSRF / Origin-Host / path-traversal). The shell guards are careful
  (normalization, fail-safe sourcing, anchored regexes). The tribunal engine's
  core safety envelope (off→defer, advisory→non-binding, injection/abstain/
  high-blast→defer) holds under the mock paths exercised.
