---
name: dependency-update-sweep
description: When a tracked host tool (Claude Code, Copilot CLI/Chat, Codex CLI, Cursor, Gemini CLI, Aider, Windsurf — read live from host-support.json) ships a new version, scan the repo for citation-marked drift, auto-apply safe mechanical fixes, and queue judgment calls for review. Reach for this skill on "a host tool updated, what needs to change" or via the SessionStart nudge.
---

# Skill: dependency-update-sweep

Answers one question on demand: *a tracked host tool shipped a new version — what in this repo now
needs updating or deprecating because of it?* It does not answer "is every fact about this host
current" — see Honesty / known limits below.

## When to invoke this skill

- You (or a maintainer) know a tracked host tool bumped its version and want to know what's affected.
- The SessionStart capability banner nudges "run `dependency-update-sweep` — <host> may have moved" (a
  zero-subprocess, file-read-only signal — see [`capability-orientation.py`](../../scripts/capability-orientation.py)).
- Before a release, as a targeted pre-flight for the hosts that changed since the last sweep.

**Not this skill's job:** general knowledge-file staleness (calendar-driven, any topic) — that's
[`knowledge-file-staleness-sweep`](../knowledge-file-staleness-sweep/SKILL.md), the sibling sweep. This
one is host-version-triggered; that one is calendar-triggered. Also not this skill's job: whether a
claim is cited *at all* — that's Gate 208; this sweep answers whether a claim that *is* dated is now
stale.

## Scope

Tracked hosts are **`host-support.json`'s top-level `hosts{}` keys, read live** at run time — never
hardcoded here. As of this writing: `claude-code`, `copilot`, `codex`, `cursor`, `gemini`, `aider`,
`windsurf`. **Grok Build CLI is explicitly out of scope** — no entry in `host-support.json`, no
`scripts/ravenclaude install --host` wiring; it is tracked only in `substrate-tier-map.json` for
model-tier resolution, an unrelated system. Do not "fix" the roster back to a hardcoded list.

## Discovery mechanism

A bounded `git grep -n` for the fixed citation-marker family (`[docs-verified YYYY-MM-DD]`,
`[verified YYYY-MM-DD]`, `[web-sourced …]`, `[unverified — training knowledge]`), plus a direct JSON
walk of `host-support.json`/`model-catalog.json`, plus a structural match over `_SKIP` dict entries in
the `generate-copilot-hooks.py` / `-gemini-hooks.py` / `-cursor-hooks.py` generators and any
`_FLOOR=`/`_RECOMMENDED=`-shaped constant in `scripts/ravenclaude`. This is **not** a general-purpose
repo scan — every version-sensitive fact this repo already carries by convention already has a marker,
and a full-repo re-scan multiplies judgment cost for a benefit the marker convention already exists to
make unnecessary. The one confirmed gap in this approach is fixed forward, not silently accepted — see
Honesty / known limits.

## Sweep mechanics

1. **`scan --host <id> --old-version <v> --new-version <v>`** — read-only. Walks the scan surfaces
   above, produces a citation map + a `_meta.skipped_surfaces` list naming any absent surface (a
   consumer's installed project won't have the marketplace-dev-only surfaces).
2. **`classify`** — applies the rule table below to every citation-map row, producing a disposition
   (`mechanical` / `judgment` / `no-finding`) + priority + which check was performed.
3. **`apply --host <id> --yes`** — handles every `mechanical` row, from inside a fixed-slug FORGE
   worktree (`forge-dependency-sweep-<host>`), with dirty-tree refusal, per-write covering-gate
   re-verification, and the fingerprint update landing in the same commit as any content fixes. Two
   distinct outcomes, never conflated: `applied` (a file's bytes actually changed — reported only when a
   real editor exists for that row's citation kind) and `verified` (nothing was written — the row's
   floor comparison was re-confirmed, its own mechanical action). As of this writing the only shipped
   citation kind (`version_floor_constant`, §3 row 2) always resolves to `verified` — the floor constant
   itself is never edited by a version bump, only re-checked.
4. **`queue --host <id>`** — writes `judgment` rows to a capped, priority-ordered PR-review queue
   (top 25, P0 first, overflow to a continuation file) — reuses `/repo-review`'s P0-P3 shape rather
   than inventing a second scheme.

## Merged classification rule table

| Citation kind | Example (this repo) | Disposition | Priority if judgment | Why |
|---|---|---|---|---|
| Pinned exact version string, no behavior claim | a bare version literal, no interpretive claim | **Mechanical** | — | Pure substitution; nothing about host behavior is asserted. |
| Version-floor comparison that still holds | `COPILOT_FLOOR="1.0.52"`; an `activation_gate: version_floor` cell already satisfied | **Mechanical** (the one case a date bump is ever auto-applied — the re-check *is* the re-verification) | — | Deterministic comparison the sweep itself just ran; the row records which check ran. |
| Version-floor comparison the sweep cannot establish `>=` for | non-semver host versioning, a date-expressed floor | **Judgment** | P2 | Needs a human/agent read of the version scheme. |
| `[docs-verified]`/`[verified]`/`[web-sourced]` date stamp on a capability claim (not the floor-still-holds case above) | any prose marker describing what a host can do | **Judgment** | P2 | Requires reading the changelog delta — exactly what `knowledge-file-staleness-sweep`'s anti-pattern forbids automating. |
| `host-support.json` capability cell (`supported`/`basis`/`caveat`) naming the bumped host | any `hosts.<host>.<component>` cell | **Judgment, always** | **P0** if the changelog delta names the same event by name, else P1 | Gate 154/208 exist precisely because this class needs a dated citation a human writes. |
| `activation_gate` cross-reference | Codex's hash-trust re-arm cross-reference | **Judgment, always** | P1 | A two-file fact; changing one without the other is a real, already-seen drift class. |
| `model-catalog.json` entry/slot decision | `current`/`stale` moves | **Judgment, out of this sweep's write path entirely** | P1 (note only) | Gate 134 already owns model-ID drift, CI-enforced. |
| `_SKIP` reason whose text names an absent event/capability **and** the changelog delta mentions it by name | `_SKIP["agent-dispatch-evaluator.sh"]` | **Judgment (high-priority)** | **P0** | The skip might now be falsified; closing it is design work. |
| `_SKIP` reason with no changelog match | same shape, no match | **No finding — silent** | — | Matches `knowledge-file-staleness-sweep`'s "don't flood the queue" discipline. |
| Version-gated code path whose branch condition names the bumped host | macOS-door-style `if version >= X:` shape | **Judgment, always** | P1 | Behavior-shaping code; retiring a compatibility branch changes runtime behavior. |
| Bare, uncited host-capability claim | anything Gate 208 would flag as missing-citation | **Not this sweep's job** — advisory pointer to Gate 208 | — | Out of scope by construction: this sweep answers "is a *dated* citation stale," not "is a claim cited at all." |

**Never blind-bumps a date.** A `[docs-verified]` date is mechanical **only** when the sweep's own
deterministic sub-check positively confirms the underlying claim still holds (the version-floor row
above) — every other date-stamped citation is judgment, always, even when the resulting edit looks like
a one-liner. `knowledge-file-staleness-sweep`'s own anti-pattern: *"Fixing the date without
re-verifying is worse than letting it go stale — it silently launders untrustworthy content."*

## State file

`plugins/ravenclaude-core/knowledge/host-version-fingerprint.json` — `schema_version: 1`, one entry per
`host-support.json` key, each carrying `last_swept_version` / `last_checked_at` (updated on every
sweep run, mechanical fixes or not) / `last_change_detected_at` (updated only on a real delta) /
`written_by` (provenance, `dependency-sweep.py vN`). Written only by `apply`'s step 5, always in the
same commit as the content fixes it reports on — never a silent, separate, local-only write.

## Routing table (judgment rows)

| Citation kind | Route to |
|---|---|
| `host-support.json` cell | maintainer (binding edit) + `deep-researcher` if the basis needs re-verifying against the host's own docs |
| `_SKIP` reason in a generator | maintainer — closing a `_SKIP` is a small feature (new wiring + test), not a data edit |
| Version-floor candidate | maintainer, with the *exact* changelog citation the sweep found |
| Version-gated code path retirement | maintainer, explicitly flagged "confirm the floor host no longer needs this" — never auto-proposed as a deletion |

## Anti-patterns

- **Blind date-bumping.** See "Never blind-bumps a date" above — a `[docs-verified]` date is mechanical
  only in the one deterministic-floor-comparison case, never as a general rule.
- **Classifying by diff size or file path.** Diff size is anti-correlated with risk here (a boolean
  flip in `host-support.json` is one line and highly dangerous); file path collapses citation kinds
  that need different treatment purely because they share an extension.
- **Writing the fingerprint separately from the content fixes it reports on.** An unmerged, separate
  fingerprint-only write is exactly the worktree-artifact-loss exposure this skill's own design run
  hit on this machine — see Honesty / known limits and Phase 4's same-commit requirement.
- **Silently truncating an oversized judgment queue.** Cap at 25/run, priority-ordered, overflow to a
  named continuation file — never a flat unreviewable wall of findings.
- **Minting a new worktree slug per run.** `apply` reuses one fixed slug per host
  (`forge-dependency-sweep-<host>`) so `worktree-guard`'s lease actually protects concurrent runs.

## Honesty / known limits

This sweep discovers drift by finding citation **markers** — `[docs-verified]`/`[verified]`/
`[web-sourced]` prose, `host-support.json` JSON cells, `_SKIP` dict entries. **A version-sensitive fact
with no marker of any kind is structurally invisible to it, permanently, by construction — not a bug to
be fixed, a limitation to be stated.** The confirmed example that motivated this note:
`docs/best-practices/2026-q1-q2-failure-modes.md`'s "Tool-version floors that prevent regression-class
failures" table carried zero markers before this skill's Phase 1 fixed it forward — and, once checked,
turned out to carry **fabricated and unsourced facts** (three Copilot floors that don't exist in the
real changelog, and an uncited Cursor floor), already corrected once in this repo's
`external-agent-onboarding/SKILL.md` but never back-ported to that table until this fix. A second,
structurally identical instance — `AGENTS.md`'s inline "Requires Copilot CLI ≥ 1.0.52" bolded-prose
floor with no adjacent marker — is named here but deliberately left unmarked (a docs-only edit outside
this skill's own file inventory), a stated follow-up, not hidden. No success report from a real sweep
run may claim completeness beyond "every marked citation naming the bumped host was found and
classified" — never "every fact about this host is now current."

A consumer's installed project lacks the marketplace-dev-only scan surfaces (`scripts/ravenclaude`, the
three `_SKIP` generators) — `_meta.skipped_surfaces` exists specifically so that shrinkage is visible,
never silently read as "clean."

## Output

```
---RESULT_START---
{
  "status": "complete",
  "summary": "swept <host> N->M; X mechanical applied, Y judgment queued, Z overflow",
  "deliverables": [".ravenclaude/runs/<sweep-id>/citation-map.json", ".ravenclaude/runs/<sweep-id>/dependency-sweep-queue.md"],
  "handoff_recommendation": {"to_specialist": "maintainer", "reason": "review the judgment queue"},
  "confidence": 0.9,
  "risks_or_open_questions": ["marker-blind-spot limitation — see Honesty / known limits"],
  "next_actions": ["review .ravenclaude/runs/<sweep-id>/dependency-sweep-queue.md", "open the apply PR if not already open"]
}
---RESULT_END---
```

## See also

- [`knowledge-file-staleness-sweep`](../knowledge-file-staleness-sweep/SKILL.md) — the calendar-triggered
  sibling sweep.
- [`plugins/ravenclaude-core/scripts/dependency-sweep.py`](../../scripts/dependency-sweep.py) — the tool
  this skill drives.
- [`plugins/ravenclaude-core/scripts/host-version-probe.py`](../../scripts/host-version-probe.py) — the
  manual-invocation-only version probe (never called from SessionStart).
- [`plugins/ravenclaude-core/knowledge/host-support.json`](../../knowledge/host-support.json) — the host
  roster this skill reads live.
