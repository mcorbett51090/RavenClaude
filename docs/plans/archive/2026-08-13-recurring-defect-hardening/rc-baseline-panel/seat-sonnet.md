# RC_BASELINE fork — seat: sonnet

## Vote: (b) — keep RC_BASELINE golden

## Code-grounded reasoning

`scripts/check-plugin-detail-render.mjs` (Gate 141) derives its `nine{}` counts
entirely by parsing the **committed `index.html`**'s embedded JSON — the eager
`window.__RC_DATA__` blob and the `plugin-detail-payload` island (lines 97-152).
It never touches the filesystem. So RC_BASELINE today is a golden regression
fixture on *rendered output*, not a filesystem cross-check.

The crux question — is an "independent filesystem scanner" for option (a) real
independence or a tautology — resolves against (a) once two other facts are on
the table:

1. **Freshness (committed `index.html` == what the generator currently
   produces from source) is already a separately-enforced gate, and I verified
   it does a real content diff, not a trivial check.** `scripts/audit-gates.sh`
   Gate 97 ("index.html freshness — template round-trip", L286 and L4625) runs
   `python3 scripts/generate-index-dashboard.py --check`. Reading its
   implementation (`generate-index-dashboard.py:1174-1199`): it re-runs
   `scan_repo()` + `render_html()` fresh, reads the committed output file, and
   compares the two strings **in full** (only stripping four documented
   volatile timestamp surfaces — generated/generated_date/footer-updated/
   last-updated-git-date; L1182-1198). Control run this session:
   `python3 scripts/generate-index-dashboard.py --check -o index.html` →
   `[ok] index.html is up to date`, exit 0, against the actual repo tree. Since
   this is a full-content diff of the rendered HTML (which embeds every one of
   the nine section arrays RC_BASELINE checks), any filesystem change that
   would move a real count — the exact scenario an independent fs-scanner in
   Gate 141 would also be trying to catch — already flips Gate 97 red. Adding
   a second fs-scan inside Gate 141 substantially duplicates Gate 97's job.

2. **The H4 "dropped card" hazard (data present in the generator's scan but
   lost during HTML/JS embedding) is already caught structurally, across all
   167 plugins, by Gate 141's own existing assertions** — not just the RC
   baseline block. Lines 174-214 already assert: no islanded key leaks into
   the eager blob, every eager plugin has a matching island record with all 4
   keys (`islandMissing === 0`), no plugin is orphaned from the island
   (`orphans.length === 0`), and `counts.tools`/`counts.scenarios` agree with
   the island's index length for **every** plugin, not just
   `ravenclaude-core`. These are structural, self-maintaining, and already
   independent-in-the-relevant-sense (they check render-internal consistency,
   which is exactly the failure mode H4 describes).

Given (1) and (2), what does RC_BASELINE add on top? Reading its own inline
history (lines 55-63: `52 -> 53: skills/design-clone`, `28 -> 29:
guard-memory-compaction.sh`, etc.) shows its actual, demonstrated use has been
as a **deliberate-change checkpoint** — a human bumps the number and leaves a
one-line reason, forcing conscious acknowledgment of a count change rather
than silent drift. A self-maintaining independent-scanner oracle, by
construction, never pauses for that acknowledgment — it just recomputes and
agrees. That is precisely the property plan-B (Sonnet, prior ruling)
identifies and plan-A's own risk table concedes as "Med (if naive)" tautology
risk, mitigated only by fixtures that re-test the same staleness/dropped-card
scenarios Gate 97 and Gate 141's existing assertions already cover — not a
fixture that isolates a genuine *scan-logic* bug unique to an independently
authored scanner. A from-scratch reimplementation that avoids tautology has to
diverge from `_scan_skills`/`_scan_hooks`/`_scan_scripts`'s definitional edge
cases (SKILL.md presence, hooks.json parsing, docstring-purpose extraction) —
but to avoid false positives on every legitimate definitional nuance, its
author is practically forced to read and mirror those same rules, which is
exactly how independence quietly degrades into tautology in practice.

(a)'s independence is therefore not clearly real: its strongest catch
(staleness) is already Gate 97's job — confirmed by reading `--check`'s
implementation and by an actual control run — its second-strongest catch
(dropped card) is already Gate 141's own structural-assertion job, and what's
left is either a near-duplicate of existing logic (tautology risk) or a source
of maintenance-burden false positives — while it discards the one property
RC_BASELINE demonstrably provides today: a human-reviewed "did you mean this?"
checkpoint. (c) is defensible but leaves the manual-bump toil unaddressed with
no offsetting gain; (b) is the correct call — preserve RC_BASELINE as-is.

## Vote
**b** — keep RC_BASELINE golden (hand-maintained, hand-bumped, annotated).

Confidence: 0.72
