---
id: skill-index-self-reference-convergence
title: "The skill-index generator indexes its own output, so the first write always undercounts by one"
category: "Inventory — measured mechanisms"
kind: ravenclaude-built
entry_class: inventory
order: 931
summary: "generate-skill-index.py's first write omits its own not-yet-written output file from the count; a second run is required to converge on a stable total."
last_verified: 2026-09-08
covers:
  - scripts/generate-skill-index.py
  - plugins/ravenclaude-core/skills/skill-index/SKILL.md
covers_digest: "sha256:b1471be6e21c4a6137e8a33e7c7a4f81f7ff016a8a68e1a5e4e18147f459b290"
nuance: "The generator discovers skills by globbing plugins/*/skills/*/SKILL.md, and its own output
  file matches that glob. On a fresh repo the first write cannot see itself (the file does not exist
  yet), so it writes N entries; running it again now finds N+1 (itself included) and writes THAT count
  -- a fixed point reached on the second pass, never the first."
nuance_evidence:
  measured: 2026-09-08
  control: "ran the generator twice in a row against the real marketplace tree: pass 1 wrote 953
    entries and immediately failed its own --check (954 discovered vs 953 committed); pass 2 wrote 954
    and --check then reported fresh. A fixture repo seeded with the output file pre-existing at the
    correct count would show no undercounting on its first pass -- the control that separates
    self-reference from a generic off-by-one."
  falsifier: "excluding the generator's own output path from discover_skills()'s glob would remove the
    self-reference; that untested alternative design is the one falsifying probe this nuance names."
  probe: scripts/generate-skill-index.py
nuance_source: "scripts/generate-skill-index.py (discover_skills / render), verified this session by
  running --check immediately after a fresh write and observing exit 2, then re-running the write and
  observing --check exit 0"
verify:
  tier: reachability
  strength: observational
  probe: "python3 scripts/generate-skill-index.py && python3 scripts/generate-skill-index.py --check
    (exit 2 first pass would indicate a regression); run twice, expect the second --check to exit 0"
  teeth_exit: 2
sources:
  - label: FORGE run dynamic-skill-context, plan.md phase P0
    url: https://github.com/mcorbett51090/RavenClaude
---

## What a reader would have assumed instead

That a "generate the index" script is idempotent on its first run — write it once, done. That
assumption holds for every other generator in this repo (`sync-plugin-versions.py`,
`generate-copilot-plugin.py`) because none of them indexes a directory that includes their own output.

## The discriminator

control: pass 1 wrote 953 entries and immediately failed its own `--check` (954 discovered vs 953
committed); pass 2 wrote 954 and `--check` then reported fresh.

`skill-index`'s whole purpose is to enumerate every skill in the marketplace, including itself — a
disabled `ravenclaude-core` plugin should still show `skill-index` in its own index as the way back in.
That correctness requirement is exactly what makes it self-referential: `discover_skills()`'s glob
(`plugins/*/skills/*/SKILL.md`) matches the file the script is about to write. On a repo where the file
doesn't exist yet, the first write is computed over N skills (itself absent); by the time `--check` (or
a second write) runs, the file now exists and the count is N+1.

## Why it matters

A maintainer who runs the generator once, sees it "wrote 953 entries," and commits that file will find
CI's freshness gate (`--check`) immediately red on the very next run — not because anything drifted,
but because the committed file was never at the generator's own fixed point to begin with. The fix is
procedural, not code: run the generator twice (or once, then `--check`, then once more) before
committing. This is documented in the script's own module docstring so a future editor doesn't
mistake the two-pass requirement for a bug and "fix" it into an infinite regeneration loop.

The untested alternative — excluding the generator's own output path from `discover_skills()`'s glob —
is the probe named in `nuance_evidence.falsifier` above, not attempted here because it would also
remove `skill-index` from its own index, defeating the "still shows the way back in" requirement.
