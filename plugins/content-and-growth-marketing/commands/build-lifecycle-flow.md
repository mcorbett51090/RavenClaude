---
description: "Design a segmented, behavior-triggered lifecycle flow with deliverability baked in: the trigger and entry/exit criteria, the segmentation, the message steps, and the metrics that matter."
argument-hint: "[the flow to build (welcome/nurture/onboarding/win-back) + audience + current funnel/deliverability state]"
---

You are running `/content-and-growth-marketing:build-lifecycle-flow`. Use `lifecycle-marketing-engineer` + the `lifecycle-and-email` skill.

## Steps
1. Place the flow in the lifecycle map (acquisition → activation → nurture → conversion → retention → reactivation) and name the funnel stage it serves.
2. Define the trigger, entry/exit criteria, branching on behavior, and suppression rules. If you can't name the trigger and exit, it's a broadcast — reshape it.
3. Define the segmentation that personalizes the flow and the message steps + content slots (route the copy to `content-strategist`).
4. Bake in deliverability: SPF/DKIM/DMARC authentication, list hygiene + sunset policy, sender-reputation/engagement plan. Fix deliverability before optimizing copy.
5. Instrument the flow: inbox placement, clicks, conversion, engaged-list health, revenue per recipient — never opens alone. Diagnose any funnel leak stage-by-stage.
6. Route the rest: A/B variants → experimentation-growth-engineering; forms/landing pages → web-design; attribution/warehouse → data-platform; consent/PII → data-governance-privacy.
7. Emit the lifecycle-flow spec + the Structured Output block (with `Funnel stage served:` and `Handoff to build/measurement:`).
