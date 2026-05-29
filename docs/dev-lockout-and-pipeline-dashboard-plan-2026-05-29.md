# Plan — fix the dev-repo lockout + a guardrail-pipeline dashboard tab

> **Status:** PLAN / SCOPE ONLY (2026-05-29). Awaiting Matt's approval before any build.
> Origin: this session got derailed twice by the dev-repo lockout (the Thing fail-denied routine
> substrate edits; the runaway brake tripped at 200 mid-edit). Matt asked for (1) a scope to fix the
> lockout, and (2) a dashboard diagram of the whole guardrail process with per-stage on/off toggles +
> editable variables (e.g. the runaway number) + 5th-grade-level info/tooltips at each stage.

---

## Part A — the dev-repo lockout (root cause + fix)

### What happened (observed, twice, this session)
1. **Tribunal fail-deny.** Every comfort-posture category in this marketplace repo is toggled `thing: on`.
   The tribunal seats spawn nested `claude -p` calls (one per seat). Under the panel deadline those calls
   timed out → the panel **abstained** → the orchestrator **failed closed (DENY)** on my `Write`/`Edit` to
   `dashboard.sh` and `scripts/ravenclaude`. Result: I could not edit the substrate at all.
2. **Runaway brake.** The default ceiling was 200 total tool calls/session; a long substrate session blew
   past it mid-edit and every tool (even Read) was blocked. (The default is now **1200** as of v0.59.0.)

### Root cause (grounded in the code this session)
- `plugins/ravenclaude-core/scripts/thing-seat.sh` → each seat runs a fresh **nested `claude -p`** from a
  scratch cwd. Cold-start is ~24-29s per seat `[unverified — needs a `time claude -p` benchmark]`. When
  several seats contend on a modest machine, they exceed the per-seat soft cap → abstain.
- `plugins/ravenclaude-core/scripts/thing-decision.py` → an abstaining/inconclusive panel **fails closed
  (deny)** at every tier (the T5 safety posture). Correct for safety; wrong for a maintainer editing the
  Thing's own engine in the Thing's own repo.
- A `dev_repo_exempt` flag EXISTS but **only suppresses the substrate-path _self-disable_ DENY** — it does
  **not** rescue an _abstain-driven_ fail-closed deny. And this repo's posture doesn't set it. So the two
  gaps are: (a) abstain≠self-disable, the exemption misses it; (b) the flag is off here anyway.

### The fix options (pick the posture in approval; I recommend a layered fix)

| # | Fix | Effect | Risk |
| --- | --- | --- | --- |
| A1 | **Extend `dev_repo_exempt` to also downgrade an _abstain_ fail-closed DENY → ASK** in the verified marketplace-maintainer context (the same 3-signal gh-bound check). | Maintainer keeps reviewing, but an abstain no longer hard-blocks substrate edits. | Low — still gated by the 3 signals; hard-rule floor (force-push/curl\|sh), secret-egress, injection unchanged. |
| A2 | **Make seats warm / faster:** raise the per-seat soft cap when seats cold-start, or run a single warm seat for low/medium tiers in dev. | Fewer spurious abstains for everyone, not just the maintainer. | Medium — touches timing; must not weaken high-tier review. |
| A3 | **Document the clean dev loop:** when editing the Thing's substrate in THIS repo, set `command_review.enabled: false` (master off) for the session, then back on. | Zero code change; pure runbook. | Low, but it's the manual dance we keep repeating — not a real fix. |

**Recommendation:** ship **A1** (the principled fix — the exemption should cover abstain, since an abstain
in the maintainer context is a latency artifact, not a security signal) + **A3 as the documented fallback**.
Treat **A2** as a separate, optional performance follow-up (it helps all consumers but is timing-sensitive).

### Part-A deliverables
- `thing-decision.py`: in the verified maintainer-exempt context, an abstain/inconclusive panel on a
  toggled category downgrades **DENY → ASK** (never auto-allow) for substrate edits. New Gate fixture proving:
  (a) exempt + abstain → ask; (b) NON-exempt + abstain → still deny (fail-closed preserved);
  (c) exempt does NOT rescue a hard-rule deny.
- Runbook section in `plugins/ravenclaude-core/CLAUDE.md` for the master-off fallback.
- Version bump + regen + gates. Ships as its own PR.

---

## Part B — the guardrail-pipeline dashboard tab

### Goal (Matt's words, mapped)
A diagram of the **whole guardrail process** the agent passes through, where the user can **see where each
stage sits**, **toggle stages on/off**, **edit each stage's variables** (e.g. the runaway number), and read
**5th-grade-level info/tooltips** explaining what each stage is and what's happening. No memorized commands.

### The pipeline to draw (ALL hooks, ALL events — per Matt's chosen depth)
Grounded in `plugins/ravenclaude-core/hooks/hooks.json` (verified this session):

```
SessionStart ─▶ reapply-posture ─▶ ensure-default-mode ─▶ capability-orientation
                                                                    │
        (every tool call) ─▶ PreToolUse ─────────────────────────┐ │
            guard-destructive ─▶ thing-orchestrator (the Thing) ─▶ runaway-brake ─▶ enforce-layout (+task-scope) ─▶ route-decision-review
                                                                    │
        (after a tool runs) ─▶ PostToolUse                          │
            format-on-write ─▶ guard-recursive-spawn ─▶ claim-grounding-lint
                                                                    │
        (agent tries to stop) ─▶ Stop                               │
            dod-gate ─▶ remind-tests
```

Each box on the diagram carries: **(1)** an on/off toggle (where the stage is toggle-able), **(2)** its
editable variables, **(3)** a 5th-grade "what is this / what's happening now" tooltip + an info panel.

### Per-stage controls + the kid-level explanation (draft copy — refine in build)

| Stage | Event | Toggle? | Editable variables | 5th-grade tooltip (draft) |
| --- | --- | --- | --- | --- |
| guard-destructive | PreToolUse | via category | (none) | "Stops really dangerous commands (like deleting everything) before they run." |
| thing-orchestrator (the Thing) | PreToolUse | per-category `thing:` + master `enabled` + `dev_repo_exempt` + `gate_floor` + per-tier seats/models/confidence | "A panel of robot reviewers votes yes/no/fix on a command before it runs. You pick how strict." |
| runaway-brake | PreToolUse | `max_total` (default 1200), `max_consecutive` (8), `off` | "Counts the robot's steps. If it loops forever or takes too many steps, it pauses so it doesn't run away." |
| enforce-layout + task-scope | PreToolUse | `.repo-layout.json` globs; `.ravenclaude/task-scope.json` | "Makes sure new files go in the right folders, and only the files this task is allowed to touch." |
| route-decision-review | PreToolUse(AskUserQuestion) | `decision_review: off/advisory/binding` | "When the robot would ask you a yes/no question, the panel answers the easy ones so you're not interrupted." |
| format-on-write | PostToolUse | (none) | "Tidies up a file's formatting right after it's saved." |
| claim-grounding-lint | PostToolUse | advisory | "Reminds the robot to say where a fact came from when it writes one into a doc." |
| dod-gate | Stop | `definition_of_done.cmd`, `max_blocks` (8) | "Before the robot says 'done,' it runs your tests. If they fail, it keeps working." |
| reapply-posture / capability-orientation | SessionStart | (none) | "When a session starts, it loads your settings and reminds the robot what it's allowed to do." |

### How it plugs into the existing dashboard (grounded in the generator)
- `scripts/generate-dashboards.py` builds `dashboard.html` from Python f-string templates; tabs today are
  `settings / commands / trees / activity / install / learn / saga / simulator`. **`trees` is a stub.**
- The `learn` tab already embeds **SVG diagrams** (precedent for drawing a flow). So the pipeline tab is a
  **new generated tab** (e.g. `data-tab="pipeline"`) rendered as inline SVG/HTML — **no new dependency**,
  consistent with the "self-contained, no CDN" rule.
- The toggles/variables **read and write the same `.ravenclaude/comfort-posture.yaml`** the Settings tab
  already round-trips via `/__save` + `/__read` (no new server endpoint needed for the posture-backed knobs).
- Stages backed by other files (`.repo-layout.json`, `task-scope.json`, `definition_of_done.cmd`) either
  (a) deep-link to where they're edited, or (b) get a small `/__read`-allow-listed surface — **decide in
  build; default to read-only display + deep-link to avoid widening the write surface.**

### Part-B deliverables
- A new generated **Pipeline tab** in `generate-dashboards.py`: the all-events flow diagram, per-stage
  on/off + variable editors for the posture-backed knobs, and info/tooltips at 5th-grade reading level.
- Tooltip/info copy reviewed for reading level.
- Freshness gate keeps `dashboard.html` in lockstep (the generator already has `--check`).
- Ships as its own PR (it changes `dashboard.html`, a consumer-installed artifact).

### Open questions for Part B (answer at build time)
1. **Write surface:** should the tab edit `.repo-layout.json` / `task-scope.json` / `definition_of_done`
   directly, or display + deep-link only? (Recommend display+deep-link first — smallest blast radius.)
2. **Live state:** should each stage show "currently ON/OFF for THIS repo" by reading the live posture, or
   just be a configurator? (Recommend: show live state — it's the "where am I in the process" Matt asked for.)
3. **Diagram tech:** hand-built inline SVG (full control, matches `learn` tab) vs. a tiny JS flow lib
   (none currently bundled — would break the no-CDN rule). Recommend inline SVG.

---

## Sequencing
Part A (lockout) and Part B (dashboard) are independent and each ship as their own PR. Recommend **A first**
(it stops the recurring friction that derails substrate work, including building Part B itself), then B.
Both are gated on Matt's approval of this plan.
