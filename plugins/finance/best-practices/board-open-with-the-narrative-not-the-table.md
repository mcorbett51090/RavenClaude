# Open with the narrative, close with the ask — a board pack is a story, not a data dump

**Status:** Pattern
**Domain:** Board reporting / narrative structure
**Applies to:** `finance`

---

## Why this exists

A board pack that opens with a table is a request to skim, and a board that skims makes worse decisions. The `board-pack-composer` agent is narrative-first by design: "open with the headline — not the agenda, not the team — the thing the board most needs to know," "one page, one idea," "cash slide before profit slide (cash is closer to mortal)," and "decisions / asks on the last body slide — boards remember the close." The constitution makes it a house opinion (#7, numbers don't ship without commentary; #9, plain English first) and a §4 anti-pattern ("a board pack that opens with a table instead of a narrative summary"). The cost of getting this wrong is a meeting that drifts: without a narrative spine the discussion follows whoever talks loudest, and without an explicit ask the board leaves having decided nothing the company needed decided.

## How to apply

Sequence the pack as a story — headline, then why it matters, then the financial and operating evidence, then the explicit asks — and put detail in the appendix:

```
1. Executive summary    — the headline + why it matters + what we're asking   (narrative, not a table)
2. Cash / runway        — cash before profit; the "we run out here" date if applicable
3. Financial summary    — variance commentary IN LINE with the table, not in a separate section
4. Operating KPIs       — 5-7 max on the front pages (KPI cards: trend + number + one-sentence read)
5. Decisions / asks      — the last body slide; the specific calls the board has authority over
6. Appendix             — evidence, detail, back-up; the safety net, not the body
Every slide title says what it MEANS ("Q3 revenue beat plan on enterprise upsell"), not what it is ("Q3 revenue").
Confidentiality/status mark on every page; pre-read 48-72h before the meeting.
```

**Do:**
- Lead each section and the pack as a whole with the **meaning**, then the number — slide titles assert a conclusion, not a label.
- Cap front-page KPIs at **5–7** as cards (trend + single number + one-line read); push the rest to the appendix.
- End the body with explicit **decisions / asks** the board can actually action, and place variance commentary *in line* with its table.

**Don't:**
- Open with a table, an agenda, or the team — open with the headline (named §4 anti-pattern).
- Bury or omit the cash slide, or split variance commentary into a separate section from its table (forces context-switching).
- Change a KPI definition between periods without a footnote, or ship a draft with no confidentiality/status mark.

## Edge cases / when the rule does NOT apply

- **Audience reshapes framing, not structure** — a founder board, a PE board, and a lender read the same data differently; adapt the emphasis and the asks, but the narrative-first / cash-first / ask-last spine holds for all.
- **A lender or covenant pack** leads with covenant compliance and the borrowing-base certificate rather than an operating headline — the "open with what the reader most needs" principle is the same, applied to a different reader.
- **A one-number flash** (a single KPI update between board cycles) is not a full pack and does not need the full arc — but the moment it becomes the quarterly pack, the structure attaches.

## See also

- [`./reconcile-before-you-narrate.md`](./reconcile-before-you-narrate.md) — the variance commentary the pack carries must clear the recon gate first.
- [`./fpa-build-the-variance-bridge-price-volume-mix.md`](./fpa-build-the-variance-bridge-price-volume-mix.md) — the PVM-decomposed commentary that goes in line with the table.
- [`../agents/board-pack-composer.md`](../agents/board-pack-composer.md) — "open with the headline"; "cash before profit"; "decisions/asks on the last body slide"; the open-with-a-table anti-pattern.
- [`../skills/board-pack-composition/SKILL.md`](../skills/board-pack-composition/SKILL.md) — narrative-arc-first assembly, section sequencing, executive-summary patterns.

## Provenance

Codifies the `board-pack-composer` agent's narrative-first opinions ("open with the headline," "one page one idea," "cash slide before profit slide," "decisions/asks on the last body slide," slide-titles-say-meaning) and the open-with-a-table anti-pattern ([`../agents/board-pack-composer.md`](../agents/board-pack-composer.md)), plus house opinions #7 and #9 and the §4 anti-pattern "a board pack that opens with a table instead of a narrative summary" ([`../CLAUDE.md`](../CLAUDE.md)). New.

---

_Last reviewed: 2026-05-30 by `claude`_
