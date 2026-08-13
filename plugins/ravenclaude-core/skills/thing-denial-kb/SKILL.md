---
description: The Thing-denial knowledge base (Muninn). When the command/decision tribunal DENIES or DEFERS an action, consult this to identify WHY the same block keeps happening and the known fix, then teach the KB a new resolution once you solve one. Read it the moment the Thing blocks you. Reads the Sága audit logs; never touches the tribunal's live path.
allowed-tools: Bash, Read
---

# thing-denial-kb — remember why the Thing blocked you, and how to get past it

When the command-review or decision-review tribunal ("the Thing") **DENIES** a command or
**DEFERS/refuses** a decision, the raw Sága record tells you *what* was blocked. It does not tell you
*why this keeps happening* or *how to get unblocked*. This skill is that memory — **Muninn**, the
raven of memory — a small, per-repo knowledge base that turns repeated denials into a lookup of
`denial shape → known resolution`.

Engine: [`scripts/thing-denial-kb.py`](../../scripts/thing-denial-kb.py) (stdlib-only, fail-safe —
every subcommand exits 0 even on error, so it can never break a hook or a session).

## When to reach for it

- **The moment the Thing blocks you this session.** Don't retry the command verbatim and don't
  immediately page the human — first `recall` and see if this exact block has a recorded fix.
- **At session start it is already surfaced.** The `thing-denial-kb-recall.sh` SessionStart hook
  injects the most-recent denial shapes + resolutions into context automatically (no-op when the KB
  is empty). This skill is the on-demand + write surface.

## The loop: recall → identify → solve → resolve

```shell
KB=plugins/ravenclaude-core/scripts/thing-denial-kb.py

# 1. IDENTIFY — what has the Thing blocked here, and what's the known fix?
python3 "$KB" recall                 # DERIVED labels only (source/category/count/sig + fix); newest first
python3 "$KB" recall --unresolved    # only the shapes that still have NO recorded fix (the gaps)
python3 "$KB" recall --json          # full rows incl. the (secret-scrubbed) sample — to pin down a specific one

# 2. SOLVE — apply the resolution the KB hands you (e.g. "use scripts/archive-branch.sh instead of
#    git branch -D"), or, for an unresolved shape, work out the smaller-blast-radius route yourself
#    (Capability-Grounding: read the cited concern, enumerate alternatives, try the next-easiest).

# 3. RESOLVE — once you get past a block that had NO resolution, teach the KB so the next session is
#    handed the fix immediately:
python3 "$KB" resolve --signature <sig> \
  --resolution "How you actually got unblocked, in one or two sentences." \
  --doc "optional/pointer/to/the/authoritative/file.md"
```

`sync` (materialise new denials from the Sága logs) runs automatically from the Stop hook — you
rarely call it by hand, but `python3 "$KB" sync` is safe and idempotent if you want the KB current
mid-session.

## What it reads, and the safety contract

- **Sources (read-only):** `.ravenclaude/runs/thing/decisions/*.json` (decision-review: `no` / `defer`)
  and `.ravenclaude/runs/thing/*.json` (command-review: `deny`). These are the audit records the
  tribunal **already** writes — this skill never touches `thing-orchestrator.sh` /
  `route-decision-review.sh` or the live PreToolUse emit path, so it cannot change a verdict.
- **Resolutions** come from the shipped, committed map
  [`knowledge/thing-denial-resolutions.json`](../../knowledge/thing-denial-resolutions.json)
  (cross-consumer knowledge) plus any local resolutions you author with `resolve` (which win).
- **Runtime KB** lives at `.ravenclaude/runs/thing/denial-kb.jsonl` (gitignored, per-repo).
- Full mechanism, schema, and how to author a good seed rule:
  [`knowledge/thing-denial-kb.md`](../../knowledge/thing-denial-kb.md).

## The important distinction: a real block vs. a false-positive defer

Some denials are **correct and load-bearing** — a force-push deny, a `security_deny` floor, a
high-blast decision defer. The KB's resolution for those says *"this is correct by design — surface
it to the human, do not route around it."* Honor that.

Others are **false-positive defers** the KB helps you clear — e.g. the decision-review tribunal
deferring because a seat flagged phantom prompt-injection in a benign, factual decision context. The
resolution there tells you the real move (re-file with a sterile context; proceed under standing
authorization if the action is reversible and not high-blast). **Never** use this skill to route
around a genuine security stop — see the Capability-Grounding clause *"Check why a constraint exists
before obeying (or citing) it"* and its high-blast exception.
