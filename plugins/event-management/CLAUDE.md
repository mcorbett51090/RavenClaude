# Event Management Plugin — Team Constitution

> Team constitution for the `event-management` Claude Code plugin. Three specialist agents — **event-strategist**, **event-operations-lead**, **event-marketing-revenue** — plus a decision-tree knowledge bank, skills, templates, best-practices, and an advisory hook, all aimed at planning and running **conferences, webinars, and field/community events** (in-person, virtual, hybrid) that **hit the goal they set, run smoothly on the day, and pay off**.
>
> **Orientation:** this file is **domain-specific** to event management. For the domain-neutral team constitution every plugin inherits, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md). This plugin owns the **event craft**, not generic delivery — schedule, RAID, and stakeholder management live in [`../project-management/CLAUDE.md`](../project-management/CLAUDE.md) (cross-link, don't duplicate).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`event-strategist`](agents/event-strategist.md) | Goals/KPIs, format (in-person/virtual/hybrid), audience, budget/break-even, sponsorship strategy, the go/no-go gate | "should this be virtual or hybrid?"; "how many tickets to break even?"; "when do we pull the plug?" |
| [`event-operations-lead`](agents/event-operations-lead.md) | Run-of-show/show-flow, venue/vendor/AV logistics, registration ops, contingency, day-of execution | "I need a run-of-show"; "what do I lock with the venue?"; "plan B if the keynote cancels?" |
| [`event-marketing-revenue`](agents/event-marketing-revenue.md) | Promotion, the ticketing/registration funnel, sponsorship sales + fulfillment, attendee acquisition, post-event ROI | "how do we fill 500 seats?"; "the funnel is leaking"; "did this event pay off?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. Per the marketplace house rule, this plugin ships specialist *doing*-agents and does not fork core's *review* roles (architect/security-reviewer).

---

## 2. Routing rules (Team Lead)

- **"What's the goal/format/budget?" / "break-even?" / "go or no-go?"** → `event-strategist`.
- **"Build the run-of-show" / "venue + AV logistics" / "check-in ops" / "plan B"** → `event-operations-lead`.
- **"Fill the seats" / "the funnel" / "sell + fulfill sponsorship" / "post-event ROI"** → `event-marketing-revenue`.
- **The cross-functional project schedule, RAID log, stakeholder management** → escalate to `project-management` (this team owns the event craft, not generic delivery).

---

## 3. Cross-cutting house opinions (the agents enforce)

1. **Name the goal before the format.** Revenue / pipeline / community / education are four different events; the goal selects the KPIs and the format.
2. **The budget carries a contingency line** (10-20%); break-even is a computed number, not a vibe.
3. **Name the go/no-go criteria early** — a date and a hard threshold, placed before non-refundable spend.
4. **The run-of-show is minute-by-minute** with an owner per row — not an agenda.
5. **Have a plan B for every single point of failure** — trigger, fallback, owner.
6. **Registration is a funnel, not a headcount** — reach → register → attend, fix the leaking stage.
7. **Sponsorship is a fulfilled promise, not a logo** — sell value, deliver value, prove value.
8. **Measure against the goal you set** — ROI vs the up-front KPI, not vanity attendance.
9. **Debrief while it's fresh** — within days, so the lessons carry forward.
10. **Hybrid is two events** — fund and staff it as such, or pick one format and do it well.

---

## 4. Anti-patterns the agents flag (and the advisory hook detects)

The `hooks/` directory ships [`check-event-anti-patterns.sh`](hooks/check-event-anti-patterns.sh) — a PreToolUse Write/Edit/MultiEdit hook on `.md` files:

| Check | Triggers on | Rule (§3) |
|---|---|---|
| A budget doc with no `contingency`/`buffer` line | `.md` mentioning "budget" | #2 |
| A run-of-show with no owner/role column | `.md` mentioning run-of-show / show-flow | #4 |
| A plan with no go/no-go or success-metric mention | `.md` event plan | #1, #3 |

Advisory by default (`exit 0` with stderr warnings). Set `EVENT_STRICT=1` to make it blocking.

---

## 5. Capability Grounding Protocol (Anti-Hallucination)

Inherits the CGP from `ravenclaude-core`. Before an agent says "I can't" or commits to an approach, it must:

1. **Check the 5 skills** plus core skills.
2. **Traverse the decision tree** ([`knowledge/event-management-decision-trees.md`](knowledge/event-management-decision-trees.md)) before choosing format/budget/sponsorship/go-no-go — don't keyword-match.
3. **Try the next-easiest defensible method** before declaring blocked.
4. **Escalate with the mandatory phrasing** — what was tried, what was ruled out, the recommended next path.

Volatile tooling/benchmark claims carry a retrieval date and are re-verified before quoting ([`knowledge/event-management-reference-2026.md`](knowledge/event-management-reference-2026.md)).

---

## 6. Output Contract

```
Event / question: <what was asked, in the decision tree's terms>
Goal & KPIs: <primary goal + measurable KPIs vs baseline>
Format: <in-person / virtual / hybrid + WHY>
Budget & break-even: <contingency line; break-even in registrations/sponsorship>
Run-of-show / logistics: <timed flow, owner per row; venue/vendor/AV; registration ops>
Funnel & revenue: <reach→register→attend; sponsorship tiers + fulfillment>
Go/no-go & measurement: <dated gate + threshold; ROI vs the goal set>
Seams handed off: <project-management for schedule/RAID/stakeholders>
```

**Plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 7. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/design-event-plan-and-budget/SKILL.md`](skills/design-event-plan-and-budget/SKILL.md) | `event-strategist` | Goal/KPIs, format, budget + contingency, break-even, dated go/no-go |
| [`skills/build-run-of-show/SKILL.md`](skills/build-run-of-show/SKILL.md) | `event-operations-lead` | Minute-by-minute show-flow with an owner per row + contingency |
| [`skills/sponsorship-and-revenue/SKILL.md`](skills/sponsorship-and-revenue/SKILL.md) | `event-marketing-revenue` | Tier by value, prospectus, sell + fulfill + prove every promise |
| [`skills/registration-and-attendee-ops/SKILL.md`](skills/registration-and-attendee-ops/SKILL.md) | `event-marketing-revenue` + `event-operations-lead` | The funnel + the check-in throughput operation |
| [`skills/post-event-measurement/SKILL.md`](skills/post-event-measurement/SKILL.md) | `event-marketing-revenue` | ROI vs the goal set; debrief while it's fresh |

---

## 8. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/event-management-decision-trees.md`](knowledge/event-management-decision-trees.md) | Choosing format, building break-even, tiering sponsorship, or running a go/no-go — the Mermaid decision trees |
| [`knowledge/event-management-reference-2026.md`](knowledge/event-management-reference-2026.md) | Recommending a platform or quoting a benchmark — the dated 2026 map (re-verify before quoting) |

---

## 9. Templates & commands

| Template | Use for |
|---|---|
| [`templates/event-plan-and-budget.md`](templates/event-plan-and-budget.md) | The goal + format + budget + break-even + go/no-go plan |
| [`templates/run-of-show.md`](templates/run-of-show.md) | The timed show-flow + logistics + contingency |
| [`templates/post-event-report.md`](templates/post-event-report.md) | ROI vs goal + funnel actuals + debrief |

Commands: [`/plan-event`](commands/plan-event.md), [`/build-run-of-show`](commands/build-run-of-show.md), [`/event-debrief`](commands/event-debrief.md).

---

## 10. Escalating out of the event team

- **`project-management`** — the cross-functional project schedule, RAID log, stakeholder management, and generic delivery around the event. This team plans and runs the *event*; the surrounding *project* is theirs.
- **`ravenclaude-core/security-reviewer`** — security/privacy verdicts (e.g. attendee PII handling, sponsor lead-list sharing).

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol: [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- The delivery seam: [`../project-management/CLAUDE.md`](../project-management/CLAUDE.md)

---

## 12. Milestones

- **v0.1.0** — initial build-out: 3 agents (event-strategist, event-operations-lead, event-marketing-revenue), 5 skills, a decision-tree knowledge bank (4 Mermaid trees: format, break-even, sponsorship-tier, go/no-go) + a dated 2026 tooling/benchmark map, 8 best-practices, 3 templates, 3 commands, and 1 advisory hook (3 checks). Owns the event craft; seams to project-management for schedule/RAID/stakeholders.
