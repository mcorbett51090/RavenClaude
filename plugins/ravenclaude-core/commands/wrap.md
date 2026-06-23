---
description: Capture a lesson-learned scenario from the current engagement and write it directly to the RavenClaude marketplace as a structured YAML+markdown file. Low-friction replacement for the multi-step /contribute-finding flow.
---

You are helping the user (Matt or a consultant using RavenClaude) capture a lessons-learned **scenario** from the current engagement. This is the **`/wrap` flow** — the end-of-engagement step that turns a hard-won lesson into a re-readable file that the marketplace's agents can consult on future engagements.

## What a scenario is (and isn't)

A **scenario** is a dated, scope-tagged narrative of: *"We hit problem X. The context was Y. We tried A, B, C. D worked."* It lives in `plugins/<plugin>/scenarios/<YYYY-MM-DD>-<slug>.md` inside the RavenClaude marketplace, ships with the plugin (visible to all consumers via `/plugin install`), and is consulted by relevant agents as a **fallback source of advice** — explicitly flagged as unverified to the end-user.

A scenario is **not** a canonical best-practice. Best-practices live in `docs/best-practices/` in the marketplace and require human review. Scenarios are the raw narrative material. When ≥2 independent scenarios corroborate the same finding, an agent will eventually propose promotion to best-practices (v0.2.0+ feature).

A scenario is **not** an internal post-mortem of vendor failure or a client confidentiality breach. The scrub step below filters those.

## The 9-field schema

```yaml
---
scenario_id: <YYYY-MM-DD-short-slug>     # e.g., 2026-05-21-spn-flow-create-403
contributed_at: <YYYY-MM-DD>             # today's date
plugin: <plugin-name>                    # power-platform | edtech-partner-success | data-platform | core | finance | regulatory-compliance | web-design
product: <product-or-surface>            # e.g., dataverse | power-automate | canvas-lms | quickbooks-online
product_version: <version-or-"unknown">  # e.g., "2026.04" or "unknown"
scope: <one-of>                          # tenant-specific | version-specific | likely-general
tags: [tag1, tag2, ...]                  # 3-7 short keywords
confidence: <low | medium | high>        # how sure the contributor is the resolution is right
reviewed: false                          # always false for fresh scenarios; flips to true on promotion

# --- run_context (additive, OPTIONAL, backward-compatible) -----------------
# A MINIMAL, SAFE machine-captured bundle attached by `/wrap` (Step 3b). Captured
# by scripts/capture-run-context.py from a FIXED safe allowlist ONLY. It NEVER
# carries an environment NAME (active_env / role / tenant / auth_mechanism_name) —
# those are structurally never captured (R-PRIV), because scenario files ship to
# every installer. The whole block is optional; older scenarios omit it and read
# unchanged.
run_context:
  model: <model-id-or-omitted>           # the contributing session's model
  plugin_versions:                       # {plugin: version} from each plugin.json
    ravenclaude-core: <semver>
  posture_label: <open|default|balanced|strict|unknown>  # DERIVED preset label, not raw YAML
  capture_method: <auto|degraded>        # degraded => a source was absent (field(s) omitted)
  load_bearing: [<field>, ...]           # contributor-confirmed: which captured fields drove the fix
---

## Problem
<1-2 sentence problem statement in the user's voice>

## Permissions context
<what role / service principal / OAuth scope / district admin / etc. was in play>

## Attempts
- Tried: <approach A> → <outcome>
- Tried: <approach B> → <outcome>
- Tried: <approach C> → <outcome>

## Resolution
<what worked, and why — the takeaway the next consultant should remember>
```

The schema is enforced at write-time. Missing required fields fail the write.

## Step 1 — Locate the marketplace repo

The scenario file must land in the RavenClaude marketplace repo, not the consumer's working tree. Find it in this order:

1. **Environment variable** `$RAVENCLAUDE_MARKETPLACE_DIR` — if set and the path exists, use it.
2. **Claude Code setting** `ravenclaude.marketplaceDir` — look in `~/.claude/settings.json`. If set and the path exists, use it.
3. **Ask the user** (use AskUserQuestion):

   > "Where is the RavenClaude marketplace repo on this machine? (Provide an absolute path, e.g., `/workspaces/RavenClaude` or `/Users/matt/code/RavenClaude`.)"

   Once they answer, **save it** to `~/.claude/settings.json` under `ravenclaude.marketplaceDir` so future `/wrap` invocations skip this step. Use `Edit` or `Write` on `~/.claude/settings.json` to add the setting (merge with existing JSON; don't overwrite other settings).

4. **Verify** the path: it must contain `.claude-plugin/marketplace.json`. If not, tell the user and ask again.

Once located, refer to it as `$MARKETPLACE_DIR` in your reasoning.

## Step 2 — Detect engagement context from the session

Skim the conversation history for clues. Look for:

- **Which plugin's domain is this scenario relevant to?** Power Platform (Dataverse, Power Automate, Power BI)? EdTech (Canvas, OneRoster, FERPA)? Data platform (Supabase, Cube, JWT)? Etc.
- **What product / version was in play?** Quote the user's words when possible.
- **What was the problem?** Look for "didn't work", "had to fall back", "the trick was", "blocked on", "took us X hours".
- **What did they try?** Look for "tried X", "first attempted", "then we", "next we tried".
- **What worked?** Look for "the fix was", "we ended up", "what finally worked".

Form a hypothesis. Don't ask the user "tell me about your engagement" — you should be able to draft from context.

### Step 2b — Consult the event substrate (situational awareness)

The chat transcript is one source; the **structured event substrate** is a second, often-sharper one — it's a machine record of what the guardrails actually saw this engagement, which is prime raw material for a grounded scenario. Before drafting, glance at:

- **`.ravenclaude/runs/<session>/hook-events.jsonl`** — the deny/warn verdicts that fired (the `rule` tokens: `off-allow-list`, `destructive-pattern`, `task-scope-out-of-scope`, …). A repeated deny is a strong signal of where the engagement hit friction — exactly the "we kept getting blocked on X" shape a scenario captures. The same data is in the **Heimdall** dashboard tab.
- **`.ravenclaude/posture-events.jsonl`** — posture changes during the session (what `security_deny`/override rules were added/removed, and why). The **Víðarr** tab surfaces the same. A mid-engagement posture change often *is* the lesson ("we had to relax X to get unblocked").

Treat these as **corroboration for your transcript hypothesis**, not a replacement: they tell you *what tripped*, the transcript tells you *why and how it was resolved*. If a deny fired repeatedly and the transcript shows how it was worked around, that pairing is the ideal scenario. This is the `/wrap`-time application of the [`best-practices/check-runtime-state.md`](../best-practices/check-runtime-state.md) discipline. (Both files are git-ignored/per-consumer; if absent — e.g. the guardrails never fired — just rely on the transcript. Never block on them.)

## Step 3 — Ask the 4 minimum questions (use AskUserQuestion)

Even with strong context, confirm these explicitly. Ask all 4 in **one** AskUserQuestion batch:

1. **Which plugin?** (Pre-select your best guess from Step 2.)
   - power-platform / edtech-partner-success / data-platform / ravenclaude-core / finance / regulatory-compliance / web-design

2. **What's the scope?** (Critical for filtering one-off vs general.)
   - `tenant-specific` — only this customer's config; future engagements probably won't see this
   - `version-specific` — depends on product version X; will need re-verification when version changes
   - `likely-general` — probably applies broadly; corroboration will promote it to best-practices later

3. **How confident are you in the resolution?**
   - low / medium / high

4. **Is there any client-identifying information in the draft I'm about to write?** (If yes, you'll scrub it in Step 4.)
   - no / yes-let-me-redact

### Step 3b — Capture + confirm the run-context bundle (additive, low-friction)

After the 4 questions, attach a **minimal, safe `run_context` bundle** to the scenario so a future reader (and `scenario-retrieval`) has the few output-shaping variables that decide whether the lesson generalizes — instead of relying on the contributor's cold `scope` guess.

1. **Auto-capture (silent).** Run the bundler against the marketplace repo:

   ```bash
   python3 "$MARKETPLACE_DIR/scripts/capture-run-context.py" --project-root "$MARKETPLACE_DIR" --model "<this session's model id>"
   ```

   It reads ONLY a fixed safe allowlist — `model`, `plugin_versions`, a **derived** `posture_label` (open/default/balanced/strict/unknown — a label, *not* the raw posture YAML), and `capture_method`. It **never** reads `environment-context.md` or any env / role / tenant / auth source — that exclusion is structural (R-PRIV), because the scenario file ships to every installer and an env *name* is itself a sensitive token. A missing source → that field is omitted and `capture_method: degraded`; the bundler never crashes. If it returns `capture_method: degraded`, just note that and continue — a partial bundle still beats none.

2. **Show the bundle, don't re-ask it.** Surface the captured block to the user (read-only), then ask **one** `load_bearing` multi-select (pre-checked by your best guess):

   > "I captured this run context for the scenario — which of these were **load-bearing** for the fix?"
   > - [ ] `model` — the lesson is specific to this model's behavior
   > - [ ] `plugin_versions` — the lesson depends on a plugin version in play
   > - [ ] `posture_label` — the guardrail posture shaped what happened

   The selected fields are written into `run_context.load_bearing`. This is the only new round-trip — everything else is auto-filled.

3. **Derive `scope` ONLY for the two machine-derivable cases; leave `tenant-specific` to the human (FM5).**

   | Derived scope | When to propose it (from the bundle) |
   |---|---|
   | `version-specific` | `product_version` is pinned (not `unknown`) AND `plugin_versions` is load-bearing AND the resolution references version-specific behavior. |
   | `likely-general` | No version pinned, nothing tenant-shaped in the body, and the load-bearing set is empty or model/posture-only. |
   | `tenant-specific` | **NOT auto-derived.** Env identifiers are banned from the bundle (R-PRIV), so the bundle cannot evidence a tenant. This stays the **human-asserted** choice from Step 3 question 2 — if the contributor said `tenant-specific`, keep it; the lesson must carry a *non-identifying* qualifier in the body (e.g. "only for orgs using product X with permission model Y") for retrieval to match on. |

   When you derive `version-specific` or `likely-general`, **show the one-line derivation** ("proposed *version-specific* because the version is pinned and you marked plugin_versions load-bearing") and let the contributor override. The override is now *informed by* the captured variables, not a cold guess.

4. **Embed** the resulting `run_context` block into the scenario's YAML frontmatter (Step 4 / Step 5). It is additive and optional — never block the write on it; if capture failed entirely, omit the block and write the scenario exactly as before.

## Step 4 — Draft the scenario + scrub

Draft the full file using the schema in this command's header. Auto-fill what you can from session context; leave `unknown` for what you can't determine.

**Scrub for client-identifying info before writing:**

Run a check on the drafted content for:

- Client / district / institution names (e.g., "Acme School District", "Hartwell University") → replace with generic placeholders ("a mid-sized K-12 district", "a regional university")
- Specific named individuals (e.g., "the curriculum director Jane Smith") → generic roles only
- Specific tenant URLs or domains (e.g., `acme.crm.dynamics.com`) → replace with `<tenant-uuid>.crm.dynamics.com` or similar
- Email addresses
- API keys, secrets, OAuth tokens — these should NEVER be in a scenario (if you spot one in the user's transcript, refuse to write the file and tell the user to rotate the secret immediately)
- Phone numbers, SSNs, student PII (FERPA-protected fields), HIPAA-protected fields

When you scrub, **show the user** the redacted version before writing. They can approve or push back.

**Filename convention:** `<contributed_at>-<short-slug>.md` where the slug is 3-5 hyphenated keywords from the problem (e.g., `2026-05-21-spn-flow-create-403`). The file lives at `$MARKETPLACE_DIR/plugins/<plugin>/scenarios/<filename>`.

If the target directory doesn't exist yet (most plugins haven't enabled scenarios — only power-platform has it as of v0.1.0 of the feedback loop), create it. Drop a `.gitkeep` if you're the first.

## Step 5 — Write the file

Use the `Write` tool. Confirm the file path before writing.

After writing, verify it exists and has the expected content.

## Step 6 — Commit (with confirmation)

Show the user the new file's path and ask (use AskUserQuestion):

> "Commit this scenario to the marketplace repo now?"
> - yes — commit + push to origin (long-term default)
> - yes-no-push — commit locally only (manual push later)
> - not yet — leave uncommitted for the user to review

If **yes** or **yes-no-push**:

```bash
cd "$MARKETPLACE_DIR" && \
  git add plugins/<plugin>/scenarios/<filename> && \
  git commit -m "scenario(<plugin>): <one-line summary>

Captured via /wrap from a real engagement.
Scope: <scope-value>
Confidence: <confidence-value>
Scrub: applied (no client PII, no secrets)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

If **yes** (push too):

```bash
cd "$MARKETPLACE_DIR" && git push
```

Report success and the resulting file path / commit SHA to the user.

## Step 7 — Tell the user what happens next

After a successful capture, briefly explain:

- The scenario will be picked up automatically by the relevant plugin's agents on the next engagement that matches its tags / plugin / product. Agents will surface it with a mandatory unverified-scenario preamble.
- If a second independent scenario corroborates this one's resolution, the marketplace will eventually prompt for promotion to canonical best-practices.
- The scenario is **not** reviewed; treat it as an unverified field note.

## Errors to handle

- **Marketplace repo not found / `marketplace.json` missing** → ask the user; don't try to auto-create.
- **Plugin directory doesn't exist** (e.g., they picked a plugin that hasn't been built yet) → tell the user; offer to write into `core` as a fallback or cancel.
- **Schema validation fails** (missing required field) → re-prompt for the missing field; don't write a half-schema file.
- **Secret detected during scrub** → STOP. Tell the user the secret must be rotated before continuing. Do not write the file.
- **Git commit fails** (e.g., uncommitted changes in the marketplace repo) → tell the user; offer to stash + retry or skip the commit.

## Failure modes to avoid

- **Don't ask "tell me about your engagement"** — that's exactly the friction `/wrap` exists to remove. Draft from context first; only ask the 4 minimum questions.
- **Don't write the file before confirming the redaction** — privacy regression is a one-way door.
- **Don't write into the consumer's working tree** — the file must land in the marketplace repo.
- **Don't push without confirmation** — pushing is shared-state action.
- **Don't write a scenario with `reviewed: true`** — that's the maintainer-side decision, not the contributor's.

## When NOT to use `/wrap`

- The user wants to capture a general best-practice, not a scenario → route them to `/contribute-finding` (which already exists and handles canonical-bank submissions).
- The user wants to update an existing scenario → tell them to edit the file in the marketplace directly; `/wrap` only writes new files.
- The user is in the marketplace repo itself (not a consumer session) → still works, but the engagement-context detection in Step 2 won't have a real session to mine. Ask the user directly in that case.

---

**Companion docs:**
- `plugins/ravenclaude-core/skills/scenario-retrieval/SKILL.md` — how agents consult scenarios
- `plugins/power-platform/scenarios/README.md` — the first plugin to enable scenarios
- `docs/staging/README.md` — the older, more elaborate `/contribute-finding` → `/review-staged-contributions` flow (still works for canonical best-practices)
