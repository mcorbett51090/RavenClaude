# Autonomous 3-panel repo review — decisions that need your judgment (2026-07-08)

**Run:** three-panel review (Panel 1 find → Panel 2 validate → Panel 3 tie-break) over the repo's
entire executable surface — **208 files / 22 batches** (all `scripts/*.py|sh|mjs`, `ravenclaude-core`
engine + hooks, the finance engine + connectors, ~100 domain calculators, and the 6 CI workflows).
**35 findings confirmed:** 5 P1, 18 P2, 12 P3 — **no P0**. 31 were mechanically fixable and are
implemented in the accompanying PR (grouped by priority). This document covers the **4 findings the
panels flagged `design_required`** — each rests on a decision that changes security/tribunal/finance
semantics, so I'm surfacing them rather than choosing unilaterally.

For each: the defect, why it needs you, the options with my recommendation, and a link to the code.

---

## 1. `bind_entitlement_to_identity` honors an expired entitlement token (P1)

**Code:** [`plugins/finance/scripts/entity_rls.py:139-185`](../../plugins/finance/scripts/entity_rls.py#L139)
· test: [`test_warehouse_rls.py:236`](../../plugins/finance/scripts/test_warehouse_rls.py#L236)

**Defect.** `bind_entitlement_to_identity` binds `allowed_entities[]` to a SoD-verified identity after
checking only `identity.verified` and the `iss/sub` binding — it takes no `now` and **never validates
the entitlement token's `iat`/`exp`/`ttl`**. An entitlement (warehouse-embed) token that expired hours
ago, replayed alongside a freshly-verified identity carrying the same `iss/sub`, is honored and returns
the full grant with reason `'ok'`. This contradicts the file's own stated deny-all-on-expiry invariant
(lines 19-24), which the *sibling* `resolve_from_claim`/`validate_claim` path does enforce. The gap is
structural, not incidental: the passing test `test_entity_rls_bind_split_brain` feeds `good_claims`
with **no `iat`/`exp`** and expects a successful bind — so `bind` is blind to freshness by construction.

**Why P1 not P0 (and why it's contestable):** this file is explicitly a *reference resolver*, not a
live-verified authz system — it verifies no signature and enforces nothing at the DB, and the parallel
`resolve_from_claim` path does check expiry. But the `idp-segregation`/`warehouse-dashboard` skills
position `bind` as the authorization decision, and a caller who trusts its docstring contract (which
enumerates fail-closed conditions *as if exhaustive* but omits freshness) would wrongly assume expired
tokens are rejected.

**The decision (why I can't just "add `validate_claim`"):** `validate_claim` demands `iat`/`exp`, but
the current tested `entity_claims` shape for `bind` omits them. So the fix forces a contract choice:

| Option | What it means | Trade-off |
|---|---|---|
| **(a) `bind` validates its own envelope** | Require the bind-path entitlement token to carry `iat`/`exp`; add a `now` param; call `validate_claim`; fail closed with `'split-brain: entitlement token expired/invalid'` on any envelope failure. Update `good_claims` + tests. | Strongest (fail-closed at the bind seam) but a **breaking change** to the tested claim shape and every caller that builds a bind claim. |
| **(b) `bind` accepts only an already-validated claim** | Formally document + enforce that `resolve_from_claim`/`validate_claim` MUST run first; `bind` accepts only a validated claim object. | Smaller code change; pushes the obligation onto the caller (and onto the docstring being read). |

**My recommendation: (a)** — fail-closed at the seam is the right default for anything shaped like an
authz decision, even a reference one, and the "someone trusts the contract" failure mode is exactly
what (b) leaves open. It's a breaking change to the claim shape, which is why it's your call.
**Either way**, add the regression test the panel specified: *an expired entitlement token with matching
`iss/sub` yields `[]` (deny-all) through the bind path.*

---

## 2. A lone Heimdall abstention drops injection screening from the tribunal (P2)

**Code:** [`plugins/ravenclaude-core/scripts/thing-decide.py:426-473`](../../plugins/ravenclaude-core/scripts/thing-decide.py#L426)
(abstention gate at `:449`, seat briefs at `:135-140`, `_SEATS` at `:59`)

**Defect.** In `decision_review: binding` mode, `_tally` sets `injection` only from seats that **voted**,
and the escape-to-`defer` gate fires only at `abstained >= 2`. Since `_SEATS = (forseti, mimir,
heimdall)` and **Heimdall is the only seat tasked with injection detection** (Forseti judges safety,
Mimir judges rules/facts), a single Heimdall abstention (timeout/error) leaves `abstained == 1` — below
the gate — and the panel proceeds on Forseti+Mimir alone. If those two return a unanimous confident
`'yes'` on a smuggled framing, the panel returns a **binding `'yes'` with injection never assessed** and
no Thor convened. Unlike `thing-decision.py`'s tier model (which has a mandatory-security-seat concept
at `extreme` tier), the decision path has no rule forcing a defer when the *specifically-mandatory*
injection seat is the one that abstained.

**Why P2 (bounded):** the feature is off by default, only binding mode auto-resolves, and the
deterministic `_screen_high_blast` + high-blast-defer keep any **irreversible** decision from
auto-resolving — so only *reversible* decisions can slip through. A reviewer weighting injection-defense
integrity could hold P1; that's the ambiguity.

**The decision.** Both fixes are small; they differ in posture. The engine already knows which role
abstained (the loop counts them):

- **(a) Heimdall-abstain → `defer` directly** (simplest; mirrors the existing `injection → defer` branch).
- **(b) Heimdall-abstain → force a Thor convene** that re-screens injection before resolving.

**My recommendation: (a)** — deferring a *reversible* decision to the human when injection screening
couldn't run is the fail-safe default and matches the documented safety envelope (injection → defer);
(b) adds a seat spawn + latency for a case that is already rare. This changes tribunal outcomes (more
defers under Heimdall timeouts), which is why I'm not changing it unilaterally. Add the mock-driven
tally test (`THING_DECIDE_MOCK_VERDICT` supports per-seat mocking): *Heimdall abstain + Forseti/Mimir
unanimous `yes` → must be `defer`, not `yes`.*

---

## 3. Heredoc-write-then-execute slips past `guard-destructive.sh` (P2)

**Code:** [`plugins/ravenclaude-core/hooks/guard-destructive.sh:153-161`](../../plugins/ravenclaude-core/hooks/guard-destructive.sh#L153)

**Defect.** `_strip_heredoc` collapses a quoted heredoc body that feeds a **non-interpreter** target
(`cat <<'EOF' > /tmp/x.sh`) to the placeholder `<<HEREDOC` *before* the deny-pattern / structural
`rm`/`dd` checks run. That blanking is **correct** for the false-positive it was built for (writing text
that documents `rm -rf` should not trip the guard). The gap: the heredoc regex terminates at the tag, so
a trailing `bash /tmp/x.sh` **survives** in the scanned string — but after the body is blanked there is
no `rm` token left to match, and nothing resolves/scans the target of a `bash|sh|source <file>` call.
Net: `cat <<'EOF' > /tmp/x.sh\nrm -rf /\nEOF\nbash /tmp/x.sh` as **one Bash command** is allowed.

**Why P2 (bounded), and the honest scope limit.** This only bites a consumer whose *only* destructive
protection is this hook — no OS container/worktree, no tribunal — the exact minimal posture the plugin's
own "Containment posture" docs warn against relying on. The **broader** Write-tool / two-tool-call
variant (write the script with one call, execute with another) is an *inherent* limit of any
command-string scanner and is explicitly assigned to the OS layer, **not** fixable in this file.

**The decision.** The panel scoped a *bounded, closable* fix and explicitly warned off the general one:

- **Do:** in `_strip_heredoc`, when the heredoc target is a file **and** the surrounding command string
  later references that same path via an interpreter (`bash|sh|dash|zsh|source|. <path>` or `./<path>`),
  **do not blank the body** — treat it like an interpreter heredoc (mirroring the existing
  `_heredoc_feeds_interpreter` branch) and let the structural checks see the `rm -rf`. Add a test
  fixture for the same-command write-then-execute case, and document in the header that
  *cross-tool-call* write-then-execute is out of scope by design (OS containment owns it).
- **Do NOT:** attempt the general "resolve and scan any `bash <file>`" fix — the target often doesn't
  exist at hook time, can be written by a parallel tool call, and is reachable via `printf`/`tee`/`base64`
  anyway.

**My recommendation: implement the bounded same-command fix** (it's a real, closable hardening) **and**
add the header scope note. I left this for you because it's a security-guard behavior change to a
false-positive-sensitive code path — I want your sign-off on the exact interpreter-reference match set
before touching the deny path. (If you'd rather, `security-reviewer` can own the diff.)

---

## 4. Rotating-provider refresh silently reuses the just-invalidated prior token (P2)

**Code:** [`plugins/finance/scripts/connectors/oauth_client.py:266-271`](../../plugins/finance/scripts/connectors/oauth_client.py#L266)

**Defect.** `new_refresh = body.get('refresh_token') if rotating_refresh else None`, then
`refresh_token = new_refresh or body.get('refresh_token') or prior_refresh`. For a **rotating** provider
(qbo/xero) whose 200 response omits `refresh_token`, both `new_refresh` and `body.get('refresh_token')`
are `None`, so the result is `prior_refresh` — a token the provider's rotation may **already have
killed** — persisted atomically as if valid. The next refresh then fails `invalid_grant → ReauthRequired`,
deferring a lockout that was **detectable one cycle earlier**. This contradicts the module's central
invariant (correct handling of rotating refresh tokens is its entire reason for existing). The middle
`or body.get('refresh_token')` is dead code in the rotating branch. *(For non-rotating providers the
`prior_refresh` fallback is correct and must stay.)*

**Why P2 (contestable vs P3):** the failure is still *eventually* detected rather than silently lost —
but it violates the stated invariant and defers a detectable lockout, so P2 is defensible.

**The decision — fail-closed vs. grace-window reuse:**

| Provider | `grace_seconds` | Behavior to choose |
|---|---|---|
| **qbo** | `0` | **Always fail** on a rotating 200 that omits `refresh_token` — fire `self._alert('missing_rotated_refresh')` and raise `TokenRefreshError`/`ReauthRequired`. |
| **xero** | `> 0` | Reusing `prior_refresh` **within the grace window** may be legitimate — gate the fallback on the grace window rather than reusing unconditionally. |

**My recommendation: gate on the grace window** — fail closed when `grace_seconds == 0`, allow the
`prior_refresh` reuse only inside a positive grace window, and alert in both cases. This preserves
xero's legitimate grace behavior while closing qbo's silent-reuse. It's a behavior change to live
token-rotation handling against real providers, so I want your confirmation on the grace-window
semantics before shipping it. Remove the dead middle `or` in the rotating branch either way.

---

## Summary

| # | Finding | Pri | My recommendation | Your call is about |
|---|---|---|---|---|
| 1 | `entity_rls` bind honors expired token | P1 | (a) bind validates its own envelope, fail-closed | Breaking the tested claim shape |
| 2 | Lone Heimdall abstain drops injection screening | P2 | (a) Heimdall-abstain → `defer` | Changing tribunal auto-resolve outcomes |
| 3 | Heredoc write-then-execute past guard | P2 | Bounded same-command fix + scope note | A security-guard deny-path change |
| 4 | Rotating refresh reuses invalidated token | P2 | Gate reuse on `grace_seconds` window | Live OAuth rotation semantics per provider |

Reply with **keep / adjust / drop** per row (or "do all four as recommended") and I'll implement the
chosen options with the regression tests each finding specifies. Everything else from the review is
already in the PR.
