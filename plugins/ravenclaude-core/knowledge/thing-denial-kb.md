# The Thing-denial knowledge base (Muninn)

**What it is:** a small, per-repo, durable knowledge base that turns the tribunal's raw denial audit
records into a lookup of `denial shape → known resolution`, so an agent that gets blocked by "the
Thing" can **quickly identify the issue and solve it** instead of retrying blindly or paging the
human. Named **Muninn** — one of Odin's two ravens, *memory* (the RavenClaude fit: the agent
*remembers* why it was blocked before and how it got past it).

It is the **learn-from-denials** complement to the existing observability surfaces: Heimdall/Víðarr
show *what* tripped and *when* (pull dashboards); the event substrate records deny verdicts
(`hook-events.jsonl`); this layer adds the missing piece — *why it keeps happening* and *the fix*.

Engine: [`../scripts/thing-denial-kb.py`](../scripts/thing-denial-kb.py). Agent-facing workflow:
[`../skills/thing-denial-kb/SKILL.md`](../skills/thing-denial-kb/SKILL.md).

## How it works (write → identify → solve → teach)

| Step | Mechanism |
|---|---|
| **Write on denial** | The `Stop` hook [`thing-denial-kb-sync.sh`](../hooks/thing-denial-kb-sync.sh) runs `thing-denial-kb.py sync` at the end of any turn. `sync` reads the Sága audit records the tribunal **already** wrote and materialises each **new** denial into the KB. It is **hot-path-safe** — it never touches `thing-orchestrator.sh` / `route-decision-review.sh` or the live `PreToolUse` emit path, so it cannot change a verdict or corrupt a hook's stdout. |
| **Identify** | The `SessionStart` hook [`thing-denial-kb-recall.sh`](../hooks/thing-denial-kb-recall.sh) surfaces the most-recent shapes + resolutions into context automatically — **derived labels only** (source / category / count / signature + the trusted resolution), never the raw `sample`. On demand: `thing-denial-kb.py recall` (`--unresolved`, `--limit`) for the same digest, or `recall --json` for the full rows **including the (secret-scrubbed) sample** when you need to identify a specific denial. |
| **Solve** | Each shape is matched against the shipped resolutions map and carries a known fix (or a clear "no resolution yet — author one"). |
| **Teach** | `thing-denial-kb.py resolve --signature <sig> --resolution "…"` records a fix an agent discovered, so the next session that hits the same shape is handed it. |

## Sources it reads (read-only)

- `.ravenclaude/runs/thing/decisions/*.json` — decision-review verdicts. Captured when `final_verdict`
  is `no` or `defer` (a `yes` did not block the agent, so it is not a "denial").
- `.ravenclaude/runs/thing/*.json` — command-review verdicts. Captured when `final_verdict` is `deny`.

Both are the audit records the tribunal writes itself (see the v0.110.0 "Tribunal denies now emit to
the event substrate" milestone). This KB is a **reader** of them.

## The signature (how denials are grouped)

Distinct denials are grouped by a stable 12-char signature so a shape that recurs is one KB row with
a count, not N rows:

- **decision-review** → grouped by *reason class*, since the question text is unique every time:
  `high-blast-defer`, `injection-defer`, `low-confidence-defer`, `split-defer`, `policy-no`,
  `policy-defer`. (Two different questions that both defer for phantom injection collapse to one
  `injection-defer` shape — exactly what you want to learn from.)
- **command-review** → grouped by `category:command-head` (the classified comfort-posture category
  plus the first few tokens of the command).

## Runtime + shipped split

| File | Where | Committed? |
|---|---|---|
| `knowledge/thing-denial-resolutions.json` | plugin | **yes** — the seed resolutions, shared across consumers |
| `.ravenclaude/runs/thing/denial-kb.jsonl` | consumer repo | no (gitignored `.ravenclaude/runs/`) — the materialised per-repo KB |
| `.ravenclaude/runs/thing/denial-learned.json` | consumer repo | no — resolutions an agent authored with `resolve` (override the seed) |
| `.ravenclaude/runs/thing/denial-kb-cursor.json` | consumer repo | no — which source records have been synced (idempotency) |

## Authoring a seed resolution rule

Rules live in `knowledge/thing-denial-resolutions.json` under `rules[]`, evaluated **top-to-bottom,
first match wins** (so order specific-before-general). A rule matches an extracted denial event when
**every present `match` field** is satisfied:

```json
{
  "id": "cmd-branch-delete",
  "match": {
    "source": "command-review",      // exact: "command-review" | "decision-review"
    "verdict": "deny",                // optional, exact: "deny" | "no" | "defer"
    "category": "shell_local_mutate", // optional regex, case-insensitive, over the event category
    "pattern": "git\\s+branch\\s+-D"  // optional regex, ci, over "<sample command> <cited reasoning>"
  },
  "resolution": "Use the branch-archive skill … (one or two sentences).",
  "doc": "plugins/ravenclaude-core/skills/branch-archive/SKILL.md"
}
```

Guidelines:

- **Make the resolution actionable** — name the concrete alternative route (`scripts/archive-branch.sh`,
  the sanctioned MCP path, an in-place flag), not just "don't do that".
- **For correct-by-design denials, say so.** A force-push / `security_deny` / high-blast defer should
  resolve to *"this is correct — surface it to the human, do not route around it"* — the KB must not
  teach an agent to defeat a real security stop (see the Capability-Grounding clause *"Check why a
  constraint exists before obeying it"* and its high-blast exception).
- **Keep a general catch-all last** (`{source: command-review, verdict: deny}`) so every denial gets
  *something* useful even before a specific rule exists.

## Safety / fail-safe invariants

These two are load-bearing (they were the blocking findings of the pre-merge security review) and are
proven bidirectionally by **Gate 143** (`hooks/tests/test-thing-denial-kb.sh`):

- **Derived-labels-only auto-injection.** The SessionStart recall banner injects the KB into session
  context, so — exactly like `capability-orientation.sh` / `watch-run-state.sh` / Gate 19 — it emits
  only *derived* fields (source / category / count / signature + the *trusted* resolution). The raw
  denied command/question (`sample`) is **never** in the banner: it is a hostile-controllable string
  (a denied command or a decision question that may carry `ignore previous instructions`, role tags,
  verdict-flip text), and auto-injecting it would replay that into context every session. The sample
  lives only in `recall --json` (agent-pulled on demand, never auto-injected).
- **Secret-scrub before storage.** `sample` and `reasoning` pass through `_scrub_secrets` (a Python
  port of `hooks/_scrub.sh` `_secret_patterns` — keep the two in sync) *before* they are written, so a
  denied `curl … Bearer …` / `mysql -p…` / connection-string leaks no credential to the KB on disk or
  to `recall --json`. Injection-*phrase* blocklisting is deliberately NOT attempted (unwinnable); the
  defense is "don't auto-inject the sample" + "scrub secrets", not phrase filtering.
- **Resolution selection is not attacker-steerable.** Decision-review rules match on the **derived
  reason class** (`_reason_class`, computed from the tribunal's own trusted `high_blast` / verdict /
  reasoning fields), never on free-text over the sample; the correct-by-design (high-blast / security)
  rules are ordered **first** so a permissive rule can't be pre-empted by planted text.

Plus the ordinary hook-hygiene invariants:

- **Stdlib-only, no network.** Nothing new to install.
- **Exits 0 on every internal/runtime error.** Every subcommand is wrapped; an error prints a
  diagnostic to stderr and the process still exits 0, so a hook calling it can never break a session.
  (The one non-zero exit is an argparse *usage* error — a missing/invalid subcommand exits 2 — which
  the hooks never trigger.)
- **Silent when idle.** No comfort-posture → no denials → no KB → both hooks no-op with no output.
- **Read-only of the substrate.** It never mutates the tribunal's records or its live path; it only
  appends to its own KB files under the gitignored `.ravenclaude/runs/thing/`, via a per-process
  atomic write (the dual plugin+dev-mirror wiring can run `sync` concurrently at SessionStart).

## Timing boundary (honest limitation)

`sync` runs on `Stop` and `recall` surfaces at `SessionStart`, so a **brand-new** denial shape (not
already in the KB from a prior session) is recorded at end-of-turn but not surfaced back into context
until the *next* session. So the "identify + solve" loop is immediate for **recurring** shapes and
one-session-delayed for a genuinely first-seen one. This is a deliberate v1 tradeoff of the hot-path
safety constraint (nothing runs at deny time on the tribunal's live path). The `record` subcommand
already echoes the matched resolution in-band and is the seam a future opt-in `PostToolUse`-on-deny
capture would use to close the gap without touching the tribunal.
