# G4a — Critic brief (correlated-error hunt + premise attack + risk matrix)

The gap-delta catches where A and B DISAGREE. This gate catches where they AGREE on something wrong.

## Correlated errors (both panels share the blind spot)

### CE-1 — Both make the tool OWN `pac solution import`; the novel value is the reactivation pass
Both plans wrap `pac solution import` as the spine of the orchestrator. But that half is the LOW-value,
HIGH-maintenance half: `pac`'s flag surface evolves (G1 already showed two flags Microsoft now
discourages), and most real pipelines already run `pac import` via Power Platform Build Tools / ADO
tasks. BTCSI's own notes say "ADO pipeline wiring lives ADO-side." The genuinely novel, hard-to-get-
right, nobody-else-does-it part is **baseline → reactivate (baseline-aware, retry) → verify** via the
Dataverse Web API. **Mitigation:** make the reactivation+verify pass the spine and a fully usable
standalone path (`reactivate`/`verify` subcommands work without ever calling `pac`); keep the
`import` orchestration as a documented convenience that composes them — so the tool stays valuable even
where `pac import` is driven elsewhere. (This also satisfies B's standalone-reactivation use case.)

### CE-2 — Both assumed a NEW `scripts/` surface; the repo already answered this differently
Both inherited the framing "power-platform ships zero code → we're adding a new scripts/ surface" (which
inflated A's threat-model ceremony). But the plugin's ONE existing Python file, `dataverse-payload-
preflight/preflight.py`, lives **inside its skill directory** (verified in-session). The established
pattern is **script co-located with its skill** — discoverable next to its how-to, covered by existing
skill-dir globs, no "new surface" precedent to defend. **Mitigation:** co-locate the script in the new
skill dir (like preflight.py); drop the new-scripts/-surface framing and the heavyweight design-gate it
motivated.

### CE-3 — Both treat the `statecode` PATCH activation mechanism as settled; it is [unverified]
Both inherit from BTCSI that reactivation = PATCH `statecode`/`statuscode` on the `workflow` row, and
both add only a `[verify-at-use]` doc note. But the activation mechanism for MODERN cloud flows is the
load-bearing assumption the whole tool rests on, and G1 could not surface the enum/mechanism from
first-party docs (only that the Dataverse Web API is the supported transport). BTCSI confirmed it
EMPIRICALLY for one tenant. **Mitigation:** the script must (a) PATCH both statecode AND statuscode,
(b) post-PATCH re-query to confirm it actually took (both panels have this — keep it), and (c) on a flow
that won't activate, degrade to a clear actionable warning rather than asserting success; (d) the docs
carry the [unverified] marker + the route to confirm (live query of `workflow` EntityDefinitions).

### CE-4 — Both conflate the two causes of `ConnectionAuthorizationFailed` (403)
Both port BTCSI's "403 → retry with backoff (3×, 15s/45s)" as if every 403 is transient propagation lag.
But G1 claim 7 is explicit: the importing identity must HAVE PERMISSION to the connection to turn a flow
on. So a 403 has TWO causes: (a) transient — the connection-reference binding hasn't propagated yet
(retry fixes it); (b) durable — the SPN genuinely lacks permission to the connection (retry NEVER fixes
it; the connection must be SHARED with the SPN). Blind retry-then-fail wastes 60s and then emits a
misleading "auth_fail_after_retries" that points the operator at the wrong fix. **Mitigation:** after
retries exhaust, the tool must distinguish and say which — and for the durable case, emit the G1
remediation ("share the connection with the importing identity / bind the connection reference"), not
a generic retry-failed message.

### CE-5 — Both ship impersonation as an available knob (privilege-escalation footgun)
Both keep BTCSI's `--impersonate-oid` (acts as another Dataverse user via the caller header). BTCSI
NEEDED it (flow-ownership requirement). But a generalized copy-paste tool that exposes "act as any
user" by availability is exactly what ages into a security finding. **Mitigation:** OFF by default,
GUID-validated, gated behind an explicit flag, documented `prvActOnBehalfOfAnotherUser` prerequisite +
"flows run under the impersonated user's connections, not the SPN's" caveat; security-reviewer assesses
it specifically.

## Premise attack
Matt chose the heaviest scope (ship runnable Python). The decision stands — but the standing cost is
real and must be carried honestly: this becomes the plugin's first EXECUTABLE the team maintains,
coupling power-platform to (a) `pac` CLI's evolving flag surface and (b) the Dataverse flow-activation
mechanism — both moving targets. **Mitigation (adopt B's Alt-A insight):** the SKILL.md + knowledge +
best-practice must STAND ALONE and remain correct even if the script ages out; ship the script with an
explicit "verified against pac <version> / Dataverse Web API v9.2 on 2026-06-30; re-verify on pac
upgrades" compatibility note so staleness is detectable, not silent.

## Risk matrix (probability × impact)

| Risk | Prob | Impact | Mitigation owner |
|------|------|--------|------------------|
| Activation mechanism (statecode PATCH) behaves differently in a consumer tenant → tool reports false success | Med | High | CE-3: PATCH both codes + post-verify + degrade-to-warning + [unverified] doc |
| 403 misdiagnosis sends operator down wrong fix path | High | Med | CE-4: two-cause split + G1 remediation message |
| Impersonation knob abused / flagged in a consumer's security review | Low | High | CE-5: off-by-default + gated + reviewer sign-off |
| Script ages vs pac flag surface; silent staleness | Med | Med | Premise: standalone docs + version-compat note + co-location near skill |
| Manifest skill-count drift (46) mis-"fixed", breaks a gate | Med | Med | GAP-1: investigate Gate 12 before touching 46; bump only plugin.json 22→23 |
| Over-scoped pac-wrapping raises maintenance for the low-value half | Med | Low | CE-1: reactivation pass is the spine; import is optional convenience |
| Secret leakage via logs/argv (pac auth secret-on-argv) | Low | High | security-reviewer gate (mandatory) + redaction + env-only secrets |

No third plan produced (per gate contract). These feed G4b tiebreaks, G5 red-team, and G6 synthesis.
