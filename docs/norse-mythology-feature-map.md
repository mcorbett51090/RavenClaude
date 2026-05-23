# Norse Mythology — Feature-Fit Pass for RavenClaude

**Date:** 2026-05-23
**Author:** Ideation pass (research + design synthesis)
**Status:** Ideation / not a build plan. Per-figure verdicts and a ranked shortlist.

---

## 1. What this is

RavenClaude is leaning into Norse mythology as a coherent product identity — the raven motif (Huginn & Muninn) is already in flight, the command-review system is being styled as a "tribunal" with Thor as tie-breaker and Forseti as the justice role, the assembly is the "Thing," and the dashboard is framed as Hliðskjálf (Odin's seat from which he sees all worlds).

The risk with mythological theming is that it becomes _decorative_ — clever names painted over features without aiding comprehension. The point of this pass is the opposite: for each major god and concept, ask whether **embodying it would genuinely help a user understand what the feature is**. If the metaphor sharpens the mental model, it earns its place. If it just supplies a logo, it's a skip.

The bar for "Strong fit" is high: the myth must make the feature _easier to grasp at a glance_ than its plain name would.

## 2. What is already claimed

These figures are spoken-for in existing or in-motion designs. New ideas below relate to them but do not re-assign them:

| Figure / concept | Role in RavenClaude |
|---|---|
| **Huginn & Muninn** (Odin's ravens) | The reconnaissance / memory dashboard panel — agents that scout the working tree (thought) and recall prior sessions (memory). See `docs/huginn-muninn-recon-design.md` (in flight). |
| **Thor** | The tie-breaking vote in the tribunal command-review feature — raw decisive force when the lighter judges deadlock. |
| **Forseti** | The justice / arbiter role in the tribunal — settles a dispute by formal verdict. |
| **The Thing** (Old Norse _þing_) | The tribunal assembly itself — the convened review body. |
| **Hliðskjálf** | The dashboard — the high seat from which the user oversees all plugins / realms. |

> One brief in the brief: the sibling design docs (`huginn-muninn-recon-design.md`, `tribunal-review-feature-design.md`, `dashboard-buildout-plan.md`) are referenced by the brief that triggered this ideation but are not yet committed to `docs/`. This map is written so it stays correct whether those docs land verbatim or evolve.

---

## 3. The pass — Aesir & Vanir

For each figure: a short summary grounded in the _Poetic Edda_ / _Prose Edda_ (Snorri Sturluson), a feature-fit assessment against RavenClaude's actual surfaces (plugins, agents, the Team Lead dispatch model, comfort-posture, dashboard, hooks, CI gates, memory bank, marketplace), and a verdict.

### Odin (Allfather)

**Myth.** Chief of the Aesir; god of wisdom, war, poetry, and sovereignty. Sacrificed an eye at Mímir's well for cosmic wisdom and hung nine nights on Yggdrasil, wounded by his own spear, to win the runes. Sends Huginn ("thought") and Muninn ("memory") out across the worlds each dawn; rides Sleipnir; wields Gungnir, which never misses; surveys all realms from Hliðskjálf.

**Feature-fit.** Odin is structurally the **user themselves**, not a feature. The dashboard (Hliðskjálf), the ravens (Huginn/Muninn), and the spear of decree (Gungnir, possible future feature — see below) are the user's _instruments_. Trying to embody Odin as a specific agent or component would either steal authority from the user or duplicate Hliðskjálf.

**Verdict: Worth exploring — as a framing device, not a feature.** Use "Odin" sparingly in copy ("from Hliðskjálf you see what Huginn and Muninn report") to anchor the user's POV. Do not build an "Odin agent."

---

### Thor

**Myth.** Thunder-god, defender of Midgard and Asgard; wields Mjölnir, which always returns when thrown and consecrates births, marriages, and funerals. Kills Jörmungandr at Ragnarök but takes nine venom-poisoned steps and falls.

**Feature-fit.** Already claimed as the tribunal's tie-breaking vote. The deeper metaphor of Mjölnir as both _weapon and consecrator_ has a separate possible use (see **Mjölnir** below) but is distinct from Thor-as-tiebreaker — the hammer is the tool, not the god.

**Verdict: Already claimed.**

---

### Freyja

**Myth.** Vanir goddess of love, fertility, war, gold, and seiðr (Norse magic of seeing and shaping fate). Receives half the battle-slain into Fólkvangr; the other half go to Odin. Wears the necklace Brísingamen; flies in a falcon-cloak.

**Feature-fit.** Freyja's two strongest hooks for a software product are (a) **seiðr — the magic of foresight and pattern-reading**, which could anchor a forecasting / prediction feature, and (b) **the 50/50 split of the slain with Odin**, which models a _dual-channel routing_ pattern. Neither has an obvious current home. Forecasting overlaps with the existing project-manager and partner-success-manager agents without needing a new metaphor; the dual-channel split is a clever idea looking for a problem.

**Verdict: Thin — skip.** Vivid, but no current surface in RavenClaude reaches for her. Reconsider if a "predictive lane" feature emerges.

---

### Frigg

**Myth.** Queen of the Aesir, wife of Odin, mother of Baldr. Knows the fate of all things but does not speak it. Extracted oaths from every thing in the cosmos not to harm Baldr — overlooked the mistletoe.

**Feature-fit.** "Foreknowledge held silent" is a poor fit for software, which should _surface_ what it knows. The oath-from-all-things-except-one is closer to something useful — it maps to **the test-coverage trap**: every case is checked except the one obvious thing that's been written off as harmless. But that's a cautionary lesson, not a feature, and the existing tester-qa agent already owns it.

**Verdict: Thin — skip.** Beautiful myth, no traction here.

---

### Loki

**Myth.** Trickster, shapeshifter, blood-brother of Odin; both helps the gods (recovers Mjölnir, retrieves Idunn) and undermines them (orchestrates Baldr's death). Father of Fenrir, Jörmungandr, Hel, and Sleipnir.

**Feature-fit.** A "devil's advocate" agent — one that deliberately argues the opposing case in a tribunal — has obvious appeal, and Loki-as-trickster is the cleanest mythological hook. But the tribunal already has its full roster (Forseti as judge, Thor as tie-breaker, the Thing as assembly), and adding a trickster role risks turning the review into theater. A separate possible read: **chaos-testing / red-team agent** that intentionally tries to break things — Loki's generative-by-being-disruptive arc. That has a stronger argument.

**Verdict: Worth exploring — narrowly, as a red-team agent.** If a "break-it-on-purpose" QA capability is ever scoped (intentional permission abuse, prompt injection probes, hook bypass attempts), Loki is the right name for it. Otherwise skip — do not add to the tribunal.

---

### Heimdall

**Myth.** The ever-vigilant watchman at Himinbjörg, where Bifröst meets Asgard. Hears grass growing on earth and wool growing on sheep; sees a hundred leagues by day or night; needs less sleep than a bird. Sounds Gjallarhorn to wake the gods at the onset of Ragnarök. Kills (and is killed by) Loki at the end.

**Feature-fit.** This is one of the strongest. RavenClaude already has multiple perimeter-watchers — the `enforce-layout.sh` hook (denies off-pattern writes), the `validate-layout.yml` CI workflow (cross-tool backstop), the `guard-recursive-spawn` hook, the prettier check, the gate-audit meta-test, the manifest-validity checks. Today these are scattered files with workmanlike names. Bundling them under a **Heimdall** identity — _the watch on the perimeter_, with a unified "Heimdall alarm" surface in the dashboard — would give users a single mental model for "the alarms that fire when something crosses a boundary."

This is _distinct_ from Huginn & Muninn: the ravens go _out_ to scout the wider working tree and report back. Heimdall stays _at the gate_ and triggers when something crosses inward. Together they cover the full perception loop: active reconnaissance + passive perimeter alarm.

**Specific mapping.** Dashboard tab labeled "Heimdall" that surfaces: (a) most recent layout-violation denials, (b) CI gate status across plugins, (c) any hook that fired with a deny verdict in the last N sessions, (d) the Gjallarhorn — a banner that surfaces when something irrecoverable is about to happen (push to main, force-push, plugin uninstall on a project with state). The horn is the loud one. The other three are quiet.

**Verdict: Strong fit.**

---

### Týr

**Myth.** God of war, law, oaths, and judicial sacrifice. Bound Fenrir with Gleipnir by placing his right hand in the wolf's mouth as surety — and lost it when Fenrir realized he could not break free. The willing forfeit that makes binding-by-oath possible.

**Feature-fit.** Týr is _the right metaphor for explicit, costly user consent_ — the moment in the workflow where the user must put something on the line for a high-risk action to proceed. The current comfort-posture system has tiers (deny / allow / etc.), but the moment of "the user must explicitly authorize this" is unnamed. Týr's hand is the cleanest possible name for that interaction: **the user accepts a small cost (a confirmation, an audit log entry, a posture downgrade) in exchange for being allowed to do the dangerous thing**.

This pairs naturally with **Gleipnir** (below) — Gleipnir is the binding, Týr is the price paid to make the binding hold.

**Verdict: Worth exploring.** Strong concept; lives or dies on whether a "consent-with-cost" interaction actually emerges in the comfort-posture UX. If posture stays purely declarative, Týr has nowhere to land.

---

### Baldr

**Myth.** Beloved shining son of Odin and Frigg. Frigg extracted oaths from every thing not to harm him — except mistletoe, deemed too young to swear. Loki guided a mistletoe dart into the blind Höðr's hand, killing Baldr. Returns to rule the renewed world after Ragnarök.

**Feature-fit.** Baldr is a _morality tale_, not a feature: "the one thing you forgot to defend against is what kills you." That maps to test-coverage gaps, posture allow-lists that miss an edge case, the unenumerated path in a layout glob. Useful as a cautionary frame, but no specific feature claims it without contortion.

**Verdict: Thin — skip.** Possibly cite Baldr in best-practices prose ("the Baldr problem: extracting oaths from every thing except the one that kills you") but do not build around him.

---

### Bragi

**Myth.** God of poetry and skaldic art; welcomes the einherjar into Valhalla with verse. Long-bearded, runes carved on his tongue.

**Feature-fit.** The existing `documentarian` agent already does what Bragi would do — turn events into formal, well-shaped prose. Adding the name on top adds nothing.

**Verdict: Thin — skip.**

---

### Idunn

**Myth.** Keeper of the apples of youth. Without them the Aesir grey and weaken. Lost briefly to the jötunn Þjazi; Loki retrieved her.

**Feature-fit.** "Renewal as a maintained resource" is an interesting frame for `/plugin marketplace update` — the gods (consumer projects) must periodically eat new apples (new plugin versions) or they grey and weaken (drift away from current best-practices). But this is a frame, not a feature; the update mechanism already exists and works.

**Verdict: Thin — skip.** Possibly use "Idunn" in copy for the update-prompt banner ("eat the apples — `/plugin marketplace update`") if a playful tone is wanted.

---

### Njörðr

**Myth.** Vanir god of the sea, wind, fishing, and coastal prosperity. Came to the Aesir as a hostage to seal the peace after the Aesir-Vanir war. Mismatched marriage to Skaði (he could not bear her mountains, she could not bear his shore).

**Feature-fit.** Njörðr's _interesting_ angle is being the hostage who became integrated — the metaphor for **a cross-plugin dependency that started as a tense compromise and ended as a stable part of the system**. But that's an internal architectural observation, not a user-facing feature.

**Verdict: Thin — skip.**

---

### Skaði

**Myth.** Jötunn-goddess of winter, mountains, skiing, hunting. Came to Asgard armed for vengeance after her father's death; chose Njörðr by feet alone. Later placed the venom-serpent over the bound Loki.

**Feature-fit.** Skaði fits no specific RavenClaude surface. Her vengeance-and-mountains energy is vivid but unanchored.

**Verdict: Thin — skip.**

---

### Forseti

**Already claimed** as the justice role in the tribunal review.

---

### Víðarr

**Myth.** Silent god of vengeance, second-strongest after Thor. Wears a thick shoe assembled across all of time from leather scraps cobblers discard, in slow patient accumulation. At Ragnarök, after Fenrir devours Odin, Víðarr places that shoe on the wolf's lower jaw and tears him apart. One of the few who survives.

**Feature-fit.** Víðarr is **patient accumulation toward a single moment of force**. The closest real RavenClaude surface is the **audit trail / activity log** — every small action stored against the day someone needs to reconstruct what happened. The "shoe of scraps" is the slowly-accumulated record. But that frame is more poetic than functional; the audit trail is workmanlike and doesn't need a name.

**Verdict: Thin — skip.** Reconsider if a "long-prepared escalation" feature emerges (e.g. an agent that quietly logs evidence until a threshold triggers a tribunal).

---

### Freyr

**Myth.** Vanir god of peace, fertility, sunshine, kingship. Ship Skíðblaðnir (foldable, always granted fair wind). Boar Gullinbursti. Gave away his sword to woo Gerðr — falls weaponless at Ragnarök against Surtr.

**Feature-fit.** "Gave away the sword that protects you in exchange for a short-term want" is the canonical posture-misconfiguration cautionary tale — the moment a consumer adds `"Bash(*)"` to their allow-list because one command was annoying and now nothing is gated. Could appear in posture-related copy.

**Verdict: Thin — skip.** Best left as a cautionary phrase in comfort-posture docs ("the Freyr trade — don't give away the sword").

---

### Höðr & Váli

**Myth.** Höðr is the blind god who unwittingly kills Baldr at Loki's direction. Váli is Odin's son born for the sole purpose of avenging Baldr — grew to adulthood in a day, killed Höðr without delay.

**Feature-fit.** Single-purpose accuracy is real (Váli) and the "unwitting hand of harm" frame is real (Höðr) but neither names a clean feature. Both are characters _in_ the Baldr tale rather than independent identities.

**Verdict: Thin — skip.**

---

## 4. The pass — cosmology, places, artifacts, creatures

### Yggdrasil — the World Tree

**Myth.** Immense ash tree at the center of the cosmos. Three roots reach three wells (Urðr, Mímir, Hvergelmir). Gnawed at the base by Níðhöggr, browsed at the crown by an eagle, with the squirrel Ratatoskr ferrying insults up and down. The Norns nourish it daily with water and clay from the Well of Urðr.

**Feature-fit.** Yggdrasil maps onto the **marketplace itself as a living structure** with surprising precision: `marketplace.json` is the trunk, each `plugins/<name>/` is a branch, each agent/skill/hook a leaf. The three roots map to three sustaining wells — the lessons-learned log, the decision log, and the proposals folder (memory of the past, judgment of the present, plans for the future — see Norns below). Níðhöggr at the root is technical debt. Ratatoskr is the cross-plugin dispatch carrying messages between agents.

The strongest specific feature is a **Yggdrasil view in the dashboard**: an interactive tree visualization of the marketplace's plugin/agent/skill structure, with the three "wells" (lessons / decisions / proposals) visible at the roots, technical-debt items shown as Níðhöggr-marked nodes, and version-state shown via root health. This is more than decoration — it gives users a single canonical mental model for "what's in this marketplace" that the current README's nested-folder tables don't.

**Verdict: Strong fit.** Yggdrasil-as-marketplace is the spine the rest of the theming hangs from. Build the visualization.

---

### The Norns (Urðr / Verðandi / Skuld)

**Myth.** Three women — Urðr (what-has-become / past / fate), Verðandi (what-is-becoming / present), Skuld (what-shall-be / debt and future) — dwell beside the Well of Urðr at the foot of Yggdrasil and weave the destiny of gods and men. They also tend Yggdrasil by drawing water and clay from the well daily.

**Feature-fit.** The triad maps onto the **temporal axis of any plugin's life** almost too cleanly: Urðr = the lessons-learned + decision-log + git history (what was), Verðandi = the current head / current version (what is), Skuld = the proposals folder + roadmap (what shall be). RavenClaude already _has_ these three artifacts; the Norns supply the unifying name.

**Specific mapping.** A dashboard panel called "the Norns" for each plugin showing three columns: **Urðr** (recent lessons + decision log entries + last N commits), **Verðandi** (current version + active hooks + active rules), **Skuld** (open proposals + planned version bumps). One glance answers "where did this plugin come from, what is it now, where is it going." This is a strong improvement over today's separate-page browsing.

The deeper pull: the Norns _also tend the tree_ — they don't just observe fate, they actively keep Yggdrasil alive. That maps to the user's role in the marketplace: lessons + decisions + proposals are not passive logs, they are how the marketplace is _kept healthy_.

**Verdict: Strong fit.** Build the Norns panel as the temporal/lineage view per plugin.

---

### Well of Urðr (Urðarbrunnr)

**Myth.** The sacred well under the Asgard-bound root of Yggdrasil. Anything entering it emerges "white as the membrane within an eggshell." The Norns scoop water and clay from it daily to nourish the tree; the gods hold their daily assembly (þing) at its banks.

**Feature-fit.** Strongly associated with the Norns (above) — best treated as part of that mapping. The independent angle is "the gods assemble daily at the well" — i.e. the place where the **the Thing convenes** (already claimed). The well _is_ the Thing's location.

**Verdict: Strong fit, but folded into the Norns + the Thing.** Use "Well of Urðr" as the dashboard's geography label where lessons/decisions/proposals live and where the Thing convenes. Not a new feature; a name for a place.

---

### Mímir & Mímir's Well

**Myth.** Mímir is the wisest of beings; his well sits under another root of Yggdrasil and contains cosmic wisdom. Odin sacrificed an eye to drink from it. Mímir was sent to the Vanir as a hostage after the war; they beheaded him; Odin embalmed the head with herbs and charms so it could continue to speak, and consulted it as his perpetual oracle.

**Feature-fit.** Two distinct mappings, both strong:

1. **Mímir's well = the knowledge bank.** Each plugin already has (or could have) a `knowledge/` directory and the cross-plugin `docs/best-practices/`. Naming this collection "Mímir's well" gives the user a single phrase for "the deep reference content you can consult when you need to." Stronger than "knowledge base" because it carries the cost-of-wisdom frame: you _go_ to the well; you don't expect the answer to come to you.

2. **Mímir's preserved head = retained context across session boundaries.** Auto-memory _already_ does this — `MEMORY.md` and the typed memory files persist across sessions. The Mímir-head metaphor is the cleanest possible name for that mechanism: _a wise interlocutor who keeps speaking after the body (the session) is dead._ The memory system today is described mechanically; calling it "Mímir's head" makes the user-facing concept legible in one phrase.

These two are coherent because both _are_ Mímir: the well is the deep static knowledge; the head is the conversational ongoing wisdom. Together they cover the full knowledge-retention surface.

**Verdict: Strong fit.** Adopt "Mímir's well" for the knowledge bank surface and consider "Mímir's head" as the name for the memory subsystem (or as a section label inside the dashboard's memory panel).

---

### Ragnarök

**Myth.** The foretold cataclysm. Three-winter Fimbulvetr; moral collapse; Fenrir breaks free; Jörmungandr floods the world; Surtr leads Muspelheim across a shattering Bifröst. Odin is devoured by Fenrir; Víðarr avenges him; Thor and Jörmungandr kill each other; Heimdall and Loki kill each other; Surtr's fire consumes the cosmos. Then a green world resurfaces; Baldr returns; Víðarr, Váli, Móði, Magni inherit it.

**Feature-fit.** "Disaster recovery / total rollback / clean rebuild" is the obvious mapping and it actually fits — there is real value in a single named pathway for "everything is broken; reset the consumer's plugin state to a known-good cosmos." But the metaphor is heavy. Naming a `/plugin reset` flow "Ragnarök" sets a tone the feature must earn — destructive, irreversible, _and_ followed by something better. That's actually accurate to good disaster-recovery UX (the rebuilt world _is_ better than the one it replaced).

**Specific mapping.** A `/ragnarok` (or similarly-named) command for "burn the plugin cache and re-install from marketplace head" — explicit, gated by confirmation, accompanied by a snapshot of what's about to be lost (audit log = the Mímir-head that survives to advise the renewed world). The "the world reborn is greener" angle could anchor a post-reset checklist: what to verify, what came back, what is genuinely new.

**Verdict: Worth exploring.** The metaphor is heavy but accurate. Build only if there's a real DR / reset workflow that needs naming; do not invent the feature to use the name.

---

### Valhalla

**Myth.** Odin's hall of the slain, roofed with shields and spear-shafts, 540 doors. The einherjar — warriors chosen by valkyries from the battle-dead — fight and feast daily, in eternal preparation for Ragnarök.

**Feature-fit.** Closest mapping is "the roster of agents — they 'fight by day and feast by night,' i.e. they take dispatch jobs during a session and are version-bumped between sessions." But the existing dispatch playbook handles this functionally, and naming the agent list "Valhalla" adds nothing the user needs to understand. Alternate mapping: "merged PRs archive" — the honored dead. Also thin.

**Verdict: Thin — skip.** Decorative for what RavenClaude actually does. Reconsider if a chosen-agent / honored-roster feature emerges with real selection logic.

---

### Fólkvangr

**Myth.** Freyja's field. She receives _half_ the battle-slain; Odin gets the other half. A structurally equal counterweight to Valhalla.

**Feature-fit.** A "second routing lane" pattern needs an actual second lane to live in. RavenClaude doesn't have one today. The Aesir/Vanir-style dual routing is intellectually pleasing but unattached.

**Verdict: Thin — skip.**

---

### Bifröst

**Myth.** The burning rainbow bridge linking Asgard to Midgard. Three-colored; great strength; the red band is fire that keeps the jötnar out. Guarded by Heimdall. Breaks under Muspell's fire-sons at Ragnarök.

**Feature-fit.** Bifröst is the **install / connector bridge** — the path between the marketplace (Asgard) and a consumer project (Midgard). The `/plugin marketplace add` + `/plugin install` flow _is_ Bifröst. Today this is described in workmanlike CLI terms; naming it gives users a mental model for the directionality (the plugin _crosses over_ to their world) and the guardedness (Heimdall — see above — fires on misuse).

The "doomed to break" detail is design wisdom: any cross-tool bridge is going to fail eventually under enough load (cache desync, version drift, marketplace.json malformed), and naming the bridge after one that's _known_ to break in the foundational story gives the user permission to expect that and prepare for it (i.e. there's a Heimdall watching the bridge, and a Ragnarök reset if it shatters).

**Specific mapping.** Use "Bifröst" in the dashboard's plugin-install panel and in user-facing copy for the install/update flow. The flow today is several CLI commands; one Bifröst-named panel that orchestrates them (add → install → reload → verify) would be a real usability improvement.

**Verdict: Strong fit.**

---

### Mjölnir

**Myth.** Thor's hammer. Always returns, never misses, can be shrunk into the tunic. Used both to slay jötnar _and_ to consecrate births, marriages, and funerals. Forged by Sindri and Brokkr with a famous short-handle flaw caused by Loki interfering as a fly.

**Feature-fit.** The dual nature — weapon _and_ consecrator — is the interesting bit. The "weapon" side is just a sharp action; many features could be called Mjölnir. The "consecrator" side is more specific: **the formal blessing of an artifact as ready to ship.** Today RavenClaude has fragments of this: the CI passes, the prettier check passes, the gate-audit passes, the version is bumped, the changelog is updated. None of these collectively names "this plugin is consecrated and ready."

**Specific mapping.** A `/mjolnir` command (or button) that runs the full release blessing on a plugin: version-bump verified, all gates green, marketplace.json synced, NOTICE.md present if needed, hooks executable, contract tests pass. On success, the plugin is "consecrated" — a single named act that's currently four or five separate manual checks. The short-handle flaw is also worth invoking honestly: every release has a flaw the smith couldn't help. The blessing names that explicitly.

**Verdict: Worth exploring.** Strong if the release process is centralized; thin if releases stay ad-hoc.

---

### Gungnir

**Myth.** Odin's spear, forged by the Sons of Ivaldi. Carved with runes on the point. Never misses; always returns. Odin opens the Aesir-Vanir war by hurling it over the Vanir host.

**Feature-fit.** Gungnir is **the sovereign decree** — the user's irrevocable command. Possible mapping: the "promote to plugin canonical" or "approve and merge to main" action — the throw that cannot be taken back. But this overlaps heavily with Mjölnir (release blessing) and Forseti (formal verdict). Forcing Gungnir in risks proliferation of sovereign-action names that the user has to keep distinct.

**Verdict: Thin — skip.** Conserve the name. If a strictly "user-final, no-recall" action ever needs a separate identity from Forseti and Mjölnir, Gungnir is its name.

---

### Sleipnir

**Myth.** Odin's eight-legged horse, born from Loki (as a mare) and the stallion Svaðilfari. Carries Odin across all worlds, including to Hel and back.

**Feature-fit.** **Cross-realm mobility = the worktree mechanism.** RavenClaude already uses git worktrees heavily (`EnterWorktree`, `.claude/worktrees/` directory). Sleipnir is the cleanest possible name for the agent capability of "leave the main world, enter an isolated copy, work, return safely with what was needed." The eight legs visibly carry the metaphor — multiple parallel branches at once.

This also gives a name to a real user-facing surface that's currently called "worktree" and feels infrastructural. "I'll send Sleipnir to that branch" is more intuitive than "I'll spawn an EnterWorktree call."

**Specific mapping.** Use "Sleipnir" in dashboard copy and agent dispatch language for worktree operations. Particularly: the worktree-list view ("Sleipnir's stables") and the worktree-creation action ("send Sleipnir"). Possibly: a status indicator showing which Sleipnir-journey (worktree) each active agent is on.

**Verdict: Strong fit.** Cheap, natural, gives a navigable name to an infrastructure layer users already encounter.

---

### Fenrir

**Myth.** Monstrous wolf, son of Loki and Angrboða. Prophesied to kill Odin at Ragnarök. The gods raised him in Asgard while attempting to bind him; he snapped two iron chains; the dwarves of Niðavellir forged Gleipnir; Týr placed his hand in Fenrir's mouth as surety and lost it. Fenrir remains bound until Ragnarök.

**Feature-fit.** Fenrir is **the bound catastrophe** — a recognized danger held in place by an explicit, deliberate constraint. In RavenClaude this maps to **the security_deny lane of comfort-posture**: dangerous capabilities (force-push to main, posture-rewriting without consent, recursive agent spawn) that are known and held off by specific rules. The metaphor's power is that it acknowledges the danger is real, not hypothetical — Fenrir _will_ break free eventually, the binding is buying time, and the system is designed knowing that.

This pairs with Gleipnir (the binding) and Týr (the price paid to bind).

**Specific mapping.** A "Fenrir" lane in the comfort-posture YAML / dashboard that explicitly names the known-dangerous capabilities the system is _deliberately_ holding back, distinct from the general allow/deny list. Each Fenrir-marked rule comes with: why it's dangerous, what binds it (which Gleipnir-ingredient), and what would happen if it broke free (the Ragnarök linkage).

**Verdict: Strong fit.** Names a part of the posture system that's currently nameless: the _consciously-bound_ dangers, as opposed to mere disallow rules.

---

### Jörmungandr

**Myth.** The Midgard serpent, sibling to Fenrir. Encircles the world, gripping his own tail. Thor's archenemy.

**Feature-fit.** The encircling-the-world-as-its-boundary frame _could_ map to a perimeter-enforcement system, but Heimdall already covers that better (Heimdall is alert, Jörmungandr is just _there_). The ouroboros-as-cosmic-boundary angle is striking but unanchored.

**Verdict: Thin — skip.** Reconsider if a specific "the encircling boundary" concept emerges that's distinct from Heimdall's perimeter watch.

---

### Hel

**Myth.** Daughter of Loki; half-flesh, half-corpse. Rules Helheim, the realm of the dead who did _not_ die in battle. Her hall is Éljúðnir; her dish is Hunger, her knife Famine, her bed Sick-bed.

**Feature-fit.** Closest mapping is "deprecated / archived plugin storage" — the realm of plugins that didn't die a heroic death but just aged out. But this is more decorative than useful; "deprecated/" works fine.

**Verdict: Thin — skip.**

---

### Gleipnir

**Myth.** The impossibly thin silken ribbon that finally binds Fenrir, forged by the dwarves of Niðavellir from six things that do not exist: the sound of a cat's footfall, the beard of a woman, the roots of a mountain, the sinews of a bear, the breath of a fish, and the spittle of a bird. It looked weightless. It held the wolf who had snapped iron.

**Feature-fit.** **This is the strongest single fit in the whole roster.** Gleipnir is _what RavenClaude's comfort-posture system already is_: an unbreakable constraint composed of six (or whatever number) individually-trivial-looking ingredients — allow-lists, deny-lists, per-pattern overrides, security_deny, hook deny verdicts, layout globs. None of them are heavy on their own. Together they hold Claude inside the lines.

The current posture YAML reads like a config file. Reframing it as Gleipnir — a binding _whose strength comes from the composition of light, paradoxical, individually-soft constraints_ — makes the design philosophy legible. It also gives the user the right intuition for failure modes: a Gleipnir-binding fails when one of its ingredients turns out to exist in the world (the sound of a cat's footfall becomes audible — i.e. an assumption the rule depended on no longer holds).

**Specific mapping.** Reframe the comfort-posture documentation around the Gleipnir metaphor. Each rule in the YAML names which "ingredient" it provides. The dashboard's posture view shows the six ingredients explicitly, with which rules contribute to each. The binding-strength is shown _as the composition_, not as a single number. When a rule is removed, the UI shows _which ingredient is now missing from Gleipnir_ — making posture decay visible rather than invisible.

This pairs directly with **Fenrir** (the bound danger) and **Týr** (the cost paid to bind).

**Verdict: Strong fit — strongest of the roster.**

---

### The Aesir-Vanir War

**Myth.** Two tribes of gods fought, ended in stalemate, sealed peace via hostage exchange (Njörðr/Freyr/Freyja to Aesir; Mímir/Hænir to Vanir) and by spitting jointly into a vat from which Kvasir was born.

**Feature-fit.** "Two tribes that reconciled via hostage exchange" is the metaphor for **cross-plugin dependency declarations**. E.g. `finance` requires `ravenclaude-core@>=0.5.0` — the core is the hostage. This is interesting structurally but doesn't need a name; the `requires:` syntax is already self-explanatory.

**Verdict: Thin — skip.** Possibly use the war as a frame in architecture docs to explain why cross-plugin dependencies exist, but not as a feature.

---

### Mead of Poetry (Óðrœrir)

**Myth.** Kvasir (born from the Aesir-Vanir spit-vat) was the wisest being. The dwarves Fjalar and Galar murdered him and brewed his blood with honey into the Mead of Poetry. Whoever drinks it becomes a skald.

**Feature-fit.** Inspiration-from-distilled-wisdom maps loosely to the existing `prompt-engineer` agent and the documentarian. No new feature claims it.

**Verdict: Thin — skip.** Lovely myth, no surface.

---

### Ratatoskr

**Myth.** Squirrel who runs up and down Yggdrasil carrying slanderous messages between the eagle at the crown and Níðhöggr at the root, deliberately inflaming their mutual hatred.

**Feature-fit.** Cross-plugin / inter-agent message-passing has a real surface in RavenClaude (the Structured Output Protocol that returns from a subagent, the cross-plugin dispatch pattern). Calling that "Ratatoskr" is amusing but the squirrel is _slanderous_ — the messenger _distorts_ — which is the opposite of what we want subagent communication to do.

**Verdict: Thin — skip.** The myth's content is wrong-direction for the feature it might fit.

---

### Níðhöggr

**Myth.** Dragon at Yggdrasil's deepest root. Gnaws at the tree from below. Feeds on the corpses of the dishonored dead.

**Feature-fit.** **Technical debt that gnaws at the foundations.** The marketplace has best-practices docs, lessons-learned, and a decision log — none of which directly enumerate "the slow-rotting bits at the bottom that need attention." A Níðhöggr panel in the dashboard listing the marketplace's known tech-debt items (deprecated patterns still in use, plugins that haven't been version-bumped in N months, hook scripts that don't have a corresponding CI gate, TODOs in commits) would be more useful than the current absence.

**Verdict: Worth exploring.** Reasonable feature; needs a small build (a TODO/debt scanner + a panel).

---

### The Nine Realms

**Myth.** _Níu Heimar_ — the conventional nine being Asgard, Vanaheim, Midgard, Jötunheim, Alfheim, Svartalfheim/Niðavellir, Niflheim, Muspelheim, Helheim. The exact list is a modern synthesis; primary sources don't enumerate.

**Feature-fit.** Tempting mapping: **each plugin is a realm.** `ravenclaude-core` is Asgard (sovereign team), `power-platform` is one of the elf-realms (specialist craft), `finance` is its own realm, etc. The nine-realms naming gives the marketplace a navigable cosmology — but only if there are _roughly_ nine plugins, and if their identities map cleanly. Today there are six plugins and the mapping is forced.

The reverse risk: locking the count at nine is gimmicky (do we stop adding plugins?), and assigning realm-names to each plugin (Asgard, Vanaheim, etc.) becomes work to maintain.

**Verdict: Worth exploring — as flavor, not structure.** Use "the realms" as a collective name for the plugin set in marketing/copy. Do not enforce a count or assign a fixed realm to each plugin.

---

## 5. Ranked shortlist — strongest 3-6 additions worth pursuing

In priority order. Each is a feature the metaphor _earns_, not decorates.

| # | Addition | One-line rationale |
|---|---|---|
| **1** | **Gleipnir** — reframe comfort-posture as a binding-of-paradoxes | Strongest single fit. Names what posture _is_ (composition of light constraints producing unbreakable binding) and makes posture-decay visible. Pairs natively with Fenrir + Týr. |
| **2** | **Yggdrasil view** — interactive marketplace-as-world-tree visualization | Gives users one canonical mental model for the marketplace structure with the three wells (lessons / decisions / proposals) as the roots. Becomes the spine the rest of the theming hangs from. |
| **3** | **The Norns panel** — Urðr / Verðandi / Skuld view per plugin | Past (lessons + git log) / present (current version) / future (proposals) in three columns. Maps onto existing artifacts; collapses three browses into one glance. |
| **4** | **Heimdall surface** — unified perimeter-alarm dashboard | Bundles the layout hook, CI gates, deny-verdict hooks, and Gjallarhorn-style "loud" warnings under one identity. Distinct from Huginn/Muninn (out-scouting vs at-the-gate). |
| **5** | **Mímir's well + Mímir's head** — naming the knowledge bank and the memory subsystem | Two complementary surfaces under one figure: deep static knowledge (the well) and retained-conversation context (the speaking head). Better names than "knowledge base" + "memory system." |
| **6** | **Sleipnir** — naming the worktree-traversal capability | Cheap, natural, and gives a user-friendly name to an infrastructure layer (worktrees) that currently feels mechanical. "Send Sleipnir to that branch." |

**Honorable mentions worth a second look later:**

- **Fenrir** (the bound danger lane in posture — strong, but only lands once Gleipnir is in place)
- **Bifröst** (the install bridge — strong but small surface)
- **Mjölnir** (release blessing — strong if releases are centralized)
- **Ragnarök** (DR/reset — only if a real reset workflow gets scoped)
- **Níðhöggr** (tech-debt panel — small build, real value)

**Explicit skips** (with rationale):

- Freyja, Frigg, Loki (as agent), Bragi, Idunn, Njörðr, Skaði, Víðarr, Freyr, Höðr/Váli, Gungnir, Jörmungandr, Hel, Valhalla, Fólkvangr, the Aesir-Vanir war, Mead of Poetry, Ratatoskr — either no current surface (most), redundant with an existing role (Bragi/documentarian), or carries the wrong directional meaning (Ratatoskr distorts; we want fidelity).

---

## 6. Discipline — coherence over decoration

The shortlist above passes a single test: **does the name make the thing easier to understand?** Every entry on it does. Every skip failed it.

A few principles to keep the theming from drifting into gimmick:

1. **One myth per surface; one surface per myth.** If Heimdall is the perimeter alarm, no other feature is Heimdall. If Gleipnir is posture-composition, no other feature is Gleipnir. Proliferation kills metaphor.

2. **The name must shorten the explanation.** "Mímir's well = the knowledge bank" is shorter and more memorable than "the knowledge bank." "Bragi = the documentarian agent" adds a syllable and tells you less. Reject any name that lengthens the doc.

3. **The myth's _content_ has to point the right way.** Ratatoskr is a tempting name for inter-agent messaging until you remember he _slanders_ — the metaphor pushes the user's intuition in exactly the wrong direction. Refuse those.

4. **The user is Odin.** Hliðskjálf, Huginn, Muninn, Gungnir are the user's instruments. Building an "Odin agent" steals the seat the user sits in. Keep the seat clear.

5. **Cite the myth in copy at least once.** A one-sentence "Gleipnir was forged from six impossible things — your posture binding is the same idea" in the docs is what teaches the metaphor. Without that line, users get a name they don't recognize. With it, the name carries weight forever.

6. **Skip is a valid verdict.** Most of this roster is "thin — skip." That's the correct ratio. A pantheon with three loud myths in active service does more work than one with twenty quiet ones decorating the corners.

---

## 7. Sources

Cross-checked against the _Poetic Edda_ (especially _Völuspá_, _Grímnismál_, _Lokasenna_, _Skírnismál_, _Þrymskviða_, _Sigrdrífumál_), Snorri Sturluson's _Prose Edda_ (_Gylfaginning_ and _Skáldskaparmál_), and modern reference summaries (Wikipedia, Norse Mythology for Smart People, World History Encyclopedia, Mythopedia). Notable specific source URLs:

- Yggdrasil — <https://en.wikipedia.org/wiki/Yggdrasil>
- Norns + Urðarbrunnr — <https://en.wikipedia.org/wiki/Norns>, <https://en.wikipedia.org/wiki/Ur%C3%B0arbrunnr>
- Mímir + Mímisbrunnr — <https://en.wikipedia.org/wiki/M%C3%ADmir>, <https://en.wikipedia.org/wiki/M%C3%ADmisbrunnr>
- Ragnarök — <https://en.wikipedia.org/wiki/Ragnar%C3%B6k>
- Bifröst — <https://en.wikipedia.org/wiki/Bifr%C3%B6st>
- Heimdall — <https://en.wikipedia.org/wiki/Heimdall>
- Gleipnir + the binding of Fenrir — <https://en.wikipedia.org/wiki/Fenrir>, <https://norse-mythology.org/tales/the-binding-of-fenrir/>
- Týr — <https://en.wikipedia.org/wiki/T%C3%BDr>
- Sleipnir — <https://en.wikipedia.org/wiki/Sleipnir>
- Mjölnir — <https://en.wikipedia.org/wiki/Mj%C3%B6lnir>
- Æsir–Vanir War + Mead of Poetry — <https://en.wikipedia.org/wiki/%C3%86sir%E2%80%93Vanir_War>, <https://en.wikipedia.org/wiki/Mead_of_poetry>
- Forseti — <https://en.wikipedia.org/wiki/Forseti>
- Norse cosmology + nine realms — <https://en.wikipedia.org/wiki/Norse_cosmology>

Source disagreements were preserved in entries where they matter (e.g. Yggdrasil's three roots have two competing maps in the _Prose Edda_ vs. _Grímnismál_; the nine-realms list is a modern synthesis rather than a canonical enumeration).
