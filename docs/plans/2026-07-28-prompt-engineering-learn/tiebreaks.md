# G4b — Tiebreak verdicts

Both top-ranked conflicts from `gap-delta.md` were settled **empirically in-session**, not by model
argument. Recorded here so G6 synthesis carries the verdict rather than re-litigating it.

---

## T1 — The DOM-ratchet divergence (A: +7/surface · B: ~+38/surface)

**Verdict: A's number is right, but B was not wrong — the disagreement was ARCHITECTURAL, not factual.**

Measured the real static-element cost of every panel in the shipped `dashboard.html` (html.parser,
`script`/`style` contents excluded — the same method Gate 132 uses):

```
panel-prompt-builder     4     <- JS-built: bare mount + noscript, UI rendered at activate()
panel-learn              5     <- content islanded into a JSON payload
panel-trees              6
panel-nidhoggr           7
...
panel-mimir             36     <- static card hosts in markup
panel-heimdall          39
```

A costed the page **Prompt-Builder-shaped** (4-7); B costed it **Mímir-shaped** (36-39). *Both are
accurate for the pattern they assumed.* The question was never "how many elements is this page" — it
was "**which construction pattern does this page use**", and neither plan stated that it was choosing.

**Ruling — use the JS-built (Prompt-Builder) pattern.** Two independent reasons, and the second is the
load-bearing one:

1. **Budget.** Gate 132 is at exact zero slack (6,114 / 7,000). ~9× cheaper is decisive when every
   element needs owner sign-off.
2. **Correctness — the content is inherently RUNTIME.** The page's whole job is "which host am I in,
   and is this project wired". That answer comes from a `/__host` read, cannot be known at generate
   time, and — per the binding detection contract in `scope-amendment-1.md` — **must degrade to an
   explicit "cannot determine" state** on a static host or a server that didn't inherit a session env.
   Static markup would bake in a verdict that is wrong or empty exactly when honesty matters most. The
   JS-built pattern's `<noscript>` fallback *is* the "cannot determine" state, for free.

**Resulting ask: ~+7 per surface** (nav relink +1, Control page ~+6) → **6,114 → 6,121** and
**7,000 → 7,007**, with the frozen tail lifted in lockstep to keep the ratchet monotonic.
Concept cards contribute **zero** (panel-learn is 5 static elements with its content islanded), so
concept authoring does **not** block on the owner gate — only the Control page and the relink do.

---

## T2 — Category naming (A: one shared "Prompt engineering" · B: two tier-specific names)

**Verdict: two tier-specific category names. This is a repo INVARIANT, not a preference — B is right.**

`plugins/ravenclaude-core/CLAUDE.md` (v0.136.0) states the Learn tab's categories are authored
**tier-pure** "so grouping within a tier never straddles the divide". Verified that this actually holds
in the shipped data, not just in prose:

```
categories: 12
categories straddling BOTH tiers: NONE
```

All 58 concepts across all 12 categories are tier-pure today. A single `Prompt engineering` category
used by both a `platform-fact` and a `ravenclaude-built` concept would be the **first** category in the
repo to straddle, and would render the same heading inside both the "How agentic AI works" and
"RavenClaude features" tiers — the exact confusion the invariant exists to prevent.

**No owner question is warranted here**; the answer is derivable and was derived. G6 picks the two
names, both tier-pure, and states them in the plan.

---

## T3 — Regen-chain coverage (each plan silent where the other is explicit)

**Verdict: UNION them — this is additive, not a conflict.** A names the router / committed-routes gates
for the new route (`check-shell-router.mjs`, `check-router-execution.mjs`, `check-committed-routes.mjs`);
B names steps A omits. A missing gate is a silent CI failure, never a saving. Note for G6: this session
independently proved the union is still incomplete in both plans — a shared-token edit staled
`feedback-report.html`, a **fifth** generated surface neither plan lists. G6 must enumerate generators
from `grep -l shared-tokens scripts/*.py`, not from either plan's prose.

---

## T4 — Plan A over-serializes (B's critique)

**Verdict: B is right; adopt B's sequencing.** A hard-gates Phase 3 (relink) → Phase 4 (Control page)
on a mergeable-conflict concern rather than a real dependency, and gates *all* implementation behind
pre-build owner ratchet approval. Per T1 the ratchet ask is now a **measured** +7 rather than an
estimate, and concept authoring is budget-free — so the owner gate blocks only the Control page and the
relink. Concept authoring, the render-pipeline work, and the knowledge-file projection all parallelize
ahead of it.

---

## T5 — `render-concepts.py` (both plans list it as work)

**Verdict: DONE — remove from both plans' scope.** Fixed and verified end-to-end this session: it now
discovers a Puppeteer-managed Chrome and supplies `PUPPETEER_EXECUTABLE_PATH`, but only as a repair —
attempt 1 remains puppeteer's own resolution so hosts that already work never switch engines and
committed SVG bytes cannot churn. A truncated-download guard rejects a cache entry with an executable
stub but no payload (verified bidirectionally against the real broken artifact). G6 should carry it as
a completed prerequisite, not a phase.
