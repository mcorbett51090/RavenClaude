# Repo review — decisions needed (2026-09-22)

Companion to [`docs/reviews/2026-09-22-repo-review-findings.md`](reviews/2026-09-22-repo-review-findings.md).

The autonomous review fixed everything mechanical (see that doc + the PR). Two
items below are **judgment calls, not mechanical fixes** — each has a
recommendation, but each changes behavior or policy in a way a human should sign
off on, so neither was applied autonomously. Both were verified on the real
`origin/main` tree, not the stale checkout the sweep started from.

---

## Decision 1 — should the WebFetch sanitizer's `system` code-fence rule stay greedy? (P3)

**Finding (verified this session, on real main).** `sanitize-webfetch-body.py`
pattern 5 (the ` ```system … ``` ` fenced-block rule, `plugins/ravenclaude-core/scripts/sanitize-webfetch-body.py:119`)
uses a **greedy** `.*` (not `.*?`), so it strips **everything from the first
`system` fence to the last ``` fence in the whole document**. A benign fetched
doc containing an early `system` code fence _plus_ any later ``` fence loses all
content in between, including legitimate trailing code.

- This is the **deliberate, documented** "prefer the floor / accept over-
  stripping" posture — the file's own comments state it for patterns 1, 2, and 5,
  and the greedy choice is there for a real reason (a non-greedy match stops at
  the first closing fence, leaving a **nested-decoy** payload — `` ```system\ndecoy\n```\nREAL PAYLOAD\n``` `` — as bare surviving text). It **never fails
  open**: greedy only ever strips _more_, so no injection survives. The cost is
  availability — a benign fetched doc can be over-redacted.

**The tension.** The module's own goal is that "a fetched canonical doc's real
content survives." Greedy pattern 5 trades against that for benign inputs, while
the security benefit over a bounded/non-greedy per-block match is marginal (a
non-greedy per-block match still removes each real `system` fence individually).

**Question:** keep the greedy floor as-is (security-maximal, accept over-
stripping), or make pattern 5 match **per-block, non-greedy** (each ` ```system …
``` ` removed individually) so benign interleaved content survives?

**Recommendation (leaning non-greedy, low confidence):** a per-block non-greedy
match still strips every injection block and stops eating legitimate content
between unrelated fences — it looks like a strict improvement, not a weakening.
But because this is the security perimeter and the greedy posture is a
deliberate, load-bearing choice (with the nested-decoy case its comments call
out), I did **not** change it autonomously. If you agree, this becomes a small,
well-scoped follow-up PR with a new acceptance test (benign interleaved fences
survive; the nested-decoy payload is still fully stripped; every `system` block
still removed).

---

## Decision 2 — add a gate for the catalog's domain-plugin count? (P3, preventive)

**Finding.** The `marketplace.json` headline description's plugin-count integer
has now drifted for the **third** time: `144` (fixed 2026-08-31), then `180` (set
when the total was ~180), and now stale at `180` while the real count is **183**
(184 plugins − 1 non-domain core). The 2026-08-31 review explicitly noted "no
existing gate validates this specific number," and it has drifted again — the
predictable outcome of a hand-maintained count with no check, in a marketplace
that adds plugins continuously.

- Derivation is unambiguous and script-checkable: `#plugins − (#plugins without
  `requires.plugins`)` = domain-plugin count (this session computed it directly:
  184 total, exactly `ravenclaude-core` lacks `requires.plugins`, → 183).

**Question:** add a CI gate (and/or fold it into `check-marketplace-claims.py`)
that asserts the description's "N domain plugins" integer equals the derived
count — or accept manual upkeep and just fix drift as it's found?

**Recommendation (add the gate):** it's a few lines, the derivation is
deterministic, and it converts a recurring manual-drift class into a build
failure — squarely in line with this repo's "don't restate what a gate can
enforce" house rule (House rule #4). I did not add it autonomously because a new
gate is a policy addition (it can fail others' PRs, and this repo's own CLAUDE.md
records repeated pain from gate-number collisions on concurrent PRs) and belongs
with owner sign-off on the exact gate slot. If you want it, it's a clean
follow-up.
