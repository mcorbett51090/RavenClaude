# Demos must survive a real developer

**Status:** Pattern.

**Rule:** A demo or sample app must be reproducible by a developer typing along from a clean state.
No magic setup, no pre-warmed state, no undeclared versions, no happy-path-only. Show one realistic
failure and its recovery.

## Why

Trust with a technical audience is won or lost on reproducibility. A demo that "just works" by sleight
of hand teaches nothing and, worse, reads as dishonest the moment the developer tries it themselves
and it breaks. The failure-and-recovery beat is not optional polish — it is precisely where the
audience decides whether to trust you, because real use always hits errors.

## What it looks like in practice

- The demo starts from a clean, declared state and pins every version.
- Setup is part of the demo (and timed), not "left as an exercise."
- One common error (bad key, missing param, rate limit) is triggered deliberately and recovered.
- The artifact clones-and-runs with one command and becomes an activation path.

## Anti-pattern

The flawless on-stage demo built on hidden state that no audience member can reproduce. The hook
flags content/demo work that names no journey stage; this rule adds that a demo with no
failure-and-recovery and no declared setup is not done.
