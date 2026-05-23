# Nine Realms → Dashboard Mapping — Reassessment

**Date:** 2026-05-23
**Author:** Re-research pass on a specific question from the broader Norse-mythology ideation.
**Status:** Assessment / not a build plan. Single verdict + a narrowly-scoped alternative.
**Relates to:** `docs/norse-mythology-feature-map.md` (the parent ideation pass, §4 "The Nine Realms"), `docs/dashboard-buildout-plan.md` (the dashboard's planned IA — 7 tabs).

---

## 1. Why this doc exists

The parent ideation map gave the Nine Realms a soft verdict: _"Worth exploring — as flavor, not structure. Use 'the realms' as a collective name for the plugin set. Do not enforce a count or assign a fixed realm to each plugin."_ The framing there was **plugins-as-realms**.

The question now is different: can the **dashboard itself** — its tabs, zones, or conceptual organization — be usefully mapped onto the nine realms? This doc re-researches the realms accurately and tests the mapping against the actual planned dashboard, then issues a clear verdict.

I am genuinely re-examining, not rubber-stamping. The prior verdict survives, but with a sharper rationale and a more concrete alternative form than the parent doc offered.

---

## 2. The Nine Realms — what they actually are

### 2.1 The canonical-list problem (state this honestly)

The phrase _níu heimar_ ("nine worlds") appears in the _Poetic Edda_ — most explicitly _Völuspá_ stanza 2: "níu man ek heima, níu íviðjur" ("nine worlds I remember, nine giantesses-of-the-wood"). **The Eddas never actually enumerate all nine.** The list everyone cites today is a modern scholarly synthesis assembled from scattered references in _Grímnismál_, _Lokasenna_, _Völuspá_, and Snorri Sturluson's _Prose Edda_ (_Gylfaginning_, c. 1220).

Any design that leans on "the nine" as if it were a fixed catalog is leaning on a 19th–20th-century reconstruction, not Viking-Age doctrine. That doesn't make the synthesis wrong; it does make claims of mythological authority weaker than they sound.

### 2.2 The conventional modern list

| # | Realm | Inhabitants | Character | Relation to Yggdrasil |
|---|---|---|---|---|
| 1 | **Asgard** | Aesir gods (Odin, Thor, Heimdall) | Sovereign order, war, governance | Highest reaches; one of Snorri's three-root destinations (Well of Urðr) |
| 2 | **Vanaheim** | Vanir gods (Freyr, Freyja, Njörðr) | Fertility, foresight, older nature-magic (_seiðr_) | High but vaguely placed — location inferred from context, never stated |
| 3 | **Midgard** | Humans | The middle, the inhabited world — order's outpost surrounded by wilderness | At the trunk; encircled by Jörmungandr; linked to Asgard by Bifröst |
| 4 | **Jötunheim** | Jötnar (giants) | Untamed forces, chaos, the "other" the gods continually defend against | Beyond Midgard; one root reaches it (Mímir's well sits there, in Snorri's mapping) |
| 5 | **Alfheim** | Light-elves (_ljósálfar_) — ruled by Freyr | Light, beauty, beneficence | Upper reaches; barely described in any source |
| 6 | **Svartalfheim / Niðavellir** | Dwarves (and Snorri's "dark elves," _svartálfar_) | Craft, smithy, hidden treasure | Beneath the earth, among the roots |
| 7 | **Niflheim** | None civilized | Primordial mist, ice, cold; spring of Hvergelmir | One of the three root-destinations; predates the ordered cosmos |
| 8 | **Muspelheim** | Surtr and his fire-jötnar | Primordial fire; will burn the cosmos at Ragnarök | Mirror to Niflheim; also predates the ordered cosmos |
| 9 | **Helheim** | The dead who did _not_ fall in battle | Underworld — residence, mostly, not punishment | Below, beyond a river and a wall; one root reaches it in Grímnismál's mapping |

### 2.3 Variants worth surfacing

- **Svartalfheim vs. Niðavellir** are arguably the _same realm_ under two names — Snorri's "Svartalfheim" terminology blurs into "Niðavellir" ("dark fields") in older sources. Some modern lists pick one; some count both, dropping another realm to keep nine.
- **Muspelheim and Niflheim** predate the ordered nine in the creation myth; some scholars treat them as pre-cosmic rather than fully part of the nine.
- **Vanaheim** is mentioned but never described physically — its inclusion is by inference.
- **Helheim and Niflhel** are sometimes conflated, sometimes distinguished (Niflhel as the deeper, punitive level _within_ Helheim).
- **Yggdrasil's three roots have two competing mappings:**
  - _Grímnismál_ (older, Poetic Edda): roots reach **Hel, Jötunheim, Midgard**.
  - _Gylfaginning_ (Snorri, Prose Edda): roots reach **Asgard (Well of Urðr), Jötunheim (Mímir's well), Niflheim (Hvergelmir)**.
  - Snorri's is more symmetrical and is what most modern art depicts. The older mapping is messier and gives a different cosmic logic.

The point of surfacing all this is not pedantry; it's that **claiming a precise nine-to-N mapping leans on a list that the primary sources themselves did not fix.** Any design built on it is building on a modern scholarly consensus, not bedrock.

### 2.4 Structural relationships (the part that matters for mapping)

- **Primordial opposites:** Muspelheim (fire) ↔ Niflheim (ice).
- **Divine dynasties:** Asgard (Aesir, sovereign order) ↔ Vanaheim (Vanir, fertility/foresight).
- **Beings-of-craft hierarchy:** Alfheim (light-elves, beneficent) ↔ Svartalfheim (dwarves/dark-elves, subterranean craft).
- **Mortal axis:** Midgard at the center; Jötunheim surrounds it (chaos pressing in); Asgard above (order overseeing).
- **Death:** Helheim distinct from Niflheim, but the boundary is fuzzy.

These pairings are real and load-bearing in the myth. They are also _strongly oppositional_ (fire/ice, gods/giants, light/dark) — a logic of **polarity**, not a logic of **functional partition**.

---

## 3. The dashboard — what it actually is

Per `docs/dashboard-buildout-plan.md` §B.1, the planned dashboard has **7 tabs**:

| Tab | Purpose | Already mythologically claimed? |
|---|---|---|
| **Settings** | Comfort-posture editor + per-agent toggles + scope selector | Gleipnir (per the parent ideation pass) — strongest fit in the roster |
| **Commands** | Slash-command launcher | (no figure assigned) |
| **Trees** | Worktree visualizer | Sleipnir (parent pass — cross-realm mobility) |
| **Activity** | Recent agent/hook events | (no figure assigned — Víðarr was considered and skipped) |
| **Install** *(new)* | Onboarding walkthrough | Bifröst (parent pass — the install bridge) |
| **Agents** *(new)* | Per-agent enable/configure | (no figure assigned) |
| **Health** *(new, stretch)* | Diagnostics + permission visualizer | Heimdall (parent pass — perimeter alarms) |

Two cosmological frames are also already in motion:

- **Hliðskjálf** — _the dashboard itself_ (the high seat). The dashboard isn't a thing _on_ Hliðskjálf; it _is_ Hliðskjálf.
- **Yggdrasil view** — a planned structural visualization showing the marketplace as a world-tree (plugins as branches, agents as leaves, lessons/decisions/proposals at the three roots).

So when we ask "can the nine realms map to dashboard areas?" we are already operating inside a cosmology where the dashboard is the throne and the marketplace is the tree. The realms would need to slot into _that_ existing geometry.

---

## 4. The mapping attempts — does any of them actually help?

I'll test four candidate mappings, from most-literal to most-flexible.

### 4.1 Tabs ↔ realms, 1:1

| Tab | Forced realm | Honest fit |
|---|---|---|
| Settings | Asgard (governance) | Forced — Asgard is sovereign authority, Settings is config |
| Commands | Midgard (where users live and act) | Plausible-ish — Commands is the daily-use surface |
| Trees | Jötunheim (the wilds outside Midgard) | Stretched — worktrees are isolated copies, not chaos |
| Activity | Helheim (record of the past) | Decorative — Activity is a live log, not a realm of the dead |
| Install | Bifröst — but Bifröst isn't a realm | Doesn't even fit the schema |
| Agents | Alfheim (beneficent helpers) | Vague |
| Health | Vanaheim (foresight) | Backwards — Health is diagnostic, not prophetic |

**Verdict on 1:1: fails.**

- The arithmetic is wrong: 7 tabs, 9 realms — one of them already "claimed" by Bifröst (the bridge to Midgard, not a realm of its own). To preserve nine you have to invent two tabs to fill Niflheim/Muspelheim/Svartalfheim, or drop two realms and admit you're using "selected realms" rather than "the nine."
- The grammars don't match: each tab is a _verb-noun_ ("Install something," "Configure agents," "Launch commands") whereas each realm is a _noun-place_ ("home of the giants," "home of the dwarves"). You can name a place after a function (Asgard = governance) but the metaphor strains the moment a user expects realm-shaped content (who lives there? what do you do when you visit?).
- The pairings that give the realms their mythological weight (fire/ice, light/dark, Aesir/Vanir) have no analogue in the dashboard's functional tabs. Asgard-vs-Vanaheim has nothing to say about Settings-vs-Health.

This is exactly the failure mode the parent ideation pass warned against: "Locking the count at nine is gimmicky… assigning realm-names to each plugin becomes work to maintain." The same applies to tabs.

### 4.2 Realms as conceptual zones (grouping, not 1:1)

What if the realms group the tabs?

- **Asgard zone** (sovereign / admin): Settings, Install
- **Midgard zone** (daily work): Commands, Trees
- **Jötunheim zone** (perimeter / wild): Health
- **Helheim zone** (records): Activity
- **Alfheim zone** (helpers): Agents

That uses 5 realms; 4 are unused (Vanaheim, Svartalfheim, Niflheim, Muspelheim). Either we drop them — at which point we are no longer doing "the nine" — or we invent placeholder zones to keep the count. The first is honest but defeats the premise. The second is gimmick.

Also: a zone-grouping atop the tab bar adds a layer of nav (zone → tab → content) for ~7 destinations. UX cost without UX benefit.

**Verdict on zones: fails — better than 1:1, still strained.**

### 4.3 Realms as an overlay on the Yggdrasil view

The parent pass already endorses a "Yggdrasil view" — an interactive marketplace-as-world-tree visualization. Could the nine realms be a layer on top of that view, marking _where in the tree each kind of feature lives_? E.g.:

- Asgard (canopy) = the governance plugins (`ravenclaude-core`)
- Vanaheim (canopy, off to one side) = specialist-craft plugins (`power-platform`, `finance`)
- Midgard (trunk) = the marketplace itself
- Svartalfheim (roots) = hooks, scripts, the smithy
- Niflheim (deepest root) = lessons-learned + decision log (cold, ancient memory)
- Helheim (sideways from the deep) = archived/deprecated plugins
- Muspelheim (south, off-tree) = destructive ops (Ragnarök / plugin reset)

This is the **strongest version** of the idea, because:

- It piggybacks on a visualization already planned (Yggdrasil view) — no new surface to maintain.
- It uses realms _where they actually fit_ and quietly drops the ones that don't (Vanaheim and Alfheim, in honesty, have less to add).
- It respects the realms' character (Niflheim _is_ cold ancient memory; Helheim _is_ where things go when they didn't die heroically — i.e. deprecated; Muspelheim _is_ destructive primordial fire).
- It doesn't promise users "nine destinations" they can navigate to. The realms are a _legend on a map_, not a tab bar.

**Verdict on overlay: this is the version worth considering** — but with discipline (next section).

### 4.4 Realms as marketing/copy-only

The parent pass's verdict. "The realms" as a collective name for the plugin set, used in user-facing copy without enforcement. Cheap, low-maintenance, no information-architecture impact. The cost is near-zero and the benefit is near-zero. Fine as a fallback.

---

## 5. Verdict

**Skip the 1:1 tabs-as-realms mapping. Skip the zones-as-realms grouping.** Both fail the test the parent ideation pass set out: "does the name make the thing easier to understand?" Forcing nine destinations on a seven-tab dashboard makes the dashboard harder to understand, not easier — and the count itself rests on a modern synthesis the primary sources never fixed.

**This does not differ in direction from the prior verdict.** The parent doc said "flavor, not structure," and that holds. What this re-research adds:

1. **A sharper reason for the skip.** The realms are a _polarity_ system (fire/ice, gods/giants, light/dark), not a _partition_ system. Dashboard tabs are a partition. Mapping one onto the other discards exactly the structural feature that makes the realms meaningful.

2. **A concrete alternative form that does work** — the overlay-on-Yggdrasil approach in §4.3. The parent doc gestured at "use 'the realms' as a collective name." This sharpens that into: **on the planned Yggdrasil-view visualization, label regions of the tree with the realm names that genuinely fit (Asgard, Midgard, Svartalfheim, Niflheim, Helheim, Muspelheim — six, not nine), and leave the rest unused.** This is consistent with the parent pass's "one myth per surface; one surface per myth" discipline and with the discomfort of forcing a count the sources don't support.

3. **A discipline to apply if the overlay is built.** Three rules, all derived from the parent pass's principles:
   - **Only realms that point the right way.** Niflheim _earns_ cold-ancient-memory because that _is_ what Niflheim is. Vanaheim doesn't earn anything because Vanaheim is a place we know little about; using it for "specialist plugins" is decoration.
   - **Six (or however many) is the honest number, not nine.** Refusing to invent uses for realms that don't fit is a strength, not a failure. The primary sources themselves refused to list all nine.
   - **The realm name is a label on the map, not a route in the URL.** No realm becomes a tab. No realm becomes a sub-page. If a user clicks the "Svartalfheim" label on the Yggdrasil view, they should see the existing hooks/scripts surface, not a separate realm-themed page.

---

## 6. What the answer would have to look like to overturn the skip

For completeness — what _would_ make a full nine-realms mapping work?

- A dashboard with ~9 genuinely distinct destinations, each with a noun-place character (not a verb-noun function).
- A reason to surface oppositions (fire/ice, light/dark) that maps onto a real product tension.
- A user base that already shares the Norse vocabulary so the realm names _shorten_ explanation rather than lengthen it.

The RavenClaude dashboard satisfies none of these. The realms remain a vivid backdrop, not a viable IA.

---

## 7. Recommendation in one paragraph

Maintain the parent doc's skip on a literal nine-realms dashboard mapping; do not force tabs or zones into a nine-slot structure. Instead, **when the Yggdrasil-view visualization is built, label its regions with the 5–6 realm names that genuinely fit the content already there (Asgard for governance, Midgard for the marketplace trunk, Svartalfheim for hooks/smithy, Niflheim for cold-storage memory like lessons + decision log, Helheim for deprecated plugins, optionally Muspelheim for destructive/reset operations).** Use fewer realms honestly rather than nine awkwardly. Cite once in copy that the labels are a deliberate selection from the modern-synthesis nine, not the full set — that honesty is itself part of the metaphor.

---

## 8. Sources

- _Poetic Edda_ — _Völuspá_ stanza 2 ("níu man ek heima"), _Grímnismál_ on Yggdrasil's roots, _Lokasenna_ on Vanaheim.
- Snorri Sturluson, _Prose Edda_ (_Gylfaginning_, c. 1220) — the systematized cosmology and the three-roots-three-wells mapping.
- Wikipedia: <https://en.wikipedia.org/wiki/Norse_cosmology>, <https://en.wikipedia.org/wiki/Yggdrasil>, <https://en.wikipedia.org/wiki/Nine_Worlds>, and individual realm pages.
- Norse-mythology.org's cosmology survey (<https://norse-mythology.org/cosmology/the-nine-worlds/>) — useful per-realm summaries; explicitly modern synthesis.
- Parent ideation pass: `docs/norse-mythology-feature-map.md` §4 "The Nine Realms" (prior verdict: flavor-not-structure).
- Dashboard plan: `docs/dashboard-buildout-plan.md` §B.1 (7-tab IA: Settings, Commands, Trees, Activity, Install, Agents, Health).
