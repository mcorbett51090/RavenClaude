# Prospecting Message Must Include a Lane-Specific Hook

**Status:** Absolute rule
**Domain:** Freight-forwarding sales
**Applies to:** `freight-forwarding-sales`

---

## Why this exists

"We offer competitive rates, reliable service, and a dedicated account team" is a message that every freight forwarder sends to every shipper, every day. A supply chain manager who receives this message discards it as spam — and they are correct to do so. A message that names the shipper's actual trade lane, references a trigger event (a new sourcing location, a carrier announcement, a trade lane disruption), and leads with a specific proof point — "on the USEC-Vietnam lane, we moved 12% of our FCL volume from transshipment via Singapore to direct Haiphong service and cut average transit by 4 days" — is a message that gets read. The lane-specific hook is what converts outreach from spam to a credible opening.

## How to apply

Before writing any cold or warm prospecting message, build a one-line hook from lane intelligence:

```
Prospecting Hook Builder
─────────────────────────
Target shipper:  ________________
Known trade lane(s):  ________________
Trigger event (if any):  ________________
  Sources:  [ ] Trade press  [ ] Company LinkedIn  [ ] Import/export data (Panjiva, Import Genius)
            [ ] Carrier announcement  [ ] Earnings call / investor release  [ ] Referral

Hook formula:
  "[Specific lane or trade pattern] + [Trigger event or pain point] + [Our proof point or solution]"

Example hook (do not use verbatim — customize):
  "On the China-Chicago lane, service reliability dropped when [carrier X] cut the direct
   service to transhipment in June. We kept three clients on direct USEC discharge and averaged
   26-day transit while the market went to 34+. Worth a quick call if you're moving electronics
   or high-velocity retail on that lane?"

Message length target:  3–5 sentences max for email; 2–3 for LinkedIn.
```

**Do:**
- Research the prospect's actual shipping profile before writing — LinkedIn job postings, import data services, news, and SEC filings all reveal trade lanes, origin countries, and recent supply chain changes.
- Lead with the trigger event, not with the forwarder's capabilities — the trigger event makes the message timely; capabilities make it generic.
- Include a specific, low-friction call to action: "15 minutes this week?" not "let me know if you'd like more information."

**Don't:**
- Send a message with no lane reference, no trigger event, and a generic capability statement — it is spam and it damages the brand.
- Personalize only the greeting ("Hi [First Name]") and leave the body generic — shallow personalization is worse than none because it is detectable.
- Use fabricated "intel" as the hook — if the trigger event is unverified, mark it as a question: "I noticed you may be sourcing from [region] — are you running FCL from there currently?"

## Edge cases / when the rule does NOT apply

Account expansion outreach to an existing customer who already knows the forwarder's capabilities can lead with the customer's performance data or a new service offering rather than a lane hook. The rule applies to cold and warm outreach to prospects with no active commercial relationship.

## See also

- [`../agents/prospecting-outreach-strategist.md`](../agents/prospecting-outreach-strategist.md) — owns prospecting message development and the value-first message framework.
- [`../agents/trade-lane-compliance-advisor.md`](../agents/trade-lane-compliance-advisor.md) — provides lane-level intelligence that enriches the hook.

## Provenance

Codifies CLAUDE.md §3 #9 (personalize or don't send) with a specific hook-building method. The trigger-event-led prospecting message format is standard practice in freight-forwarding and logistics BD training programs [unverified — training knowledge].

---

_Last reviewed: 2026-06-05 by `claude`_
