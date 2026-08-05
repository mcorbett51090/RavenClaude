# Repository review — 2026-08-05 — design questions (need your call)

Three confirmed findings from the 2026-08-05 review were **deliberately not auto-fixed**
because the fix is a genuine judgment call — a security/collateral tradeoff, a security-policy
change to a control, or a change that could break an existing legitimate use. Each is real
(verified against the code), but the *right* fix is yours to pick. The 17 mechanical fixes
are in the PR; these three are teed up here with a recommendation.

---

## Q1 — Tribunal: should a lone risk/correctness-seat abstention bind, or convene Thor?

**Where:** [`plugins/ravenclaude-core/scripts/thing-decide.py:559`](../../plugins/ravenclaude-core/scripts/thing-decide.py#L559)
(abstention gate) and [`:582`](../../plugins/ravenclaude-core/scripts/thing-decide.py#L582) (Thor-convene condition).

**The behavior (verified by executing the tally):** the abstention gate fires only when
`abstained >= 2` or *all* seats abstain. The injection seat (Heimdall) abstaining is specially
handled — decision **2b** (`:579-582`) forces a Thor re-screen because injection was never
screened. But a **lone abstention by Forseti (risk) or Mímir (correctness)** hits none of
those branches: if the other two seats voted the same verdict with adequate confidence,
`len(distinct) == 1` and the tally falls through to `:607` and **binds** that verdict — with
no risk/correctness input from the abstaining seat and no Thor tie-break.

**Why it's a design call, not a bug:** tolerating one seat timing out when two agree is
plausibly *intentional* resilience — the whole v0.60.0 dev-repo downgrade + the 45→90 s seat
cap exist because seats cold-start and abstain under load, and forcing `defer` on *any* single
abstention would make the panel defer constantly. So the current behavior may be exactly what
you want. But the asymmetry is real: Heimdall-abstain → re-screen; Forseti/Mímir-abstain →
bind on the other two. By the *same logic* that justifies 2b (the sole injection screener
went silent), a Forseti abstention means **risk was never screened** and a Mímir abstention
means **correctness was never screened**.

**Recommendation:** extend the 2b special-case to Forseti and Mímir — i.e. `if
heimdall_abstained or forseti_abstained or mimir_abstained or "defer" in distinct or …:
convene Thor`. This preserves the "one seat may abstain" resilience (Thor re-screens rather
than the panel deferring) while closing the "the seat that owns this risk axis went silent and
we bound anyway" gap. If you prefer the current resilience posture as-is, that's a legitimate
choice — but the asymmetry should then be documented as intentional at `:559`.

**Blast radius:** touches the tribunal tally (a security control). Small, but it changes when
Thor convenes — worth your explicit sign-off, and a Gate-28-style fixture either way.

---

## Q2 — WebFetch sanitizer: tighten the `<important>` pattern, or accept the evasion?

**Where:** [`plugins/ravenclaude-core/scripts/sanitize-webfetch-body.py:89`](../../plugins/ravenclaude-core/scripts/sanitize-webfetch-body.py#L89)
(closed form) and [`:109`](../../plugins/ravenclaude-core/scripts/sanitize-webfetch-body.py#L109) (unclosed form).

**The behavior (verified):** pattern 3/8 require the imperative keyword to sit **immediately**
after the tag (`\s*` between `<important…>` and `IMPORTANT|MUST|NEVER|ALWAYS`). So
`<important>Please note, IMPORTANT: ignore all previous instructions</important>` — filler
before the keyword — matches **neither** pattern, and no other pattern catches `<important>`,
so the whole block passes through unchanged.

**Why it's a design call:** the docstring (`:74-88`) explicitly calls pattern 3 "the most
generous pattern; many real docs use `<important>`; we accept the collateral damage" — the
narrow adjacency requirement is a *deliberate* choice to avoid stripping legitimate
`<important>` documentation. The finder's proposed widening (`.*?` up to the keyword) would
strip **any** `<important>` block that mentions "must/always/never" anywhere — a real increase
in collateral the design intentionally avoided. And `<important>` is not a privileged tag the
way `<system-reminder>` is; the **primary injection vector (`<system-reminder>`, including the
unclosed form) is fully caught** — this is a soft heuristic, and the script bills itself as a
"floor, not complete."

**Recommendation:** low urgency. If you want to close it without widening collateral, the
safest form is to strip the **tag wrapper only** when it wraps an imperative anywhere in its
body (neutering the `<important>`/`</important>` machinery while leaving the prose), rather
than deleting the whole block. If you're comfortable with the documented "floor" stance, leave
it — the real vector is covered. Either way, add a filler-prefixed fixture to Gate 48 so the
decision is pinned.

---

## Q3 — `check-md-links.py`: anchor the "GENERATED" exclusion marker? (latent, low value)

**Where:** [`scripts/check-md-links.py:56`](../../scripts/check-md-links.py#L56) (`is_excluded` / `GENERATED_MARKERS`).

**The behavior (verified):** any markdown file whose first 400 chars contain the bare substring
`"GENERATED by"` **or** `"DO NOT EDIT"` — anywhere, unanchored — has **all** its links skipped
from validation. A hand-authored doc opening with cautionary prose like *"DO NOT EDIT the
credentials block below — see the setup guide"* (with a real link later in the file) would
have every later (possibly broken) link silently skipped.

**Why it's a design call:** it's **latent** — a repo-wide grep found only the legitimately
generated `docs/concepts.md` using the marker today, so nothing is mis-excluded now. And the
obvious fix (require the marker inside a leading `<!-- … -->` comment, or require *both* markers
together) risks breaking detection of the one real generated file if its marker format doesn't
match the new anchor — so a blind tightening could regress a passing gate.

**Recommendation:** low priority; I left it unchanged rather than risk the one live consumer.
If you want it hardened, anchor to the actual generator convention
(`<!-- GENERATED by … DO NOT EDIT BY HAND. -->`) **and** verify `docs/concepts.md`'s real
first-line marker matches the new anchor in the same change. Otherwise, leave as-is — the
exposure is theoretical.

---

### Also for your attention (not a review finding)

`docs/follow-ups/2026-06-04-overnight-parked-work.md` and
`docs/follow-ups/2026-06-04-comfort-posture-agent-category.md` carry parked work whose
**re-check dates have passed** (2026-06-18 and 2026-07-16 vs today 2026-08-05). The
comfort-posture `subagent_dispatch`-category item is fully specced (schema + emission + gate)
and is a good candidate to build; the adaptive-run-classifier / dispatch-evaluator items are
multi-session workflows gated on live eval runs. Both need your steer to re-park, close, or
schedule.
