# caveman-auto-routing.md — caveman auto-routing knowledge file

This file is named as a deliverable in both P5 and P7 of
`.ravenclaude/runs/forge/caveman-routing-decision-tree/plan.md`. P5's own acceptance test (c)
requires *"a dated addendum… committed now"* — that addendum is the section below. P7 will later
add the full contract (Q1–Q4 decisions with runners-up, the runtime version-drift resolution
order, the kill-switch procedure, and the honest limits carried verbatim from the plan) once the
live-shadow soak closes P7's own two-stage entry gate. Nothing in this file is a claim that P7 has
run.

---

## 2026-09-03 — P5 offline replay calibration: the thresholds table's disconfirming probe

**What this is.** `caveman-route.py --replay <transcript>` streams an archived transcript through
the classifier turn-by-turn and emits the verdict trace it *would have* produced. This addendum
runs that mode across 12 real transcripts under `~/.claude/projects/` (P0.5 confirmed 5,534+ exist
on this host and that `caveman-stats.js --session-file <path>` runs non-interactively), correlates
the verdict trace against `caveman-stats.js`'s measured net-token estimate for the same transcript,
and reports the result honestly — including the part that came out weaker/reversed from naive
expectation, per the plan's own explicit instruction not to launder that away.

**Sample.** 12 transcripts: the 11 most-recently-modified **top-level session** transcripts across
this host's `~/.claude/projects/` tree (excluding `subagents/*.jsonl`, which are partial
sub-dispatch transcripts, not full sessions), spanning 6 distinct projects/worktrees, plus this
authoring session's own transcript (independently known tool-heavy, per P0.5's own positive
control) — which happened to also be the most-recently-modified file, so it needed no special
inclusion. Sizes ranged 5 KB–11.3 MB; turn counts 1–711.

| transcript | turns | density* | pct_off** | output tok | Est. net | net/turn |
|---|---:|---:|---:|---:|---:|---:|
| `967c7c3b…` (this session) | 136 | 0.853 | 0.412 | 142,236 | **+94,153** | 692.3 |
| `b4770ccf…` | 9 | 1.000 | 1.000 | 3,610 | **−4,546** | −505.1 |
| `5216c119…` | 38 | 0.921 | 0.711 | 53,458 | **+51,779** | 1362.6 |
| `318603d2…` | 53 | 0.981 | 0.642 | 68,486 | **+60,938** | 1149.8 |
| `40f3dcb2…` | 87 | 0.851 | 0.483 | 100,293 | **+77,508** | 890.9 |
| `878b95d0…` | 2 | 0.000 | 0.000 | 187 | **−2,153** | −1076.5 |
| `37b04c3e…` | 1 | 0.000 | 0.000 | 5 | **−1,241** | −1241.0 |
| `062f27a6…` | 451 | 1.073 | 0.882 | 403,484 | *excluded†* | — |
| `2f7a3803…` | 183 | 0.907 | 0.443 | 109,698 | *excluded†* | — |
| `b64cef65…` | 83 | 0.867 | 0.482 | 74,848 | *excluded†* | — |
| `d021398c…` | 58 | 1.034 | 0.828 | (n/a) | *excluded†* | — |
| `b3bd7749…` | 711 | (n/a) | (n/a) | (n/a) | *excluded†* | — |

\* `density` = unwindowed `tool_use_blocks / responses` over the **whole** transcript (the
classifier's own deduped aggregation, not the trailing-6 window `--replay` uses per turn — this is
a session-level summary statistic computed for this correlation only, not something the classifier
itself produces).
\** `pct_off` = fraction of the `--replay` trace's turn-by-turn verdicts that were `"off"`
(`pct_on` was 0.000 in every one of these 12 — none contained a sustained 4-response clean-prose
streak; expected, since this host's real sessions skew tool-heavy).
† **`caveman-stats.js` genuinely could not produce a net figure for 5 of the 12 transcripts** —
its own stdout states *"Mode was set mid-session — only output after the change is attributed"* and
excludes the whole span rather than guess. This is a real, load-bearing finding in itself (below).

### The finding, reported in two layers because the naive number is misleading on its own

**Layer 1 — the naive, full-sample correlation is POSITIVE, the opposite sign from the naive
expectation.** Across the 7 transcripts with a usable `net`: Pearson r(density, net/turn) = **+0.80**,
r(pct_off, net/turn) = **+0.55**. Taken at face value this says *more* tool-heavy sessions
correlate with *more* net savings — backwards from claims-table row 3's premise that a tool-dense
stretch is where caveman's rule overhead stops paying for itself.

**Layer 2 — the reversal is a confound, and controlling for it flips the sign to the expected
direction.** `caveman-stats.js`'s own net formula is (verified directly from its own output,
`docs/HONEST-NUMBERS.md`-cited): `net = tokens_saved − rule_overhead`, where `rule_overhead` is a
**flat** `1,250 tokens × turns` and `tokens_saved` is a **flat ~65% reduction applied uniformly to
whatever output tokens exist**, regardless of turn shape. Algebraically this collapses to
`net/turn ≈ 1.857 × (output_tokens/turn) − 1250` — and measured directly on this sample,
**r(output_tokens/turn, net/turn) = 0.99999999...** (as close to deterministic as floating point
allows). `caveman-stats.js`'s aggregate net is therefore driven almost entirely by **response
verbosity**, not tool-call density, by construction of its own model. In this small sample the two
shortest sessions (1 and 2 turns) happened to have both zero density *and* the lowest
output-tokens-per-turn — not because prose-only sessions are inherently terse, but because a
1–2-turn session is too short to be a real signal of anything, and its overhead dominates on pure
arithmetic. Excluding those two (`turns < 9`) and recomputing on the remaining **n=5** substantive
sessions: **r(density, net/turn) = −0.40, r(pct_off, net/turn) = −0.62** — moderate, and now in the
**expected** direction (more tool-heavy → lower net-per-turn). The single cleanest, least-confounded
data point in the whole sample — `b4770ccf…`, a sustained 9-turn session the classifier scored
`pct_off = 1.000` (every turn tool-heavy) — is also the only substantive-length session with a
**negative** net (−505/turn), exactly what the premise predicts.

### The honest verdict on row 3 (claims-table's load-bearing inference)

**Weak-to-moderate, and it took controlling for a confound to see it.** The signal exists (n=5,
r=−0.62, direction-consistent with the premise), but:

- **This is not a settlement.** n=5 substantive sessions is not enough to fit or validate any of
  the plan's specific `[unverified]` thresholds (`W=6`, the off-trigger's `≥2`/`≥1.0`, the 4-response
  on-streak). It is evidence the underlying *direction* of the premise is not obviously wrong — no
  more.
- **A genuine instrument mismatch, not just a small-sample problem.** `caveman-stats.js` produces
  **one aggregate number per session** (or per contiguous same-mode span); the classifier's replay
  trace is **turn-by-turn**. Correlating a single scalar against a whole trace necessarily throws
  away exactly the within-session shape-change signal row 3 is about (*"a session's shape can change
  mid-conversation"*) — the two instruments are at different granularities by construction, and no
  amount of additional whole-session sampling fixes that; it would need either a per-turn savings
  breakdown `caveman-stats.js` does not expose, or genuinely single-shape (all-tool or all-prose)
  sustained real sessions to compare cleanly, which are rare in this host's actual usage (every
  substantive session in this sample mixed both).
- **The mode-attribution exclusion (5 of 12, 42%) is itself informative.** A meaningful fraction of
  real transcripts on this host already had caveman manually toggled mid-session, which
  `caveman-stats.js` correctly refuses to attribute rather than guess. Any future, larger replay run
  should expect a comparable exclusion rate and budget the sample accordingly (i.e., sampling *more*
  than the number of comparisons ultimately needed).

**What this changes for P7's entry gate.** Per plan.md, *"if the shadow verdict does not correlate
with the measured net token delta, the thresholds change before the flip — or the flip does not
happen."* This addendum's finding is neither a clean pass nor a clean fail: it is **weak,
direction-consistent evidence once a real confound is controlled for, on a sample too small to
fit numbers from.** The honest reading is that offline replay on this host's available corpus
cannot, by itself, settle the thresholds precisely — which is exactly why plan.md sequences P7's
entry gate as **two stages**, not one: this addendum satisfies stage 1's spirit (replay run,
correlated, reported honestly — including the reversal and its cause) without pretending it
substitutes for stage 2's live shadow soak, which sees genuine per-turn behavior this instrument
mismatch cannot.

**Reproducing this analysis.** The transcript list, `--replay` invocations, and the pure-Python
Pearson-correlation arithmetic used above are one-off / not shipped as a plugin script (per the
plan's file table, only `caveman-route.py` itself — including `--replay` — is a P1/P5 deliverable).
Anyone re-running this: `python3 plugins/ravenclaude-core/scripts/caveman-route.py --replay
<transcript.jsonl>` for the trace, `node <caveman install>/src/hooks/caveman-stats.js
--session-file <transcript.jsonl>` for the net figure (same invocation P0.5 already verified
non-interactive), and a plain Pearson correlation over whatever pairs both instruments can produce
(watch for the mode-attribution exclusion above — a `net` field absent from `caveman-stats.js`'s
output means that transcript should be excluded, not treated as zero).
