# Give a cold agent a document map, not just behaviour rules

**Status:** Pattern — strong default; deviate only with a written reason.

**Domain:** Agent design / cross-tool onboarding.

**Applies to:** `any Claude Code project` whose repo carries more than ~50 documents an agent is expected to locate — especially repos operated by **non-Claude-Code agents** (GitHub Copilot CLI, Cursor, Aider).

---

## Why this exists

A cold coding agent re-runs `find`/`grep` every turn to relocate a document it already "knows" exists — 4–6 tool calls to answer one question that a location index would answer in one. The instinct is to blame missing memory, but that framing is wrong and leads to the wrong fix: Copilot CLI (and peers) **auto-include** their instruction files (`AGENTS.md`, `.github/copilot-instructions.md`, `CLAUDE.md`) on _every_ request. What those files carry is _behaviour_, not a **document-location index** — and a path merely _referenced inside_ an auto-loaded file is not itself auto-loaded. So the agent still has to go looking. A flat, keyword-indexed **topic → path** table placed where the agent already reads closes the gap: one lookup, not a filesystem sweep.

The mechanism, placement trade-offs (inline vs. standalone), sizing thresholds, and the seed-then-curate maintenance rule live in one canonical place — the Copilot-CLI knowledge doc — so this best-practice **points at it** rather than restating it (restated mechanics drift out of sync):

**Canonical mechanism:** [`copilot-cli-customization.md` §7 "Document discovery"](../../plugins/ravenclaude-core/knowledge/copilot-cli-customization.md).

## How to apply

1. **Decide placement by size.** If the index is small, **inline** the topic→path table into an already-auto-loaded instruction file (0 extra tool calls). If it's too large to inline, put it in a standalone `DOCUMENT-MAP.md` **and** add one line in an auto-loaded file telling the agent to read it first (a bare file nothing points at is invisible).
2. **Keep it flat and keyword-first** so the agent can `grep` the _map_ instead of the filesystem. A domain-neutral shape (replace with your repo's real, high-traffic documents — the topic labels are the load-bearing part and must be written by a human who knows which file answers which question):

```markdown
## Reports & designs
| Topic | File |
|---|---|
| Quarterly revenue model         | finance/models/revenue-q3.xlsx |
| Onboarding runbook (new hires)  | docs/runbooks/onboarding.md |

## Architecture & planning
| Topic | File |
|---|---|
| Service boundaries + data owners | docs/architecture/boundaries.md |
| Current migration status         | docs/architecture/migration-tracker.md |
```

3. **Seed, then hand-curate.** Run [`scripts/generate-document-map.py`](../../scripts/generate-document-map.py) once to enumerate files and best-effort titles; then **hand-edit the topic column** — a script cannot judge "this is the file an agent looks up when asked about X." After curating, treat the file as hand-owned.

**Do:**
- Map only the documents an agent repeatedly _looks up by topic_.
- Exclude point-in-time artifacts (dated one-off plans, research write-ups) — they add noise, not lookups.

**Don't:**
- Ship a generated map as source of truth (poor auto-topics read as a broken pattern).
- Let it go stale — a **stale map is worse than none**: it routes the agent to a dead path, it greps anyway, and you paid for the map _and_ the grep.

## Edge cases / when the rule does NOT apply

- **< ~50 docs / < ~20 files:** skip it. One `grep` is faster than maintaining a map.
- **> ~1000 docs:** a flat table stops scaling — reach for a semantic index (a Copilot Space) instead. Say so; don't hand-maintain a thousand-row table.
- **No `docs/` tree / unusual layout:** the generator is config-driven (`--config`) — point it at your roots; it does not assume any one layout.
- **RavenClaude itself does not ship a committed `DOCUMENT-MAP.md`.** Its durable docs are already indexed several ways (dashboard scenario tables, repo-guide, `docs/rules/INDEX.md`) and most of `docs/` is dated one-offs looked up by date, not topic — the exact corpus this pattern says _not_ to map. The pattern is shipped for **consumer** repos; the generator is the reusable tool.

## See also

- [`../../plugins/ravenclaude-core/knowledge/copilot-cli-customization.md`](../../plugins/ravenclaude-core/knowledge/copilot-cli-customization.md) — §7 is the canonical mechanism.
- [`../../plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md`](../../plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md) — wires the session-start read into a non-Claude-Code agent's first five minutes.
- [`lessons-vs-best-practices.md`](./lessons-vs-best-practices.md) — this is a rule (no story), so no companion lessons entry.

## Provenance

Surfaced 2026-07-08 from consumer engagement: a GitHub Copilot CLI session in a large Power Platform repo (100+ HTML/MD docs, nested SOP dirs) spent 4–6 tool calls per known-document lookup versus a Claude Code session that retained locations in-session. Forged through the FORGE planning pipeline (two-panel review + correlated-error critic), which corrected the original "no persistent memory" framing to the auto-loaded-but-no-location-index framing above and scoped RavenClaude out of dogfooding a live map.

---

_Last reviewed: 2026-07-08 by `mcorbett51090`_
