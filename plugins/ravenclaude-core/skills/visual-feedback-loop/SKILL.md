---
name: visual-feedback-loop
description: "Render → see → critique → edit → re-render: the discipline (and a deterministic referee) that lets an agent inspect its OWN rendered output — a web page, a dashboard, a Power BI / Tableau report — and iterate toward correctness/pixel-perfection against objective stopping signals instead of 'looks better'. The referee (driver.py) merges the pbir-layout-engine layout linter with agent-captured console/Lighthouse evidence into one pass/fail verdict. Use when building or refining any visual surface; the standalone canon is knowledge/visual-feedback-loop.md."
---

# Skill: visual-feedback-loop

## What this is

A render-loop **referee** plus the discipline that wraps it. The agent that builds
a visual surface should not work blind: it renders, **sees** its own output, judges
it against the intent **and** objective signals, edits, and re-renders — until the
signals pass. This skill provides the deterministic "are we done yet?" half so the
loop **converges** instead of wandering on subjective taste.

The full conceptual canon — the loop, the two ways to "see", the surface→mechanism
map, the security rules — lives in
[`../../knowledge/visual-feedback-loop.md`](../../knowledge/visual-feedback-loop.md).
This SKILL is the operating reference for the runnable piece.

## The two ways an agent "sees"

| Mode | How | Best for |
|---|---|---|
| **Visual** (pixels) | Drive a real browser via the `chrome-devtools-mcp` server → `take_screenshot` (the model literally sees it), `list_console_messages`, `lighthouse_audit` | Web pages, web dashboards, embedded BI — catching "looks wrong" |
| **Structural** (coordinates) | Read the layout definition's exact numbers — PBIR JSON `x/y/width/height` via the [`pbir-layout-engine`](../pbir-layout-engine/SKILL.md) linter; the DOM/accessibility tree for web | **Power BI / Tableau pixel-perfection** (layout is just numbers — more reliable than vision), and any surface where the definition is inspectable |

**Structural-first for BI.** For Power BI / Fabric / Tableau the *primary* loop is
structural (the coordinate linter), because (a) layout correctness is exact
arithmetic, not a judgment, and (b) screenshotting a BI report needs it
published/embedded + authenticated, which the agent often can't reach. Screenshots
are the *secondary* check for what coordinates can't show (did the theme apply, did
conditional formatting fire, does it overlap once real data loads). For **web**, the
screenshot is first-class.

## The referee — `driver.py`

`driver.py` is **NOT** a browser driver. It cannot navigate Chrome or run
Lighthouse — that is the agent's job via `chrome-devtools-mcp`. It is the
**referee**: given the evidence the agent has captured, it merges it into one
verdict with an objective `next_action`. It earns its existence by fanning **three
independent evidence sources** into one verdict — something the layout linter alone
structurally can't do.

### CLI contract

```text
python3 plugins/ravenclaude-core/skills/visual-feedback-loop/driver.py <config.json>
```

`<config.json>` (every path is repo-relative, `..`-free, inside the repo root):

```json
{
  "surface": "web | web-dashboard | pbir | fabric | tableau | bi",
  "layout": "path/to/page.json",          // optional → delegated to pbir-layout-engine
  "parity": {                              // optional → structural diff vs. a known-good exemplar
    "candidate": "path/to/failing/visual.json",
    "reference": "path/to/confirmed-working/visual.json"
  },
  "console": "path/to/console.json",       // optional → agent-captured browser console
  "lighthouse": "path/to/lighthouse.json", // optional → agent-captured Lighthouse run
  "thresholds": {                          // optional — overrides the defaults
    "lighthouse_accessibility_min": 90,
    "lighthouse_performance_min": 80,
    "lighthouse_best_practices_min": 80,
    "max_console_errors": 0
  }
}
```

**The `parity` gate — diff against a known-good exemplar** (a structural diff
surfacer, **not** a render oracle — it is only as good as the reference you pick).
A visual can be *perfectly placed* yet render **blank** because its render skeleton
is missing something its working twin has. Point `candidate` at the suspect
`visual.json` and `reference` at a confirmed-working `visual.json` **of the same
`visualType`**. The gate is **asymmetric**: it **fails**
(`next_action: match-reference-exemplar`) on what the candidate is **MISSING**
relative to the exemplar — a missing query role (`Values`/`Data`/`Indicator`), a
dropped objects key (e.g. a `card` that dropped `labels` and substituted
`calloutValue`), or a missing per-item `$id` — and **passes benign additions** (an
extra cosmetic object key, an optional role). It reports `not_captured` (never a
false fail) for a different `visualType`, a non-PBIR shape, a **self-reference**,
or a **degenerate exemplar** (no query role — it refuses to launder a bad reference
into a pass). Highest-leverage move when a deploy renders blank with no error:
replicate the nearest *genuinely-working* exemplar instead of guess-and-check.
(PBIR `visual.json` today; the *technique* generalizes — see the canon.)

**Agent-captured evidence shapes** (the contract you fill from `chrome-devtools-mcp`):

- `console.json` — `{"messages": [{"level": "error|warning|info"}, ...]}` (the
  driver counts `level == "error"`; it never reads the message text).
- `lighthouse.json` — Lighthouse's native shape `{"categories": {"accessibility":
  {"score": 0.96}, "performance": {"score": 0.85}, ...}}` (scores are 0–1; the
  driver surfaces them as 0–100 and compares to the threshold).

### Exit codes & verdict

| Exit | Meaning |
|---|---|
| `0` | `passed: true` (clean) **or** `passed: null` (nothing determinate to judge / needs more evidence / manual review). **Absence of a browser tool is NOT a failure.** |
| `1` | `passed: false` — a determinate gate failed |
| `2` | I/O, parse, oversize (>5 MiB), or path-rejection (`..` / outside repo) — the purity-contract failure |

The JSON envelope: `{schema_version, driver_version, surface, passed, gates[],
next_action, notes}`. `passed` is a **pure function of the determinate gates**
(`pass`/`fail`/`error`); `not_captured` and `degraded` gates are excluded — so
"evidence not captured yet" and "tooling absent" are first-class states, never
silent failures. `next_action` is the loop's instruction: `ship` /
`capture-runtime-evidence` / `fix-layout` / `match-reference-exemplar` /
`fix-console-errors` / `improve-accessibility` / `manual-visual-review`.

### How the layout gate maps the linter's exit codes

`driver.py` calls `pbir-layout-engine/lint.py` as a **subprocess** (`--format json`),
never an import — it treats the linter as a CLI with a versioned envelope, so the
linter's internals are not a dependency, and it asserts the linter's
`schema_version` matches what it was built against (loud on drift). The mapping:

| linter exit | driver gate status | meaning |
|---|---|---|
| `0` | `pass` | layout clean |
| `1` | `fail` | a layout check fired |
| `2` | `error` (→ overall fail) | the layout JSON itself is broken |
| `3` | `degraded` (excluded from `passed`) | the PBIR `visualType` enum reference is absent/unparseable — e.g. `ravenclaude-core` installed without `power-platform`. Could-not-verify, **not** a failure. |

## The loop (how the agent uses this)

1. Build / edit the surface.
2. **See it.** Web: via `chrome-devtools-mcp` → `navigate_page`, `take_screenshot`
   (look at it), save `list_console_messages` → `console.json` and
   `lighthouse_audit` → `lighthouse.json`. BI: read the PBIR page JSON.
3. **Referee.** Run `driver.py <config.json>` pointing at the evidence + layout.
4. Read `passed` / `next_action`. `false` → do the `next_action` and loop.
   `null` → capture the missing evidence (or do the named manual review) and loop.
   `true` + `next_action: ship` → done.
5. The screenshot is for *your* eyes (the model's visual judgment); the referee is
   the objective floor. Use both — vision catches "ugly", the referee catches
   "wrong", and the referee is what tells you when to **stop**.

## Security invariants (load-bearing — see the knowledge file for the full rules)

- **Path safety.** Every input path is resolved through the same rule as the layout
  linter (reject `..`, reject outside-repo). Reimplemented in `driver.py` (not
  imported, to stay decoupled from the linter's internals); **Gate 100 asserts the
  two guards reject the same traversal input** so they can't drift.
- **Size ceiling.** A 5 MiB cap is enforced *before* `json.load` on every file — a
  malicious page can write an unbounded `console.json`.
- **No-echo.** The verdict carries **only** driver-derived primitives — booleans,
  counts, numeric scores/thresholds, and fixed-vocabulary strings. It **never**
  echoes raw console text, Lighthouse titles, or page content: a hostile page can
  write fake "instructions" to the console, and the model reads this verdict back as
  trusted context. The driver reads *numbers* out of evidence, never prose.
- **MCP adoption gate.** `chrome-devtools-mcp` drives a **live** browser
  (stateful, side-effecting); it is **recommended-not-bundled** and its adoption is
  `security-reviewer`-gated. Do **not** point a credentialed/networked render loop
  at attacker-influenced URLs — render untrusted dashboards against synthetic/fixture
  data, or in an isolated profile with no credentials. Launch with
  `--no-usage-statistics`. Screenshots/evidence write to
  **`.ravenclaude/runs/<session>/visual-evidence/`** (already git-ignored) and are never
  committed (a dashboard can render real PII/secrets).

## Proven by Gate 100

[`scripts/audit-gates.sh`](../../../../scripts/audit-gates.sh) Gate 100 +
[`hooks/tests/test-gate100-visual-feedback-loop.sh`](../../hooks/tests/test-gate100-visual-feedback-loop.sh)
\+ the fixtures under [`tests/fixtures/visual-feedback-loop/`](../../../../tests/fixtures/visual-feedback-loop/)
are the bidirectional floor: good fixtures pass, bad fixtures fail, a `..` config is
rejected (and the linter rejects the same shape — path-guard parity), and an
always-pass mutant lets a known-bad through (teeth).

## Output Contract

When a reviewer critiques a render-loop integration in a PR, the response ends with
the cross-plugin Structured Output JSON block per
[`../structured-output/SKILL.md`](../structured-output/SKILL.md).
