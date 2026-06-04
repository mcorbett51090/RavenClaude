---
description: "Integrate a PSP correctly: idempotency keys, verified idempotent webhooks, 3DS/SCA, explicit charge state machine."
argument-hint: "[PSP + integration need]"
---

You are running `/fintech-payments-engineering:integrate-payments`. Use `payments-integration-engineer` + the `psp-integration` skill.

## Steps
1. Idempotency key on every money op; model the charge state machine.
2. Verify webhook signatures; handle idempotently + out-of-order (drive state from webhooks).
3. Handle 3DS/SCA and hard-vs-soft declines.
4. Emit (from `templates/charge-state-machine.md` + `webhook-handler.md`) + Structured Output block.
