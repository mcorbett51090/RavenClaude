# Use Step Functions for multi-step async orchestration, not chained Lambdas

**Status:** Pattern
**Domain:** AWS compute / event-driven
**Applies to:** `aws-cloud`

---

## Why this exists

Chaining Lambdas by having one invoke another synchronously creates hidden tight coupling: the caller waits, the callee's failure is the caller's failure, retries are bespoke, and the execution path is invisible unless you read code. Step Functions makes the workflow the artifact — state transitions, retry strategies, error handling, parallel branches, and wait-for-callback are first-class, observable, and recoverable without code changes. Long-running business processes (order fulfillment, ETL pipelines, human approval gates) belong in Step Functions, not in Lambda-invokes-Lambda chains.

## How to apply

Key Step Functions patterns:

| Pattern | Use | State type |
|---|---|---|
| Sequential pipeline | Steps that must run in order with dependencies | `Task` → `Task` |
| Retry with backoff | Transient failures (API calls, DB writes) | `Retry` block on `Task` |
| Error handling | Branch on failure type | `Catch` block + `Fail` state |
| Parallel processing | Fan-out to independent branches | `Parallel` state |
| Human approval gate | Pause until a token is returned | `Task` with `waitForTaskToken` |
| Map over items | Process each item in a list | `Map` state |

```json
{
  "Comment": "Order fulfillment workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123:function:validate-order",
      "Retry": [
        {
          "ErrorEquals": ["Lambda.ServiceException", "Lambda.TooManyRequestsException"],
          "IntervalSeconds": 2,
          "MaxAttempts": 3,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["ValidationError"],
          "Next": "RejectOrder"
        }
      ],
      "Next": "ChargePayment"
    },
    "ChargePayment": { "Type": "Task", "Resource": "...", "Next": "FulfillOrder" },
    "FulfillOrder": { "Type": "Task", "Resource": "...", "End": true },
    "RejectOrder": { "Type": "Task", "Resource": "...", "End": true }
  }
}
```

**Do:**
- Use Express Workflows for high-volume, short-duration (< 5 min) flows; Standard Workflows for long-running, durable, auditable flows (order, approval, ETL).
- Define retry strategies and error catchers in the ASL — don't put retry logic in the Lambda.
- Emit custom metrics from Step Functions executions via EventBridge to CloudWatch for SLO tracking.
- Use `waitForTaskToken` for human-in-the-loop steps; the token can be returned days later.

**Don't:**
- Use Lambda-invokes-Lambda synchronously for anything requiring > 2 steps.
- Put business logic in the Step Functions definition — the Lambdas own the logic; the SFN owns the flow.
- Use Standard Workflows for truly high-frequency fan-out (> 1,000/sec) — Express is cheaper.
- Skip execution history review — Step Functions gives you a visual trace of every execution.

## Edge cases / when the rule does NOT apply

- **Pure event-driven, fire-and-forget fan-out** without a multi-step sequential dependency: EventBridge + SNS/SQS is lighter.
- **Simple A→B Lambda chains with no failure modes or parallelism**: a direct Lambda invocation may be acceptable for a pair of steps; re-evaluate when a third step or a retry is needed.

## See also

- [`../agents/aws-compute-platform-engineer.md`](../agents/aws-compute-platform-engineer.md) — owns compute and integration service selection.
- [`./eventbridge-over-direct-coupling.md`](./eventbridge-over-direct-coupling.md) — for decoupled event routing vs sequential orchestration.
- [`./idempotency-and-dlqs-for-async.md`](./idempotency-and-dlqs-for-async.md) — idempotency in the Lambda functions that Step Functions invokes.

## Provenance

Codifies the `aws-compute-platform-engineer` remit in `CLAUDE.md` §1: "Step Functions" as the orchestration option at a selection level. Derives from the AWS serverless application architecture patterns and the difference between orchestration (Step Functions) and choreography (EventBridge) documented in the Serverless Land guide.

---

_Last reviewed: 2026-06-05 by `claude`_
