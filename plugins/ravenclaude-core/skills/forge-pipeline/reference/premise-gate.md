# G3b — the premise gate (full contract)

> Loaded when a run reaches G3b (**quick** and above). `micro` skips it — it runs no panels, so there
> is no `depends_on_claims` edge to check.

## The incident this gate exists for

2026-08-08. A probe of a Cloudflare email-obfuscation href returned **404**. From that single negative
result an agent concluded *"the decoder is broken, therefore every visitor sees a mangled address"* and
built on it: an 85-line component, 10 converted call sites, 15 addresses opted **out** of anti-scraping
protection, an owner go-live checklist item, and two turns of architectural advice to the owner.

**All of it was wrong.** That URL is an href placeholder that nothing fetches — it is *supposed* to
404. The real decoder returned 200, `/cdn-cgi/trace` returned 200, and a real browser against the
supposedly-broken production site showed **zero** mangled spans. No user ever experienced the defect.

Cost asymmetry, which is the entire argument for this gate: the disconfirming probe cost **~10
seconds**; the construction cost hours, touched 16 files, and reached the owner's cutover checklist.

⛔ **The wrong hypothesis was not the failure.** Wrong hypotheses are cheap and normal. The failure was
the hypothesis being **silently promoted to a premise by being written down**, after which every
downstream artifact cited it instead of re-testing it. Nothing in the process ever returned to ask.

## Why G1 does not catch it

G1's BLOCK/WARN split keys on **provenance** — *is this claim sourced?* The false claim **was** sourced:
an in-session `curl`, exactly the grounding G1 accepts as WARN-and-continue. G1 has no notion of
**inferential distance**:

| | claim | true? |
|---|---|---|
| observation | `GET /cdn-cgi/l/email-protection` returned 404 | ✅ yes |
| inference | the decoder is broken, every visitor is affected | ❌ no |

The observation was true. The inference drawn from it was false. **Grounding an observation is not
grounding an inference drawn from it** — that is the gap, and `kind` is the column that closes it.

## Trigger — three conjuncts, all required

1. **`kind: inference`** on the cited claims-table row, as typed by `${CLAUDE_PLUGIN_ROOT}/scripts/classify_claim.py`
   (grammatical, **upward-only**: an author may raise a row to `inference`, never lower it — which is
   what makes it not-self-report).
2. **Cited by a build phase** via that phase's `depends_on_claims: [...]`. This conjunct is the friction
   collapse: most inferences in a plan are never load-bearing for construction, so the gate stays quiet.
3. **Blast radius over the floor** — the phase creates a new module/abstraction, or touches more files
   than the floor.

⛔ **Confidence is not a conjunct, and that is deliberate.** At the moment of the incident the author
was *confident*, with a real tool call behind them. Any gate keyed on self-reported uncertainty would
not have fired. Every conjunct above is read off **artifacts**, never off the author's state of mind.

## Conjunct 2 is the one that gets silently broken

G3b **reads** `depends_on_claims` off the plan. If the G2/G3 plan contract does not **emit** it, the
gate runs, finds no claim edges, and passes green **while checking nothing**.

That defect shipped in a draft of this very design — the trigger was specified against a field the plan
schema never added, and the accompanying gate supplied the field in a **synthetic fixture**, so the gate
would have been green while inert in production. **A fixture is not a wiring proof.** If you change the
plan schema, re-verify against a real plan, not a fixture.

## Three exits — none of them is "block and stop"

| exit | when | effect |
|---|---|---|
| **`probe-run`** | `cost ≤ CHEAP_FLOOR` (default 300 s) | Probe executed, result recorded. Claim → `settled` or `falsified`. **A `falsified` claim voids every citing phase.** |
| **`probe-deferred-with-cheapest-partial`** | the full kill-shot needs prod or credentials, but a cheaper partial exists | The partial is **mandatory**. (The incident's partial: one real-browser load of the **public** site — no credentials, ~10 s.) Status `partially-settled`. |
| **`owner-gated`** | genuinely needs the human | **Does not block — reshapes.** Every citing phase is capped to a single reversible file, feature-flagged, and the exact question is emitted into G0's open questions. Non-citing work proceeds. |

Every exit other than `probe-run` **must** write an inline
`[unverified — premise not disconfirmed: <reason>]` marker into the artifact's own header, using the
repo's existing Claim-Grounding marker vocabulary. A marker spoken in chat and absent from the file
launders into an unmarked, trusted-looking prior — the Memory Engineering Protocol's Rule 1 failure.

## A control, not just a probe

A probe and a **control** are different things, and the incident turned on the difference. Before a
negative result licenses a conclusion, a **positive-capable** probe on the same subsystem must have
been observed — otherwise you cannot tell "the subject is broken" from "I probed the wrong thing."

Each claim therefore carries `expected_if_true` and `expected_if_false`, and **they must differ**. If
they do not, the probe cannot discriminate and does not settle anything, however green it comes back.
`rc probe` (engine: the plugin's `bin/probe-kit.sh`) ships ready-made control probes for the common subsystems.

## Exit codes (a contract — do not conflate)

| code | meaning |
|---|---|
| `0` | clean — no unsettled inference is cited by a phase over the floor |
| `2` | tripped — an unsettled inference is load-bearing; take one of the three exits |
| `1` | **could not run** — malformed run dir, unreadable plan, no claims table |

⛔ `1` is never "clean". A checker that cannot see must not report clean: those two outcomes are
indistinguishable afterward, which is exactly how a green gate ends up protecting nothing.
